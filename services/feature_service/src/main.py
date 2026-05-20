import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

# Ensure the parent directory of 'src' is in sys.path to resolve local development paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.config import settings
from src.windows.window_manager import WindowManager
from src.services.feature_builder import FeatureBuilder
from src.redis_store.feature_store import RedisFeatureStore
from src.producers.feature_producer import FeatureProducer
from src.workers.producer_worker import ProducerWorker
from src.workers.consumer_supervisor import ConsumerSupervisor

from src.services.monitoring_service import MonitoringService
from src.monitoring.reporter import MetricsReporter

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("feature_service.main")

# Global instances for startup/shutdown reference inside lifespan
redis_store = None
producer_worker = None
consumer_supervisor = None
reporter_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_store, producer_worker, consumer_supervisor, reporter_task
    logger.info("Starting Aetherion Real-Time Feature Service Pipeline...")

    # 1. Initialize sliding window manager
    window_manager = WindowManager()

    # 2. Initialize feature calculation engine
    feature_builder = FeatureBuilder(window_manager=window_manager)

    # 3. Initialize Redis Feature Store
    redis_store = RedisFeatureStore()

    # 4. Initialize async Kafka producer
    producer = FeatureProducer()

    # 5. Initialize the pipeline dispatch worker
    producer_worker = ProducerWorker(redis_store=redis_store, producer=producer)

    # 6. Initialize consumer supervisor with pipeline references
    consumer_supervisor = ConsumerSupervisor(
        window_manager=window_manager,
        feature_builder=feature_builder,
        producer_worker=producer_worker,
    )

    # 7. Initialize Monitoring Service with live instances for readiness checks
    MonitoringService.initialize(
        redis_store=redis_store,
        producer=producer,
        consumer_supervisor=consumer_supervisor
    )

    logger.info("Connecting to core datastores (Redis & Kafka)...")

    # Connect to Redis
    redis_connected = await redis_store.connect()
    if not redis_connected:
        logger.warning(
            "Could not connect to Redis Feature Store on startup. "
            "Pipeline will boot, but caches will be disabled until reconnected."
        )

    # Start Kafka Producer connections through the dispatcher worker
    try:
        await producer_worker.start()
        logger.info("Pipeline producer started and connected to Kafka")
    except Exception as kafka_error:
        logger.critical(
            f"Failed to establish connection with Kafka Bootstrap Brokers: {kafka_error}. "
            "Halting service initialization.",
            exc_info=True,
        )
        await redis_store.close()
        sys.exit(1)

    logger.info("Initializing raw streams consumption...")
    # Start consumer supervisor to begin streaming & computing
    await consumer_supervisor.start()

    logger.info("Feature Service Pipeline is now fully OPERATIONAL and processing streams.")

    # Start the periodic background metrics reporter
    if settings.METRICS_ENABLED:
        reporter = MetricsReporter()
        reporter_task = asyncio.create_task(reporter.start())

    yield

    logger.info("Shutdown signal intercepted. Initiating graceful shutdown...")
    # Stop background metrics reporter if running
    if reporter_task:
        reporter_task.cancel()
        try:
            await reporter_task
        except asyncio.CancelledError:
            pass

    # 1. Cancel raw market streams
    if consumer_supervisor:
        await consumer_supervisor.stop()
    # 2. Stop pipeline producer connection
    if producer_worker:
        await producer_worker.stop()
    # 3. Close Redis connection
    if redis_store:
        await redis_store.close()

    logger.info("Feature Service has gracefully shutdown. Goodbye.")


app = FastAPI(
    title="AETHERION Feature Service",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return MonitoringService.health()


@app.get("/ready")
async def readiness():
    return MonitoringService.readiness()


@app.get("/metrics")
async def metrics():
    return MonitoringService.metrics()


if __name__ == "__main__":
    try:
        # Determine port from env, or settings, falling back to 8002
        port = int(os.getenv("SERVICE_PORT", 8002))
        logger.info(f"Starting web server on port {port}")
        uvicorn.run("src.main:app", host="0.0.0.0", port=port, log_level="info")
    except KeyboardInterrupt:
        logger.info("Process terminated by user KeyboardInterrupt.")