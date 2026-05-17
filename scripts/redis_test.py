import time

from shared.redis.cache import set_cache
from shared.redis.cache import get_cache

from shared.redis.health import redis_health_check


print("Redis Health:", redis_health_check())


set_cache(
    "test_key",
    "AETHERION_WORKING",
    ttl=5
)

print("Stored Value:")
print(get_cache("test_key"))


print("Waiting for TTL expiration...")
time.sleep(6)

print("Value After Expiration:")
print(get_cache("test_key"))