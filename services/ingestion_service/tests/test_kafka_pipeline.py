import asyncio

from services.ingestion_service.src.workers.supervisor import (
    WorkerSupervisor,
)


async def main():

    supervisor = WorkerSupervisor()

    await supervisor.start()


if __name__ == "__main__":

    asyncio.run(main())