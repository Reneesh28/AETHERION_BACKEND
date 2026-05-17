from shared.database.mongodb import get_mongo_client


client = get_mongo_client()

db = client["aetherion"]


market_ticks = db["market_ticks"]

order_book = db["order_book"]


market_ticks.insert_one({
    "status": "initialized"
})

order_book.insert_one({
    "status": "initialized"
})


print("MongoDB collections initialized successfully")