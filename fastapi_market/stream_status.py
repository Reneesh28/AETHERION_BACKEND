from datetime import datetime, timezone

stream_status = {
    "CRYPTO": {
        "connected": False,
        "last_tick_time": None,
        "last_price": None,
        "ticks_received": 0,
    },
    "NASDAQ": {
        "connected": False,
        "last_tick_time": None,
        "last_price": None,
        "ticks_received": 0,
    },
    "NYSE": {
        "connected": False,
        "last_tick_time": None,
        "last_price": None,
        "ticks_received": 0,
    }
}


def update_status(market_type: str, price: float):
    """
    Update stream heartbeat + tick stats
    """

    if market_type not in stream_status:
        return

    now = int(datetime.now(timezone.utc).timestamp() * 1000)

    stream_status[market_type]["connected"] = True
    stream_status[market_type]["last_tick_time"] = now
    stream_status[market_type]["last_price"] = price
    stream_status[market_type]["ticks_received"] += 1


def set_disconnected(market_type: str):
    """
    Mark stream as disconnected
    """

    if market_type not in stream_status:
        return

    stream_status[market_type]["connected"] = False