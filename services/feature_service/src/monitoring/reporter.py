import asyncio
import logging
from src.monitoring.counters import counters
from src.monitoring.metrics import MetricsCollector

logger = logging.getLogger("feature_service.monitoring.reporter")


class MetricsReporter:

    async def start(self) -> None:
        logger.info("MetricsReporter background task started")
        while True:
            try:
                metrics = MetricsCollector.collect()
                logger.info(
                    f"""
=========================================================
FEATURE SERVICE PIPELINE METRICS
=========================================================
Ticks Consumed:        {metrics['pipeline']['ticks_consumed']}
Orderbooks Consumed:   {metrics['pipeline']['orderbooks_consumed']}
Features Computed:     {metrics['pipeline']['features_computed']}

Cache Writes Success:  {metrics['cache']['redis_writes_success']}
Cache Writes Failed:   {metrics['cache']['redis_writes_failed']}

Kafka Pub Success:     {metrics['kafka']['kafka_pub_success']}
Kafka Pub Failed:      {metrics['kafka']['kafka_pub_failed']}
=========================================================
"""
                )
            except Exception as e:
                logger.error(f"Error reporting metrics: {e}", exc_info=True)
            await asyncio.sleep(10)
