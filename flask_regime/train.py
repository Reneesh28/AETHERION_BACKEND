import os
import joblib
import pandas as pd
from pymongo import MongoClient
from hmmlearn.hmm import GaussianHMM

from flask_regime.scaler import FeatureScaler


class RegimeTrainer:

    def __init__(self, mongo_uri, db_name, model_dir="flask_regime/models"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db["market_features"]
        self.model_dir = model_dir

        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

    def train(self, market, symbol, timeframe, model_name, limit=10000):

        cursor = (
            self.collection
            .find({
                "market": market,
                "symbol": symbol,
                "timeframe": timeframe
            })
            .sort("timestamp", 1)
            .limit(limit)
        )

        data = list(cursor)

        if not data:
            raise ValueError("No feature data found.")

        df = pd.DataFrame(data)

        # ✅ Candle-based features only
        feature_cols = [
            "rolling_volatility",
            "atr",
            "volume_delta"
        ]

        df = df[feature_cols].dropna()

        if len(df) < 50:
            raise ValueError("Not enough data to train HMM.")

        X = df.values

        # Scale
        scaler = FeatureScaler()
        X_scaled = scaler.fit_transform(X)

        # ✅ 3 regimes only
        model = GaussianHMM(
            n_components=3,
            covariance_type="full",
            n_iter=300,
            random_state=42,
            verbose=True
        )

        model.fit(X_scaled)

        hidden_states = model.predict(X_scaled)
        df["state"] = hidden_states

        # Identify regimes by volatility
        state_stats = df.groupby("state").agg({
            "rolling_volatility": "mean"
        }).reset_index()

        sorted_states = state_stats.sort_values("rolling_volatility")

        low_vol_state = sorted_states.iloc[0]["state"]
        high_vol_state = sorted_states.iloc[-1]["state"]

        remaining = state_stats[
            ~state_stats["state"].isin([low_vol_state, high_vol_state])
        ]

        mid_state = remaining.iloc[0]["state"]

        state_mapping = {
            int(low_vol_state): "Sideways",
            int(mid_state): "Bull",
            int(high_vol_state): "Crisis"
        }

        # Save
        model_path = os.path.join(self.model_dir, f"{model_name}_hmm.pkl")
        scaler_path = os.path.join(self.model_dir, f"{model_name}_scaler.pkl")
        mapping_path = os.path.join(self.model_dir, f"{model_name}_mapping.pkl")

        joblib.dump(model, model_path)
        scaler.save(scaler_path)
        joblib.dump(state_mapping, mapping_path)

        print("Training completed successfully.")
        print("State mapping:", state_mapping)

        return state_mapping


if __name__ == "__main__":
    trainer = RegimeTrainer("mongodb://localhost:27017", "aetherion")

    trainer.train(
        market="CRYPTO",
        symbol="BTCUSDT",
        timeframe="1m",
        model_name="crypto_1m"
    )