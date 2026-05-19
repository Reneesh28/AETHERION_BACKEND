import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from services.ingestion_service.src.monitoring.logging import (
    configure_logging,
)

from services.ingestion_service.src.services.monitoring_service import (
    MonitoringService,
)

from services.ingestion_service.src.workers.supervisor import (
    WorkerSupervisor,
)


configure_logging()

logger = logging.getLogger(__name__)



supervisor = None
worker_task = None



@asynccontextmanager
async def lifespan(app: FastAPI):

    global supervisor, worker_task

    logger.info(
        "Starting ingestion service..."
    )

    supervisor = WorkerSupervisor()

    worker_task = asyncio.create_task(
        supervisor.start()
    )

    def on_worker_task_done(task):
        try:
            task.result()
        except Exception as e:
            logger.error(f"Worker task crashed: {e}", exc_info=True)
            
    worker_task.add_done_callback(on_worker_task_done)

    yield

    logger.info(
        "Stopping ingestion service..."
    )

    worker_task.cancel()



app = FastAPI(
    title="AETHERION Ingestion Service",
    version="1.0.0",
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