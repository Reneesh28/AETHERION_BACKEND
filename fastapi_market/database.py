from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "aetherion")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

trade_collection = db["real_market_ticks"]

crypto_orderbook_collection = db["crypto_orderbooks"]

nasdaq_orderbook_collection = db["nasdaq_orderbooks"]

nyse_orderbook_collection = db["nyse_orderbooks"]

candle_collection = db["candles"]


async def create_indexes():
    await trade_collection.create_index(
        [("symbol", 1), ("exchange_timestamp", -1)]
    )

    await candle_collection.create_index(
        [("symbol", 1), ("timeframe", 1), ("open_time", -1)]
    )