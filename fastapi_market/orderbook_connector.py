import asyncio
import websockets
import json
import time
from datetime import datetime, timezone
from fastapi_market.database import order_book_collection

# CONFIGURATION
SYMBOL = "btcusdt"
WS_URL = f"wss://stream.binance.com:9443/ws/{SYMBOL}@depth@100ms"
HEARTBEAT_TIMEOUT = 20  # seconds
RECONNECT_DELAY = 5  # seconds

# MESSAGE VALIDATION
def validate_message(data):
    """
    Validate order book message structure
    """
    if not isinstance(data, dict):
        return False

    if "b" not in data or "a" not in data:
        return False

    if not isinstance(data["b"], list) or not isinstance(data["a"], list):
        return False

    return True

# STREAM FUNCTION
async def stream_orderbook():
    """
    Connects to Binance order book stream
    Includes:
    - Auto reconnect
    - Heartbeat monitoring
    - Message validation
    """

    while True:
        try:
            print("🔌 Connecting to Binance order book...")

            async with websockets.connect(WS_URL) as websocket:
                print("✅ Connected to Order Book stream")

                last_message_time = time.time()

                async for message in websocket:

                    data = json.loads(message)

                    # Validate structure
                    if not validate_message(data):
                        print("⚠ Invalid message received. Skipping...")
                        continue

                    last_message_time = time.time()

                    snapshot = {
                        "symbol": SYMBOL.upper(),
                        "bids": data.get("b", []),
                        "asks": data.get("a", []),
                        "exchange_timestamp": data.get("E"),
                        "receive_timestamp": int(time.time() * 1000),
                        "created_at": datetime.now(timezone.utc)
                    }

                    # ✅ Async insert using Motor
                    await order_book_collection.insert_one(snapshot)

                    print("📥 Snapshot stored")

                    # Heartbeat check
                    if time.time() - last_message_time > HEARTBEAT_TIMEOUT:
                        print("⚠ Heartbeat lost. Breaking connection...")
                        break

        except Exception as e:
            print(f"❌ Disconnected: {e}")
            print(f"🔄 Reconnecting in {RECONNECT_DELAY} seconds...\n")
            await asyncio.sleep(RECONNECT_DELAY)
