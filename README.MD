# 🧠 AETHERION

## 🚀 Real-Time Market Regime Detection & Strategy Switching Engine

---

# 🏆 PROJECT STATUS

### ✅ Day 1 — System Bootstrap

### ✅ Day 2 — Market Data Simulator

### ✅ Day 3 — Feature Engineering Layer

### ✅ Day 4 — HMM Regime Model Training

### ✅ Day 5 — Live Regime Detection + WebSocket Broadcasting

AETHERION backend now runs a fully asynchronous multi-market ingestion engine with live ML-based regime detection and WebSocket broadcasting.

---

# 🧱 FINALIZED TECH STACK

| Layer            | Technology      | Purpose                      |
| ---------------- | --------------- | ---------------------------- |
| Core Platform    | Django          | Auth, users, risk controls   |
| Market Ingestion | FastAPI         | Async ingestion + WebSockets |
| ML Engines       | Flask           | Regime detection             |
| Databases        | MySQL + MongoDB | Structured + tick storage    |
| Real-Time        | WebSockets      | Live streaming               |
| Async            | asyncio         | Low-latency ingestion        |

---

# 🏗 SYSTEM ARCHITECTURE

```
Django Core (Port 8000)     → MySQL (3306)
FastAPI Market (Port 8001)  → MongoDB (27017)
Flask Regime (Port 8002)    → HMM Model Service

FastAPI → Flask (REST ML inference)
FastAPI → MySQL (Regime storage)
FastAPI → WebSocket (Live streaming)
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

# ⚙️ ENVIRONMENT SETUP

## 1️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🗄 DATABASE CONFIGURATION

## 🟦 MySQL

### Create Databases

```sql
CREATE DATABASE aetherion_core;
CREATE DATABASE aetherion;
```

### Regime Table

```sql
CREATE TABLE regime_state (
    id INT AUTO_INCREMENT PRIMARY KEY,
    market VARCHAR(50) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    regime VARCHAR(20) NOT NULL,
    confidence FLOAT NOT NULL,
    state INT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

```sql
CREATE INDEX idx_market_symbol_time
ON regime_state (market, symbol, detected_at);

CREATE INDEX idx_regime
ON regime_state (regime);
```

---

## 🟩 MongoDB

```
mongodb://localhost:27017
```

### Collections

```
market_ticks
market_candles
market_features
crypto_orderbook
us_orderbook
nse_orderbook
```

---

# ▶ RUNNING THE SERVICES

## 🟦 Django Core (Port 8000)

```bash
cd django_core
python manage.py runserver 8000
```

Base URL:

```
http://127.0.0.1:8000/
```

---

## 🟩 FastAPI Market (Port 8001)

```bash
uvicorn fastapi_market.main:app --port 8001 --reload
```

### Swagger Docs

```
http://127.0.0.1:8001/docs
```

### OpenAPI JSON

```
http://127.0.0.1:8001/openapi.json
```

---

## 🟧 Flask Regime (Port 8002)

```bash
python -m flask_regime.app
```

Base URL:

```
http://127.0.0.1:8002/
```

---

# 🔄 INTER-SERVICE COMMUNICATION

### FastAPI → Flask

```
POST http://127.0.0.1:8002/detect_regime
```

### Sample Response

```json
{
  "market": "CRYPTO",
  "symbol": "BTCUSDT",
  "regime": "Bull",
  "confidence": 0.87,
  "state": 2
}
```

---

# 📡 REST ENDPOINTS (FastAPI - Port 8001)

```
GET  http://127.0.0.1:8001/api/market/snapshot/{market}
GET  http://127.0.0.1:8001/api/market/trades/{market}
GET  http://127.0.0.1:8001/api/market/orderbook/{market}
GET  http://127.0.0.1:8001/api/market/features/{market}
GET  http://127.0.0.1:8001/api/market/status
```

---

# 🔌 WEBSOCKET ENDPOINTS

## 🟢 Live Market Stream

```
ws://127.0.0.1:8001/ws/market
```

Streams:

* Tick data
* OHLC candles
* Volume updates

---

## 🟣 Live Regime Stream

```
ws://127.0.0.1:8001/ws/regime
```

Example Payload:

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

---

# 📊 DAY 2 — MARKET SIMULATOR (COMPLETE)

* Random-walk price generator
* Volume simulation
* 1-second tick interval
* MongoDB persistence
* 10-second OHLC aggregation
* WebSocket streaming

---

# 🧠 DAY 3 — FEATURE ENGINE (COMPLETE)

Computed in real time:

* Log returns
* Rolling volatility
* ATR
* Volume delta
* Spread estimation

Stored in:

```
market_features
```

---

# 🤖 DAY 4 — HMM REGIME MODEL (COMPLETE)

* Gaussian Hidden Markov Model
* 4 States → Bull / Bear / Sideways / Crisis
* Feature scaling (StandardScaler)
* Automatic state mapping
* Model persistence (joblib)

Saved Artifacts:

```
crypto_1m_hmm.pkl
crypto_1m_scaler.pkl
crypto_1m_mapping.pkl
```

---

# 🚀 DAY 5 — LIVE REGIME ENGINE (COMPLETE)

## Polling System

FastAPI polls Flask every 10 seconds:

* Applies confidence threshold
* Inserts only on regime change
* Stores in MySQL
* Broadcasts via WebSocket

---

# 🔁 REAL-TIME FLOW

```
Market Data
   ↓
Feature Engineering
   ↓
HMM Regime Detection
   ↓
Confidence Filter
   ↓
MySQL Persistence
   ↓
WebSocket Broadcast
```

---

# 🏆 WHAT HAS BEEN ACHIEVED

✔ Microservice backend separation
✔ Async multi-market ingestion
✔ Mongo feature engineering layer
✔ HMM-based regime classification
✔ Confidence-filtered regime transitions
✔ MySQL historical regime storage
✔ WebSocket real-time regime streaming
✔ Production-style polling architecture

---

# 🔮 NEXT PHASE

* Strategy Switching Engine
* Liquidity Stress Simulator
* Portfolio Risk Engine
* Trade Surveillance System

---

# 🧠 CURRENT SYSTEM STATE

AETHERION Backend

Day 1: COMPLETE
Day 2: COMPLETE
Day 3: COMPLETE
Day 4: COMPLETE
Day 5: COMPLETE

Live multi-market ingestion + ML regime detection operational.
