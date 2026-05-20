# =========================================================
# EVENT TYPES / METADATA
# =========================================================

EVENT_MARKET_TICK = "market.tick.raw"

EVENT_MARKET_ORDERBOOK = "market.orderbook.raw"

EVENT_FEATURE_VECTOR = "feature.vector.computed"


# =========================================================
# WINDOW NAMES
# =========================================================

WINDOW_1S = "1s"

WINDOW_5S = "5s"

WINDOW_30S = "30s"

SUPPORTED_WINDOWS = [
    WINDOW_1S,
    WINDOW_5S,
    WINDOW_30S,
]


# =========================================================
# REDIS KEYS
# =========================================================

FEATURE_KEY_PREFIX = "feature"


# =========================================================
# SCHEMA
# =========================================================

SCHEMA_VERSION_V1 = "v1"


# =========================================================
# DATA QUALITY FLAGS
# =========================================================

DATA_QUALITY_COMPLETE = "complete"

DATA_QUALITY_PARTIAL = "partial"

DATA_QUALITY_DEGRADED = "degraded"


# =========================================================
# FEATURE DEFAULTS (FALLBACK VALUES)
# =========================================================

DEFAULT_RETURNS = 0.0

DEFAULT_VOLATILITY = 0.0

DEFAULT_SPREAD = 0.0

DEFAULT_IMBALANCE = 0.0

DEFAULT_LIQUIDITY_SCORE = 0.0
