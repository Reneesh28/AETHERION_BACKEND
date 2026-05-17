from shared.config.base import BaseConfig


class KafkaConfig(BaseConfig):

    KAFKA_BOOTSTRAP_SERVERS: str

    KAFKA_TOPIC_MARKET_RAW: str
    KAFKA_TOPIC_FEATURE_VECTOR: str
    KAFKA_TOPIC_ML_OUTPUT: str
    KAFKA_TOPIC_DECISION_OUTPUT: str