import numpy as np
from src.windows.orderbook_window import OrderbookWindow


class LiquidityCalculator:
    """
    Pure, stateless calculator for liquidity metrics from OrderbookWindow.
    """

    @staticmethod
    async def compute_liquidity_score(window: OrderbookWindow) -> float:
        """
        Liquidity Score = average_depth / average_spread.
        If average_spread is 0.0, returns the average_depth directly.
        """
        spreads = await window.get_spreads()
        depths = await window.get_depths()
        if not spreads or not depths:
            return 0.0

        avg_spread = float(np.mean(spreads))
        avg_depth = float(np.mean(depths))

        if avg_spread <= 0.0:
            return avg_depth
        return avg_depth / avg_spread

    @staticmethod
    async def compute_average_depth(window: OrderbookWindow) -> float:
        """
        Computes the average depth in the window.
        """
        depths = await window.get_depths()
        if not depths:
            return 0.0
        return float(np.mean(depths))

    @staticmethod
    async def compute_average_spread(window: OrderbookWindow) -> float:
        """
        Computes the average spread in the window.
        """
        spreads = await window.get_spreads()
        if not spreads:
            return 0.0
        return float(np.mean(spreads))

    @staticmethod
    async def compute_spread_efficiency(window: OrderbookWindow) -> float:
        """
        Spread Efficiency = 1.0 / average_spread (lower spread is more efficient).
        """
        spreads = await window.get_spreads()
        if not spreads:
            return 0.0
        avg_spread = float(np.mean(spreads))
        if avg_spread <= 0.0:
            return 0.0
        return 1.0 / avg_spread
