import numpy as np
from src.windows.orderbook_window import OrderbookWindow, OrderbookSnapshot


class ImbalanceCalculator:
    """
    Pure, stateless calculator for orderbook volume imbalances from OrderbookWindow.
    """

    @staticmethod
    def _calculate_imbalance_for_snapshot(snapshot: OrderbookSnapshot) -> float:
        """
        Imbalance = (BidVolume - AskVolume) / (BidVolume + AskVolume).
        """
        bid_vol = sum(vol for _, vol in snapshot.bids)
        ask_vol = sum(vol for _, vol in snapshot.asks)

        total_vol = bid_vol + ask_vol
        if total_vol == 0.0:
            return 0.0
        return (bid_vol - ask_vol) / total_vol

    @staticmethod
    async def compute_latest_imbalance(window: OrderbookWindow) -> float:
        """
        Imbalance of the latest orderbook snapshot in the window.
        """
        latest = await window.get_latest_snapshot()
        if not latest:
            return 0.0
        return ImbalanceCalculator._calculate_imbalance_for_snapshot(latest)

    @staticmethod
    async def compute_rolling_imbalance(window: OrderbookWindow) -> float:
        """
        Arithmetic average of aggregate imbalance across all snapshots in the window.
        """
        # Accessing snapshots safely under the lock
        async with window._lock:
            if not window.snapshots:
                return 0.0
            imbalances = [
                ImbalanceCalculator._calculate_imbalance_for_snapshot(s)
                for s in window.snapshots
            ]
            return float(np.mean(imbalances))

    @staticmethod
    async def compute_order_pressure(window: OrderbookWindow) -> float:
        """
        Order Pressure: alias for rolling imbalance.
        """
        return await ImbalanceCalculator.compute_rolling_imbalance(window)
