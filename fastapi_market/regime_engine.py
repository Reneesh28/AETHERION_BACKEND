import numpy as np
import asyncio
from hmmlearn.hmm import GaussianHMM
from fastapi_market.database import db

TIMEFRAMES = ["1m", "5m", "15m", "1h"]

MIN_TRAIN_SIZE = 200
TRAIN_LIMIT = 1500
PREDICT_WINDOW = 200
RETRAIN_INTERVAL_SECONDS = 300  # 5 minutes


class RegimeEngine:

    def __init__(self, n_states=4):
        self.db = db
        self.feature_collection = db["market_features"]
        self.regime_collection = db["market_regimes"]

        self.models = {
            tf: GaussianHMM(
                n_components=n_states,
                covariance_type="full",
                n_iter=300
            )
            for tf in TIMEFRAMES
        }

        self.trained = {tf: False for tf in TIMEFRAMES}
        self.last_trained_at = {tf: None for tf in TIMEFRAMES}

        self.training_lock = asyncio.Lock()

    # ================================
    # TRAINING
    # ================================
    async def fetch_training_matrix(self, market, symbol, timeframe):

        cursor = self.feature_collection.find(
            {
                "market": market,
                "symbol": symbol,
                "timeframe": timeframe
            }
        ).sort("timestamp", 1).limit(TRAIN_LIMIT)

        data = await cursor.to_list(length=TRAIN_LIMIT)

        if len(data) < MIN_TRAIN_SIZE:
            return None

        X = np.array([
            [
                d.get("rolling_volatility", 0),
                d.get("atr", 0),
                d.get("volume_delta", 0)
            ]
            for d in data
        ])

        return X

    async def train_timeframe(self, market, symbol, timeframe):

        async with self.training_lock:

            X = await self.fetch_training_matrix(
                market, symbol, timeframe
            )

            if X is None:
                return

            model = self.models[timeframe]

            try:
                model.fit(X)
                self.trained[timeframe] = True
                self.last_trained_at[timeframe] = asyncio.get_event_loop().time()
                print(f"✅ Trained HMM for {timeframe}")
            except Exception as e:
                print(f"❌ Training failed {timeframe}: {e}")

    async def retrain_scheduler(self, market, symbol):

        while True:
            try:
                for tf in TIMEFRAMES:
                    await self.train_timeframe(market, symbol, tf)

                await asyncio.sleep(RETRAIN_INTERVAL_SECONDS)

            except Exception as e:
                print("Retrain Scheduler Error:", e)
                await asyncio.sleep(10)

    # ================================
    # PREDICTION
    # ================================
    async def predict_timeframe(self, market, symbol, timeframe):

        if not self.trained[timeframe]:
            return None

        cursor = self.feature_collection.find(
            {
                "market": market,
                "symbol": symbol,
                "timeframe": timeframe
            }
        ).sort("timestamp", -1).limit(PREDICT_WINDOW)

        data = await cursor.to_list(length=PREDICT_WINDOW)

        if len(data) < 50:
            return None

        X = np.array([
            [
                d.get("rolling_volatility", 0),
                d.get("atr", 0),
                d.get("volume_delta", 0)
            ]
            for d in reversed(data)
        ])

        try:
            states = self.models[timeframe].predict(X)
            current_state = int(states[-1])
        except Exception:
            return None

        regime_doc = {
            "market": market,
            "symbol": symbol,
            "timeframe": timeframe,
            "regime_state": current_state,
            "timestamp": data[0]["timestamp"]
        }

        await self.regime_collection.insert_one(regime_doc)

        return current_state

    async def predict_all(self, market, symbol):

        results = {}

        for tf in TIMEFRAMES:
            state = await self.predict_timeframe(
                market, symbol, tf
            )
            if state is not None:
                results[tf] = state

        return results