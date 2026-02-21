from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os
from pymongo import MongoClient

app = Flask(__name__)


MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "aetherion"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["market_features"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")


@app.route("/detect_regime", methods=["POST"])
def detect_regime():

    request_data = request.json

    if not request_data:
        return jsonify({"error": "Invalid JSON body"}), 400

    market = request_data.get("market")
    symbol = request_data.get("symbol")
    model_name = request_data.get("model_name")

    if not market or not symbol or not model_name:
        return jsonify({"error": "Missing parameters"}), 400

    try:
        model = joblib.load(
            os.path.join(MODEL_DIR, f"{model_name}_hmm.pkl")
        )

        scaler = joblib.load(
            os.path.join(MODEL_DIR, f"{model_name}_scaler.pkl")
        )

        mapping = joblib.load(
            os.path.join(MODEL_DIR, f"{model_name}_mapping.pkl")
        )

    except Exception as e:
        return jsonify({
            "error": f"Model load failed: {str(e)}"
        }), 500
    
    cursor = (
        collection
        .find({"market": market, "symbol": symbol})
        .sort("timestamp", -1)
        .limit(200)
    )

    data = list(cursor)

    if not data:
        return jsonify({"error": "No feature data found"}), 404

    df = pd.DataFrame(data)

    # 🔥 Important: Chronological Order
    df = df.sort_values("timestamp")

    feature_cols = [
        "log_return",
        "rolling_volatility",
        "atr",
        "volume_delta",
        "spread"
    ]

    df = df[feature_cols].dropna()

    if len(df) < 20:
        return jsonify({"error": "Not enough data for inference"}), 400

    X = df.values
    X_scaled = scaler.transform(X)
    hidden_states = model.predict(X_scaled)

    current_state = int(hidden_states[-1])
    regime_label = mapping[current_state]

    # Confidence Score
    state_probs = model.predict_proba(X_scaled)
    confidence = float(state_probs[-1][current_state])

    return jsonify({
        "market": market,
        "symbol": symbol,
        "regime": regime_label,
        "confidence": round(confidence, 4),
        "state": current_state
    })


if __name__ == "__main__":
    app.run(port=5001, debug=True)