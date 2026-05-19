import asyncio

from services.ingestion_service.src.queues.queue_manager import (
    queue_manager,
)

from services.ingestion_service.src.workers.normalizer_worker import (
    NormalizerWorker,
)


async def main():

    raw_event = {
        "s": "BTCUSDT",
        "p": "104000.50",
        "q": "0.001",
        "m": False,
        "t": 12345,
    }

    await (
        queue_manager
        .ingress_queue
        .put(raw_event)
    )

    worker = NormalizerWorker()

    task = asyncio.create_task(
        worker.start()
    )

    await asyncio.sleep(1)

    normalized_event = await (
        queue_manager
        .producer_queue
        .get()
    )

    print(normalized_event)

    task.cancel()


if __name__ == "__main__":

    asyncio.run(main())