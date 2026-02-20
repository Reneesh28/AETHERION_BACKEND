import os
import json
import asyncio
import logging
import websockets

from datetime import datetime, timezone
from dotenv import load_dotenv

from fastapi_market.connectors.base_connector import BaseMarketConnector
from fastapi_market.schemas import unified_trade_schema
from fastapi_market.database import (
    trade_collection,
    us_orderbook_collection
)

load_dotenv()

logger = logging.getLogger("us_base_connector")


class USBaseConnector(BaseMarketConnector):
    """
    Base connector for US exchanges (NASDAQ, NYSE)
    Handles Alpaca WebSocket trade stream.
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
                logger.info(
                    f"🔌 Connecting to Alpaca trade stream for {self.symbol}..."
                )

                async with websockets.connect(self.ws_url) as ws:

                    # Authenticate
                    auth_msg = {
                        "action": "auth",
                        "key": self.api_key,
                        "secret": self.secret_key
                    }

                    await ws.send(json.dumps(auth_msg))
                    await ws.recv()
                    await ws.recv()

                    logger.info(
                        f"✅ Authenticated for {self.exchange}:{self.ticker}"
                    )

                    # Subscribe to trades
                    sub_msg = {
                        "action": "subscribe",
                        "trades": [self.ticker]
                    }

                    await ws.send(json.dumps(sub_msg))
                    logger.info(
                        f"📡 Subscribed to {self.ticker}"
                    )

                    async for message in ws:
                        data = json.loads(message)

                        for event in data:
                            if event.get("T") == "t":
                                normalized = self.normalize_trade(event)
                                await trade_collection.insert_one(normalized)

            except Exception as e:
                logger.error(f"❌ US trade stream error: {e}")
                logger.info(
                    f"🔄 Reconnecting in {self.reconnect_delay}s..."
                )
                await asyncio.sleep(self.reconnect_delay)

    async def start_orderbook_stream(self):
        """
        Alpaca free tier does not provide full orderbook depth.
        Reserved for future paid integration.
        """
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

        return unified_trade_schema(
            market_type="US_STOCK",
            symbol=f"{self.exchange}:{self.ticker}",
            price=float(raw["p"]),
            quantity=float(raw["s"]),
            side="BUY",  # Aggressor side not available
            exchange_timestamp=exchange_ts,
            receive_timestamp=receive_time
        )

    def normalize_orderbook(self, raw):
        """
        Placeholder for future US orderbook support.
        """
        return None