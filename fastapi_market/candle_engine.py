import asyncio
from fastapi_market.database import trade_collection, candle_collection


class CandleEngine:
    """
    Aggregates real_market_ticks into 1-minute candles
    Uses Mongo _id for streaming cursor (safe)
    Uses receive_timestamp for time bucketing
    """

    def __init__(self):
        self.current_candles = {}

    async def start(self):

        print("🕯️ Candle Engine Started (1m aggregation)")

        # 🔥 Initialize cursor from latest document
        latest_doc = await trade_collection.find_one(
            sort=[("_id", -1)]
        )

        last_id = latest_doc["_id"] if latest_doc else None

        while True:

            query = {}

            if last_id:
                query["_id"] = {"$gt": last_id}

            cursor = trade_collection.find(
                query
            ).sort("_id", 1).limit(1000)

            ticks = await cursor.to_list(length=1000)

            if not ticks:
                await asyncio.sleep(0.5)
                continue

            for tick in ticks:
                await self.process_tick(tick)
                last_id = tick["_id"]

            await asyncio.sleep(0.1)

    async def process_tick(self, tick):

        symbol = tick["symbol"]
        ts = int(tick["receive_timestamp"])  # ✅ Use receive time
        price = float(tick["price"])
        qty = float(tick["quantity"])

        minute_bucket = ts // 60000

        if symbol not in self.current_candles:

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

            # Update current candle
            current["high"] = max(current["high"], price)
            current["low"] = min(current["low"], price)
            current["close"] = price
            current["volume"] += qty

        else:

            # 🔥 Minute changed → close previous candle
            await self.store_candle(symbol, current)

            # 🔥 Start new candle
            self.current_candles[symbol] = {
                "bucket": minute_bucket,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": qty,
                "open_time": minute_bucket * 60000
            }

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