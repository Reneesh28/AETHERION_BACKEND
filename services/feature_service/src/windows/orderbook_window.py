import collections
import asyncio
from dataclasses import dataclass
from typing import List, Deque, Tuple, Optional


@dataclass
class OrderbookSnapshot:
    """
    Representation of a single market orderbook snapshot.
    """
    timestamp: float  # epoch_ms as float
    bids: List[Tuple[float, float]]  # List of (price, volume) tuples
    asks: List[Tuple[float, float]]  # List of (price, volume) tuples
    spread: float
    depth: float


class OrderbookWindow:
    """
    Manages rolling orderbook snapshots for a specific window duration.
    Evicts snapshots older than (latest event timestamp - window_size_ms).
    Enforces a strict size bound (max_size) to prevent memory leaks.
    """

    def __init__(self, window_size_seconds: float, max_size: int = 1000) -> None:
        self.window_size_ms = window_size_seconds * 1000.0
        self.max_size = max_size
        self.snapshots: Deque[OrderbookSnapshot] = collections.deque()
        self._lock = asyncio.Lock()

    async def add_snapshot(
        self,
        timestamp: float,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]],
        spread: float,
        depth: float,
    ) -> None:
        """
        Appends an orderbook snapshot and evicts older ones.
        Both time-aware eviction and size-bounded eviction are applied.
        """
        async with self._lock:
            snapshot = OrderbookSnapshot(
                timestamp=timestamp, bids=bids, asks=asks, spread=spread, depth=depth
            )
            self.snapshots.append(snapshot)

            # Evict snapshots older than window duration cutoff
            cutoff = timestamp - self.window_size_ms
            while self.snapshots and self.snapshots[0].timestamp < cutoff:
                self.snapshots.popleft()

            # Bounded memory check
            while len(self.snapshots) > self.max_size:
                self.snapshots.popleft()

    async def get_latest_snapshot(self) -> Optional[OrderbookSnapshot]:
        """
        Returns the most recent orderbook snapshot.
        """
        async with self._lock:
            if not self.snapshots:
                return None
            return self.snapshots[-1]

    async def get_spreads(self) -> List[float]:
        """
        Returns all spreads in the window.
        """
        async with self._lock:
            return [s.spread for s in self.snapshots]

    async def get_depths(self) -> List[float]:
        """
        Returns all depths in the window.
        """
        async with self._lock:
            return [s.depth for s in self.snapshots]

    async def get_timestamps(self) -> List[float]:
        """
        Returns all snapshot timestamps in the window.
        """
        async with self._lock:
            return [s.timestamp for s in self.snapshots]

    async def get_size(self) -> int:
        """
        Returns the number of orderbook snapshots currently in the window.
        """
        async with self._lock:
            return len(self.snapshots)

    async def clear(self) -> None:
        """
        Clears all snapshots in the window.
        """
        async with self._lock:
            self.snapshots.clear()
