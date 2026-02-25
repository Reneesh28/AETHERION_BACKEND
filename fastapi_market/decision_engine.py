# fastapi_market/decision_engine.py

from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict


# =====================================================
# DECISION MODEL
# =====================================================

class TradeDecision(BaseModel):
    market: str
    symbol: str
    meta_regime: str
    strategy: str
    action: str              # BUY | SELL | HOLD
    confidence: float
    timestamp: datetime


# =====================================================
# CONFIGURATION (Can be externalized later)
# =====================================================

CONFIDENCE_THRESHOLD: float = 0.60
COOLDOWN_MINUTES: int = 5


# =====================================================
# STRATEGY → ACTION POLICY
# =====================================================

STRATEGY_ACTION_MAP: Dict[str, str] = {
    "TrendFollowing": "BUY",
    "MeanReversion": "SELL",
    "Neutral": "HOLD",
    "Defensive": "HOLD"
}


# =====================================================
# INTERNAL STATE (In-memory execution guard)
# =====================================================

# { symbol: {"strategy": str, "timestamp": datetime} }
_last_decision_cache: Dict[str, Dict] = {}


# =====================================================
# INTERNAL HELPERS
# =====================================================

def _map_strategy_to_action(strategy: str) -> str:
    return STRATEGY_ACTION_MAP.get(strategy, "HOLD")


def _passes_confidence_filter(confidence: float) -> bool:
    return confidence >= CONFIDENCE_THRESHOLD


def _passes_cooldown(symbol: str, strategy: str) -> bool:
    """
    Prevent:
    - Duplicate strategy signals
    - Signals inside cooldown window
    """

    now = datetime.now(timezone.utc)

    if symbol not in _last_decision_cache:
        return True

    last_record = _last_decision_cache[symbol]
    last_strategy = last_record["strategy"]
    last_time = last_record["timestamp"]

    # Duplicate strategy block
    if last_strategy == strategy:
        return False

    # Cooldown block
    if now - last_time < timedelta(minutes=COOLDOWN_MINUTES):
        return False

    return True


def _update_cache(symbol: str, strategy: str):
    _last_decision_cache[symbol] = {
        "strategy": strategy,
        "timestamp": datetime.now(timezone.utc)
    }


# =====================================================
# PUBLIC DECISION ENGINE
# =====================================================

def generate_decision(
    market: str,
    symbol: str,
    meta_regime: str,
    strategy: str,
    confidence: float
) -> Optional[TradeDecision]:
    """
    Institutional Decision Policy:

    1. Validate confidence threshold
    2. Enforce cooldown and duplicate protection
    3. Map strategy to action
    4. Generate structured trade intent
    """

    # --- Confidence Gate ---
    if not _passes_confidence_filter(confidence):
        return None

    # --- Execution Guard ---
    if not _passes_cooldown(symbol, strategy):
        return None

    action = _map_strategy_to_action(strategy)

    decision = TradeDecision(
        market=market,
        symbol=symbol,
        meta_regime=meta_regime,
        strategy=strategy,
        action=action,
        confidence=confidence,
        timestamp=datetime.now(timezone.utc)
    )

    _update_cache(symbol, strategy)

    return decision