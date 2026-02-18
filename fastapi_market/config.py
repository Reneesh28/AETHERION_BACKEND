from enum import Enum


class MarketType(str, Enum):
    """
    Defines supported market types inside AETHERION.
    This makes the system market-agnostic.
    """

    CRYPTO = "CRYPTO"
    US_STOCK = "US_STOCK"
    NSE = "NSE"
