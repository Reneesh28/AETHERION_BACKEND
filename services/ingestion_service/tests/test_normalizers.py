from services.ingestion_service.src.normalizers.tick_normalizer import (
    TickNormalizer,
)


def test_binance_tick_normalization():

    raw_event = {
        "s": "BTCUSDT",
        "p": "104000.50",
        "q": "0.001",
        "m": False,
        "t": 12345,
    }

    event = (
        TickNormalizer
        .normalize_binance_trade(
            raw_event
        )
    )

    assert event.symbol == "BTCUSDT"

    assert event.payload.price == 104000.50

    assert event.payload.side == "buy"

    assert event.event_type == "market.tick.raw"