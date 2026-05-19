from services.ingestion_service.src.queues.queue_manager import (
    queue_manager,
)


def get_queue_metrics():

    return {
        "ingress_queue_size":
            queue_manager.ingress_queue.size(),

        "producer_queue_size":
            queue_manager.producer_queue.size(),

        "ingress_queue_full":
            queue_manager.ingress_queue.is_full(),

        "producer_queue_full":
            queue_manager.producer_queue.is_full(),
    }