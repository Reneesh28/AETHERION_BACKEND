import asyncio
import httpx
import mysql.connector
from datetime import datetime
from collections import deque

from fastapi_market.regime_ws import regime_manager
from fastapi_market.regime_fusion import RegimeFusion
from fastapi_market.strategy_engine import StrategyEngine
from fastapi_market.decision_engine import generate_decision
from fastapi_market.decision_ws import decision_manager   # ✅ NEW


FLASK_REGIME_URL = "http://127.0.0.1:5001/detect_regime"

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "3508925143@Rt",
    "database": "aetherion"
}

POLL_INTERVAL = 10
TIMEFRAMES = ["1m", "5m", "15m"]
STABILITY_WINDOW = 5
MIN_CONFIRMATIONS = 3

state_buffers = {
    tf: deque(maxlen=STABILITY_WINDOW)
    for tf in TIMEFRAMES
}

stable_state = {tf: None for tf in TIMEFRAMES}

fusion_engine = RegimeFusion()
strategy_engine = StrategyEngine()

last_meta_regime = None
last_strategy = None


# =========================================
# MYSQL CONNECTION
# =========================================
def get_mysql_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)


# =========================================
# STABILITY EVALUATION
# =========================================
def evaluate_stability(timeframe):

    buffer = state_buffers[timeframe]

    if len(buffer) < STABILITY_WINDOW:
        return None

    counts = {}
    for state in buffer:
        counts[state] = counts.get(state, 0) + 1

    majority_state = max(counts, key=counts.get)

    if counts[majority_state] >= MIN_CONFIRMATIONS:
        return majority_state

    return None


# =========================================
# MAIN POLLER
# =========================================
async def poll_regime():

    global last_meta_regime
    global last_strategy

    conn = None
    cursor = None

    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        print("✅ MySQL connection established.")

        while True:
            try:
                async with httpx.AsyncClient() as client:

                    payload = {
                        "market": "CRYPTO",
                        "symbol": "BTCUSDT"
                    }

                    response = await client.post(
                        FLASK_REGIME_URL,
                        json=payload,
                        timeout=10
                    )

                    if response.status_code != 200:
                        await asyncio.sleep(POLL_INTERVAL)
                        continue

                    data = response.json()
                    regimes = data.get("regimes", {})

                    # =====================================
                    # 1️⃣ TIMEFRAME STABILITY
                    # =====================================
                    for tf in TIMEFRAMES:

                        tf_data = regimes.get(tf)
                        if not tf_data or "error" in tf_data:
                            continue

                        state = tf_data["state"]
                        confidence = tf_data["confidence"]

                        state_buffers[tf].append(state)
                        confirmed_state = evaluate_stability(tf)

                        if confirmed_state is None:
                            continue

                        if confirmed_state != stable_state[tf]:

                            insert_timeframe_regime(
                                cursor,
                                conn,
                                data["market"],
                                data["symbol"],
                                tf,
                                tf_data["regime"],
                                confidence,
                                confirmed_state
                            )

                            await regime_manager.broadcast({
                                "type": "timeframe",
                                "market": data["market"],
                                "symbol": data["symbol"],
                                "timeframe": tf,
                                "regime": tf_data["regime"],
                                "confidence": confidence,
                                "state": confirmed_state,
                                "timestamp": datetime.utcnow().isoformat()
                            })

                            print(f"🔒 {tf} Stable Regime → {tf_data['regime']}")
                            stable_state[tf] = confirmed_state

                    # =====================================
                    # 2️⃣ META FUSION
                    # =====================================
                    meta = fusion_engine.fuse(stable_state)

                    if not meta:
                        await asyncio.sleep(POLL_INTERVAL)
                        continue

                    # Insert only if meta regime changed
                    if meta["meta_regime"] != last_meta_regime:

                        insert_meta_regime(cursor, conn, meta)

                        await regime_manager.broadcast({
                            "type": "meta",
                            "meta_regime": meta["meta_regime"],
                            "confidence": meta["confidence"],
                            "components": meta["components"],
                            "timestamp": datetime.utcnow().isoformat()
                        })

                        print(f"🧠 META REGIME → {meta['meta_regime']}")
                        last_meta_regime = meta["meta_regime"]

                    # =====================================
                    # 3️⃣ STRATEGY SWITCHING
                    # =====================================
                    strategy_data = strategy_engine.select_strategy(meta)

                    if strategy_data:
                        strategy_name = strategy_data["strategy"]

                        if strategy_name != last_strategy:

                            insert_strategy_state(
                                cursor,
                                conn,
                                strategy_data
                            )

                            await regime_manager.broadcast({
                                "type": "strategy",
                                "meta_regime": strategy_data["meta_regime"],
                                "strategy": strategy_name,
                                "timestamp": datetime.utcnow().isoformat()
                            })

                            print(f"🎯 Strategy Switched → {strategy_name}")
                            last_strategy = strategy_name

                    # =====================================
                    # 4️⃣ DECISION ENGINE (Event Driven)
                    # =====================================
                    decision = generate_decision(
                        market=data["market"],
                        symbol=data["symbol"],
                        meta_regime=meta["meta_regime"],
                        strategy=last_strategy,
                        confidence=meta["confidence"]
                    )

                    if decision:

                        insert_decision(cursor, conn, decision)

                        # ✅ Broadcast decision event
                        await decision_manager.broadcast({
                            "type": "decision",
                            "market": decision.market,
                            "symbol": decision.symbol,
                            "meta_regime": decision.meta_regime,
                            "strategy": decision.strategy,
                            "action": decision.action,
                            "confidence": decision.confidence,
                            "timestamp": decision.timestamp.isoformat()
                        })

                        print(f"📈 Decision Generated → {decision.action} ({decision.strategy})")

            except Exception as e:
                print("❌ Polling Error:", e)

            await asyncio.sleep(POLL_INTERVAL)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================
# INSERT FUNCTIONS
# =========================================

def insert_timeframe_regime(cursor, conn, market, symbol,
                            timeframe, regime, confidence, state):

    query = """
    INSERT INTO regime_state
    (market, symbol, timeframe, regime, confidence, state, detected_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        market,
        symbol,
        timeframe,
        regime,
        confidence,
        state,
        datetime.utcnow()
    )

    cursor.execute(query, values)
    conn.commit()


def insert_meta_regime(cursor, conn, meta):

    query = """
    INSERT INTO meta_regime_state
    (meta_regime, confidence, detected_at)
    VALUES (%s, %s, %s)
    """

    values = (
        meta["meta_regime"],
        meta["confidence"],
        datetime.utcnow()
    )

    cursor.execute(query, values)
    conn.commit()


def insert_strategy_state(cursor, conn, strategy_data):

    query = """
    INSERT INTO strategy_state
    (meta_regime, strategy, detected_at)
    VALUES (%s, %s, %s)
    """

    values = (
        strategy_data["meta_regime"],
        strategy_data["strategy"],
        datetime.utcnow()
    )

    cursor.execute(query, values)
    conn.commit()


def insert_decision(cursor, conn, decision):

    query = """
    INSERT INTO decisions
    (market, symbol, meta_regime, strategy, action, confidence, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        decision.market,
        decision.symbol,
        decision.meta_regime,
        decision.strategy,
        decision.action,
        decision.confidence,
        decision.timestamp
    )

    cursor.execute(query, values)
    conn.commit()