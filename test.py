import asyncio
import websockets

async def test():
    uri = "wss://echo.websocket.events"
    async with websockets.connect(uri) as ws:
        print("Connected to echo server!")

asyncio.run(test())