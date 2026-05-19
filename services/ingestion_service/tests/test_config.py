from src.config import settings
from src.config import kafka_settings


def test_settings_loaded():

    assert settings.SERVICE_NAME == "ingestion_service"

    assert settings.BINANCE_WS_URL.startswith("wss://")

    assert kafka_settings.KAFKA_BOOTSTRAP_SERVERS is not None

    assert (
        settings.KAFKA_TOPIC_MARKET_TICK_RAW
        == "market.tick.raw"
    )

    assert (
        settings.KAFKA_TOPIC_MARKET_ORDERBOOK_RAW
        == "market.orderbook.raw"
    )