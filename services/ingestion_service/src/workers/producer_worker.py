import logging

from services.ingestion_service.src.kafka.producer_manager import (
    ProducerManager,
)

from services.ingestion_service.src.kafka.serializer import (
    EventSerializer,
)

from services.ingestion_service.src.kafka.topic_router import (
    TopicRouter,
)

from services.ingestion_service.src.queues.queue_manager import (
    queue_manager,
)

from services.ingestion_service.src.resilience.retry import (
    retry_with_backoff,
)

from services.ingestion_service.src.monitoring.counters import (
    counters,
)

logger = logging.getLogger(__name__)


class ProducerWorker:

    def __init__(self):

        self.producer_manager = (
            ProducerManager()
        )

    @retry_with_backoff
    async def publish_event(
        self,
        topic,
        serialized_event,
    ):

        await (
            self.producer_manager
            .publish(
                topic,
                serialized_event,
            )
        )

    async def start(self):

        logger.info(
            "Starting producer worker..."
        )

        await (
            self.producer_manager
            .start()
        )

        while True:

            event = await (
                queue_manager
                .producer_queue
                .get()
            )

            serialized_event = (
                EventSerializer
                .serialize(event)
            )

            topic = (
                TopicRouter
                .get_tick_topic()
            )

            await self.publish_event(
                topic,
                serialized_event,
            )

            counters.published_events += 1

            logger.debug(
                "Event published to Kafka"
            )