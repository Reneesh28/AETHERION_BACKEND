from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "aetherion"

FEATURE_COLS = [
    "rolling_volatility",
    "atr",
    "volume_delta"
]
TIMEFRAMES = ["1m", "5m", "15m", "1h"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["market_features"]

MODEL_CACHE = {}


def load_model(timeframe):
    if timeframe in MODEL_CACHE:
        return MODEL_CACHE[timeframe]

    try:
        model_path = os.path.join(
            MODEL_DIR,
            f"regime_crypto_{timeframe}.pkl"
        )
        scaler_path = os.path.join(
            MODEL_DIR,
            f"scaler_crypto_{timeframe}.pkl"
        )

        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)

        MODEL_CACHE[timeframe] = (model, scaler)
        return model, scaler

    except Exception:
        return None, None

@app.route("/detect_regime", methods=["POST"])
def detect_regime():

    request_data = request.json

    if not request_data:
        return jsonify({"error": "Invalid JSON body"}), 400

    market = request_data.get("market")
    symbol = request_data.get("symbol")

    if not market or not symbol:
        return jsonify({"error": "Missing parameters"}), 400

    results = {}

    for timeframe in TIMEFRAMES:

        model, scaler = load_model(timeframe)

        if model is None:
            results[timeframe] = {
                "error": "Model not available"
            }
            continue

        cursor = (
            collection
            .find({
                "market": market,
                "symbol": symbol,
                "timeframe": timeframe
            })
            .sort("timestamp", -1)
            .limit(200)
        )

        data = list(cursor)

        if not data:
            results[timeframe] = {
                "error": "No data"
            }
            continue

        df = pd.DataFrame(data)
        df = df.sort_values("timestamp")

        if not all(col in df.columns for col in FEATURE_COLS):
            results[timeframe] = {
                "error": "Feature mismatch"
            }
            continue

        df = df[FEATURE_COLS].dropna()

        if len(df) < 20:
            results[timeframe] = {
                "error": "Not enough data"
            }
            continue

        X = df.values
        X_scaled = scaler.transform(X)

        states = model.predict(X_scaled)
        current_state = int(states[-1])

        results[timeframe] = {
            "state": current_state
        }

    return jsonify({
        "market": market,
        "symbol": symbol,
        "regimes": results
    })


if __name__ == "__main__":
    app.run(port=5001, debug=True)