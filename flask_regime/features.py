import numpy as np
import pandas as pd
from pymongo import MongoClient


class FeatureEngineer:

    def __init__(self, mongo_uri, db_name):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

    def fetch_candles(self, collection_name, limit=10000):
        collection = self.db[collection_name]
        cursor = collection.find().limit(limit)
        data = list(cursor)
        if not data:
            raise ValueError("No data found in Mongo collection.")
        df = pd.DataFrame(data)
        possible_time_cols = ["timestamp", "event_time", "open_time", "time"]
        time_col = None
        for col in possible_time_cols:
            if col in df.columns:
                time_col = col
                break
        if time_col is None:
            raise ValueError(f"No valid time column found. Columns available: {df.columns}")
        df = df.sort_values(time_col)
        df.reset_index(drop=True, inplace=True)
        return df

    def compute_features(self, df):
        # Log Return
        df["log_return"] = np.log(df["close"] / df["close"].shift(1))

        # Rolling Means
        df["mean_20"] = df["log_return"].rolling(20).mean()
        df["mean_50"] = df["log_return"].rolling(50).mean()

        # Rolling Volatility
        df["vol_20"] = df["log_return"].rolling(20).std()
        df["vol_50"] = df["log_return"].rolling(50).std()

        # ATR (14)
        df["tr"] = np.maximum(
            df["high"] - df["low"],
            np.maximum(
                abs(df["high"] - df["close"].shift(1)),
                abs(df["low"] - df["close"].shift(1))
            )
        )
        df["atr_14"] = df["tr"].rolling(14).mean()

        # Volume Z-score
        df["volume_mean_20"] = df["volume"].rolling(20).mean()
        df["volume_std_20"] = df["volume"].rolling(20).std()
        df["volume_z_20"] = (
            (df["volume"] - df["volume_mean_20"]) /
            df["volume_std_20"]
        )

        # Skewness
        df["skew_20"] = df["log_return"].rolling(20).skew()

        # Volatility of Volatility
        df["vol_of_vol"] = df["vol_20"].rolling(20).std()

        # Drop NaNs
        df = df.dropna()

        feature_cols = [
            "log_return",
            "mean_20",
            "mean_50",
            "vol_20",
            "vol_50",
            "atr_14",
            "volume_z_20",
            "skew_20",
            "vol_of_vol"
        ]

        return df[feature_cols].values, df

