from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseMarketConnector(ABC):
    """
    Abstract Base Class for all market connectors.

    Every market type (CRYPTO, US_STOCK, NSE) must inherit this.
    This enforces architectural discipline.
    """
    def __init__(self, symbol: str):
        self.symbol = symbol
    # STREAM METHODS (ASYNC)
    @abstractmethod
    async def start_trade_stream(self):
        """
        Start live trade stream from exchange.
        Must be async.
        """
        pass

    @abstractmethod
    async def start_orderbook_stream(self):
        """
        Start order book stream from exchange.
        Must be async.
        """
        pass

    # NORMALIZATION METHODS
    @abstractmethod
    def normalize_trade(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw exchange trade payload
        into unified internal schema.
        """
        pass

    @abstractmethod
    def normalize_orderbook(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw order book payload
        into unified internal schema.
        """
        pass