from services.ingestion_service.src.monitoring.health import (
    HealthCheck,
)

from services.ingestion_service.src.monitoring.metrics import (
    MetricsCollector,
)

from services.ingestion_service.src.monitoring.readiness import (
    ReadinessCheck,
)


class MonitoringService:

    @staticmethod
    def health():

        return HealthCheck.status()

    @staticmethod
    def readiness():

        return ReadinessCheck.status()

    @staticmethod
    def metrics():

        return MetricsCollector.collect()