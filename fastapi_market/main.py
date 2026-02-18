"""
@title AETHERION Market Engine (FastAPI Service)
@notice Market-agnostic ingestion engine
@dev
    - Connector Factory driven
    - UTC timezone-aware timestamps
"""

from dotenv import load_dotenv
load_dotenv()


from fastapi import FastAPI, WebSocket
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi_market.simulator import MarketSimulator
from fastapi_market.service import save_tick, get_snapshot
from fastapi_market.database import (
    candle_collection,
    order_book_collection
)

from fastapi_market.config import MarketType
from fastapi_market.connectors.connector_factory import get_connector


# MARKET CONFIG
# MARKET_TYPE = MarketType.CRYPTO
# SYMBOL = "btcusdt"
MARKET_TYPE = MarketType.US_STOCK
SYMBOL = "NASDAQ:TSLA"
DATA_MODE = "LIVE"  # LIVE | SIMULATION


# LIFESPAN
@asynccontextmanager
async def lifespan(app: FastAPI):

    tasks = []

    if DATA_MODE == "LIVE":

        connector = get_connector(MARKET_TYPE, SYMBOL)

        trade_task = asyncio.create_task(
            connector.start_trade_stream()
        )

        orderbook_task = asyncio.create_task(
            connector.start_orderbook_stream()
        )

        tasks.extend([trade_task, orderbook_task])

    yield

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)


app = FastAPI(lifespan=lifespan)

simulator = MarketSimulator()
current_candle = None
candle_start_time = None


# HEALTH CHECK
@app.get("/")
def root():
    return {"status": "AETHERION Market Engine Running"}


# SNAPSHOT
@app.get("/api/market/snapshot")
async def market_snapshot():
    data = await get_snapshot()
    return {"data": data}


# CANDLES
@app.get("/api/market/candles")
async def get_candles():

    cursor = candle_collection.find().sort("start_time", -1).limit(20)
    data = await cursor.to_list(length=20)

    for item in data:
        item["_id"] = str(item["_id"])

    return {"candles": data}


# SIMULATION WEBSOCKET
@app.websocket("/ws/market")
async def market_websocket(websocket: WebSocket):

    global current_candle, candle_start_time

    await websocket.accept()

    while True:

        tick = simulator.generate_tick()
        result = await save_tick(tick)
        tick["_id"] = str(result.inserted_id)

        now = datetime.now(timezone.utc)

        if current_candle is None:
            candle_start_time = now
            current_candle = {
                "open": tick["price"],
                "high": tick["price"],
                "low": tick["price"],
                "close": tick["price"],
                "volume": tick["volume"],
                "start_time": candle_start_time
            }

        elif (now - candle_start_time).total_seconds() >= 10:

            current_candle["end_time"] = now
            await candle_collection.insert_one(current_candle)

            candle_start_time = now
            current_candle = {
                "open": tick["price"],
                "high": tick["price"],
                "low": tick["price"],
                "close": tick["price"],
                "volume": tick["volume"],
                "start_time": candle_start_time
            }

        else:
            current_candle["high"] = max(current_candle["high"], tick["price"])
            current_candle["low"] = min(current_candle["low"], tick["price"])
            current_candle["close"] = tick["price"]
            current_candle["volume"] += tick["volume"]

        await websocket.send_json(tick)

        await asyncio.sleep(1)


# ORDERBOOK ENDPOINT
@app.get("/api/market/orderbook")
async def get_latest_orderbook():

    latest = await order_book_collection.find_one(
        sort=[("receive_timestamp", -1)]
    )

    if latest:
        latest["_id"] = str(latest["_id"])

    return {"orderbook": latest}
