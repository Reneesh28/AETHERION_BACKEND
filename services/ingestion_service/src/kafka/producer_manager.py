import logging

from aiokafka import AIOKafkaProducer

from services.ingestion_service.src.config import (
    kafka_settings,
)

from services.ingestion_service.src.resilience.retry import (
    retry_with_backoff,
)

logger = logging.getLogger(__name__)


class ProducerManager:

    def __init__(self):

        self.producer = AIOKafkaProducer(

            bootstrap_servers=
                kafka_settings
                .get_bootstrap_servers,

            value_serializer=lambda v:
                v.encode("utf-8"),

            acks="all",

            compression_type="gzip",
        )

    @retry_with_backoff
    async def start(self):

        logger.info(
            "Starting Kafka producer..."
        )

        await self.producer.start()

    async def stop(self):

        logger.info(
            "Stopping Kafka producer..."
        )

        await self.producer.stop()

    async def publish(
        self,
        topic: str,
        payload: str,
    ):

        await self.producer.send_and_wait(
            topic,
            payload,
        )