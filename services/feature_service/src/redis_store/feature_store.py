import json
import logging
from typing import Dict, Any, Optional
import redis.asyncio as aioredis
from src.config import settings
from src.redis_store.cache_keys import get_feature_key

logger = logging.getLogger("feature_service.redis_store")


class RedisFeatureStore:
    """
    Asynchronous online feature store using Redis.
    Handles low-latency snapshot reads and writes with built-in fault tolerance.
    """

    def __init__(self, client: Optional[aioredis.Redis] = None) -> None:
        self._client = client
        self.host = settings.REDIS_HOST
        self.port = settings.REDIS_PORT
        self.db = settings.REDIS_DB
        self.ttl = settings.FEATURE_TTL_SECONDS
        self._connected = False

    def _get_client(self) -> aioredis.Redis:
        """
        Lazy initializer for the Redis client.
        """
        if self._client is None:
            self._client = aioredis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
                socket_timeout=1.0,
                socket_connect_timeout=1.0,
            )
        return self._client

    async def connect(self) -> bool:
        """
        Tests the connection to Redis. Returns True if successful, False otherwise.
        """
        try:
            client = self._get_client()
            await client.ping()
            self._connected = True
            logger.info("Successfully connected to Redis Feature Store")
            return True
        except Exception as e:
            self._connected = False
            logger.error(f"Failed to connect to Redis Feature Store: {e}")
            return False

    async def close(self) -> None:
        """
        Closes the Redis client connection.
        """
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            self._connected = False
            logger.info("Closed Redis Feature Store connection")

    async def store_snapshot(
        self,
        symbol: str,
        window: str,
        features: Dict[str, Any],
        timestamp: int,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """
        Stores a standardized feature snapshot in Redis with an expiration TTL.
        Returns True if successful, False if a Redis exception occurred (graceful failure).
        """
        try:
            client = self._get_client()
            key = get_feature_key(symbol, window)

            payload = {
                "symbol": symbol,
                "window": window,
                "timestamp": timestamp,
                "features": features,
            }

            serialized = json.dumps(payload)
            expire_ttl = ttl_seconds if ttl_seconds is not None else self.ttl

            await client.set(key, serialized, ex=expire_ttl)
            return True
        except Exception as e:
            logger.error(f"Redis store failed for key '{symbol}:{window}': {e}")
            return False

    async def get_snapshot(self, symbol: str, window: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the latest feature snapshot for a symbol and window.
        Returns None if expired/not found or if a Redis failure occurs (graceful).
        """
        try:
            client = self._get_client()
            key = get_feature_key(symbol, window)
            data = await client.get(key)
            if not data:
                return None

            return json.loads(data)
        except Exception as e:
            logger.error(f"Redis get failed for key '{symbol}:{window}': {e}")
            return None
