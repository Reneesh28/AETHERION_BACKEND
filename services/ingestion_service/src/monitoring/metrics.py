from services.ingestion_service.src.queues.queue_metrics import (
    get_queue_metrics,
)


class MetricsCollector:

    @staticmethod
    def collect():

        return {

            "queues":
                get_queue_metrics(),
        }