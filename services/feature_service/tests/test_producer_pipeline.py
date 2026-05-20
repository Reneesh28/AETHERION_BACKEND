import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from src.producers.serializer import serialize_feature_event
from src.producers.feature_producer import FeatureProducer
from src.workers.producer_worker import ProducerWorker
from src.redis_store.feature_store import RedisFeatureStore


def test_serialize_feature_event():
    # Setup test inputs
    symbol = "BTC-USD"
    window = "5s"
    features = {"returns": 0.02, "volatility": 0.15, "vwap": 105000.0}
    trace_id = "test-trace-123"

    # Run serialization
    serialized_bytes = serialize_feature_event(
        symbol=symbol, window=window, features=features, trace_id=trace_id
    )

    # Deserialize and assert fields
    envelope = json.loads(serialized_bytes.decode("utf-8"))

    assert "event_id" in envelope
    assert envelope["trace_id"] == trace_id
    assert envelope["event_type"] == "feature.vector.computed"
    assert envelope["symbol"] == symbol
    assert envelope["source"] == "feature_service"
    assert envelope["schema_version"] == "v1"
    assert "event_time" in envelope
    assert "processing_time" in envelope

    # Validate nested payload
    payload = envelope["payload"]
    assert payload["window"] == window
    assert payload["features"] == features
    assert payload["features"]["returns"] == 0.02
    assert payload["features"]["volatility"] == 0.15


@pytest.mark.asyncio
async def test_feature_producer_lifecycle_and_publish():
    # Mock AIOKafkaProducer client
    mock_aiokafka = MagicMock()
    mock_aiokafka.start = AsyncMock()
    mock_aiokafka.stop = AsyncMock()
    mock_aiokafka.send_and_wait = AsyncMock()

    producer = FeatureProducer(producer=mock_aiokafka)

    # Test connect/start lifecycle
    await producer.start()
    assert producer._connected is True
    mock_aiokafka.start.assert_called_once()

    # Test publish_feature_event
    test_event = b'{"mock": "data"}'
    published = await producer.publish_feature_event(
        symbol="BTC-USD", serialized_event=test_event
    )
    assert published is True
    mock_aiokafka.send_and_wait.assert_called_once_with(
        producer.topic, value=test_event, key=b"BTC-USD"
    )

    # Test disconnect/stop lifecycle
    await producer.stop()
    assert producer._connected is False
    mock_aiokafka.stop.assert_called_once()


@pytest.mark.asyncio
async def test_feature_producer_fault_tolerance():
    # Mock AIOKafkaProducer client that throws exceptions
    mock_aiokafka = MagicMock()
    mock_aiokafka.start = AsyncMock(side_effect=Exception("Kafka Broker Down"))
    mock_aiokafka.send_and_wait = AsyncMock(side_effect=Exception("Send Timeout"))

    producer = FeatureProducer(producer=mock_aiokafka)

    # Verify lifecycle start handles exception by raising to supervisor
    with pytest.raises(Exception, match="Kafka Broker Down"):
        await producer.start()

    # Artificially set connection state to True to test sending fault tolerance
    producer._connected = True
    producer._producer = mock_aiokafka

    # Verify send failure is caught and handles gracefully returning False
    success = await producer.publish_feature_event(
        symbol="BTC-USD", serialized_event=b"{}"
    )
    assert success is False


@pytest.mark.asyncio
async def test_producer_worker_orchestration_success():
    # Mock dependencies
    mock_redis = MagicMock(spec=RedisFeatureStore)
    mock_redis.store_snapshot = AsyncMock(return_value=True)

    mock_producer = MagicMock(spec=FeatureProducer)
    mock_producer.start = AsyncMock()
    mock_producer.stop = AsyncMock()
    mock_producer.publish_feature_event = AsyncMock(return_value=True)

    worker = ProducerWorker(redis_store=mock_redis, producer=mock_producer)

    # Start worker
    await worker.start()
    mock_producer.start.assert_called_once()

    # Dispatch event
    symbol = "BTC-USD"
    window = "5s"
    features = {"returns": 0.01, "volatility": 0.05}
    timestamp = 1684500000000
    trace_id = "trace-456"

    dispatched = await worker.process_and_dispatch(
        symbol=symbol,
        window=window,
        features=features,
        timestamp=timestamp,
        trace_id=trace_id,
    )

    assert dispatched is True

    # Assert Redis was cached
    mock_redis.store_snapshot.assert_called_once_with(
        symbol=symbol, window=window, features=features, timestamp=timestamp
    )

    # Assert Kafka was dispatched
    mock_producer.publish_feature_event.assert_called_once()

    # Stop worker
    await worker.stop()
    mock_producer.stop.assert_called_once()


@pytest.mark.asyncio
async def test_producer_worker_fault_tolerance():
    # 1. Test case: Redis caching fails, but Kafka streaming succeeds
    # The pipeline should be resilient and still complete the Kafka publication
    mock_redis = MagicMock(spec=RedisFeatureStore)
    mock_redis.store_snapshot = AsyncMock(return_value=False)  # Redis Failure

    mock_producer = MagicMock(spec=FeatureProducer)
    mock_producer.publish_feature_event = AsyncMock(return_value=True)  # Kafka Success

    worker = MagicMock()
    worker = ProducerWorker(redis_store=mock_redis, producer=mock_producer)

    resilient_success = await worker.process_and_dispatch(
        symbol="BTC-USD",
        window="5s",
        features={"returns": 0.01},
        timestamp=123456,
        trace_id="trace-789",
    )

    # Worker should return True since Kafka publishing was successful
    assert resilient_success is True
    mock_redis.store_snapshot.assert_called_once()
    mock_producer.publish_feature_event.assert_called_once()

    # 2. Test case: Kafka publishing fails
    mock_redis.store_snapshot.reset_mock()
    mock_redis.store_snapshot.return_value = True
    mock_producer.publish_feature_event.reset_mock()
    mock_producer.publish_feature_event.return_value = False  # Kafka Failure

    kafka_fail_success = await worker.process_and_dispatch(
        symbol="BTC-USD",
        window="5s",
        features={"returns": 0.01},
        timestamp=123456,
        trace_id="trace-789",
    )

    assert kafka_fail_success is False

    # 3. Test case: Serialization throws unhandled exception
    mock_producer.publish_feature_event.reset_mock()
    with patch(
        "src.workers.producer_worker.serialize_feature_event",
        side_effect=Exception("Serialization Error"),
    ):
        serialization_fail_success = await worker.process_and_dispatch(
            symbol="BTC-USD",
            window="5s",
            features={"returns": 0.01},
            timestamp=123456,
            trace_id="trace-789",
        )
        assert serialization_fail_success is False
        mock_producer.publish_feature_event.assert_not_called()


def test_parse_timestamp():
    from src.workers.consumer_supervisor import parse_timestamp

    # Numeric timestamps
    assert parse_timestamp(12345.67) == 12345.67
    assert parse_timestamp(12345) == 12345.0

    # ISO format string with Z
    assert parse_timestamp("2026-05-20T00:00:00Z") == 1779235200.0

    # ISO format string with offset
    assert parse_timestamp("2026-05-20T00:00:00+00:00") == 1779235200.0

    # Invalid timestamp fallback
    assert parse_timestamp("invalid-date") > 0.0


@pytest.mark.asyncio
async def test_consumer_supervisor_pipeline_tick_processing():
    # Mock pipeline dependencies
    from src.workers.consumer_supervisor import ConsumerSupervisor, parse_timestamp
    from src.windows.window_manager import WindowManager
    from src.services.feature_builder import FeatureBuilder

    mock_window_manager = MagicMock(spec=WindowManager)
    mock_window_manager.add_tick = AsyncMock()

    mock_feature_builder = MagicMock(spec=FeatureBuilder)
    mock_feature_builder.build_feature_vector = AsyncMock(
        return_value={
            "payload": {
                "volatility": 0.05,
                "returns": 0.01,
                "orderbook_imbalance": 0.1,
                "spread": 1.5,
                "liquidity_score": 10.0,
                "vwap": 50000.0,
                "momentum": 2.0,
            }
        }
    )

    mock_producer_worker = MagicMock(spec=ProducerWorker)
    mock_producer_worker.process_and_dispatch = AsyncMock(return_value=True)

    supervisor = ConsumerSupervisor(
        window_manager=mock_window_manager,
        feature_builder=mock_feature_builder,
        producer_worker=mock_producer_worker,
    )

    # Mock raw tick event received from Kafka
    tick_event = {
        "symbol": "BTC-USD",
        "event_time": 1779235200.0,
        "trace_id": "test-trace-tick",
        "payload": {
            "price": 50000.0,
            "quantity": 1.5,
            "bid": 49999.0,
            "ask": 50001.0,
        },
    }

    # Mock tick consumer to yield one event
    async def mock_consume():
        yield tick_event

    supervisor.tick_consumer.consume = mock_consume
    supervisor._running = True

    await supervisor._run_tick_consumer()

    # Assertions
    mock_window_manager.add_tick.assert_called_once_with(
        symbol="BTC-USD",
        timestamp=1779235200.0,
        price=50000.0,
        volume=1.5,
        bid=49999.0,
        ask=50001.0,
    )

    assert mock_feature_builder.build_feature_vector.call_count == 3
    assert mock_producer_worker.process_and_dispatch.call_count == 3


@pytest.mark.asyncio
async def test_consumer_supervisor_pipeline_orderbook_processing():
    # Mock pipeline dependencies
    from src.workers.consumer_supervisor import ConsumerSupervisor, parse_timestamp
    from src.windows.window_manager import WindowManager
    from src.services.feature_builder import FeatureBuilder

    mock_window_manager = MagicMock(spec=WindowManager)
    mock_window_manager.add_orderbook = AsyncMock()

    mock_feature_builder = MagicMock(spec=FeatureBuilder)
    mock_feature_builder.build_feature_vector = AsyncMock(
        return_value={
            "payload": {
                "volatility": 0.05,
                "returns": 0.01,
                "orderbook_imbalance": 0.1,
                "spread": 1.5,
                "liquidity_score": 10.0,
                "vwap": 50000.0,
                "momentum": 2.0,
            }
        }
    )

    mock_producer_worker = MagicMock(spec=ProducerWorker)
    mock_producer_worker.process_and_dispatch = AsyncMock(return_value=True)

    supervisor = ConsumerSupervisor(
        window_manager=mock_window_manager,
        feature_builder=mock_feature_builder,
        producer_worker=mock_producer_worker,
    )

    # Mock raw orderbook event received from Kafka
    ob_event = {
        "symbol": "BTC-USD",
        "event_time": 1779235200.0,
        "trace_id": "test-trace-ob",
        "payload": {
            "bid_price": 49999.0,
            "ask_price": 50001.0,
            "bid_quantity": 2.0,
            "ask_quantity": 3.0,
            "spread": 2.0,
        },
    }

    # Mock orderbook consumer to yield one event
    async def mock_consume():
        yield ob_event

    supervisor.orderbook_consumer.consume = mock_consume
    supervisor._running = True

    await supervisor._run_orderbook_consumer()

    # Assertions
    mock_window_manager.add_orderbook.assert_called_once_with(
        symbol="BTC-USD",
        timestamp=1779235200.0,
        bids=[(49999.0, 2.0)],
        asks=[(50001.0, 3.0)],
        spread=2.0,
        depth=5.0,
    )

    assert mock_feature_builder.build_feature_vector.call_count == 3
    assert mock_producer_worker.process_and_dispatch.call_count == 3
