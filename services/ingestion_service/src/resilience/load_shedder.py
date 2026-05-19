from services.ingestion_service.src.queues.queue_manager import (
    queue_manager,
)


class LoadShedder:

    @staticmethod
    def should_shed_load():

        ingress_size = (
            queue_manager
            .ingress_queue
            .size()
        )

        return ingress_size > 8000