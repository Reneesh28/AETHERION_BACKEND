import json
import uuid
import time
from typing import Dict, Any


def serialize_feature_event(
    symbol: str,
    window: str,
    features: Dict[str, Any],
    trace_id: str,
    source: str = "feature_service",
    schema_version: str = "v1",
) -> bytes:
    """
    Creates and serializes the global Kafka envelope for computed feature vectors.

    Args:
        symbol: The asset symbol (e.g. 'BTC-USD')
        window: The time window (e.g. '5s')
        features: Computed metrics (volatility, returns, spread, etc.)
        trace_id: Correlation tracer string
        source: Identifies the originating service
        schema_version: Schema format version

    Returns:
        JSON-encoded bytes of the event envelope.
    """
    current_time_ms = int(time.time() * 1000)
    envelope = {
        "event_id": str(uuid.uuid4()),
        "trace_id": trace_id,
        "event_type": "feature.vector.computed",
        "event_time": current_time_ms,
        "processing_time": current_time_ms,
        "symbol": symbol,
        "source": source,
        "schema_version": schema_version,
        "payload": {
            "window": window,
            "features": features,
        },
    }
    return json.dumps(envelope).encode("utf-8")
