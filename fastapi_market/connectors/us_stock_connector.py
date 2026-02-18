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


load_dotenv()

logger = logging.getLogger("us_stock_connector")


class USStockConnector(BaseMarketConnector):
    """
    Alpaca US Stock Trade Stream Connector
    Supports symbol format: NASDAQ:AAPL
    """

    def __init__(self, symbol: str):
        super().__init__(symbol)

        self.exchange, self.ticker = symbol.split(":")

        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")
        self.ws_url = os.getenv("ALPACA_DATA_WSS")

        self.reconnect_delay = 5

    async def start_trade_stream(self):

        while True:
            try:
                logger.info("🔌 Connecting to Alpaca trade stream...")

                async with websockets.connect(self.ws_url) as ws:

                    # Authenticate
                    auth_msg = {
                        "action": "auth",
                        "key": self.api_key,
                        "secret": self.secret_key
                    }

                    await ws.send(json.dumps(auth_msg))
                    await ws.recv()  # connected
                    await ws.recv()  # authenticated

                    logger.info("✅ Authenticated with Alpaca")

                    # Subscribe to trades
                    sub_msg = {
                        "action": "subscribe",
                        "trades": [self.ticker]
                    }

                    await ws.send(json.dumps(sub_msg))
                    logger.info(f"📡 Subscribed to {self.ticker}")

                    async for message in ws:
                        data = json.loads(message)

                        for event in data:
                            if event.get("T") == "t":
                                normalized = self.normalize_trade(event)
                                await trade_collection.insert_one(normalized)

            except Exception as e:
                logger.error(f"❌ Alpaca stream error: {e}")
                logger.info(f"🔄 Reconnecting in {self.reconnect_delay}s...")
                await asyncio.sleep(self.reconnect_delay)

    async def start_orderbook_stream(self):
        # Alpaca free tier does not support full depth
        pass

    def normalize_trade(self, raw):

        receive_time = int(
            datetime.now(timezone.utc).timestamp() * 1000
        )

        return unified_trade_schema(
            market_type="US_STOCK",
            symbol=f"{self.exchange}:{self.ticker}",
            price=float(raw["p"]),
            quantity=float(raw["s"]),
            side="BUY",  # Aggressor side not provided in free feed
            exchange_timestamp=int(
                datetime.fromisoformat(raw["t"].replace("Z", "+00:00"))
                .timestamp() * 1000
            ),
            receive_timestamp=receive_time
        )
    
    def normalize_orderbook(self, raw):
        """
        Alpaca free tier does not provide full orderbook depth.
        Placeholder to satisfy abstract base class.
        """
        return None
