import asyncio
from collections import defaultdict

from fastapi_market.database import trade_collection, candle_collection


class CandleEngine:
    """
    Aggregates real_market_ticks into 1-minute candles
    """

    def __init__(self):
        self.current_candles = {}
        self.last_processed_ts = 0

    async def start(self):
        print("🕯️ Candle Engine Started (1m aggregation)")

        while True:

            # Fetch new ticks since last processed timestamp
            cursor = trade_collection.find(
                {
                    "market_type": "CRYPTO",
                    "exchange_timestamp": {"$gt": self.last_processed_ts}
                }
            ).sort("exchange_timestamp", 1)

            ticks = await cursor.to_list(length=1000)

            if not ticks:
                await asyncio.sleep(0.5)
                continue

            for tick in ticks:
                await self.process_tick(tick)

            await asyncio.sleep(0.1)

    async def process_tick(self, tick):

        symbol = tick["symbol"]
        ts = int(tick["exchange_timestamp"])
        price = float(tick["price"])
        qty = float(tick["quantity"])

        minute_bucket = ts // 60000
        candle_key = (symbol, minute_bucket)

        if symbol not in self.current_candles:

            # First tick ever for this symbol
            self.current_candles[symbol] = {
                "bucket": minute_bucket,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": qty,
                "open_time": minute_bucket * 60000
            }

        current = self.current_candles[symbol]

        if minute_bucket == current["bucket"]:

            # Update existing candle
            current["high"] = max(current["high"], price)
            current["low"] = min(current["low"], price)
            current["close"] = price
            current["volume"] += qty

        else:

            # Minute changed → close previous candle
            await self.store_candle(symbol, current)

            # Start new candle
            self.current_candles[symbol] = {
                "bucket": minute_bucket,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": qty,
                "open_time": minute_bucket * 60000
            }

        self.last_processed_ts = ts

    async def store_candle(self, symbol, candle):

        document = {
            "market": "CRYPTO",
            "symbol": symbol,
            "timeframe": "1m",
            "open": candle["open"],
            "high": candle["high"],
            "low": candle["low"],
            "close": candle["close"],
            "volume": candle["volume"],
            "open_time": candle["open_time"],
            "close_time": candle["open_time"] + 60000
        }

        await candle_collection.insert_one(document)

        print(
            f"🕯️ Stored 1m candle | {symbol} | "
            f"O:{candle['open']} C:{candle['close']}"
        )