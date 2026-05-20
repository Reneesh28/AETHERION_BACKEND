import pytest
import asyncio
from src.windows.tick_window import TickWindow
from src.windows.orderbook_window import OrderbookWindow
from src.windows.window_manager import WindowManager
from shared.constants.system import WINDOW_1S, WINDOW_5S, WINDOW_30S


@pytest.mark.asyncio
async def test_tick_window_eviction_and_bounds():
    # 1. Test time-based eviction
    # Create window of 1 second duration, max_size = 5
    window = TickWindow(window_size_seconds=1.0, max_size=5)

    # Add ticks
    # Ticks are in milliseconds: 1000ms = 1s
    await window.add_tick(timestamp=1000.0, price=100.0, volume=1.0)
    await window.add_tick(timestamp=1500.0, price=101.0, volume=1.5)
    await window.add_tick(timestamp=2000.0, price=102.0, volume=2.0)

    assert await window.get_size() == 3
    assert await window.get_prices() == [100.0, 101.0, 102.0]

    # Adding tick at 2100ms should evict the tick at 1000ms because 2100 - 1000 = 1100ms > 1000ms (1s)
    await window.add_tick(timestamp=2100.0, price=103.0, volume=2.5)
    assert await window.get_size() == 3
    assert await window.get_prices() == [101.0, 102.0, 103.0]

    # 2. Test returns
    # Prices: 101.0, 102.0, 103.0
    # Simple Returns: [(102.0-101.0)/101.0, (103.0-102.0)/102.0]
    returns = await window.get_returns()
    assert len(returns) == 2
    assert returns[0] == pytest.approx(1.0 / 101.0)
    assert returns[1] == pytest.approx(1.0 / 102.0)

    # 3. Test max size bounds
    # Add ticks at same timestamp to bypass time-eviction but hit max_size eviction
    await window.add_tick(timestamp=2100.0, price=104.0, volume=1.0)
    await window.add_tick(timestamp=2100.0, price=105.0, volume=1.0)
    await window.add_tick(timestamp=2100.0, price=106.0, volume=1.0)

    # We added 3 ticks at 2100ms. Deque now has ticks at:
    # 1500 (would be evicted by 2100-1500=600 <= 1000? No, 600ms <= 1000ms, so 1500 is not time-evicted yet)
    # But max_size is 5! So the size should be exactly 5.
    assert await window.get_size() == 5
    prices = await window.get_prices()
    assert prices == [
        102.0,
        103.0,
        104.0,
        105.0,
        106.0,
    ]  # 101.0 is evicted because of max_size constraint


@pytest.mark.asyncio
async def test_orderbook_window_eviction():
    window = OrderbookWindow(window_size_seconds=5.0, max_size=3)

    await window.add_snapshot(
        timestamp=1000.0,
        bids=[(100.0, 1.0)],
        asks=[(101.0, 1.0)],
        spread=1.0,
        depth=2.0,
    )
    await window.add_snapshot(
        timestamp=2000.0,
        bids=[(99.0, 1.0)],
        asks=[(102.0, 1.0)],
        spread=3.0,
        depth=2.0,
    )

    assert await window.get_size() == 2
    assert await window.get_spreads() == [1.0, 3.0]

    # Evict based on max_size
    await window.add_snapshot(
        timestamp=3000.0,
        bids=[(98.0, 1.0)],
        asks=[(103.0, 1.0)],
        spread=5.0,
        depth=2.0,
    )
    await window.add_snapshot(
        timestamp=4000.0,
        bids=[(97.0, 1.0)],
        asks=[(104.0, 1.0)],
        spread=7.0,
        depth=2.0,
    )

    assert await window.get_size() == 3
    assert await window.get_spreads() == [3.0, 5.0, 7.0]  # 1.0 was evicted due to max_size=3

    latest = await window.get_latest_snapshot()
    assert latest is not None
    assert latest.spread == 7.0


@pytest.mark.asyncio
async def test_window_manager_routing():
    manager = WindowManager()

    # Route tick to BTC-USD
    await manager.add_tick(
        symbol="BTC-USD",
        timestamp=10000.0,
        price=50000.0,
        volume=0.5,
        bid=49999.0,
        ask=50001.0,
    )

    await manager.add_tick(
        symbol="BTC-USD",
        timestamp=10500.0,
        price=50010.0,
        volume=0.6,
        bid=50009.0,
        ask=50011.0,
    )

    # Route tick to ETH-USD (Symbol Isolation Check)
    await manager.add_tick(
        symbol="ETH-USD",
        timestamp=10000.0,
        price=3000.0,
        volume=10.0,
        bid=2999.0,
        ask=3001.0,
    )

    # Retrieve active symbols
    active_symbols = await manager.get_active_symbols()
    assert "BTC-USD" in active_symbols
    assert "ETH-USD" in active_symbols

    # Retrieve BTC-USD 1s tick window
    btc_1s = await manager.get_tick_window(symbol="BTC-USD", window_name=WINDOW_1S)
    assert btc_1s is not None
    assert await btc_1s.get_size() == 2
    assert await btc_1s.get_prices() == [50000.0, 50010.0]

    # Retrieve ETH-USD 1s tick window
    eth_1s = await manager.get_tick_window(symbol="ETH-USD", window_name=WINDOW_1S)
    assert eth_1s is not None
    assert await eth_1s.get_size() == 1
    assert await eth_1s.get_prices() == [3000.0]

    # Clear symbol
    await manager.clear_symbol("ETH-USD")
    active_symbols = await manager.get_active_symbols()
    assert "BTC-USD" in active_symbols
    assert "ETH-USD" not in active_symbols
