import os
import json
import asyncio
import logging
import websockets
from datetime import datetime, timezone
from dotenv import load_dotenv
from fastapi_market.connectors.base_connector import BaseMarketConnector
from fastapi_market.schemas import unified_trade_schema
from fastapi_market.database import trade_collection
from fastapi_market.stream_status import update_status, set_disconnected

load_dotenv()

logger = logging.getLogger("us_market_connector")


class USMarketConnector(BaseMarketConnector):
    """
    Single WebSocket US connector (multi-symbol)
    """

    def __init__(self, symbols: list[str]):
        super().__init__("US_MULTI")

        self.symbols = symbols

        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")
        self.ws_url = os.getenv("ALPACA_DATA_WSS")

        self.reconnect_delay = 5

        self.tickers = [
            s.split(":")[1] for s in symbols
        ]

        self.exchange_map = {
            s.split(":")[1]: s.split(":")[0]
            for s in symbols
        }

    async def start_trade_stream(self):

        while True:
            try:
                logger.info(
                    f"🔌 Connecting to Alpaca trade stream for {self.tickers}..."
                )

                async with websockets.connect(
                    self.ws_url,
                    ping_interval=20,
                    ping_timeout=20
                ) as ws:

                    auth_msg = {
                        "action": "auth",
                        "key": self.api_key,
                        "secret": self.secret_key
                    }

                    await ws.send(json.dumps(auth_msg))
                    await ws.recv()
                    await ws.recv()

                    logger.info("✅ Authenticated with Alpaca")

                    sub_msg = {
                        "action": "subscribe",
                        "trades": self.tickers
                    }

                    await ws.send(json.dumps(sub_msg))

                    logger.info(
                        f"📡 Subscribed to {self.tickers}"
                    )

                    async for message in ws:

                        data = json.loads(message)

                        for event in data:
                            if event.get("T") == "t":

                                normalized = self.normalize_trade(event)

                                await trade_collection.insert_one(normalized)

                                update_status(
                                    "US_STOCK",
                                    normalized["price"]
                                )

            except Exception as e:
                set_disconnected("US_STOCK")
                logger.error(f"❌ US trade stream error: {e}")
                await asyncio.sleep(self.reconnect_delay)

    async def start_orderbook_stream(self):
        pass

    def normalize_trade(self, raw):

        receive_time = int(
            datetime.now(timezone.utc).timestamp() * 1000
        )

        exchange_ts = int(
            datetime.fromisoformat(
                raw["t"].replace("Z", "+00:00")
            ).timestamp() * 1000
        )

        ticker = raw["S"]
        exchange = self.exchange_map.get(ticker, "US")

        return unified_trade_schema(
            market_type="US_STOCK",
            symbol=f"{exchange}:{ticker}",
            price=float(raw["p"]),
            quantity=float(raw["s"]),
            side="BUY",
            exchange_timestamp=exchange_ts,
            receive_timestamp=receive_time
        )

    def normalize_orderbook(self, raw):
        return None