from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_URL)

db = client["aetherion"]

# Collection storing raw trade-by-trade market data
# Each document represents one individual trade (tick)
market_collection = db["market_ticks"]

# Collection storing aggregated OHLC price data
# Each document represents summarized price movement over a time interval (candle)
candle_collection = db["market_candles"]

# Collection storing live order book snapshots
# Each document represents depth snapshot from exchange
order_book_collection = db["order_book_snapshots"]
