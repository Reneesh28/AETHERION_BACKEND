import pytest

from services.ingestion_service.src.queues.queue_manager import (
    queue_manager,
)


@pytest.mark.asyncio
async def test_ingress_queue():

    test_data = {
        "symbol": "BTCUSDT",
        "price": 100000,
    }

    await queue_manager.ingress_queue.put(
        test_data
    )

    item = await queue_manager.ingress_queue.get()

    assert item["symbol"] == "BTCUSDT"


@pytest.mark.asyncio
async def test_producer_queue():

    test_data = {
        "event_type": "market.tick.raw",
    }

    await queue_manager.producer_queue.put(
        test_data
    )

    item = await queue_manager.producer_queue.get()

    assert (
        item["event_type"]
        == "market.tick.raw"
    )