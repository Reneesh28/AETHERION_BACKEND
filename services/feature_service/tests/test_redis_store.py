import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from src.redis_store.cache_keys import get_feature_key
from src.redis_store.feature_store import RedisFeatureStore


def test_cache_keys():
    assert get_feature_key("BTC-USD", "1s") == "feature:BTC-USD:1s"
    assert get_feature_key("ETH-USD", "30s") == "feature:ETH-USD:30s"


@pytest.mark.asyncio
async def test_redis_store_lifecycle_and_operations():
    # Mock redis client
    mock_redis = MagicMock()
    mock_redis.ping = AsyncMock(return_value=True)
    mock_redis.set = AsyncMock(return_value=True)

    # Stored snapshot json payload mock
    mock_payload = {
        "symbol": "BTC-USD",
        "window": "1s",
        "timestamp": 123456,
        "features": {"returns": 0.01, "volatility": 0.1},
    }
    mock_redis.get = AsyncMock(return_value=json.dumps(mock_payload))
    mock_redis.aclose = AsyncMock()

    # Create store and inject mocked client
    store = RedisFeatureStore(client=mock_redis)

    # Test connect / ping
    connected = await store.connect()
    assert connected is True
    mock_redis.ping.assert_called_once()

    # Test store_snapshot
    stored = await store.store_snapshot(
        symbol="BTC-USD",
        window="1s",
        features={"returns": 0.01, "volatility": 0.1},
        timestamp=123456,
    )
    assert stored is True
    mock_redis.set.assert_called_once_with(
        "feature:BTC-USD:1s",
        json.dumps(mock_payload),
        ex=60,  # Default FEATURE_TTL_SECONDS configured in Settings
    )

    # Test get_snapshot
    snapshot = await store.get_snapshot(symbol="BTC-USD", window="1s")
    assert snapshot is not None
    assert snapshot["symbol"] == "BTC-USD"
    assert snapshot["features"]["returns"] == 0.01
    mock_redis.get.assert_called_once_with("feature:BTC-USD:1s")

    # Test close
    await store.close()
    mock_redis.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_redis_store_fault_tolerance():
    # Mock redis client that raises exceptions
    mock_redis = MagicMock()
    mock_redis.ping = AsyncMock(side_effect=Exception("Connection timeout"))
    mock_redis.set = AsyncMock(side_effect=Exception("Redis write error"))
    mock_redis.get = AsyncMock(side_effect=Exception("Redis read error"))

    store = RedisFeatureStore(client=mock_redis)

    # Verify connect fails gracefully without raising unhandled exception
    connected = await store.connect()
    assert connected is False

    # Verify store_snapshot fails gracefully
    stored = await store.store_snapshot(
        symbol="BTC-USD", window="1s", features={"returns": 0.01}, timestamp=123456
    )
    assert stored is False

    # Verify get_snapshot fails gracefully
    snapshot = await store.get_snapshot(symbol="BTC-USD", window="1s")
    assert snapshot is None
