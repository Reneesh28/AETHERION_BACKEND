from services.ingestion_service.src.queues.queue_manager import (
    queue_manager,
)


class ReadinessCheck:

    @staticmethod
    def status():

        ingress_ready = not (
            queue_manager
            .ingress_queue
            .is_full()
        )

        producer_ready = not (
            queue_manager
            .producer_queue
            .is_full()
        )

        ready = (
            ingress_ready
            and producer_ready
        )

        return {
            "ready": ready
        }