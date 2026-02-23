from enum import Enum


class MarketType(str, Enum):
    """
    Defines supported market types inside AETHERION.
    This makes the system market-agnostic.
    """
    CRYPTO = "CRYPTO"
    NASDAQ = "NASDAQ"
    NYSE = "NYSE"
