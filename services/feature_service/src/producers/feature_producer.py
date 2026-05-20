import logging
from typing import Optional

from aiokafka import AIOKafkaProducer

from src.config import settings

logger = logging.getLogger("feature_service.producers.feature_producer")


class FeatureProducer:
    """
    Asynchronous Kafka publisher for computed feature vectors.
    """

    def __init__(self, producer: Optional[AIOKafkaProducer] = None) -> None:
        self._producer = producer
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.topic = settings.FEATURE_VECTOR_TOPIC
        self._connected = False

    async def start(self) -> None:
        """
        Starts the AIOKafkaProducer if it's not already running.
        """
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                key_serializer=lambda v: v.encode("utf-8"),
                retry_backoff_ms=settings.RETRY_BACKOFF_MS,
            )

        try:
            logger.info("Starting AIOKafkaProducer...")

            await self._producer.start()

            self._connected = True

            logger.info("AIOKafkaProducer started successfully.")

        except Exception as e:
            self._connected = False

            logger.error(f"Failed to start AIOKafkaProducer: {e}")

            raise

    async def stop(self) -> None:
        """
        Stops the AIOKafkaProducer.
        """
        if self._producer is not None:
            logger.info("Stopping AIOKafkaProducer...")

            await self._producer.stop()

            self._producer = None
            self._connected = False

            logger.info("AIOKafkaProducer stopped.")

    async def publish_feature_event(
        self,
        symbol: str,
        serialized_event: bytes,
    ) -> bool:
        """
        Publishes a serialized feature vector event to the designated Kafka topic.

        Uses symbol as partition key to preserve strict symbol-wise message order.
        """

        if not self._connected or self._producer is None:
            logger.error(
                "Producer is not started. Call start() before publishing."
            )
            return False

        try:
            await self._producer.send_and_wait(
                self.topic,
                value=serialized_event,
                key=symbol,
            )

            logger.info(
                f"Successfully published feature vector for symbol '{symbol}'"
            )

            return True

        except Exception as e:
            logger.error(
                f"Failed to publish event for symbol '{symbol}': {e}"
            )

            return False