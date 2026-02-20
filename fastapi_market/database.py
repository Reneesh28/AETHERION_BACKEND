from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "aetherion"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Unified trade collection
trade_collection = db["real_market_ticks"]

# Separate orderbook collections
crypto_orderbook_collection = db["crypto_orderbooks"]
us_orderbook_collection = db["us_orderbooks"]
nse_orderbook_collection = db["nse_orderbooks"]

# Candles
candle_collection = db["candles"]