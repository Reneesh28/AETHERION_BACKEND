import requests
import certifi

requests.Session().verify = certifi.where()

import os
import asyncio
import time
import pyotp
import certifi
import requests

from datetime import datetime, timezone
from SmartApi import SmartConnect

from fastapi_market.connectors.base_connector import BaseMarketConnector
from fastapi_market.schemas import (
    unified_trade_schema,
    unified_orderbook_schema
)
from fastapi_market.database import (
    trade_collection,
    nse_orderbook_collection
)
from fastapi_market.stream_status import stream_status


class NSEMarketConnector(BaseMarketConnector):

    TOKEN_MAP = {
        "2885": "RELIANCE-EQ",
        "11536": "TCS-EQ",
        "15259": "RPOWER-EQ",
        "11915": "YESBANK-EQ"
    }

    PER_TOKEN_DELAY = 1
    CYCLE_INTERVAL = 3
    INITIAL_BACKOFF = 3
    MAX_BACKOFF = 60

    def __init__(self, tokens):
        super().__init__("NSE")
        self.tokens = tokens
        self.api = None

    def _login(self):
        """
        Login with proper SSL certificate handling.
        """

        # 🔥 Force requests to use certifi CA bundle
        requests_session = requests.Session()
        requests_session.verify = certifi.where()

        self.api = SmartConnect(api_key=os.getenv("NSE_API_KEY"))

        # 🔥 Inject our verified session into SmartConnect
        if hasattr(self.api, "session"):
            self.api.session = requests_session

        totp = pyotp.TOTP(os.getenv("NSE_TOTP_SECRET")).now()

        session = self.api.generateSession(
            os.getenv("NSE_CLIENT_ID"),
            os.getenv("NSE_MPIN"),
            totp
        )

        if not session.get("status"):
            raise Exception(f"NSE Login Failed: {session}")

        print("✅ NSE REST Login Successful")

    async def _fetch_ltp(self, token):
        loop = asyncio.get_running_loop()

        def blocking_call():
            return self.api.ltpData(
                exchange="NSE",
                tradingsymbol=self.TOKEN_MAP.get(token, token),
                symboltoken=token
            )

        return await loop.run_in_executor(None, blocking_call)

    def normalize_trade(self, token, raw):
        symbol = self.TOKEN_MAP.get(token, token)
        data = raw.get("data", {})

        price = float(data.get("ltp", 0))

        return unified_trade_schema(
            market_type="NSE",
            symbol=symbol,
            price=price,
            quantity=0,
            side="UNKNOWN",
            exchange_timestamp=int(time.time()),
            receive_timestamp=int(time.time())
        )

    def normalize_orderbook(self, token, raw):
        symbol = self.TOKEN_MAP.get(token, token)
        data = raw.get("data", {})

        best_bid = float(data.get("bid", data.get("bestBid", data.get("ltp", 0))))
        best_ask = float(data.get("ask", data.get("bestAsk", data.get("ltp", 0))))

        bids = [[best_bid, 1]] if best_bid > 0 else []
        asks = [[best_ask, 1]] if best_ask > 0 else []

        return unified_orderbook_schema(
            market_type="NSE",
            symbol=symbol,
            bids=bids,
            asks=asks,
            exchange_timestamp=int(time.time()),
            receive_timestamp=int(time.time())
        )

    async def start_trade_stream(self):

        print("🚀 Starting NSE REST Polling Connector (SSL-Safe Mode)...")

        self._login()

        stream_status["NSE"] = {
            "status": "LIVE",
            "last_update": datetime.now(timezone.utc)
        }

        backoff = self.INITIAL_BACKOFF

        while True:
            try:
                for token in self.tokens:

                    raw = await self._fetch_ltp(token)

                    if not raw or "data" not in raw:
                        continue

                    trade_doc = self.normalize_trade(token, raw)
                    orderbook_doc = self.normalize_orderbook(token, raw)

                    if trade_doc["price"] > 0:
                        await trade_collection.insert_one(trade_doc)
                        await nse_orderbook_collection.insert_one(orderbook_doc)

                        stream_status["NSE"] = {
                            "status": "LIVE",
                            "last_price": trade_doc["price"],
                            "last_update": datetime.now(timezone.utc)
                        }

                    await asyncio.sleep(self.PER_TOKEN_DELAY)

                backoff = self.INITIAL_BACKOFF
                await asyncio.sleep(self.CYCLE_INTERVAL)

            except Exception as e:
                print("❌ NSE REST Polling Error:", e)

                stream_status["NSE"] = {
                    "status": "ERROR",
                    "last_update": datetime.now(timezone.utc)
                }

                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, self.MAX_BACKOFF)

    async def start_orderbook_stream(self):
        pass