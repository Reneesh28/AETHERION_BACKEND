from services.ingestion_service.src.services.monitoring_service import (
    MonitoringService,
)


def test_health():

    result = (
        MonitoringService.health()
    )

    assert result["status"] == "healthy"


def test_readiness():

    result = (
        MonitoringService.readiness()
    )

    assert "ready" in result


def test_metrics():

    result = (
        MonitoringService.metrics()
    )

    assert "queues" in result