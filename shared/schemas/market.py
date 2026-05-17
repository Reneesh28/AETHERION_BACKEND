from shared.schemas.system import BaseEvent


class MarketTickEvent(BaseEvent):

    symbol: str

    price: float
    volume: float

    timestamp: str