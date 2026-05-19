from services.ingestion_service.src.resilience.circuit_breaker import (
    CircuitBreaker,
)


def test_circuit_breaker():

    breaker = CircuitBreaker(
        failure_threshold=2
    )

    assert breaker.can_execute()

    breaker.record_failure()

    breaker.record_failure()

    assert breaker.state == "OPEN"