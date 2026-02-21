from fastapi_market.database import trade_collection
from fastapi_market.feature_engine import FeatureEngine

feature_engine = FeatureEngine()

async def save_tick(tick):

    result = await trade_collection.insert_one(tick)
    try:
        await feature_engine.process_tick({
            "market": tick.get("market_type"),
            "symbol": tick.get("symbol"),
            "price": tick.get("price"),
            "volume": tick.get("volume", 0),
            "timestamp": tick.get("receive_timestamp") or tick.get("timestamp")
        })
    except Exception as e:
        print(f"Feature Engine Error: {e}")

    return result

async def get_snapshot(limit=50):
    cursor = trade_collection.find().sort("timestamp", -1).limit(limit)
    data = await cursor.to_list(length=limit)

    for item in data:
        item["_id"] = str(item["_id"])

    return data