from datetime import datetime

from shared.schemas.market import (
    MarketTickEvent,
    TickPayload,
)


def test_market_tick_event():

    payload = TickPayload(
        price=100000.0,
        quantity=0.5,
        side="buy",
    )

    event = MarketTickEvent(
        event_id="event-1",
        trace_id="trace-1",
        event_type="market.tick.raw",
        service_name="ingestion_service",
        source="binance",
        event_time=datetime.utcnow(),
        symbol="BTCUSDT",
        payload=payload,
    )

    assert event.symbol == "BTCUSDT"

    assert event.payload.price == 100000.0

    assert event.payload.side == "buy"