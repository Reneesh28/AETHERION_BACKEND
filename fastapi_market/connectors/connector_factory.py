from fastapi_market.config import MarketType
from fastapi_market.connectors.crypto_connector import CryptoConnector


def get_connector(market_type: MarketType, symbol: str):

    if market_type == MarketType.CRYPTO:
        return CryptoConnector(symbol)

    raise ValueError(f"Unsupported market type: {market_type}")