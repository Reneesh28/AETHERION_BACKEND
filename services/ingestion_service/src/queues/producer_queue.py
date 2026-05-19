import asyncio

from services.ingestion_service.src.config import settings


class ProducerQueue:

    def __init__(self):

        self.queue = asyncio.Queue(
            maxsize=settings.PRODUCER_QUEUE_SIZE
        )

    async def put(self, item):

        await self.queue.put(item)

    async def get(self):

        return await self.queue.get()

    def size(self):

        return self.queue.qsize()

    def is_full(self):

        return self.queue.full()