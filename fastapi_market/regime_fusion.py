TIMEFRAME_WEIGHTS = {
    "1h": 0.40,
    "15m": 0.30,
    "5m": 0.20,
    "1m": 0.10
}


class RegimeFusion:

    def fuse(self, stable_regimes: dict):
        """
        stable_regimes example:
        {
            "1m": "BULL",
            "5m": "BULL",
            "15m": "SIDEWAYS",
            "1h": "BULL"
        }
        """

        if not stable_regimes:
            return None

        r = stable_regimes

        #Crisis Override
        if r.get("1h") == "CRISIS":
            return self._result("HIGH_VOL_RISK_OFF", r)

        if r.get("15m") == "CRISIS" and r.get("5m") == "CRISIS":
            return self._result("HIGH_VOL_RISK_OFF", r)

        # Trending Bull
        if r.get("1h") == "BULL" and r.get("15m") == "BULL":

            bullish_count = sum(
                1 for tf in r if r[tf] == "BULL"
            )

            if bullish_count >= 3:
                return self._result("TRENDING_BULL", r)

            if r.get("5m") == "BEAR":
                return self._result("PULLBACK_IN_UPTREND", r)

        #  Trending Bear
        if r.get("1h") == "BEAR" and r.get("15m") == "BEAR":

            bearish_count = sum(
                1 for tf in r if r[tf] == "BEAR"
            )

            if bearish_count >= 3:
                return self._result("TRENDING_BEAR", r)

            if r.get("5m") == "BULL":
                return self._result("PULLBACK_IN_DOWNTREND", r)

        #  Sideways Majority
        sideways_count = sum(
            1 for tf in r if r[tf] == "SIDEWAYS"
        )

        if sideways_count >= 3:
            return self._result("RANGE_BOUND", r)

        # Default Mixed
        return self._result("MIXED_CONDITION", r)

    def _result(self, meta_regime, regimes):

        confidence = self._calculate_confidence(regimes)

        return {
            "meta_regime": meta_regime,
            "confidence": round(confidence, 2),
            "components": regimes
        }

    def _calculate_confidence(self, regimes):

        score = 0

        for tf, regime in regimes.items():
            if regime in ["BULL", "BEAR"]:
                score += TIMEFRAME_WEIGHTS.get(tf, 0)

        return min(score, 1.0)  