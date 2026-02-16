from fastapi import FastAPI, WebSocket
import asyncio
import time

from fastapi_market.simulator import MarketSimulator
from fastapi_market.service import save_tick, get_snapshot
from fastapi_market.database import candle_collection

app = FastAPI(title="AETHERION Market Engine")

simulator = MarketSimulator()

# Candle state (10-second candles)
current_candle = None
candle_start_time = None


@app.get("/")
def root():
    return {"status": "AETHERION Market Engine Running"}


@app.get("/api/market/snapshot")
async def market_snapshot():
    data = await get_snapshot()
    return {"data": data}


@app.get("/api/market/candles")
async def get_candles():
    cursor = candle_collection.find().sort("start_time", -1).limit(20)
    data = await cursor.to_list(length=20)

    for item in data:
        item["_id"] = str(item["_id"])

    return {"candles": data}


@app.websocket("/ws/market")
async def market_websocket(websocket: WebSocket):
    global current_candle, candle_start_time

    await websocket.accept()

    while True:
        tick = simulator.generate_tick()

        # Save tick to Mongo
        result = await save_tick(tick)
        tick["_id"] = str(result.inserted_id)

        now = int(time.time())

        # Initialize first candle
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

        # If 10 seconds passed → close candle
        elif now - candle_start_time >= 10:
            current_candle["end_time"] = now

            await candle_collection.insert_one(current_candle)

            # Start new candle
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
            # Update existing candle
            current_candle["high"] = max(current_candle["high"], tick["price"])
            current_candle["low"] = min(current_candle["low"], tick["price"])
            current_candle["close"] = tick["price"]
            current_candle["volume"] += tick["volume"]

        await websocket.send_json(tick)
        await asyncio.sleep(1)
