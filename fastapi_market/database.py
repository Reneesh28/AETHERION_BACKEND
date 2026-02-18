from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "aetherion"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
trade_collection = db["real_market_ticks"]
order_book_collection = db["order_book_snapshots"]
candle_collection = db["candles"]
