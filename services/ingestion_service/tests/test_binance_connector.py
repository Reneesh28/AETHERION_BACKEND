import asyncio

from services.ingestion_service.src.connectors.binance_connector import BinanceConnector


async def main():

    connector = BinanceConnector()

    count = 0

    async for event in connector.stream_trades():

        print(event)

        count += 1

        if count >= 5:
            break

    await connector.disconnect()


if __name__ == "__main__":

    asyncio.run(main())