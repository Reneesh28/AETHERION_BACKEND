import logging

from services.ingestion_service.src.connectors.binance_connector import (
    BinanceConnector,
)

from services.ingestion_service.src.queues.queue_manager import (
    queue_manager,
)

from services.ingestion_service.src.monitoring.counters import (
    counters,
)

logger = logging.getLogger(__name__)


class ConnectorWorker:

    def __init__(self):

        self.connector = BinanceConnector()

    async def start(self):

        logger.info(
            "Starting connector worker..."
        )

        async for event in (
            self.connector.stream_trades()
        ):

            await (
                queue_manager
                .ingress_queue
                .put(event)
            )
            counters.ingress_events += 1
            logger.debug(
                "Event added to ingress queue"
            )