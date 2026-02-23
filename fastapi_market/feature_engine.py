import asyncio
from collections import deque, defaultdict
from typing import Dict
import numpy as np
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

WINDOW_SIZE = 20


class FeatureEngine:

    def __init__(self, mongo_url="mongodb://localhost:27017"):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client["aetherion"]
        self.collection = self.db["market_features"]

        # Rolling buffers
        self.price_buffer: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=WINDOW_SIZE)
        )
        self.volume_buffer: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=WINDOW_SIZE)
        )
        self.tr_buffer: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=WINDOW_SIZE)
        )

    def _buffer_key(self, market: str, symbol: str):
        return f"{market}:{symbol}"

    async def process_tick(self, tick: dict):

        try:
            market = tick["market"]
            symbol = tick["symbol"]
            price = float(tick["price"])
            volume = float(tick.get("volume", 0))
            timestamp = tick["timestamp"]
        except Exception:
            return

        key = self._buffer_key(market, symbol)

        previous_price = (
            self.price_buffer[key][-1]
            if len(self.price_buffer[key]) > 0
            else None
        )

        # Update buffers
        self.price_buffer[key].append(price)
        self.volume_buffer[key].append(volume)

        # True Range (tick-based)
        if previous_price is not None:
            true_range = abs(price - previous_price)
            self.tr_buffer[key].append(true_range)

        if len(self.price_buffer[key]) < WINDOW_SIZE:
            return

        await self.compute_and_store_features(
            market, symbol, timestamp, key
        )

    async def compute_spread(self, market, symbol):

        try:
            if market == "CRYPTO":
                collection = self.db["crypto_orderbooks"]
            elif market == "NASDAQ":
                collection = self.db["nasdaq_orderbooks"]
            elif market == "NYSE":
                collection = self.db["nyse_orderbooks"]
            else:
                return 0.0

            orderbook = await collection.find_one(
                {"symbol": symbol},
                sort=[("receive_timestamp", -1)]
            )

            if not orderbook:
                return 0.0

            bids = orderbook.get("bids", [])
            asks = orderbook.get("asks", [])

            if not bids or not asks:
                return 0.0

            best_bid = float(bids[0][0])
            best_ask = float(asks[0][0])

            return float(best_ask - best_bid)

        except Exception:
            return 0.0

    async def compute_and_store_features(self, market, symbol, timestamp, key):

        prices = np.array(self.price_buffer[key])
        volumes = np.array(self.volume_buffer[key])
        tr_values = np.array(self.tr_buffer[key])

        # Log returns
        log_returns = np.diff(np.log(prices))

        if len(log_returns) > 1:
            rolling_volatility = float(
                np.std(log_returns) * np.sqrt(WINDOW_SIZE)
            )
            latest_log_return = float(log_returns[-1])
        else:
            rolling_volatility = 0.0
            latest_log_return = 0.0

        # ATR
        if len(tr_values) > 0:
            atr = float(np.mean(tr_values))
        else:
            atr = 0.0

        # Spread
        spread = await self.compute_spread(market, symbol)

        mid_price = float(prices[-1])

        if len(volumes) > 1:
            volume_delta = float(volumes[-1] - volumes[-2])
        else:
            volume_delta = 0.0

        feature_doc = {
            "market": market,
            "symbol": symbol,
            "timestamp": timestamp,
            "mid_price": mid_price,
            "spread": spread,
            "log_return": latest_log_return,
            "rolling_volatility": rolling_volatility,
            "atr": atr,
            "volume_delta": volume_delta,
            "created_at": datetime.utcnow()
        }

        await self.collection.insert_one(feature_doc)

    async def start_feature_consumer(self):

        latest_doc = await self.db["real_market_ticks"].find_one(
            sort=[("_id", -1)]
        )

        last_id = latest_doc["_id"] if latest_doc else None

        print("🧠 Feature Consumer initialized.")

        while True:
            try:
                query = {}

                if last_id:
                    query["_id"] = {"$gt": last_id}

                cursor = self.db["real_market_ticks"].find(
                    query
                ).sort("_id", 1).limit(100)

                ticks = await cursor.to_list(length=100)

                for tick in ticks:

                    await self.process_tick({
                        "market": tick.get("market_type"),
                        "symbol": tick.get("symbol"),
                        "price": tick.get("price"),
                        "volume": tick.get("quantity", 0),
                        "timestamp": tick.get("receive_timestamp")
                    })

                    last_id = tick["_id"]

                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"Feature Consumer Error: {e}")
                await asyncio.sleep(1)