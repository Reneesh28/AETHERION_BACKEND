from fastapi_market.config import MarketType
from fastapi_market.connectors.crypto_connector import CryptoConnector
from fastapi_market.connectors.nasdaq_connector import NasdaqConnector
from fastapi_market.connectors.nyse_connector import NyseConnector

def get_connector(market_type: MarketType, symbol: str):
    """
    Factory method to return correct market connector.
    Keeps FastAPI layer clean and market-agnostic.
    """

    if market_type == MarketType.CRYPTO:
        return CryptoConnector(symbol)

    if market_type == MarketType.US_STOCK:

        if symbol.startswith("NASDAQ:"):
            return NasdaqConnector(symbol)

        elif symbol.startswith("NYSE:"):
            return NyseConnector(symbol)

        else:
            raise ValueError(
                "Unsupported US exchange. Use NASDAQ:SYMBOL or NYSE:SYMBOL"
            )

    # Future expansion
    # if market_type == MarketType.NSE:
    #     return NSEConnector(symbol)

    raise ValueError(f"Unsupported market type: {market_type}")
