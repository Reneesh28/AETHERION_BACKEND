import numpy as np
from src.windows.tick_window import TickWindow


class ReturnsCalculator:
    """
    Pure, stateless calculator for price returns from TickWindow.
    """

    @staticmethod
    async def compute_simple_returns(window: TickWindow) -> list[float]:
        """
        Retrieves the sequential simple returns in the window.
        """
        return await window.get_returns()

    @staticmethod
    async def compute_cumulative_return(window: TickWindow) -> float:
        """
        Cumulative return from the first price to the last price in the window:
        (P_last - P_first) / P_first.
        """
        prices = await window.get_prices()
        if len(prices) < 2:
            return 0.0
        first = prices[0]
        if first == 0.0:
            return 0.0
        return (prices[-1] - first) / first

    @staticmethod
    async def compute_average_return(window: TickWindow) -> float:
        """
        Arithmetic average of the simple returns in the window.
        """
        returns = await window.get_returns()
        if not returns:
            return 0.0
        return float(np.mean(returns))
