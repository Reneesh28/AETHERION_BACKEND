import collections
import math
import asyncio
from dataclasses import dataclass
from typing import List, Deque


@dataclass
class Tick:
    """
    Representation of a single market tick event.
    """
    timestamp: float  # epoch_ms as float
    price: float
    volume: float
    bid: float
    ask: float


class TickWindow:
    """
    Manages rolling tick data for a specific window duration.
    Evicts ticks older than (latest event timestamp - window_size_ms).
    Enforces a strict size bound (max_size) to prevent memory leaks.
    """

    def __init__(self, window_size_seconds: float, max_size: int = 1000) -> None:
        self.window_size_ms = window_size_seconds * 1000.0
        self.max_size = max_size
        self.ticks: Deque[Tick] = collections.deque()
        self._lock = asyncio.Lock()

    async def add_tick(
        self,
        timestamp: float,
        price: float,
        volume: float,
        bid: float = 0.0,
        ask: float = 0.0,
    ) -> None:
        """
        Appends a tick and evicts older ones.
        Both time-aware eviction and size-bounded eviction are applied.
        """
        async with self._lock:
            tick = Tick(
                timestamp=timestamp, price=price, volume=volume, bid=bid, ask=ask
            )
            self.ticks.append(tick)

            # Evict ticks that are older than the new tick's timestamp minus window duration
            cutoff = timestamp - self.window_size_ms
            while self.ticks and self.ticks[0].timestamp < cutoff:
                self.ticks.popleft()

            # Bounded memory check
            while len(self.ticks) > self.max_size:
                self.ticks.popleft()

    async def get_prices(self) -> List[float]:
        """
        Returns all tick prices in the window.
        """
        async with self._lock:
            return [t.price for t in self.ticks]

    async def get_volumes(self) -> List[float]:
        """
        Returns all tick volumes in the window.
        """
        async with self._lock:
            return [t.volume for t in self.ticks]

    async def get_timestamps(self) -> List[float]:
        """
        Returns all tick timestamps in the window.
        """
        async with self._lock:
            return [t.timestamp for t in self.ticks]

    async def get_returns(self) -> List[float]:
        """
        Calculates simple returns sequentially: (P_t - P_{t-1}) / P_{t-1}.
        """
        async with self._lock:
            if len(self.ticks) < 2:
                return []
            returns = []
            for i in range(1, len(self.ticks)):
                prev_price = self.ticks[i - 1].price
                if prev_price == 0.0:
                    returns.append(0.0)
                else:
                    returns.append((self.ticks[i].price - prev_price) / prev_price)
            return returns

    async def get_log_returns(self) -> List[float]:
        """
        Calculates log returns sequentially: ln(P_t / P_{t-1}).
        """
        async with self._lock:
            if len(self.ticks) < 2:
                return []
            returns = []
            for i in range(1, len(self.ticks)):
                prev_price = self.ticks[i - 1].price
                curr_price = self.ticks[i].price
                if prev_price <= 0.0 or curr_price <= 0.0:
                    returns.append(0.0)
                else:
                    returns.append(math.log(curr_price / prev_price))
            return returns

    async def get_size(self) -> int:
        """
        Returns the number of ticks currently in the window.
        """
        async with self._lock:
            return len(self.ticks)

    async def clear(self) -> None:
        """
        Clears all ticks in the window.
        """
        async with self._lock:
            self.ticks.clear()
