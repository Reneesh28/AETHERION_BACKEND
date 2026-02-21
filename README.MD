# 🧠 AETHERION — Backend Architecture (Day 1 → Day 5)

---

# 🏁 Current Status

**Day 1: System Bootstrap — ✅ Complete**
**Day 2: Market Data Simulator — ✅ Complete**
**Day 3: Feature Engine — ✅ Complete**
**Day 4: Regime Model Training (HMM) — ✅ Complete**
**Day 5: Live Regime Engine + WebSocket Integration — ✅ Complete**

AETHERION backend now runs a fully asynchronous multi-market ingestion engine with live ML-based regime detection and WebSocket broadcasting.

---

# 🏗 System Architecture

```
Django Core (Port 8000)     → MySQL (3306)
FastAPI Market (Port 8001)  → MongoDB (27017)
Flask Regime (Port 8002)    → HMM Model Service

FastAPI → Flask (REST Communication)
FastAPI → MySQL (Regime Storage)
FastAPI → WebSocket (Live Streaming)
```

This establishes a microservice-style backend separation with ML isolation.

---

# 📂 Project Structure

```
AETHERION_BACKEND/
│
├── django_core/        # Django + MySQL (Control Tower)
├── fastapi_market/     # FastAPI + MongoDB (Async Market Engine)
├── flask_regime/       # Flask (HMM Regime Engine)
├── shared/             # Shared utilities (future use)
├── requirements.txt
├── .gitignore
└── README.md
```

---

# ⚙️ Environment Setup

## 1️⃣ Create Virtual Environment

```
python -m venv venv
venv\Scripts\activate
```

## 2️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

# 📦 requirements.txt (Updated to Day 5)

```
# Core Frameworks
Django
djangorestframework
fastapi
uvicorn
flask

# Databases
mysqlclient
mysql-connector-python
motor

# ML Stack
numpy
pandas
scikit-learn
hmmlearn
joblib

# HTTP & Async
httpx
requests
websockets

# Utilities
python-dotenv
loguru
pyotp
certifi
python-certifi-win32

# Broker SDK
smartapi-python
```

---

# 🗄 Database Configuration

## MySQL (Django Core + Regime Storage)

Create databases:

```
CREATE DATABASE aetherion_core;
CREATE DATABASE aetherion;
```

Regime Table (Day 5):

```
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

Add indexes for performance:

```
CREATE INDEX idx_market_symbol_time
ON regime_state (market, symbol, detected_at);

CREATE INDEX idx_regime
ON regime_state (regime);
```

---

## MongoDB (FastAPI Market)

Runs locally:

```
mongodb://localhost:27017
```

Collections:

```
market_ticks
market_candles
market_features
crypto_orderbook
us_orderbook
nse_orderbook
```

---

# ▶ Running the Services

## Django Core (Port 8000)

```
cd django_core
python manage.py runserver 8000
```

---

## FastAPI Market (Port 8001)

```
uvicorn fastapi_market.main:app --port 8001
```

Swagger:

```
http://127.0.0.1:8001/docs
```

---

## Flask Regime (Port 8002)

```
python -m flask_regime.app
```

---

# 🔄 Inter-Service Communication

FastAPI → Flask Regime Detection:

```
POST http://127.0.0.1:8002/detect_regime
```

Response:

```
{
  "market": "CRYPTO",
  "symbol": "BTCUSDT",
  "regime": "Bull",
  "confidence": 0.87,
  "state": 2
}
```

---

# 📊 Day 2 — Market Data Simulator

## Features

• Random-walk price generator
• Volume simulation
• 1-second tick interval
• MongoDB persistence
• WebSocket streaming
• 10-second OHLC aggregation

WebSocket:

```
ws://127.0.0.1:8001/ws/market
```

---

# 🧠 Day 3 — Feature Engine

• Rolling volatility
• Log returns
• ATR
• Volume delta
• Spread estimation
• Mongo feature storage

Collection:

```
market_features
```

---

# 🤖 Day 4 — HMM Regime Model

• Gaussian Hidden Markov Model
• 4 States → Bull / Bear / Sideways / Crisis
• Feature scaling (StandardScaler)
• Automatic state mapping
• Model persistence (joblib)

Saved Artifacts:

```
crypto_1m_hmm.pkl
crypto_1m_scaler.pkl
crypto_1m_mapping.pkl
```

---

# 🚀 Day 5 — Live Regime Engine

## Polling System

FastAPI polls Flask every 10 seconds:

• Applies confidence threshold
• Inserts only on regime change
• Stores in MySQL
• Broadcasts via WebSocket

---

## Regime WebSocket

```
ws://127.0.0.1:8001/ws/regime
```

Streams:

```
{
  "market": "CRYPTO",
  "symbol": "BTCUSDT",
  "regime": "Sideways",
  "confidence": 0.76,
  "state": 1,
  "timestamp": "..."
}
```

---

# 📡 REST Endpoints

```
GET /api/market/snapshot/{market}
GET /api/market/trades/{market}
GET /api/market/orderbook/{market}
GET /api/market/features/{market}
GET /api/market/status
```

---

# 🧠 What Has Been Achieved (Day 1–5)

✔ Microservice backend separation
✔ Async multi-market ingestion
✔ Mongo feature engineering layer
✔ HMM-based regime classification
✔ Confidence-filtered regime transitions
✔ MySQL historical regime storage
✔ WebSocket real-time regime streaming
✔ Production-style polling architecture

AETHERION now includes:

Market Engine → Feature Layer → Regime ML → Database Persistence → WebSocket Streaming

This forms the base for:

Strategy Engine → Risk Layer → Execution Engine → Surveillance System

---

# 🚀 Current Status

AETHERION Backend

Day 1: COMPLETE
Day 2: COMPLETE
Day 3: COMPLETE
Day 4: COMPLETE
Day 5: COMPLETE

Live multi-market ingestion + ML regime detection operational.
