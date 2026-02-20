import asyncio
import json
import time
import logging
import websockets

from datetime import datetime, timezone

from fastapi_market.connectors.base_connector import BaseMarketConnector
from fastapi_market.schemas import (
    unified_trade_schema,
    unified_orderbook_schema
)
from fastapi_market.database import (
    trade_collection,
    crypto_orderbook_collection   # ✅ Updated
)

# LOGGING
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("crypto_connector")


class CryptoConnector(BaseMarketConnector):
    """
    Binance Crypto Market Connector
    - Async (Motor based)
    - Batch trade inserts
    - Orderbook snapshots
    - Reconnect logic
    """

    def __init__(self, symbol: str):
        super().__init__(symbol)

        self.trade_url = (
            f"wss://stream.binance.com:9443/ws/{symbol.lower()}@trade"
        )

        self.depth_url = (
            f"wss://stream.binance.com:9443/ws/{symbol.lower()}@depth@100ms"
        )

        self.heartbeat_timeout = 20
        self.reconnect_delay = 5

    # ==============================
    # TRADE STREAM
    # ==============================
    async def start_trade_stream(self):

        queue = asyncio.Queue()

        async def mongo_writer():
            buffer = []

            while True:
                tick = await queue.get()
                buffer.append(tick)

                if len(buffer) >= 200:
                    await trade_collection.insert_many(buffer)
                    buffer.clear()

        asyncio.create_task(mongo_writer())

        while True:
            try:
                logger.info(f"🔌 Connecting to Binance trade stream for {self.symbol}...")

                async with websockets.connect(
                    self.trade_url,
                    ping_interval=20
                ) as ws:

                    logger.info("✅ Connected to trade stream")

                    async for message in ws:
                        raw = json.loads(message)
                        normalized = self.normalize_trade(raw)
                        await queue.put(normalized)

            except Exception as e:
                logger.error(f"❌ Trade stream error: {e}")
                logger.info(
                    f"🔄 Reconnecting in {self.reconnect_delay} seconds..."
                )
                await asyncio.sleep(self.reconnect_delay)

    # ==============================
    # ORDERBOOK STREAM
    # ==============================
    async def start_orderbook_stream(self):

        while True:
            try:
                logger.info(f"🔌 Connecting to Binance orderbook stream for {self.symbol}...")

                async with websockets.connect(self.depth_url) as ws:

                    logger.info("✅ Connected to orderbook stream")

                    last_message_time = time.time()

                    async for message in ws:

                        raw = json.loads(message)

                        if "b" not in raw or "a" not in raw:
                            continue

                        last_message_time = time.time()

                        normalized = self.normalize_orderbook(raw)

                        # ✅ Write to crypto-specific collection
                        await crypto_orderbook_collection.insert_one(normalized)

                        if (
                            time.time() - last_message_time
                            > self.heartbeat_timeout
                        ):
                            logger.warning(
                                "⚠ Heartbeat lost. Reconnecting..."
                            )
                            break

            except Exception as e:
                logger.error(f"❌ Orderbook stream error: {e}")
                logger.info(
                    f"🔄 Reconnecting in {self.reconnect_delay} seconds..."
                )
                await asyncio.sleep(self.reconnect_delay)

    # ==============================
    # NORMALIZATION
    # ==============================
    def normalize_trade(self, raw_data):

        receive_time = int(
            datetime.now(timezone.utc).timestamp() * 1000
        )

        return unified_trade_schema(
            market_type="CRYPTO",
            symbol=raw_data["s"],
            price=float(raw_data["p"]),
            quantity=float(raw_data["q"]),
            side="BUY" if raw_data["m"] is False else "SELL",
            exchange_timestamp=raw_data["T"],
            receive_timestamp=receive_time
        )

    def normalize_orderbook(self, raw_data):

        receive_time = int(
            datetime.now(timezone.utc).timestamp() * 1000
        )

        return unified_orderbook_schema(
            market_type="CRYPTO",
            symbol=self.symbol.upper(),
            bids=raw_data.get("b", []),
            asks=raw_data.get("a", []),
            exchange_timestamp=raw_data.get("E"),
            receive_timestamp=receive_time
        )