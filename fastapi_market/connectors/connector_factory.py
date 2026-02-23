from fastapi_market.config import MarketType
from fastapi_market.connectors.crypto_connector import CryptoConnector
from fastapi_market.connectors.us_market_connector import USMarketConnector


def get_connector(market_type: MarketType, symbol: str):

    if market_type == MarketType.CRYPTO:
        return CryptoConnector(symbol)

    elif market_type == MarketType.NASDAQ:
        return USMarketConnector(symbol=symbol, exchange="NASDAQ")

    elif market_type == MarketType.NYSE:
        return USMarketConnector(symbol=symbol, exchange="NYSE")

    raise ValueError(f"Unsupported market type: {market_type}")