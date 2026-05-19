from services.ingestion_service.src.queues.ingress_queue import (
    IngressQueue,
)

from services.ingestion_service.src.queues.producer_queue import (
    ProducerQueue,
)


class QueueManager:

    def __init__(self):

        self.ingress_queue = IngressQueue()

        self.producer_queue = ProducerQueue()


queue_manager = QueueManager()