import asyncio
import logging


logger = logging.getLogger(__name__)


class ReconnectManager:

    @staticmethod
    async def reconnect(
        reconnect_callback,
        delay: int = 5,
    ):

        logger.warning(
            f"Reconnecting in {delay} seconds..."
        )

        await asyncio.sleep(delay)

        await reconnect_callback()