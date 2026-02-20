"""
@title AETHERION Market Engine (FastAPI Service)
@notice Multi-market ingestion engine
"""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi_market.simulator import MarketSimulator
from fastapi_market.service import save_tick
from fastapi_market.database import (
    candle_collection,
    trade_collection,
    crypto_orderbook_collection,
    us_orderbook_collection,
    nse_orderbook_collection
)

from fastapi_market.config import MarketType
from fastapi_market.connectors.connector_factory import get_connector


# MULTI-MARKET CONFIG
MARKETS = [
    {"type": MarketType.CRYPTO, "symbol": "btcusdt"},
    {"type": MarketType.US_STOCK, "symbol": "NASDAQ:TSLA"},
    {"type": MarketType.US_STOCK, "symbol": "NYSE:IBM"},
]

DATA_MODE = "LIVE"  # LIVE | SIMULATION


# LIFESPAN - START ALL CONNECTORS
@asynccontextmanager
async def lifespan(app: FastAPI):

    tasks = []

    if DATA_MODE == "LIVE":

        for market in MARKETS:

            connector = get_connector(
                market["type"],
                market["symbol"]
            )

            trade_task = asyncio.create_task(
                connector.start_trade_stream()
            )
            tasks.append(trade_task)

            if hasattr(connector, "start_orderbook_stream"):
                ob_task = asyncio.create_task(
                    connector.start_orderbook_stream()
                )
                tasks.append(ob_task)

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
    return {"status": "AETHERION Multi-Market Engine Running"}

# ACTIVE MARKETS
@app.get("/api/market/active")
async def active_markets():
    
    return {"markets": [m["symbol"] for m in MARKETS]}

# SNAPSHOT PER SYMBOL
@app.get("/api/market/snapshot/{symbol}")
async def market_snapshot(symbol: str):
    latest = await trade_collection.find_one(
        {"symbol": symbol},
        sort=[("receive_timestamp", -1)]
    )

    if latest:
        latest["_id"] = str(latest["_id"])

    return {"data": latest}


# LAST 50 TRADES PER SYMBOL
@app.get("/api/market/trades/{symbol}")
async def get_trades(symbol: str):

    cursor = trade_collection.find(
        {"symbol": symbol}
    ).sort("receive_timestamp", -1).limit(50)

    data = await cursor.to_list(length=50)

    for item in data:
        item["_id"] = str(item["_id"])

    return {"trades": data}


# ORDERBOOK PER SYMBOL
@app.get("/api/market/orderbook/{symbol}")
async def get_orderbook(symbol: str):

    if symbol.islower():  # Crypto
        collection = crypto_orderbook_collection

    elif symbol.startswith("NASDAQ:") or symbol.startswith("NYSE:"):
        collection = us_orderbook_collection

    elif symbol.startswith("NSE:"):
        collection = nse_orderbook_collection

    else:
        return {"error": "Unsupported symbol"}

    latest = await collection.find_one(
        {"symbol": symbol.upper()},
        sort=[("receive_timestamp", -1)]
    )

    if latest:
        latest["_id"] = str(latest["_id"])

    return {"orderbook": latest}


# CANDLES (SIMULATION MODE)
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