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
    Unified US Market WebSocket Connector
    Supports NASDAQ + NYSE (multi-symbol)
    """

    def __init__(self, symbols: list[str]):
        """
        symbols format:
        [
            "NASDAQ:AAPL",
            "NASDAQ:MSFT",
            "NYSE:JPM",
            "NYSE:KO"
        ]
        """
        super().__init__("US_MULTI")

        self.symbols = symbols

        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")
        self.ws_url = os.getenv("ALPACA_DATA_WSS")

        self.reconnect_delay = 5

        # Extract tickers only (AAPL, MSFT, etc.)
        self.tickers = [s.split(":")[1] for s in symbols]

        # Map ticker -> exchange
        self.exchange_map = {
            s.split(":")[1]: s.split(":")[0]
            for s in symbols
        }

    async def start_trade_stream(self):

        while True:
            try:
                logger.info(
                    f"🔌 Connecting to Alpaca trade stream for {self.tickers}"
                )

                async with websockets.connect(
                    self.ws_url,
                    ping_interval=20,
                    ping_timeout=20
                ) as ws:

                    # Authenticate
                    auth_msg = {
                        "action": "auth",
                        "key": self.api_key,
                        "secret": self.secret_key
                    }

                    await ws.send(json.dumps(auth_msg))
                    await ws.recv()
                    await ws.recv()

                    logger.info("✅ Authenticated with Alpaca")

                    # Subscribe to trades
                    sub_msg = {
                        "action": "subscribe",
                        "trades": self.tickers
                    }

                    await ws.send(json.dumps(sub_msg))
                    logger.info(f"📡 Subscribed to {self.tickers}")

                    async for message in ws:

                        data = json.loads(message)

                        for event in data:
                            if event.get("T") == "t":

                                normalized = self.normalize_trade(event)

                                await trade_collection.insert_one(normalized)

                                # Update status per exchange
                                exchange = normalized["symbol"].split(":")[0]

                                update_status(
                                    exchange,
                                    normalized["price"]
                                )

            except Exception as e:
                logger.error(f"❌ US trade stream error: {e}")

                # Mark each exchange disconnected
                for exchange in set(self.exchange_map.values()):
                    set_disconnected(exchange)

                await asyncio.sleep(self.reconnect_delay)

    async def start_orderbook_stream(self):
        # Alpaca basic feed does not provide full L2 orderbook
        return

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
            market_type=exchange,  # NASDAQ or NYSE
            symbol=f"{exchange}:{ticker}",
            price=float(raw["p"]),
            quantity=float(raw["s"]),
            side="BUY",  # Alpaca trade feed doesn't expose aggressor side
            exchange_timestamp=exchange_ts,
            receive_timestamp=receive_time
        )

    def normalize_orderbook(self, raw):
        return None