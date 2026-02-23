from fastapi_market.database import trade_collection

# 🔥 Engine will be injected at startup
_candle_engine = None


def register_candle_engine(engine):
    """
    Called once from main.py to inject CandleEngine.
    """
    global _candle_engine
    _candle_engine = engine


async def save_tick(tick):
    """
    Stores raw trade and forwards to CandleEngine.
    """

    # 1️⃣ Store raw trade
    result = await trade_collection.insert_one(tick)

    # 2️⃣ Forward to candle engine (if registered)
    if _candle_engine is not None:
        tick_for_candle = {
            "market": tick["market_type"],
            "symbol": tick["symbol"],
            "price": tick["price"],
            "volume": tick["quantity"],
            "receive_timestamp": tick["receive_timestamp"]
        }

        await _candle_engine.process_tick(tick_for_candle)

    return result


async def get_snapshot(limit=50):
    cursor = trade_collection.find() \
        .sort("receive_timestamp", -1) \
        .limit(limit)

    data = await cursor.to_list(length=limit)

    for item in data:
        item["_id"] = str(item["_id"])

    return data