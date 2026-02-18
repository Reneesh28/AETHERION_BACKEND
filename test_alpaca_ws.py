import os
import json
import asyncio
import websockets
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
WS_URL = os.getenv("ALPACA_DATA_WSS")


async def test_connection():
    async with websockets.connect(WS_URL) as ws:

        # Authenticate
        auth_msg = {
            "action": "auth",
            "key": API_KEY,
            "secret": SECRET_KEY
        }

        await ws.send(json.dumps(auth_msg))
        print("Sent auth...")

        auth_response = await ws.recv()
        print("Auth response:", auth_response)

        # Subscribe to AAPL trades
        sub_msg = {
            "action": "subscribe",
            "trades": ["AAPL"]
        }

        await ws.send(json.dumps(sub_msg))
        print("Subscribed to AAPL")

        while True:
            message = await ws.recv()
            print("Message:", message)


asyncio.run(test_connection())
