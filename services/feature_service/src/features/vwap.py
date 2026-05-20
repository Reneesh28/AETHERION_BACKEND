from src.windows.tick_window import TickWindow


class VWAPCalculator:
    """
    Pure, stateless calculator for Volume Weighted Average Price (VWAP) from TickWindow.
    """

    @staticmethod
    async def compute_vwap(window: TickWindow) -> float:
        """
        Computes the volume weighted average price: sum(P_i * V_i) / sum(V_i).
        """
        prices = await window.get_prices()
        volumes = await window.get_volumes()
        if not prices or not volumes:
            return 0.0

        sum_pv = sum(p * v for p, v in zip(prices, volumes))
        sum_v = sum(volumes)
        if sum_v == 0.0:
            return 0.0
        return sum_pv / sum_v
