import asyncio
import logging

from services.ingestion_service.src.workers.connector_worker import (
    ConnectorWorker,
)

from services.ingestion_service.src.workers.normalizer_worker import (
    NormalizerWorker,
)

from services.ingestion_service.src.workers.producer_worker import (
    ProducerWorker,
)

from services.ingestion_service.src.monitoring.reporter import (
    MetricsReporter,
)

logger = logging.getLogger(__name__)


class WorkerSupervisor:

    def __init__(self):

        self.connector_worker = (
            ConnectorWorker()
        )

        self.normalizer_worker = (
            NormalizerWorker()
        )
        self.producer_worker = (
            ProducerWorker()
        )
        self.metrics_reporter = (
            MetricsReporter()
        )

    async def start(self):

        logger.info(
            "Starting worker supervisor..."
        )

        await asyncio.gather(

            self.connector_worker.start(),

            self.normalizer_worker.start(),
            
            self.producer_worker.start(),

            self.metrics_reporter.start(),
        )