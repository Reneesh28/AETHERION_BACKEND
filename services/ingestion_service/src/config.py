from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings
from shared.config.kafka import KafkaConfig

# =========================
# LOAD ENV FILE
# =========================

ROOT_DIR = Path(__file__).resolve().parents[3]

ENV_PATH = ROOT_DIR / "envs" / "ingestion.env"

load_dotenv(ENV_PATH)


# =========================
# SETTINGS
# =========================

class Settings(BaseSettings):
    # =====================
    # SERVICE
    # =====================

    SERVICE_NAME: str = Field(default="ingestion_service")
    LOG_LEVEL: str = Field(default="INFO")

    # =====================
    # EXCHANGE WEBSOCKETS
    # =====================

    BINANCE_WS_URL: str
    COINBASE_WS_URL: str

    # =====================
    # KAFKA
    # =====================


    KAFKA_TOPIC_MARKET_TICK_RAW: str
    KAFKA_TOPIC_MARKET_ORDERBOOK_RAW: str

    # =====================
    # QUEUES
    # =====================

    INGRESS_QUEUE_SIZE: int = Field(default=10000)
    PRODUCER_QUEUE_SIZE: int = Field(default=10000)

    # =====================
    # RETRIES
    # =====================

    MAX_RETRIES: int = Field(default=2)
    RECONNECT_DELAY: int = Field(default=5)

    # =====================
    # MONITORING
    # =====================

    HEALTH_CHECK_ROUTE: str = Field(default="/health")
    READINESS_ROUTE: str = Field(default="/ready")

    class Config:
        extra = "ignore"


# =========================
# GLOBAL SETTINGS INSTANCE
# =========================

settings = Settings()
kafka_settings = KafkaConfig()