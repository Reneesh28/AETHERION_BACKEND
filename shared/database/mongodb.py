from pymongo import MongoClient

from shared.config.settings import settings


def get_mongo_client():

    # Try connecting with authentication credentials first if provided
    if settings.MONGO_USERNAME and settings.MONGO_PASSWORD:
        try:
            client = MongoClient(
                host=settings.MONGO_HOST,
                port=settings.MONGO_PORT,
                username=settings.MONGO_USERNAME,
                password=settings.MONGO_PASSWORD,
                authSource="admin",
                serverSelectionTimeoutMS=2000
            )
            # Verify if authentication succeeds
            client.admin.command("ping")
            return client
        except Exception:
            # Fallback if MongoDB is running in non-auth mode (common in local dev)
            pass

    return MongoClient(
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT
    )