import asyncio
import json
from typing import AsyncGenerator, Dict, Any

from aiokafka import AIOKafkaConsumer

from src.config import settings
from src.schemas.validator import (
    validate_market_event,
    ValidationError,
)

from shared.constants.topics import MARKET_ORDERBOOK_RAW_TOPIC


class OrderBookConsumer:
    """
    Kafka consumer for market orderbook events.
    """

    def __init__(self) -> None:

        self.consumer = AIOKafkaConsumer(
            MARKET_ORDERBOOK_RAW_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
            enable_auto_commit=settings.KAFKA_ENABLE_AUTO_COMMIT,
        )

        self._running = False

    async def start(self) -> None:
        """
        Start Kafka consumer.
        """

        await self.consumer.start()

        self._running = True

        print("[OrderBookConsumer] Started")

    async def stop(self) -> None:
        """
        Gracefully stop Kafka consumer.
        """

        self._running = False

        await self.consumer.stop()

        print("[OrderBookConsumer] Stopped")

    async def consume(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Consume and validate orderbook events.
        """

        try:
            async for message in self.consumer:

                if not self._running:
                    break

                try:
                    event = json.loads(message.value.decode("utf-8"))

                    validate_market_event(event)

                    yield event

                except ValidationError as validation_error:

                    print(
                        f"[OrderBookConsumer] Validation failed: "
                        f"{validation_error}"
                    )

                except json.JSONDecodeError as decode_error:

                    print(
                        f"[OrderBookConsumer] JSON decode failed: "
                        f"{decode_error}"
                    )

                except Exception as unexpected_error:

                    print(
                        f"[OrderBookConsumer] Unexpected error: "
                        f"{unexpected_error}"
                    )

                await asyncio.sleep(0)

        finally:
            await self.stop()