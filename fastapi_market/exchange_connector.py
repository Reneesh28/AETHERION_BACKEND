"""
@title AETHERION Live Market Exchange Connector
@notice Connects to Binance real-time trade stream and ingests live data
@dev 
    - Raw WebSocket connection
    - Producer–Consumer architecture
    - Batch Mongo writes
    - Latency tracking
    - Stream health state tracking
"""

import asyncio
import json
import logging
import websockets

from datetime import datetime, timezone
from pymongo import MongoClient

SYMBOL = "btcusdt"
DATA_MODE = "LIVE"  # LIVE | SIMULATION
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "aetherion"
COLLECTION_NAME = "real_market_ticks"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("exchange")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]


"""
@notice Tracks real-time ingestion health
"""
stream_status = {
    "mode": DATA_MODE,          # Current data source mode
    "connected": False,         # WebSocket connection state
    "last_tick_time": None,     # Timestamp of most recent received trade
    "ticks_received": 0,        # Total number of trades received since start
    "last_price": None          # Most recent traded price
}


async def start_live_stream():
    """
    @notice Starts real-time Binance trade ingestion
    @dev Updates stream_status for health tracking
    """

    url = f"wss://stream.binance.com:9443/ws/{SYMBOL}@trade"
    queue = asyncio.Queue()

    counter = 0

    async def mongo_writer():
        """
        @notice Background MongoDB batch writer
        """
        buffer = []  # Temporary storage for batch inserts

        while True:
            tick = await queue.get()
            buffer.append(tick)

            if len(buffer) >= 200:
                await asyncio.to_thread(collection.insert_many, buffer)
                buffer.clear()

    try:
        logger.info(f"Connecting to Binance raw stream for {SYMBOL.upper()}...")

        stream_status["connected"] = True
        stream_status["mode"] = "LIVE"

        asyncio.create_task(mongo_writer())

        async with websockets.connect(url, ping_interval=20) as websocket:
            while True:
                message = await websocket.recv()
                msg = json.loads(message)

                receive_time = int(datetime.now(timezone.utc).timestamp() * 1000)

                normalized = {
                    "symbol": msg["s"],            # Trading pair
                    "price": float(msg["p"]),      # Trade price
                    "quantity": float(msg["q"]),   # Trade size
                    "event_time": msg["E"],        # Binance event time
                    "trade_time": msg["T"],        # Actual trade execution time
                    "receive_time": receive_time,  # Time received by server
                    "latency_ms": max(receive_time - msg["T"], 0),  # Network latency
                }

                counter += 1

                stream_status["ticks_received"] = counter
                stream_status["last_tick_time"] = receive_time
                stream_status["last_price"] = normalized["price"]

                await queue.put(normalized)

                if counter % 500 == 0:
                    logger.info(
                        f"[LIVE] Price: {normalized['price']} | "
                        f"Latency: {normalized['latency_ms']} ms"
                    )

    except Exception as e:
        stream_status["connected"] = False
        logger.error(f"Live stream error: {str(e)}")
        logger.info("Falling back to simulation mode...")