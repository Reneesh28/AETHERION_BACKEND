import json
import logging
from services.ingestion_service.src.config import settings
from services.ingestion_service.src.connectors.base_connector import BaseConnector
logger = logging.getLogger(__name__)


class BinanceConnector(BaseConnector):

    def __init__(self):

        super().__init__(
            settings.BINANCE_WS_URL
        )

    async def subscribe_trades(
        self,
        symbol: str = "btcusdt"
    ):

        subscribe_payload = {
            "method": "SUBSCRIBE",
            "params": [
                f"{symbol}@trade"
            ],
            "id": 1
        }

        await self.websocket.send(
            json.dumps(subscribe_payload)
        )

        logger.info(
            f"Subscribed to {symbol} trades"
        )

    async def stream_trades(self):

        self.running = True

        await self.connect()

        await self.subscribe_trades()

        async for message in self.receive():

            if message.get("e") == "trade":

                yield message