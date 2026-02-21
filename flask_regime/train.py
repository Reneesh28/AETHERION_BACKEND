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

    def train(self, market, symbol, model_name, limit=10000):

        cursor = (
            self.collection
            .find({"market": market, "symbol": symbol})
            .sort("timestamp", 1)
            .limit(limit)
        )

        data = list(cursor)

        if not data:
            raise ValueError("No feature data found.")

        df = pd.DataFrame(data)

        feature_cols = [
            "log_return",
            "rolling_volatility",
            "atr",
            "volume_delta",
            "spread"
        ]

        df = df[feature_cols].dropna()

        if len(df) < 500:
            raise ValueError("Not enough data to train HMM.")

        X = df.values

        # 🔹 Scale Features
        scaler = FeatureScaler()
        X_scaled = scaler.fit_transform(X)

        # 🔹 Train HMM
        model = GaussianHMM(
            n_components=4,
            covariance_type="full",
            n_iter=300,
            random_state=42,
            verbose=True
        )

        model.fit(X_scaled)

        # 🔹 Predict Hidden States
        hidden_states = model.predict(X_scaled)
        df["state"] = hidden_states

        # 🔹 Compute Statistics Per State
        state_stats = df.groupby("state").agg({
            "log_return": "mean",
            "rolling_volatility": "mean",
            "atr": "mean"
        }).reset_index()

        print("\nState Statistics:")
        print(state_stats)

        # 🔹 Identify States

        # Sort by volatility
        sorted_by_vol = state_stats.sort_values("rolling_volatility")

        sideways_state = sorted_by_vol.iloc[0]["state"]
        crisis_state = sorted_by_vol.iloc[-1]["state"]

        # Remaining states
        remaining_states = state_stats[
            ~state_stats["state"].isin([sideways_state, crisis_state])
        ]

        bull_state = remaining_states.sort_values(
            "log_return", ascending=False
        ).iloc[0]["state"]

        bear_state = remaining_states.sort_values(
            "log_return"
        ).iloc[0]["state"]

        state_mapping = {
            int(bull_state): "Bull",
            int(bear_state): "Bear",
            int(sideways_state): "Sideways",
            int(crisis_state): "Crisis"
        }

        print("\nState Mapping:")
        print(state_mapping)

        # 🔹 Save Model, Scaler, Mapping
        model_path = os.path.join(self.model_dir, f"{model_name}_hmm.pkl")
        scaler_path = os.path.join(self.model_dir, f"{model_name}_scaler.pkl")
        mapping_path = os.path.join(self.model_dir, f"{model_name}_mapping.pkl")

        joblib.dump(model, model_path)
        scaler.save(scaler_path)
        joblib.dump(state_mapping, mapping_path)

        print("\nTraining completed successfully.")
        print("Transition Matrix:")
        print(model.transmat_)

        return {
            "model_path": model_path,
            "scaler_path": scaler_path,
            "mapping_path": mapping_path,
            "transition_matrix": model.transmat_,
            "state_mapping": state_mapping
        }