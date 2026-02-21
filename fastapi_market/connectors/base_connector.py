from abc import ABC, abstractmethod


class BaseMarketConnector(ABC):
    """
    Abstract base class for all market connectors.
    """

    def __init__(self, symbol: str):
        self.symbol = symbol

    @abstractmethod
    async def start_trade_stream(self):
        pass

    @abstractmethod
    async def start_orderbook_stream(self):
        pass

    @abstractmethod
    def normalize_trade(self, raw):
        pass

    @abstractmethod
    def normalize_orderbook(self, raw):
        pass