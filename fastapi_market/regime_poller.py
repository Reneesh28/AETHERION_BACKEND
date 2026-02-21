import asyncio
import httpx
import mysql.connector
from datetime import datetime

from fastapi_market.regime_ws import regime_manager


FLASK_REGIME_URL = "http://127.0.0.1:5001/detect_regime"

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "3508925143@Rt",
    "database": "aetherion"
}

# 🔥 Optimization Controls
POLL_INTERVAL = 10
CONFIDENCE_THRESHOLD = 0.60  # Only accept regime if confidence > 60%

# 🔥 In-memory cache
last_regime_state = None


async def poll_regime():
    """
    Poll Flask Regime Service every 10 seconds
    Insert only on regime change
    Apply confidence filtering
    Broadcast updates
    """

    global last_regime_state

    while True:
        try:
            print("⏳ Polling regime...")

            async with httpx.AsyncClient() as client:

                payload = {
                    "market": "CRYPTO",
                    "symbol": "BTCUSDT",
                    "model_name": "crypto_1m"
                }

                response = await client.post(
                    FLASK_REGIME_URL,
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:

                    data = response.json()

                    state = data["state"]
                    confidence = data["confidence"]

                    # 🔹 Confidence Filter
                    if confidence < CONFIDENCE_THRESHOLD:
                        print(f"⚠️ Low confidence ({confidence}) → Ignored")
                        await asyncio.sleep(POLL_INTERVAL)
                        continue

                    # 🔹 Insert only if regime changed
                    if state != last_regime_state:

                        insert_into_mysql(data, timeframe="1m")

                        await regime_manager.broadcast({
                            "market": data["market"],
                            "symbol": data["symbol"],
                            "regime": data["regime"],
                            "confidence": confidence,
                            "state": state,
                            "timestamp": datetime.utcnow().isoformat()
                        })

                        print(f"🔁 Regime Changed → {data['regime']} ({confidence})")

                        last_regime_state = state

                    else:
                        print("⏳ No regime change")

                else:
                    print("❌ Regime API Error:", response.text)

        except Exception as e:
            print("❌ Polling Error:", e)

        await asyncio.sleep(POLL_INTERVAL)


def insert_into_mysql(data, timeframe):
    """
    Insert regime state into MySQL
    Only called when regime changes
    """

    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        query = """
        INSERT INTO regime_state
        (market, symbol, timeframe, regime, confidence, state, detected_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data["market"],
            data["symbol"],
            timeframe,
            data["regime"],
            data["confidence"],
            data["state"],
            datetime.utcnow()
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        print("💾 Stored regime in DB")

    except Exception as e:
        print("❌ MySQL Insert Error:", e)