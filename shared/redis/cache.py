from shared.redis.client import get_redis_client


redis_client = get_redis_client()


def set_cache(key, value, ttl=None):

    redis_client.set(
        key,
        value,
        ex=ttl
    )


def get_cache(key):

    return redis_client.get(key)