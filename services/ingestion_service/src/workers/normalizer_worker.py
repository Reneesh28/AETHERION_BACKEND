import logging

from services.ingestion_service.src.queues.queue_manager import (
    queue_manager,
)

from services.ingestion_service.src.services.normalization_service import (
    NormalizationService,
)

from services.ingestion_service.src.monitoring.counters import (
    counters,
)


logger = logging.getLogger(__name__)


class NormalizerWorker:

    async def start(self):

        logger.info(
            "Starting normalizer worker..."
        )

        while True:

            raw_event = await (
                queue_manager
                .ingress_queue
                .get()
            )

            counters.normalized_events += 1

            normalized_event = (
                NormalizationService
                .normalize_trade_event(
                    raw_event
                )
            )

            await (
                queue_manager
                .producer_queue
                .put(normalized_event)
            )

            logger.debug(
                "Normalized event added to producer queue"
            )