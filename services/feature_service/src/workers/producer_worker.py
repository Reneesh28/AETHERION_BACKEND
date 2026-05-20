import logging
from typing import Dict, Any
from src.redis_store.feature_store import RedisFeatureStore
from src.producers.feature_producer import FeatureProducer
from src.producers.serializer import serialize_feature_event
from src.monitoring.counters import counters

logger = logging.getLogger("feature_service.workers.producer_worker")


class ProducerWorker:
    """
    Orchestrates the streaming feature vector pipeline:
    1. Persists computed features into the Redis Feature Store (for low-latency ML snapshot access).
    2. Envelopes and serializes features into the global Kafka event contract.
    3. Publishes the serialized features to the 'feature.vector.computed' Kafka stream.
    """

    def __init__(
        self,
        redis_store: RedisFeatureStore,
        producer: FeatureProducer,
    ) -> None:
        self.redis_store = redis_store
        self.producer = producer

    async def start(self) -> None:
        """
        Starts the producer connection.
        """
        logger.info("Starting ProducerWorker...")
        await self.producer.start()

    async def stop(self) -> None:
        """
        Stops the producer connection.
        """
        logger.info("Stopping ProducerWorker...")
        await self.producer.stop()

    async def process_and_dispatch(
        self,
        symbol: str,
        window: str,
        features: Dict[str, Any],
        timestamp: int,
        trace_id: str,
    ) -> bool:
        """
        Main orchestration function: stores to Redis, formats, and publishes to Kafka.

        Args:
            symbol: The asset symbol (e.g., 'BTC-USD')
            window: Timeframe window name (e.g., '5s')
            features: Computed metrics (returns, volatility, etc.)
            timestamp: Epoch milliseconds timestamp
            trace_id: Correlation tracing string

        Returns:
            True if Kafka publishing is successful, False otherwise.
        """
        logger.info(
            f"Processing feature dispatch for {symbol}:{window} (Trace: {trace_id})"
        )

        # 1. Write snapshot to Redis Feature Store (Low-latency ML cache)
        redis_success = await self.redis_store.store_snapshot(
            symbol=symbol,
            window=window,
            features=features,
            timestamp=timestamp,
        )
        if redis_success:
            counters.redis_writes_success += 1
        else:
            counters.redis_writes_failed += 1
            logger.warning(
                f"Transient failure storing snapshot to Redis for {symbol}:{window}. "
                f"Proceeding with Kafka publishing anyway."
            )

        # 2. Format and serialize global Kafka envelope
        try:
            serialized_event = serialize_feature_event(
                symbol=symbol,
                window=window,
                features=features,
                trace_id=trace_id,
            )
        except Exception as serialization_error:
            logger.error(
                f"Critical serialization error formatting event for {symbol}:{window}: "
                f"{serialization_error}"
            )
            return False

        # 3. Publish to Kafka 'feature.vector.computed' topic
        kafka_success = await self.producer.publish_feature_event(
            symbol=symbol,
            serialized_event=serialized_event,
        )
        if not kafka_success:
            counters.kafka_pub_failed += 1
            logger.error(
                f"Failed to publish feature vector to Kafka for {symbol}:{window}."
            )
            return False

        counters.kafka_pub_success += 1
        counters.features_computed += 1

        logger.info(
            f"Successfully cached and published feature vector for {symbol}:{window}"
        )
        return True
