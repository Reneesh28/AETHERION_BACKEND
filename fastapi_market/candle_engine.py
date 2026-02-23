import asyncio
from collections import defaultdict
from fastapi_market.feature_engine import FeatureEngine


TIMEFRAMES = {
    "1m": 60_000,
    "5m": 300_000,
    "15m": 900_000,
    "1h": 3_600_000,
}


class MultiTimeframeCandleEngine:
    def __init__(self, mongo_client):
        self.mongo = mongo_client
        self.lock = asyncio.Lock()
        self.feature_engine = FeatureEngine()

        self.active_candles = defaultdict(
            lambda: defaultdict(dict)
        )

    def get_bucket_start(self, ts_ms: int, tf_ms: int):
        return (ts_ms // tf_ms) * tf_ms

    async def process_tick(self, tick: dict):

        async with self.lock:

            market = tick["market"]
            symbol = tick["symbol"]
            price = float(tick["price"])
            volume = float(tick.get("volume", 0))
            ts = int(tick["receive_timestamp"])

            for tf_name, tf_ms in TIMEFRAMES.items():

                bucket_start = self.get_bucket_start(ts, tf_ms)
                current = self.active_candles[market][symbol].get(tf_name)

                if current is None:
                    self.active_candles[market][symbol][tf_name] = {
                        "market": market,
                        "symbol": symbol,
                        "timeframe": tf_name,
                        "bucket_start": bucket_start,
                        "open": price,
                        "high": price,
                        "low": price,
                        "close": price,
                        "volume": volume,
                    }
                    continue

                if bucket_start == current["bucket_start"]:
                    current["high"] = max(current["high"], price)
                    current["low"] = min(current["low"], price)
                    current["close"] = price
                    current["volume"] += volume

                else:
                    await self._finalize_candle(current)

                    self.active_candles[market][symbol][tf_name] = {
                        "market": market,
                        "symbol": symbol,
                        "timeframe": tf_name,
                        "bucket_start": bucket_start,
                        "open": price,
                        "high": price,
                        "low": price,
                        "close": price,
                        "volume": volume,
                    }

    async def _finalize_candle(self, candle):

        doc = {
            **candle,
            "timestamp": candle["bucket_start"]
        }

        await self.mongo["candles"].insert_one(doc)

        # 🔥 Immediately compute features
        await self.feature_engine.process_candle(doc)

    async def flush_all(self):
        async with self.lock:
            for market in self.active_candles:
                for symbol in self.active_candles[market]:
                    for tf in self.active_candles[market][symbol]:
                        candle = self.active_candles[market][symbol][tf]
                        await self._finalize_candle(candle)