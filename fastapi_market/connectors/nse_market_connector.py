import os
import json
import pyotp
import threading
import time
from datetime import datetime, timezone
from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from fastapi_market.database import trade_collection, nse_orderbook_collection
from fastapi_market.stream_status import stream_status


class NSEMarketConnector:

    TOKEN_MAP = {
        "2885": "RELIANCE",
        "11536": "TCS",
        "15259": "RPOWER",
        "11915": "YESBANK"
    }

    WATCHDOG_TIMEOUT = 30  # seconds
    WATCHDOG_CHECK_INTERVAL = 10  # seconds

    def __init__(self, tokens):
        self.tokens = tokens
        self.api = None
        self.feed_token = None
        self.ws = None
        self.is_reconnecting = False
        self.last_tick_time = None

    async def connect(self):
        print("🚀 NSE connect() triggered")
        self._initialize_connection()
        self._start_watchdog()

    def _initialize_connection(self):
        try:
            self.api = SmartConnect(api_key=os.getenv("NSE_API_KEY"))

            totp = pyotp.TOTP(os.getenv("NSE_TOTP_SECRET")).now()

            session = self.api.generateSession(
                os.getenv("NSE_CLIENT_ID"),
                os.getenv("NSE_MPIN"),
                totp
            )

            if not session.get("status"):
                print("❌ NSE Login Failed:", session)
                return

            print("✅ NSE Login Successful")

            self.feed_token = self.api.getfeedToken()

            self.ws = SmartWebSocketV2(
                os.getenv("NSE_CLIENT_ID"),
                os.getenv("NSE_API_KEY"),
                self.feed_token
            )

            self.ws.on_open = self.on_open
            self.ws.on_data = self.on_message
            self.ws.on_error = self.on_error
            self.ws.on_close = self.on_close

            threading.Thread(target=self.ws.connect, daemon=True).start()

        except Exception as e:
            print("❌ NSE Init Error:", e)
            self._schedule_reconnect()

    def on_open(self, ws):
        print("📡 NSE WebSocket Opened")

        self.ws.subscribe(
            correlation_id="nse_stream",
            mode=1,
            token_list=[
                {"exchangeType": 1, "tokens": self.tokens}
            ]
        )

        print("📡 NSE Subscribed to:", self.tokens)

        stream_status["NSE"] = {
            "status": "LIVE",
            "last_update": datetime.now(timezone.utc)
        }

        self.is_reconnecting = False
        self.last_tick_time = datetime.now(timezone.utc)

    def on_message(self, ws, message):
        try:
            self.last_tick_time = datetime.now(timezone.utc)

            data = json.loads(message)
            token = str(data.get("token"))
            symbol_name = self.TOKEN_MAP.get(token, token)

            trade_doc = {
                "symbol": symbol_name,
                "price": float(data.get("last_traded_price", 0)),
                "quantity": float(data.get("last_traded_quantity", 0)),
                "market_type": "NSE",
                "receive_timestamp": datetime.now(timezone.utc)
            }

            trade_collection.insert_one(trade_doc)

            orderbook_doc = {
                "symbol": symbol_name,
                "bids": data.get("best_5_buy_data", []),
                "asks": data.get("best_5_sell_data", []),
                "receive_timestamp": datetime.now(timezone.utc)
            }

            nse_orderbook_collection.insert_one(orderbook_doc)

            stream_status["NSE"] = {
                "status": "LIVE",
                "last_price": trade_doc["price"],
                "last_update": self.last_tick_time
            }

        except Exception as e:
            print("❌ NSE Processing Error:", e)

    def _start_watchdog(self):
        def watchdog():
            while True:
                time.sleep(self.WATCHDOG_CHECK_INTERVAL)

                if self.last_tick_time is None:
                    continue

                elapsed = (datetime.now(timezone.utc) - self.last_tick_time).total_seconds()

                if elapsed > self.WATCHDOG_TIMEOUT:
                    print("⚠️ NSE Feed Stalled. Triggering reconnect...")
                    self._schedule_reconnect()

        threading.Thread(target=watchdog, daemon=True).start()

    def on_error(self, ws, error):
        print("❌ NSE WebSocket Error:", error)
        self._schedule_reconnect()

    def on_close(self, ws):
        print("🔴 NSE WebSocket Closed")
        self._schedule_reconnect()

    def _schedule_reconnect(self):
        if self.is_reconnecting:
            return

        self.is_reconnecting = True

        stream_status["NSE"] = {
            "status": "DISCONNECTED",
            "last_update": datetime.now(timezone.utc)
        }

        print("♻️ Reconnecting to NSE in 5 seconds...")

        def reconnect():
            time.sleep(5)
            self._initialize_connection()

        threading.Thread(target=reconnect, daemon=True).start()