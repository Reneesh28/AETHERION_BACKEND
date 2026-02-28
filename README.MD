# 🧠 AETHERION

## 🚀 Real-Time Market Regime Detection & Strategy Switching Engine

---

# 📌 PROJECT OVERVIEW

AETHERION is a production-style microservice backend designed to:

• Ingest multi-market data in real time
• Engineer features asynchronously
• Detect market regimes using ML (HMM)
• Persist regime transitions
• Stream live updates via WebSockets

This README reflects the **actual Day-to-Day Implementation Plan (Day 1 → Day 5)** and the completed integration flow after each phase.

---

# 🧱 FINAL TECH STACK (LOCKED)

| Layer         | Technology      | Purpose                              |
| ------------- | --------------- | ------------------------------------ |
| Core Platform | Django          | Control layer, auth, risk, DB models |
| Market Engine | FastAPI         | Async ingestion + WebSockets         |
| ML Engine     | Flask           | Regime detection (HMM)               |
| Databases     | MySQL + MongoDB | Structured + tick storage            |
| Real-Time     | WebSockets      | Live streaming                       |
| Async Runtime | asyncio         | Low latency processing               |

---

# 🏗 FINAL ARCHITECTURE

```
Django Core (8000) → MySQL
FastAPI Market (8001) → MongoDB
Flask Regime ML (8002)

FastAPI → Flask (ML inference)
FastAPI → MySQL (Regime persistence)
FastAPI → WebSocket (Live broadcast)
```

---

# 📂 PROJECT STRUCTURE

```
AETHERION_BACKEND/
│
├── django_core/        # Django + MySQL (Control Tower)
├── fastapi_market/     # FastAPI + MongoDB (Async Market Engine)
├── flask_regime/       # Flask (HMM Regime Engine)
├── shared/             # Shared utilities
├── requirements.txt
├── .gitignore
└── README.md
```

---

# 🗓 DAY‑TO‑DAY IMPLEMENTATION BREAKDOWN

---

# ✅ DAY 1 — SYSTEM BOOTSTRAP

### Objectives

• Setup microservice separation
• Configure Django + MySQL
• Configure FastAPI service
• Configure Flask ML service
• Establish database connectivity

### Completed

✔ Django running on `http://127.0.0.1:8000/`
✔ FastAPI running on `http://127.0.0.1:8001/`
✔ Flask ML service running on `http://127.0.0.1:8002/`
✔ MySQL connected
✔ MongoDB connected

System foundation complete.

---

# ✅ DAY 2 — MARKET DATA SIMULATOR

### Objectives

• Build async market generator
• Generate random-walk price
• Simulate volume
• Store ticks in MongoDB
• Broadcast via WebSocket

### Implemented

✔ 1-second tick engine
✔ MongoDB collection: `market_ticks`
✔ OHLC aggregation (10s)
✔ WebSocket stream

### WebSocket

```
ws://127.0.0.1:8001/ws/market
```

### Integration After Day 2

Market data → MongoDB → WebSocket

Live streaming operational.

---

# ✅ DAY 3 — FEATURE ENGINE

### Objectives

• Compute rolling features
• Store features in MongoDB
• Maintain async processing loop

### Implemented Features

• Log returns
• Rolling volatility
• ATR
• Volume delta
• Spread estimation

### Storage

MongoDB collection:

```
market_features
```

### Integration After Day 3

Market Data → Feature Engine → MongoDB → WebSocket

Feature layer fully integrated.

---

# ✅ DAY 4 — HMM REGIME MODEL TRAINING

### Objectives

• Train Gaussian Hidden Markov Model
• Scale features
• Map hidden states to market regimes
• Persist model artifacts

### Model Design

• 4 Hidden States
• Bull
• Bear
• Sideways
• Crisis

### Saved Artifacts

```
crypto_1m_hmm.pkl
crypto_1m_scaler.pkl
crypto_1m_mapping.pkl
```

### Flask ML Endpoint

```
POST http://127.0.0.1:8002/detect_regime
```

### Integration After Day 4

Feature Engine → Flask ML → Regime Prediction

ML inference service operational.

---

# ✅ DAY 5 — LIVE REGIME ENGINE + PERSISTENCE

### Objectives

• Poll Flask every 10 seconds
• Apply confidence filter
• Insert only on regime change
• Store regime history in MySQL
• Broadcast regime updates

### MySQL Table

```
regime_state
```

Fields:

• market
• symbol
• timeframe
• regime
• confidence
• state
• detected_at

### WebSocket

```
ws://127.0.0.1:8001/ws/regime
```

### Example Payload

```json
{
  "market": "CRYPTO",
  "symbol": "BTCUSDT",
  "regime": "Sideways",
  "confidence": 0.76,
  "state": 1,
  "timestamp": "2026-02-28T18:10:00Z"
}
```

### Integration After Day 5

Market Data
→ Feature Engine
→ HMM Regime Detection
→ Confidence Filter
→ MySQL Persistence
→ WebSocket Broadcast

Full ML-driven real-time regime system operational.

---

# 📡 FASTAPI REST ENDPOINTS

```
GET  http://127.0.0.1:8001/api/market/snapshot/{market}
GET  http://127.0.0.1:8001/api/market/trades/{market}
GET  http://127.0.0.1:8001/api/market/orderbook/{market}
GET  http://127.0.0.1:8001/api/market/features/{market}
GET  http://127.0.0.1:8001/api/market/status
```

Swagger Docs:

```
http://127.0.0.1:8001/docs
```

---

# ▶ RUNNING THE SERVICES

## Django Core

```
cd django_core
python manage.py runserver 8000
```

## FastAPI Market

```
uvicorn fastapi_market.main:app --port 8001 --reload
```

## Flask Regime ML

```
python -m flask_regime.app
```

---

# 🏆 CURRENT SYSTEM CAPABILITIES

✔ Microservice separation
✔ Async multi-market ingestion
✔ Real-time feature engineering
✔ ML-based regime classification
✔ Confidence-filtered regime transitions
✔ MySQL regime history
✔ Live WebSocket broadcasting
✔ Production-style polling architecture

---

# 🚀 NEXT IMPLEMENTATION PHASE

Following completion of Regime Detection:

• Strategy Switching Engine
• Risk Layer Integration
• Execution Engine
• Surveillance System

---

# 📌 PROJECT STATE

Day 1: COMPLETE
Day 2: COMPLETE
Day 3: COMPLETE
Day 4: COMPLETE
Day 5: COMPLETE

AETHERION backend is fully operational with live ML regime detection.
