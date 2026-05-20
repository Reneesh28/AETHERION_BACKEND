import math
import numpy as np
from src.windows.tick_window import TickWindow


class VolatilityCalculator:
    """
    Pure, stateless calculator for price volatility metrics from TickWindow.
    """

    @staticmethod
    async def compute_variance(window: TickWindow) -> float:
        """
        Computes the variance of the log returns in the window.
        """
        log_returns = await window.get_log_returns()
        if len(log_returns) < 2:
            return 0.0
        return float(np.var(log_returns))

    @staticmethod
    async def compute_rolling_volatility(window: TickWindow) -> float:
        """
        Computes rolling volatility (standard deviation of log returns in the window).
        """
        log_returns = await window.get_log_returns()
        if len(log_returns) < 2:
            return 0.0
        return float(np.std(log_returns))

    @staticmethod
    async def compute_realized_volatility(window: TickWindow) -> float:
        """
        Computes realized volatility defined as the square root of the sum of squared log returns:
        sqrt(sum(r_t^2)).
        """
        log_returns = await window.get_log_returns()
        if not log_returns:
            return 0.0
        return float(math.sqrt(sum(r**2 for r in log_returns)))
