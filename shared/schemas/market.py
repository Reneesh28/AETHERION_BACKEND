from typing import Optional

from pydantic import BaseModel

from shared.schemas.system import BaseEvent


# =========================
# TICK PAYLOAD
# =========================

class TickPayload(BaseModel):

    price: float

    quantity: float

    side: str

    trade_id: Optional[str] = None


# =========================
# ORDERBOOK PAYLOAD
# =========================

class OrderBookPayload(BaseModel):

    bid_price: float

    ask_price: float

    bid_quantity: float

    ask_quantity: float

    spread: Optional[float] = None


# =========================
# MARKET TICK EVENT
# =========================

class MarketTickEvent(BaseEvent):

    symbol: str

    quality: str = "complete"

    payload: TickPayload


# =========================
# MARKET ORDERBOOK EVENT
# =========================

class MarketOrderBookEvent(BaseEvent):

    symbol: str

    quality: str = "complete"

    payload: OrderBookPayload