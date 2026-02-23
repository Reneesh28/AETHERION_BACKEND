import asyncio
from datetime import datetime, timezone
from collections import defaultdict


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

        # market -> symbol -> timeframe -> candle
        self.active_candles = defaultdict(
            lambda: defaultdict(dict)
        )

    def get_bucket_start(self, ts_ms: int, tf_ms: int):
        return (ts_ms // tf_ms) * tf_ms

    async def process_tick(self, tick: dict):
        """
        tick must contain:
        {
            market: str,
            symbol: str,
            price: float,
            volume: float,
            receive_timestamp: int (ms UTC)
        }
        """

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
                    # First candle ever
                    self.active_candles[market][symbol][tf_name] = (
                        self._create_new_candle(
                            market, symbol, tf_name,
                            bucket_start, price, volume
                        )
                    )
                    continue

                # -------------------------
                # Same Bucket → Update
                # -------------------------
                if bucket_start == current["bucket_start"]:

                    current["high"] = max(current["high"], price)
                    current["low"] = min(current["low"], price)
                    current["close"] = price
                    current["volume"] += volume

                # -------------------------
                # New Bucket → Close + Gap Fill
                # -------------------------
                else:
                    await self._finalize_candle(current)

                    # Gap handling
                    prev_bucket = current["bucket_start"]
                    while bucket_start > prev_bucket + tf_ms:
                        prev_bucket += tf_ms

                        gap_candle = self._create_gap_candle(
                            market, symbol, tf_name,
                            prev_bucket,
                            current["close"]
                        )

                        await self._finalize_candle(gap_candle)

                    # Start new real candle
                    self.active_candles[market][symbol][tf_name] = (
                        self._create_new_candle(
                            market, symbol, tf_name,
                            bucket_start, price, volume
                        )
                    )

    def _create_new_candle(
        self, market, symbol, tf_name,
        bucket_start, price, volume
    ):
        return {
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

    def _create_gap_candle(
        self, market, symbol, tf_name,
        bucket_start, last_close
    ):
        return {
            "market": market,
            "symbol": symbol,
            "timeframe": tf_name,
            "bucket_start": bucket_start,
            "open": last_close,
            "high": last_close,
            "low": last_close,
            "close": last_close,
            "volume": 0.0,
        }

    async def _finalize_candle(self, candle):
        """
        Store to Mongo.
        Push to WebSocket if needed.
        """

        await self.mongo["candles"].insert_one({
            **candle,
            "timestamp": candle["bucket_start"]
        })

    async def flush_all(self):
        async with self.lock:
            for market in self.active_candles:
                for symbol in self.active_candles[market]:
                    for tf in self.active_candles[market][symbol]:
                        candle = self.active_candles[market][symbol][tf]
                        await self._finalize_candle(candle)