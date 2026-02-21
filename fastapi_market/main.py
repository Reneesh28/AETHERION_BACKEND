"""
@title AETHERION Market Engine (FastAPI Service)
@notice Multi-market ingestion engine with stream monitoring
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
from fastapi_market.connectors.us_market_connector import USMarketConnector
from fastapi_market.connectors.nse_market_connector import NSEMarketConnector
from fastapi_market.stream_status import stream_status
from fastapi_market.feature_engine import FeatureEngine

feature_engine = FeatureEngine()
CRYPTO_MARKETS = [{"type": MarketType.CRYPTO, "symbol": "btcusdt"}]
US_SYMBOLS = ["NASDAQ:TSLA", "NYSE:IBM"]
NSE_TOKENS = ["2885", "11536", "15259", "11915"]
DATA_MODE = "LIVE"

@asynccontextmanager
async def lifespan(app: FastAPI):

    tasks = []

    app.state.loop = asyncio.get_running_loop()

    if DATA_MODE == "LIVE":

        for market in CRYPTO_MARKETS:
            connector = get_connector(
                market["type"],
                market["symbol"]
            )

            tasks.append(
                asyncio.create_task(connector.start_trade_stream())
            )

            if hasattr(connector, "start_orderbook_stream"):
                tasks.append(
                    asyncio.create_task(connector.start_orderbook_stream())
                )
        us_connector = USMarketConnector(US_SYMBOLS)
        tasks.append(
            asyncio.create_task(us_connector.start_trade_stream())
        )
        print("🚀 Starting NSE Connector...")
        nse_connector = NSEMarketConnector(NSE_TOKENS)
        tasks.append(
            asyncio.create_task(nse_connector.start_trade_stream())
        )
        print("🧠 Starting Feature Consumer Loop...")
        tasks.append(
            asyncio.create_task(feature_engine.start_feature_consumer())
        )

    yield

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

app = FastAPI(lifespan=lifespan)
simulator = MarketSimulator()
current_candle = None
candle_start_time = None

@app.get("/")
def root():
    return {"status": "AETHERION Multi-Market Engine Running"}

@app.get("/api/market/status")
async def market_status():
    return stream_status

@app.get("/api/market/active")
async def active_markets():
    return {
        "crypto": [m["symbol"] for m in CRYPTO_MARKETS],
        "us": US_SYMBOLS,
        "nse": NSE_TOKENS
    }

@app.get("/api/market/snapshot/{market}")
async def market_snapshot(market: str):

    market = market.lower()

    if market == "crypto":
        market_type = "CRYPTO"
    elif market == "us":
        market_type = "US_STOCK"
    elif market == "nse":
        market_type = "NSE"
    else:
        return {"error": "Invalid market type"}

    latest = await trade_collection.find_one(
        {"market_type": market_type},
        sort=[("receive_timestamp", -1)]
    )

    if latest:
        latest["_id"] = str(latest["_id"])

    return {"data": latest}

@app.get("/api/market/trades/{market}")
async def get_trades(market: str):

    market = market.lower()

    if market == "crypto":
        market_type = "CRYPTO"
    elif market == "us":
        market_type = "US_STOCK"
    elif market == "nse":
        market_type = "NSE"
    else:
        return {"error": "Invalid market type"}

    cursor = trade_collection.find(
        {"market_type": market_type}
    ).sort("receive_timestamp", -1).limit(50)

    data = await cursor.to_list(length=50)

    for item in data:
        item["_id"] = str(item["_id"])

    return {"trades": data}

@app.get("/api/market/orderbook/{market}")
async def get_orderbook(market: str):

    market = market.lower()

    if market == "crypto":
        collection = crypto_orderbook_collection
    elif market == "us":
        collection = us_orderbook_collection
    elif market == "nse":
        collection = nse_orderbook_collection
    else:
        return {"error": "Invalid market type"}

    latest = await collection.find_one(
        sort=[("receive_timestamp", -1)]
    )

    if latest:
        latest["_id"] = str(latest["_id"])

    return {"orderbook": latest}

@app.get("/api/market/features/{market}")
async def get_features(market: str, limit: int = 50):

    market = market.lower()

    if market == "crypto":
        market_type = "CRYPTO"
    elif market == "us":
        market_type = "US_STOCK"
    elif market == "nse":
        market_type = "NSE"
    else:
        return {"error": "Invalid market type"}

    cursor = feature_engine.collection.find(
        {"market": market_type}
    ).sort("created_at", -1).limit(limit)

    data = await cursor.to_list(length=limit)

    for item in data:
        item["_id"] = str(item["_id"])

    return {
        "market": market_type,
        "count": len(data),
        "features": data
    }

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