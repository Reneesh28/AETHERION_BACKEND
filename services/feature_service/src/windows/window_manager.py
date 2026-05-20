import asyncio
from typing import Dict, List, Optional, Tuple
from src.config import settings
from src.windows.tick_window import TickWindow
from src.windows.orderbook_window import OrderbookWindow
from shared.constants.system import WINDOW_1S, WINDOW_5S, WINDOW_30S


class WindowManager:
    """
    Central orchestration layer for Aetherion sliding windows.
    Manages symbol-based routing, per-symbol isolation, and tick/orderbook
    state coordination.
    """

    def __init__(self) -> None:
        # self.tick_windows[symbol][window_name] = TickWindow
        self.tick_windows: Dict[str, Dict[str, TickWindow]] = {}
        # self.orderbook_windows[symbol][window_name] = OrderbookWindow
        self.orderbook_windows: Dict[str, Dict[str, OrderbookWindow]] = {}

        # Map timeframe names to their duration configured in Settings
        self.window_durations = {
            WINDOW_1S: float(settings.WINDOW_1S),
            WINDOW_5S: float(settings.WINDOW_5S),
            WINDOW_30S: float(settings.WINDOW_30S),
        }

        self._lock = asyncio.Lock()

    def _ensure_symbol_windows(self, symbol: str) -> None:
        """
        Ensures the window structures exist for a given symbol.
        Must be called from within context holding self._lock.
        """
        if symbol not in self.tick_windows:
            self.tick_windows[symbol] = {
                w_name: TickWindow(
                    window_size_seconds=duration, max_size=settings.MAX_WINDOW_SIZE
                )
                for w_name, duration in self.window_durations.items()
            }
        if symbol not in self.orderbook_windows:
            self.orderbook_windows[symbol] = {
                w_name: OrderbookWindow(
                    window_size_seconds=duration, max_size=settings.MAX_WINDOW_SIZE
                )
                for w_name, duration in self.window_durations.items()
            }

    async def add_tick(
        self,
        symbol: str,
        timestamp: float,
        price: float,
        volume: float,
        bid: float = 0.0,
        ask: float = 0.0,
    ) -> None:
        """
        Routes an incoming tick event to all configured timeframe windows for the symbol.
        """
        async with self._lock:
            self._ensure_symbol_windows(symbol)
            windows = self.tick_windows[symbol]

        # Concurrent update of all windows for this symbol
        await asyncio.gather(
            *(
                window.add_tick(
                    timestamp=timestamp, price=price, volume=volume, bid=bid, ask=ask
                )
                for window in windows.values()
            )
        )

    async def add_orderbook(
        self,
        symbol: str,
        timestamp: float,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]],
        spread: float,
        depth: float,
    ) -> None:
        """
        Routes an incoming orderbook snapshot event to all configured timeframe windows for the symbol.
        """
        async with self._lock:
            self._ensure_symbol_windows(symbol)
            windows = self.orderbook_windows[symbol]

        # Concurrent update of all windows for this symbol
        await asyncio.gather(
            *(
                window.add_snapshot(
                    timestamp=timestamp, bids=bids, asks=asks, spread=spread, depth=depth
                )
                for window in windows.values()
            )
        )

    async def get_tick_window(self, symbol: str, window_name: str) -> Optional[TickWindow]:
        """
        Retrieves the tick window object for a given symbol and window size.
        """
        async with self._lock:
            if symbol not in self.tick_windows:
                return None
            return self.tick_windows[symbol].get(window_name)

    async def get_orderbook_window(
        self, symbol: str, window_name: str
    ) -> Optional[OrderbookWindow]:
        """
        Retrieves the orderbook window object for a given symbol and window size.
        """
        async with self._lock:
            if symbol not in self.orderbook_windows:
                return None
            return self.orderbook_windows[symbol].get(window_name)

    async def get_active_symbols(self) -> List[str]:
        """
        Returns all symbols currently being tracked by the Window Manager.
        """
        async with self._lock:
            return list(self.tick_windows.keys())

    async def clear_symbol(self, symbol: str) -> None:
        """
        Purges memory and windows for the specified symbol.
        """
        async with self._lock:
            if symbol in self.tick_windows:
                for w in self.tick_windows[symbol].values():
                    await w.clear()
                del self.tick_windows[symbol]
            if symbol in self.orderbook_windows:
                for w in self.orderbook_windows[symbol].values():
                    await w.clear()
                del self.orderbook_windows[symbol]
