from typing import Any, Dict
from datetime import datetime


REQUIRED_ENVELOPE_FIELDS = [
    "event_id",
    "trace_id",
    "event_type",
    "event_time",
    "processing_time",
    "symbol",
    "source",
    "schema_version",
    "payload",
]


class ValidationError(Exception):
    """
    Raised when market event validation fails.
    """
    pass


def validate_event_structure(event: Dict[str, Any]) -> bool:
    """
    Validate top-level Kafka event envelope.
    """

    if not isinstance(event, dict):
        raise ValidationError("Event must be a dictionary")

    for field in REQUIRED_ENVELOPE_FIELDS:
        if field not in event:
            raise ValidationError(f"Missing required field: {field}")

    return True


def validate_symbol(symbol: str) -> bool:
    """
    Validate trading symbol.
    """

    if not isinstance(symbol, str):
        raise ValidationError("Symbol must be a string")

    if not symbol.strip():
        raise ValidationError("Symbol cannot be empty")

    return True


def validate_timestamp(timestamp: Any) -> bool:
    """
    Validate timestamp fields.
    """

    if isinstance(timestamp, (int, float)):
        if timestamp <= 0:
            raise ValidationError("Timestamp must be positive")
    elif isinstance(timestamp, str):
        try:
            if timestamp.endswith('Z'):
                datetime.fromisoformat(timestamp[:-1] + '+00:00')
            else:
                datetime.fromisoformat(timestamp)
        except ValueError:
            raise ValidationError("Timestamp string must be valid ISO 8601 format")
    else:
        raise ValidationError("Timestamp must be numeric or an ISO string")

    return True


def validate_payload(payload: Dict[str, Any]) -> bool:
    """
    Validate payload structure.
    """

    if not isinstance(payload, dict):
        raise ValidationError("Payload must be a dictionary")

    return True


def validate_market_event(event: Dict[str, Any]) -> bool:
    """
    Full validation pipeline for market events.
    """

    validate_event_structure(event)

    validate_symbol(event["symbol"])

    validate_timestamp(event["event_time"])

    validate_timestamp(event["processing_time"])

    validate_payload(event["payload"])

    return True