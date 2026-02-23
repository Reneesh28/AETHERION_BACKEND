class StrategyEngine:

    def __init__(self):
        self.current_strategy = None

    def select_strategy(self, meta_regime_data):

        if not meta_regime_data:
            return None

        meta_regime = meta_regime_data.get("meta_regime")

        strategy_map = {
            "TRENDING_BULL": "TrendFollowingLong",
            "TRENDING_BEAR": "TrendFollowingShort",
            "PULLBACK_IN_UPTREND": "DipBuying",
            "PULLBACK_IN_DOWNTREND": "RallySelling",
            "RANGE_BOUND": "MeanReversion",
            "HIGH_VOL_RISK_OFF": "RiskOff",
            "MIXED_CONDITION": "Neutral"
        }

        selected = strategy_map.get(meta_regime, "Neutral")

        if selected != self.current_strategy:
            print(f"🎯 Strategy Switched → {selected}")
            self.current_strategy = selected

        return {
            "meta_regime": meta_regime,
            "strategy": selected
        }