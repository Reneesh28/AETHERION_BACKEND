import time
import uuid
from typing import Dict, Any
from src.windows.window_manager import WindowManager
from src.features.returns import ReturnsCalculator
from src.features.volatility import VolatilityCalculator
from src.features.momentum import MomentumCalculator
from src.features.vwap import VWAPCalculator
from src.features.liquidity import LiquidityCalculator
from src.features.imbalance import ImbalanceCalculator


class FeatureBuilder:
    """
    Unified feature vector generator.
    Combines computed window features and event metadata into a standardized
    global Kafka envelope.
    """

    def __init__(self, window_manager: WindowManager) -> None:
        self.window_manager = window_manager

    async def build_feature_vector(
        self,
        symbol: str,
        window_name: str,
        trace_id: str,
        source: str = "feature_service",
    ) -> Dict[str, Any]:
        """
        Computes features from tick and orderbook windows for a given symbol
        and window timeframe.
        Returns a dictionary representing the standard Kafka event envelope.
        """
        tick_window = await self.window_manager.get_tick_window(symbol, window_name)
        ob_window = await self.window_manager.get_orderbook_window(symbol, window_name)

        # 1. Compute Tick-based Features
        returns = 0.0
        volatility = 0.0
        vwap = 0.0
        momentum = 0.0

        if tick_window:
            returns = await ReturnsCalculator.compute_average_return(tick_window)
            volatility = await VolatilityCalculator.compute_rolling_volatility(tick_window)
            vwap = await VWAPCalculator.compute_vwap(tick_window)
            momentum = await MomentumCalculator.compute_price_momentum(tick_window)

        # 2. Compute Orderbook-based Features
        imbalance = 0.0
        spread = 0.0
        liquidity_score = 0.0

        if ob_window:
            imbalance = await ImbalanceCalculator.compute_rolling_imbalance(ob_window)
            spread = await LiquidityCalculator.compute_average_spread(ob_window)
            liquidity_score = await LiquidityCalculator.compute_liquidity_score(ob_window)

        current_time_ms = int(time.time() * 1000)

        # 3. Assemble Global Envelope
        envelope = {
            "event_id": str(uuid.uuid4()),
            "trace_id": trace_id,
            "event_type": "feature.vector.computed",
            "event_time": current_time_ms,
            "processing_time": current_time_ms,
            "symbol": symbol,
            "source": source,
            "schema_version": "v1",
            "payload": {
                "volatility": float(volatility),
                "returns": float(returns),
                "orderbook_imbalance": float(imbalance),
                "spread": float(spread),
                "liquidity_score": float(liquidity_score),
                "vwap": float(vwap),
                "momentum": float(momentum),
                "window": window_name,
            },
        }

        return envelope
