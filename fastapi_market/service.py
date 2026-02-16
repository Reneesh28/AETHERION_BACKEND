from fastapi_market.database import market_collection

async def save_tick(tick):
    result = await market_collection.insert_one(tick)
    return result

async def get_snapshot(limit=50):
    cursor = market_collection.find().sort("timestamp", -1).limit(limit)
    data = await cursor.to_list(length=limit)

    # Convert ObjectId to string
    for item in data:
        item["_id"] = str(item["_id"])

    return data
