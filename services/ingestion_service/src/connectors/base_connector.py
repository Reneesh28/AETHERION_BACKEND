import asyncio
import json
import logging
import websockets

logger = logging.getLogger(__name__)


class BaseConnector:
    def __init__(self, ws_url: str):

        self.ws_url = ws_url

        self.websocket = None

        self.running = False

    async def connect(self):

        logger.info(f"Connecting to {self.ws_url}")

        self.websocket = await websockets.connect(
            self.ws_url
        )

        logger.info("WebSocket connected")

    async def disconnect(self):

        if self.websocket:

            await self.websocket.close()

            logger.info("WebSocket disconnected")

    async def receive(self):

        while self.running:

            try:

                message = await self.websocket.recv()

                yield json.loads(message)

            except Exception as e:

                logger.error(f"Receive error: {e}")

                break

    async def reconnect(self):

        logger.warning("Reconnecting websocket...")

        await asyncio.sleep(5)

        await self.connect()