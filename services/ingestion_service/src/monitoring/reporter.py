import asyncio
import logging

from services.ingestion_service.src.monitoring.counters import (
    counters,
)

from services.ingestion_service.src.queues.queue_metrics import (
    get_queue_metrics,
)


logger = logging.getLogger(__name__)


class MetricsReporter:

    async def start(self):

        while True:

            queue_metrics = (
                get_queue_metrics()
            )

            logger.info(

                f"""
PIPELINE METRICS

Ingress Events:
{counters.ingress_events}

Normalized Events:
{counters.normalized_events}

Published Events:
{counters.published_events}

Queue Metrics:
{queue_metrics}
"""
            )

            await asyncio.sleep(10)