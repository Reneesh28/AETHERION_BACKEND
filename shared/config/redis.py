from shared.config.base import BaseConfig


class RedisConfig(BaseConfig):

    REDIS_HOST: str
    REDIS_PORT: int