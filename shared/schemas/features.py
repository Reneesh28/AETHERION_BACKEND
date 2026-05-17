from shared.schemas.system import BaseEvent


class FeatureVectorEvent(BaseEvent):

    symbol: str

    volatility: float
    momentum: float
    liquidity_score: float