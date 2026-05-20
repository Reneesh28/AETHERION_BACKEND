from src.windows.tick_window import TickWindow


class MomentumCalculator:
    """
    Pure, stateless calculator for momentum indicators from TickWindow.
    """

    @staticmethod
    async def compute_price_momentum(window: TickWindow) -> float:
        """
        Price Momentum: net price change between the oldest and latest price in the window:
        P_last - P_first.
        """
        prices = await window.get_prices()
        if len(prices) < 2:
            return 0.0
        return prices[-1] - prices[0]

    @staticmethod
    async def compute_directional_movement(window: TickWindow) -> float:
        """
        Calculates cumulative directional movement: positive changes (+1) minus negative changes (-1).
        """
        prices = await window.get_prices()
        if len(prices) < 2:
            return 0.0
        movement = 0.0
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i - 1]
            if diff > 0:
                movement += 1.0
            elif diff < 0:
                movement -= 1.0
        return movement

    @staticmethod
    async def compute_trend_strength(window: TickWindow) -> float:
        """
        Kaufman's Efficiency Ratio (ER): Net Change / Sum of Absolute Changes.
        Ranges from 0.0 (random noise) to 1.0 (pure straight trend direction).
        """
        prices = await window.get_prices()
        if len(prices) < 2:
            return 0.0
        net_change = abs(prices[-1] - prices[0])
        total_path = sum(abs(prices[i] - prices[i - 1]) for i in range(1, len(prices)))
        if total_path == 0.0:
            return 0.0
        return net_change / total_path
