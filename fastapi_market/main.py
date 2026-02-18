"""
@title AETHERION Market Engine (FastAPI Service)
@author AETHERION
@notice Core API service handling market data and WebSocket simulation
@dev
    - Starts live Binance ingestion in LIVE mode
    - Provides REST endpoints for snapshot & candles
    - Provides simulation WebSocket for fallback/testing
"""

from fastapi import FastAPI, WebSocket
import asyncio
import time
from contextlib import asynccontextmanager
from fastapi_market.simulator import MarketSimulator
from fastapi_market.service import save_tick, get_snapshot
from fastapi_market.database import candle_collection
from fastapi_market.database import order_book_collection
from fastapi_market.exchange_connector import start_live_stream, DATA_MODE
from fastapi_market.exchange_connector import stream_status, SYMBOL
from fastapi_market.orderbook_connector import stream_orderbook
from datetime import datetime, timezone

@asynccontextmanager
async def lifespan(app: FastAPI):

    tasks = []

    if DATA_MODE == "LIVE":
        trade_task = asyncio.create_task(start_live_stream())
        orderbook_task = asyncio.create_task(stream_orderbook())

        tasks.append(trade_task)
        tasks.append(orderbook_task)

    yield

    # Shutdown section
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

app = FastAPI(lifespan=lifespan)
simulator = MarketSimulator()
current_candle = None
candle_start_time = None

@app.get("/")
def root():
    """
    @notice Health check endpoint
    """
    return {"status": "AETHERION Market Engine Running"}

@app.get("/api/market/snapshot")
async def market_snapshot():
    """
    @notice Returns latest market snapshot
    """
    data = await get_snapshot()  # Latest tick or aggregated market state
    return {"data": data}

@app.get("/api/market/candles")
async def get_candles():
    """
    @notice Returns last 20 generated candles
    """

    cursor = candle_collection.find().sort("start_time", -1).limit(20)
    data = await cursor.to_list(length=20)

    for item in data:
        item["_id"] = str(item["_id"])

    return {"candles": data}

@app.websocket("/ws/market")
async def market_websocket(websocket: WebSocket):
    """
    @notice Simulation market WebSocket
    @dev Used when DATA_MODE = SIMULATION
    """

    global current_candle, candle_start_time

    await websocket.accept()

    while True:

        tick = simulator.generate_tick()

        result = await save_tick(tick)

        tick["_id"] = str(result.inserted_id)

        now = int(time.time())

        if current_candle is None:
            candle_start_time = now
            current_candle = {
                "open": tick["price"],     # First price of candle
                "high": tick["price"],     # Highest price in candle
                "low": tick["price"],      # Lowest price in candle
                "close": tick["price"],    # Latest price in candle
                "volume": tick["volume"],  # Accumulated trade volume
                "start_time": candle_start_time
            }

        elif now - candle_start_time >= 10:
            current_candle["end_time"] = now  # Candle closing time
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

@app.get("/api/market/source")
async def market_source():
    """
    @notice Returns current market data source status
    """

    last_tick = stream_status["last_tick_time"]

    return {
        "mode": stream_status["mode"],  # LIVE or SIMULATION
        "symbol": SYMBOL.upper(),       # Trading pair
        "connected": stream_status["connected"],  # WebSocket connection state
        "last_price": stream_status["last_price"],  # Most recent price
        "ticks_received": stream_status["ticks_received"],  # Total trades received
        "last_tick_time": (
            datetime.fromtimestamp(last_tick / 1000).isoformat()
            if last_tick else None
        )
    }

@app.get("/api/market/orderbook")
async def get_latest_orderbook():
    """
    @notice Returns latest order book snapshot
    """

    latest = await order_book_collection.find_one(
        sort=[("receive_timestamp", -1)]
    )

    if latest:
        latest["_id"] = str(latest["_id"])

    return {"orderbook": latest}
