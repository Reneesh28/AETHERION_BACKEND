import socket
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = ROOT_DIR / "envs" / "feature.env"


class Settings(BaseSettings):
    """
    Feature Service Runtime Configuration
    """

    # =========================================================
    # SERVICE METADATA
    # =========================================================

    SERVICE_NAME: str = "feature_service"
    SERVICE_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # =========================================================
    # KAFKA CONFIGURATION
    # =========================================================

    KAFKA_BOOTSTRAP_SERVERS: str = Field(
        default="localhost:29092"
    )

    KAFKA_CONSUMER_GROUP: str = Field(
        default="cg.feature"
    )

    MARKET_TICK_TOPIC: str = Field(
        default="market.tick.raw"
    )

    MARKET_ORDERBOOK_TOPIC: str = Field(
        default="market.orderbook.raw"
    )

    FEATURE_VECTOR_TOPIC: str = Field(
        default="feature.vector.computed"
    )

    KAFKA_AUTO_OFFSET_RESET: str = "latest"
    KAFKA_ENABLE_AUTO_COMMIT: bool = False

    # =========================================================
    # REDIS CONFIGURATION
    # =========================================================

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    FEATURE_TTL_SECONDS: int = 60

    # =========================================================
    # WINDOW CONFIGURATION
    # =========================================================

    WINDOW_1S: int = 1
    WINDOW_5S: int = 5
    WINDOW_30S: int = 30

    MAX_WINDOW_SIZE: int = 1000

    # =========================================================
    # PERFORMANCE CONFIGURATION
    # =========================================================

    FEATURE_BATCH_INTERVAL_MS: int = 50

    MAX_QUEUE_SIZE: int = 10000

    FEATURE_LATENCY_TARGET_MS: int = 150

    # =========================================================
    # RETRY / RESILIENCE
    # =========================================================

    MAX_RETRIES: int = 2

    RETRY_BACKOFF_MS: int = 50

    CIRCUIT_BREAKER_THRESHOLD: int = 5

    # =========================================================
    # MONITORING
    # =========================================================

    METRICS_ENABLED: bool = True

    HEALTH_CHECK_INTERVAL_SECONDS: int = 30

    LOG_LEVEL: str = "INFO"

    # =========================================================
    # PYDANTIC SETTINGS CONFIG
    # =========================================================

    @field_validator("KAFKA_BOOTSTRAP_SERVERS", mode="after")
    @classmethod
    def resolve_kafka(cls, v: str) -> str:
        if "kafka" in v:
            try:
                socket.gethostbyname("kafka")
            except socket.error:
                return v.replace("kafka", "localhost")
        return v

    @field_validator("REDIS_HOST", mode="after")
    @classmethod
    def resolve_redis(cls, v: str) -> str:
        if v == "redis":
            try:
                socket.gethostbyname("redis")
            except socket.error:
                return "localhost"
        return v

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        extra="ignore"
    )


settings = Settings()