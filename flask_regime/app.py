from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os
from pymongo import MongoClient

app = Flask(__name__)

# ==============================
# CONFIG
# ==============================

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "aetherion"

FEATURE_COLS = [
    "rolling_volatility",
    "atr",
    "volume_delta"
]

TIMEFRAMES = ["1m", "5m"]  # Fast Completion Mode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["market_features"]

MODEL_CACHE = {}


# ==============================
# MODEL LOADER
# ==============================
def load_model(timeframe):
    if timeframe in MODEL_CACHE:
        return MODEL_CACHE[timeframe]

    try:
        model_path = os.path.join(
            MODEL_DIR,
            f"crypto_{timeframe}_hmm.pkl"
        )
        scaler_path = os.path.join(
            MODEL_DIR,
            f"crypto_{timeframe}_scaler.pkl"
        )
        mapping_path = os.path.join(
            MODEL_DIR,
            f"crypto_{timeframe}_mapping.pkl"
        )

        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        mapping = joblib.load(mapping_path)

        MODEL_CACHE[timeframe] = (model, scaler, mapping)
        return model, scaler, mapping

    except Exception:
        return None, None, None


# ==============================
# REGIME DETECTION
# ==============================
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

        model, scaler, mapping = load_model(timeframe)

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

        # Confidence
        probs = model.predict_proba(X_scaled)
        confidence = float(probs[-1][current_state])

        regime_label = mapping.get(current_state, "Unknown")

        results[timeframe] = {
            "state": current_state,
            "regime": regime_label,
            "confidence": round(confidence, 4)
        }

    return jsonify({
        "market": market,
        "symbol": symbol,
        "regimes": results
    })


if __name__ == "__main__":
    app.run(port=5001, debug=True)