import asyncio
import logging
import datetime
from typing import Optional, Any

from src.consumers.tick_consumer import TickConsumer
from src.consumers.orderbook_consumer import OrderBookConsumer
from src.windows.window_manager import WindowManager
from src.services.feature_builder import FeatureBuilder
from src.workers.producer_worker import ProducerWorker
from shared.constants.system import SUPPORTED_WINDOWS
from src.monitoring.counters import counters

logger = logging.getLogger("feature_service.workers.consumer_supervisor")


def parse_timestamp(ts: Any) -> float:
    """
    Safely parses diverse timestamp formats (numeric epoch, ISO strings) into float epoch seconds.
    """
    if isinstance(ts, (int, float)):
        return float(ts)
    if isinstance(ts, str):
        try:
            # Handle ISO timestamp strings, replacing Z with UTC offset
            s = ts.replace("Z", "+00:00")
            dt = datetime.datetime.fromisoformat(s)
            return dt.timestamp()
        except Exception:
            try:
                return float(ts)
            except Exception:
                pass
    # Fallback to current local time if parsing fails
    import time
    return time.time()


class ConsumerSupervisor:
    """
    Supervises Kafka consumer lifecycle and wires the real-time event pipeline:
    Kafka Consumer -> WindowManager -> FeatureBuilder -> ProducerWorker
    """

    def __init__(
        self,
        window_manager: WindowManager,
        feature_builder: FeatureBuilder,
        producer_worker: ProducerWorker,
    ) -> None:
        self.window_manager = window_manager
        self.feature_builder = feature_builder
        self.producer_worker = producer_worker

        self.tick_consumer = TickConsumer()
        self.orderbook_consumer = OrderBookConsumer()

        self.tick_task: Optional[asyncio.Task] = None
        self.orderbook_task: Optional[asyncio.Task] = None

        self._running = False

    async def start(self) -> None:
        """
        Start all consumers and tasks.
        """
        logger.info("Starting consumers and pipeline integration...")

        await self.tick_consumer.start()
        await self.orderbook_consumer.start()

        self._running = True

        self.tick_task = asyncio.create_task(
            self._run_tick_consumer()
        )

        self.orderbook_task = asyncio.create_task(
            self._run_orderbook_consumer()
        )

        logger.info("All consumers and pipeline workers started successfully")

    async def stop(self) -> None:
        """
        Gracefully stop all consumers.
        """
        logger.info("Stopping consumers...")

        self._running = False

        if self.tick_task:
            self.tick_task.cancel()
            try:
                await self.tick_task
            except asyncio.CancelledError:
                pass

        if self.orderbook_task:
            self.orderbook_task.cancel()
            try:
                await self.orderbook_task
            except asyncio.CancelledError:
                pass

        await self.tick_consumer.stop()
        await self.orderbook_consumer.stop()

        logger.info("All consumers stopped gracefully")

    async def _run_tick_consumer(self) -> None:
        """
        Tick consumer task loop. Updates WindowManager, triggers FeatureBuilder,
        and dispatches snapshots and events via ProducerWorker.
        """
        try:
            async for event in self.tick_consumer.consume():
                if not self._running:
                    break

                counters.ticks_consumed += 1
                logger.info(f"Received tick event for {event.get('symbol')}")
                try:
                    symbol = event["symbol"]
                    payload = event.get("payload", {})
                    trace_id = event.get("trace_id", "trace-id")
                    event_time = event.get("event_time")

                    # Parse timestamp to float seconds for the window
                    timestamp = parse_timestamp(event_time)

                    price = float(payload.get("price", 0.0))
                    volume = float(payload.get("quantity", payload.get("volume", 0.0)))
                    bid = float(payload.get("bid", 0.0))
                    ask = float(payload.get("ask", 0.0))

                    # 1. Update WindowManager
                    await self.window_manager.add_tick(
                        symbol=symbol,
                        timestamp=timestamp,
                        price=price,
                        volume=volume,
                        bid=bid,
                        ask=ask,
                    )

                    # 2. Compute and dispatch features for all supported sliding windows
                    for window in SUPPORTED_WINDOWS:
                        vector = await self.feature_builder.build_feature_vector(
                            symbol=symbol,
                            window_name=window,
                            trace_id=trace_id,
                            source="feature_service",
                        )

                        features_dict = {
                            "volatility": vector["payload"]["volatility"],
                            "returns": vector["payload"]["returns"],
                            "orderbook_imbalance": vector["payload"]["orderbook_imbalance"],
                            "spread": vector["payload"]["spread"],
                            "liquidity_score": vector["payload"]["liquidity_score"],
                            "vwap": vector["payload"]["vwap"],
                            "momentum": vector["payload"]["momentum"],
                        }

                        # 3. Cache to Redis and stream to Kafka
                        await self.producer_worker.process_and_dispatch(
                            symbol=symbol,
                            window=window,
                            features=features_dict,
                            timestamp=int(timestamp * 1000),  # Kafka event uses epoch ms
                            trace_id=trace_id,
                        )

                except Exception as inner_error:
                    logger.error(f"Error processing tick event in pipeline: {inner_error}", exc_info=True)

                await asyncio.sleep(0)

        except asyncio.CancelledError:
            logger.info("Tick consumer task cancelled")
        except Exception as error:
            logger.error(f"Tick consumer task failed: {error}", exc_info=True)

    async def _run_orderbook_consumer(self) -> None:
        """
        Orderbook consumer task loop. Updates WindowManager, triggers FeatureBuilder,
        and dispatches snapshots and events via ProducerWorker.
        """
        try:
            async for event in self.orderbook_consumer.consume():
                if not self._running:
                    break

                counters.orderbooks_consumed += 1
                logger.info(f"Received orderbook event for {event.get('symbol')}")
                try:
                    symbol = event["symbol"]
                    payload = event.get("payload", {})
                    trace_id = event.get("trace_id", "trace-id")
                    event_time = event.get("event_time")

                    # Parse timestamp to float seconds for the window
                    timestamp = parse_timestamp(event_time)

                    bid_price = float(payload.get("bid_price", 0.0))
                    ask_price = float(payload.get("ask_price", 0.0))
                    bid_quantity = float(payload.get("bid_quantity", 0.0))
                    ask_quantity = float(payload.get("ask_quantity", 0.0))
                    spread = float(payload.get("spread") if payload.get("spread") is not None else (ask_price - bid_price))
                    depth = bid_quantity + ask_quantity

                    # 1. Update WindowManager
                    await self.window_manager.add_orderbook(
                        symbol=symbol,
                        timestamp=timestamp,
                        bids=[(bid_price, bid_quantity)],
                        asks=[(ask_price, ask_quantity)],
                        spread=spread,
                        depth=depth,
                    )

                    # 2. Compute and dispatch features for all supported sliding windows
                    for window in SUPPORTED_WINDOWS:
                        vector = await self.feature_builder.build_feature_vector(
                            symbol=symbol,
                            window_name=window,
                            trace_id=trace_id,
                            source="feature_service",
                        )

                        features_dict = {
                            "volatility": vector["payload"]["volatility"],
                            "returns": vector["payload"]["returns"],
                            "orderbook_imbalance": vector["payload"]["orderbook_imbalance"],
                            "spread": vector["payload"]["spread"],
                            "liquidity_score": vector["payload"]["liquidity_score"],
                            "vwap": vector["payload"]["vwap"],
                            "momentum": vector["payload"]["momentum"],
                        }

                        # 3. Cache to Redis and stream to Kafka
                        await self.producer_worker.process_and_dispatch(
                            symbol=symbol,
                            window=window,
                            features=features_dict,
                            timestamp=int(timestamp * 1000),  # Kafka event uses epoch ms
                            trace_id=trace_id,
                        )

                except Exception as inner_error:
                    logger.error(f"Error processing orderbook event in pipeline: {inner_error}", exc_info=True)

                await asyncio.sleep(0)

        except asyncio.CancelledError:
            logger.info("Orderbook consumer task cancelled")
        except Exception as error:
            logger.error(f"Orderbook consumer task failed: {error}", exc_info=True)
