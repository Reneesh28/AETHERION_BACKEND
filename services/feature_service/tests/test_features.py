import pytest
import math
from src.windows.tick_window import TickWindow
from src.windows.orderbook_window import OrderbookWindow
from src.windows.window_manager import WindowManager
from src.features.returns import ReturnsCalculator
from src.features.volatility import VolatilityCalculator
from src.features.momentum import MomentumCalculator
from src.features.vwap import VWAPCalculator
from src.features.liquidity import LiquidityCalculator
from src.features.imbalance import ImbalanceCalculator
from src.services.feature_builder import FeatureBuilder


@pytest.mark.asyncio
async def test_returns_calculator():
    window = TickWindow(window_size_seconds=10.0, max_size=10)
    # Add prices: 100.0, 102.0, 101.0
    await window.add_tick(timestamp=1000.0, price=100.0, volume=1.0)
    await window.add_tick(timestamp=2000.0, price=102.0, volume=1.0)
    await window.add_tick(timestamp=3000.0, price=101.0, volume=1.0)

    # Simple returns: [ (102-100)/100, (101-102)/102 ] = [ 0.02, -0.0098039 ]
    simple_returns = await ReturnsCalculator.compute_simple_returns(window)
    assert len(simple_returns) == 2
    assert simple_returns[0] == pytest.approx(0.02)
    assert simple_returns[1] == pytest.approx(-1.0 / 102.0)

    # Cumulative: (101 - 100) / 100 = 0.01
    cum_return = await ReturnsCalculator.compute_cumulative_return(window)
    assert cum_return == pytest.approx(0.01)

    # Average: mean of simple returns
    avg_return = await ReturnsCalculator.compute_average_return(window)
    assert avg_return == pytest.approx((0.02 + (-1.0 / 102.0)) / 2)


@pytest.mark.asyncio
async def test_volatility_calculator():
    window = TickWindow(window_size_seconds=10.0, max_size=10)
    await window.add_tick(timestamp=1000.0, price=100.0, volume=1.0)
    await window.add_tick(timestamp=2000.0, price=105.0, volume=1.0)
    await window.add_tick(timestamp=3000.0, price=103.0, volume=1.0)

    # Log returns: [ln(105/100), ln(103/105)] = [0.04879016, -0.0192308]
    r1 = math.log(105.0 / 100.0)
    r2 = math.log(103.0 / 105.0)

    log_returns = await window.get_log_returns()
    assert log_returns[0] == pytest.approx(r1)
    assert log_returns[1] == pytest.approx(r2)

    # Variance
    variance = await VolatilityCalculator.compute_variance(window)
    expected_var = ((r1 - (r1 + r2) / 2) ** 2 + (r2 - (r1 + r2) / 2) ** 2) / 2
    assert variance == pytest.approx(expected_var)

    # Rolling Volatility
    vol = await VolatilityCalculator.compute_rolling_volatility(window)
    assert vol == pytest.approx(math.sqrt(expected_var))

    # Realized Volatility
    realized_vol = await VolatilityCalculator.compute_realized_volatility(window)
    assert realized_vol == pytest.approx(math.sqrt(r1**2 + r2**2))


@pytest.mark.asyncio
async def test_momentum_calculator():
    window = TickWindow(window_size_seconds=10.0, max_size=10)
    await window.add_tick(timestamp=1000.0, price=100.0, volume=1.0)
    await window.add_tick(timestamp=2000.0, price=105.0, volume=1.0)
    await window.add_tick(timestamp=3000.0, price=102.0, volume=1.0)
    await window.add_tick(timestamp=4000.0, price=104.0, volume=1.0)

    # Price Momentum: 104 - 100 = 4.0
    momentum = await MomentumCalculator.compute_price_momentum(window)
    assert momentum == 4.0

    # Directional Movement:
    # 100 -> 105 (+1)
    # 105 -> 102 (-1)
    # 102 -> 104 (+1)
    # Net: 1 - 1 + 1 = 1.0
    directional = await MomentumCalculator.compute_directional_movement(window)
    assert directional == 1.0

    # Trend Strength (Kaufman's ER):
    # Net change: abs(104 - 100) = 4
    # Paths: abs(105-100) + abs(102-105) + abs(104-102) = 5 + 3 + 2 = 10
    # ER: 4 / 10 = 0.4
    trend = await MomentumCalculator.compute_trend_strength(window)
    assert trend == pytest.approx(0.4)


@pytest.mark.asyncio
async def test_vwap_calculator():
    window = TickWindow(window_size_seconds=10.0, max_size=10)
    await window.add_tick(timestamp=1000.0, price=10.0, volume=2.0)
    await window.add_tick(timestamp=2000.0, price=15.0, volume=3.0)

    # VWAP = (10*2 + 15*3) / (2+3) = (20 + 45) / 5 = 65 / 5 = 13.0
    vwap = await VWAPCalculator.compute_vwap(window)
    assert vwap == 13.0


@pytest.mark.asyncio
async def test_liquidity_calculator():
    window = OrderbookWindow(window_size_seconds=10.0, max_size=10)
    await window.add_snapshot(
        timestamp=1000.0,
        bids=[(10.0, 2.0), (9.0, 3.0)],
        asks=[(11.0, 1.0), (12.0, 4.0)],
        spread=1.0,
        depth=10.0,
    )
    await window.add_snapshot(
        timestamp=2000.0,
        bids=[(10.0, 1.0)],
        asks=[(13.0, 1.0)],
        spread=3.0,
        depth=2.0,
    )

    # Average Depth: (10 + 2) / 2 = 6.0
    depth = await LiquidityCalculator.compute_average_depth(window)
    assert depth == 6.0

    # Average Spread: (1.0 + 3.0) / 2 = 2.0
    spread = await LiquidityCalculator.compute_average_spread(window)
    assert spread == 2.0

    # Liquidity score = average_depth / average_spread = 6.0 / 2.0 = 3.0
    score = await LiquidityCalculator.compute_liquidity_score(window)
    assert score == 3.0

    # Spread efficiency = 1.0 / average_spread = 0.5
    eff = await LiquidityCalculator.compute_spread_efficiency(window)
    assert eff == 0.5


@pytest.mark.asyncio
async def test_imbalance_calculator():
    window = OrderbookWindow(window_size_seconds=10.0, max_size=10)

    # Snapshot 1: Bids (Sum Volume = 5.0), Asks (Sum Volume = 5.0) -> Imbalance = (5 - 5) / 10 = 0.0
    await window.add_snapshot(
        timestamp=1000.0,
        bids=[(10.0, 2.0), (9.0, 3.0)],
        asks=[(11.0, 1.0), (12.0, 4.0)],
        spread=1.0,
        depth=10.0,
    )
    # Snapshot 2: Bids (Sum Volume = 3.0), Asks (Sum Volume = 1.0) -> Imbalance = (3 - 1) / 4 = 2/4 = 0.5
    await window.add_snapshot(
        timestamp=2000.0,
        bids=[(10.0, 3.0)],
        asks=[(13.0, 1.0)],
        spread=3.0,
        depth=4.0,
    )

    # Latest aggregate imbalance should be snapshot 2's imbalance = 0.5
    latest_imbalance = await ImbalanceCalculator.compute_latest_imbalance(window)
    assert latest_imbalance == 0.5

    # Rolling imbalance: mean of [0.0, 0.5] = 0.25
    rolling_imbalance = await ImbalanceCalculator.compute_rolling_imbalance(window)
    assert rolling_imbalance == 0.25


@pytest.mark.asyncio
async def test_feature_builder():
    window_manager = WindowManager()

    # Feed data to windows
    await window_manager.add_tick(
        symbol="BTC-USD", timestamp=1000.0, price=10.0, volume=2.0, bid=9.0, ask=11.0
    )
    await window_manager.add_tick(
        symbol="BTC-USD", timestamp=2000.0, price=15.0, volume=3.0, bid=14.0, ask=16.0
    )

    await window_manager.add_orderbook(
        symbol="BTC-USD",
        timestamp=1000.0,
        bids=[(10.0, 2.0), (9.0, 3.0)],
        asks=[(11.0, 1.0), (12.0, 4.0)],
        spread=1.0,
        depth=10.0,
    )
    await window_manager.add_orderbook(
        symbol="BTC-USD",
        timestamp=2000.0,
        bids=[(10.0, 3.0)],
        asks=[(13.0, 1.0)],
        spread=3.0,
        depth=4.0,
    )

    builder = FeatureBuilder(window_manager)
    vector = await builder.build_feature_vector(
        symbol="BTC-USD", window_name="1s", trace_id="test-trace-123", source="test-source"
    )

    # Validate global Kafka envelope structure
    assert vector["trace_id"] == "test-trace-123"
    assert vector["symbol"] == "BTC-USD"
    assert vector["source"] == "test-source"
    assert vector["event_type"] == "feature.vector.computed"
    assert vector["schema_version"] == "v1"

    payload = vector["payload"]
    assert payload["window"] == "1s"

    # Verify computations were combined correctly in the payload
    assert payload["vwap"] == 13.0
    assert payload["momentum"] == 5.0
    assert payload["orderbook_imbalance"] == 0.25
    assert payload["spread"] == 2.0
    assert payload["liquidity_score"] == 3.5
