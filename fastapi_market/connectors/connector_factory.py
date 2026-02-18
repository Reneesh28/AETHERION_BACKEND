from fastapi_market.config import MarketType
from fastapi_market.connectors.crypto_connector import CryptoConnector
from fastapi_market.connectors.us_stock_connector import USStockConnector


def get_connector(market_type: MarketType, symbol: str):
    """
    Factory method to return correct market connector.
    This keeps FastAPI layer clean and market-agnostic.
    """

    if market_type == MarketType.CRYPTO:
        return CryptoConnector(symbol)
    if market_type == MarketType.US_STOCK:
        return USStockConnector(symbol)

    # if market_type == MarketType.NSE:
    #     return NSEConnector(symbol)

    raise ValueError(f"Unsupported market type: {market_type}")
