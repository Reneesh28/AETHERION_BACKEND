from shared.schemas.system import BaseEvent


class DecisionEvent(BaseEvent):

    symbol: str

    decision: str

    confidence: float
    risk_level: str