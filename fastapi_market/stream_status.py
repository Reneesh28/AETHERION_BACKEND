from datetime import datetime, timezone

# Global stream monitoring registry
stream_status = {
    "CRYPTO": {
        "connected": False,
        "last_tick_time": None,
        "last_price": None,
        "ticks_received": 0,
    },
    "US_STOCK": {
        "connected": False,
        "last_tick_time": None,
        "last_price": None,
        "ticks_received": 0,
    },
    "NSE": {
        "connected": False,
        "last_tick_time": None,
        "last_price": None,
        "ticks_received": 0,
    }
}


def update_status(market_type: str, price: float):
    now = int(datetime.now(timezone.utc).timestamp() * 1000)

    stream_status[market_type]["connected"] = True
    stream_status[market_type]["last_tick_time"] = now
    stream_status[market_type]["last_price"] = price
    stream_status[market_type]["ticks_received"] += 1


def set_disconnected(market_type: str):
    stream_status[market_type]["connected"] = False