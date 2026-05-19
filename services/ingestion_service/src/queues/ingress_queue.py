import asyncio

from services.ingestion_service.src.config import settings


class IngressQueue:

    def __init__(self):

        self.queue = asyncio.Queue(
            maxsize=settings.INGRESS_QUEUE_SIZE
        )

    async def put(self, item):

        await self.queue.put(item)

    async def get(self):

        return await self.queue.get()

    def size(self):

        return self.queue.qsize()

    def is_full(self):

        return self.queue.full()