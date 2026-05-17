from shared.schemas.system import BaseEvent


class MLOutputEvent(BaseEvent):

    symbol: str

    regime_prediction: str

    risk_score: float
    anomaly_score: float