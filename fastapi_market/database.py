from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_URL)
db = client["aetherion"]

market_collection = db["market_ticks"]
candle_collection = db["market_candles"]
