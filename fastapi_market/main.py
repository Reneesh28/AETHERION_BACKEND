"""
@title AETHERION Market Engine (FastAPI Service)
@notice Multi-market ingestion engine with stream monitoring + Regime WebSocket
"""

from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, WebSocket
import asyncio
from contextlib import asynccontextmanager
from fastapi_market.simulator import MarketSimulator
from fastapi_market.database import (
    candle_collection,
    trade_collection,
    crypto_orderbook_collection,
    nasdaq_orderbook_collection,
    nyse_orderbook_collection
)
from fastapi_market.config import MarketType
from fastapi_market.connectors.connector_factory import get_connector
from fastapi_market.connectors.us_market_connector import USMarketConnector
from fastapi_market.stream_status import stream_status
from fastapi_market.feature_engine import FeatureEngine
from fastapi_market.regime_poller import poll_regime
from fastapi_market.regime_ws import regime_manager
from fastapi_market.candle_engine import CandleEngine   # ✅ NEW IMPORT


feature_engine = FeatureEngine()
candle_engine = CandleEngine()  # ✅ NEW INSTANCE


CRYPTO_MARKETS = [{"type": MarketType.CRYPTO, "symbol": "btcusdt"}]

US_SYMBOLS = [
    "NASDAQ:TSLA",
    "NYSE:IBM"
]

DATA_MODE = "LIVE"


# =====================================================
# LIFESPAN
# =====================================================
@asynccontextmanager
async def lifespan(app: FastAPI):

    tasks = []
    app.state.loop = asyncio.get_running_loop()

    if DATA_MODE == "LIVE":

        # ----------------------------
        # CRYPTO CONNECTOR
        # ----------------------------
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

        # ----------------------------
        # US CONNECTOR
        # ----------------------------
        us_connector = USMarketConnector(US_SYMBOLS)

        tasks.append(
            asyncio.create_task(us_connector.start_trade_stream())
        )

        # ----------------------------
        # FEATURE ENGINE
        # ----------------------------
        tasks.append(
            asyncio.create_task(feature_engine.start_feature_consumer())
        )

        # ----------------------------
        # 🕯️ CANDLE ENGINE (NEW)
        # ----------------------------
        tasks.append(
            asyncio.create_task(candle_engine.start())
        )

        # ----------------------------
        # REGIME POLLER
        # ----------------------------
        tasks.append(
            asyncio.create_task(poll_regime())
        )

    yield

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)


app = FastAPI(lifespan=lifespan)

simulator = MarketSimulator()


# =====================================================
# BASIC ENDPOINTS
# =====================================================
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
        "nasdaq": [s for s in US_SYMBOLS if s.startswith("NASDAQ")],
        "nyse": [s for s in US_SYMBOLS if s.startswith("NYSE")]
    }


# =====================================================
# SNAPSHOT
# =====================================================
@app.get("/api/market/snapshot/{market}")
async def market_snapshot(market: str):

    market = market.upper()

    if market not in ["CRYPTO", "NASDAQ", "NYSE"]:
        return {"error": "Invalid market type"}

    latest = await trade_collection.find_one(
        {"market_type": market},
        sort=[("receive_timestamp", -1)]
    )

    if latest:
        latest["_id"] = str(latest["_id"])

    return {"data": latest}


# =====================================================
# TRADES
# =====================================================
@app.get("/api/market/trades/{market}")
async def get_trades(market: str):

    market = market.upper()

    if market not in ["CRYPTO", "NASDAQ", "NYSE"]:
        return {"error": "Invalid market type"}

    cursor = trade_collection.find(
        {"market_type": market}
    ).sort("receive_timestamp", -1).limit(50)

    data = await cursor.to_list(length=50)

    for item in data:
        item["_id"] = str(item["_id"])

    return {"trades": data}


# =====================================================
# ORDERBOOK
# =====================================================
@app.get("/api/market/orderbook/{market}")
async def get_orderbook(market: str):

    market = market.upper()

    if market == "CRYPTO":
        collection = crypto_orderbook_collection
    elif market == "NASDAQ":
        collection = nasdaq_orderbook_collection
    elif market == "NYSE":
        collection = nyse_orderbook_collection
    else:
        return {"error": "Invalid market type"}

    latest = await collection.find_one(
        sort=[("receive_timestamp", -1)]
    )

    if latest:
        latest["_id"] = str(latest["_id"])

    return {"orderbook": latest}


# =====================================================
# FEATURES
# =====================================================
@app.get("/api/market/features/{market}")
async def get_features(market: str, limit: int = 50):

    market = market.upper()

    if market not in ["CRYPTO", "NASDAQ", "NYSE"]:
        return {"error": "Invalid market type"}

    cursor = feature_engine.collection.find(
        {"market": market}
    ).sort("created_at", -1).limit(limit)

    data = await cursor.to_list(length=limit)

    for item in data:
        item["_id"] = str(item["_id"])

    return {
        "market": market,
        "count": len(data),
        "features": data
    }


# =====================================================
# REGIME WEBSOCKET
# =====================================================
@app.websocket("/ws/regime")
async def regime_websocket(websocket: WebSocket):
    await regime_manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(60)
    except:
        regime_manager.disconnect(websocket)