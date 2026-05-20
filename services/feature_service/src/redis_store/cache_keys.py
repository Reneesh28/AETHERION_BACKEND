from shared.constants.system import FEATURE_KEY_PREFIX


def get_feature_key(symbol: str, window: str) -> str:
    """
    Generates standard low-latency Redis cache keys for feature snapshots.
    Format: feature:{symbol}:{window}

    Args:
        symbol: The market symbol (e.g. 'BTC-USD', 'ETH-USD')
        window: The time window string (e.g. '1s', '5s', '30s')

    Returns:
        A namespaced Redis key string.
    """
    return f"{FEATURE_KEY_PREFIX}:{symbol}:{window}"
