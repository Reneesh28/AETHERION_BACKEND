from shared.config.base import BaseConfig


class KafkaConfig(BaseConfig):

    # =========================
    # KAFKA CONNECTION
    # =========================

    KAFKA_BOOTSTRAP_SERVERS: str

    @property
    def get_bootstrap_servers(self) -> str:
        from pathlib import Path
        
        # If running inside a Docker container, use the value from .env (kafka:9092)
        if Path("/.dockerenv").exists():
            return self.KAFKA_BOOTSTRAP_SERVERS
            
        # If running locally (like tests), override to localhost
        return "localhost:29092"

    # =========================
    # MARKET TOPICS
    # =========================

    KAFKA_TOPIC_MARKET_TICK_RAW: str
    KAFKA_TOPIC_MARKET_ORDERBOOK_RAW: str

    # =========================
    # FEATURE TOPICS
    # =========================

    KAFKA_TOPIC_FEATURE_VECTOR: str

    # =========================
    # ML TOPICS
    # =========================

    KAFKA_TOPIC_ML_OUTPUT: str

    # =========================
    # DECISION TOPICS
    # =========================

    KAFKA_TOPIC_DECISION_OUTPUT: str