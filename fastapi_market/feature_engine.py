import numpy as np
from collections import deque, defaultdict
from datetime import datetime
WINDOW_SIZE = 5


class FeatureEngine:

    def __init__(self):
        from fastapi_market.database import db
        self.db = db
        self.collection = self.db["market_features"]

        self.price_buffer = defaultdict(lambda: deque(maxlen=WINDOW_SIZE))
        self.tr_buffer = defaultdict(lambda: deque(maxlen=WINDOW_SIZE))
        self.volume_buffer = defaultdict(lambda: deque(maxlen=WINDOW_SIZE))

    def _key(self, market, symbol, timeframe):
        return f"{market}:{symbol}:{timeframe}"

    async def process_candle(self, candle: dict):

        market = candle["market"]
        symbol = candle["symbol"]
        timeframe = candle["timeframe"]
        close = float(candle["close"])
        high = float(candle["high"])
        low = float(candle["low"])
        volume = float(candle["volume"])
        timestamp = candle["timestamp"]

        key = self._key(market, symbol, timeframe)

        previous_close = (
            self.price_buffer[key][-1]
            if len(self.price_buffer[key]) > 0
            else None
        )
        self.price_buffer[key].append(close)
        self.volume_buffer[key].append(volume)
        if previous_close is not None:
            true_range = max(
                high - low,
                abs(high - previous_close),
                abs(low - previous_close)
            )
            self.tr_buffer[key].append(true_range)
        if len(self.price_buffer[key]) < WINDOW_SIZE:
            return
        prices = np.array(self.price_buffer[key])
        volumes = np.array(self.volume_buffer[key])
        tr_values = np.array(self.tr_buffer[key])
        log_returns = np.diff(np.log(prices))
        rolling_volatility = float(
            np.std(log_returns) * np.sqrt(WINDOW_SIZE)
        ) if len(log_returns) > 1 else 0.0
        atr = float(np.mean(tr_values)) if len(tr_values) > 0 else 0.0
        volume_delta = float(
            volumes[-1] - volumes[-2]
        ) if len(volumes) > 1 else 0.0
        feature_doc = {
            "market": market,
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": timestamp,
            "close": close,
            "rolling_volatility": rolling_volatility,
            "atr": atr,
            "volume_delta": volume_delta,
            "created_at": datetime.utcnow()
        }

        await self.collection.insert_one(feature_doc)