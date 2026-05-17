from shared.redis.client import get_redis_client


def redis_health_check():

    client = get_redis_client()

    return client.ping()