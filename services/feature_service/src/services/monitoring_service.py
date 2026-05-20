from src.monitoring.health import HealthCheck
from src.monitoring.readiness import ReadinessCheck
from src.monitoring.metrics import MetricsCollector


class MonitoringService:

    @staticmethod
    def health() -> dict:
        return HealthCheck.status()

    @staticmethod
    def readiness() -> dict:
        return ReadinessCheck.status()

    @staticmethod
    def metrics() -> dict:
        return MetricsCollector.collect()

    @staticmethod
    def initialize(redis_store, producer, consumer_supervisor) -> None:
        ReadinessCheck.initialize(
            redis_store=redis_store,
            producer=producer,
            consumer_supervisor=consumer_supervisor
        )
