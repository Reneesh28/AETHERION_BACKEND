# 🧠 AETHERION

## 🚀 Real-Time Institutional Trading Intelligence System

---

# 📌 PROJECT STATUS — COMPLETED COMPONENTS

AETHERION backend is fully operational with live multi-market ingestion, ML-based regime detection, strategy switching, and decision generation.

The following components are fully implemented and integrated.

---

# 🧱 SYSTEM ARCHITECTURE

```
Django Core (Port 8000) → MySQL
FastAPI Market Engine (Port 8001) → MongoDB
Flask ML Engine (Port 8002)

FastAPI → Flask (ML inference)
FastAPI → MySQL (State + Decisions)
FastAPI → WebSockets (Live broadcasting)
```

---

# 🗄 DATABASE LAYER

## MySQL

Used for:

• Regime state history
• Strategy decisions
• System state persistence

### Core Tables

* `regime_state`
* `decisions`

---

## MongoDB

Used for high-frequency market storage.

### Collections

* `market_ticks`
* `market_candles`
* `market_features`
* `crypto_orderbook`
* `us_orderbook`
* `nse_orderbook`

---

# 🌐 LIVE SERVICES

## Django Core

```
http://127.0.0.1:8000/
```

## FastAPI Market Engine

Swagger Docs:

```
http://127.0.0.1:8001/docs
```

## Flask ML Engine

```
http://127.0.0.1:8002/
```

---

# 📡 LIVE REST ENDPOINTS

```
GET  /api/market/snapshot/{market}
GET  /api/market/trades/{market}
GET  /api/market/orderbook/{market}
GET  /api/market/features/{market}
GET  /api/market/status
GET  /api/decision/latest
```

---

# 🔌 LIVE WEBSOCKET STREAMS

## Market Stream

```
ws://127.0.0.1:8001/ws/market
```

Streams:
• Tick data
• OHLC candles
• Volume updates

---

## Regime Stream

```
ws://127.0.0.1:8001/ws/regime
```

Streams:
• Market regime
• Confidence score
• State transitions

---

## Decision Stream

```
ws://127.0.0.1:8001/ws/decision
```

Streams:
• Strategy action
• Buy / Sell / Hold
• Confidence gating

---

# 🧠 COMPLETED INTELLIGENCE PIPELINE

### 1️⃣ Market Simulation + Live Ingestion

✔ Random-walk simulator
✔ Binance live trades ingestion
✔ US market connector
✔ Orderbook ingestion
✔ Reconnect logic
✔ Latency monitoring
✔ Multi-market normalization

---

### 2️⃣ Multi-Timeframe Feature Engine

✔ Multi-timeframe candle engine
✔ ATR
✔ Rolling volatility
✔ Volume delta
✔ Indexed Mongo collections
✔ Real-time feature computation

---

### 3️⃣ Regime Intelligence Engine

✔ Gaussian Hidden Markov Model
✔ 4-state classification (Bull / Bear / Sideways / Crisis)
✔ Confidence scoring
✔ Stability filtering
✔ Multi-timeframe fusion
✔ Strategy switching logic
✔ MySQL regime persistence
✔ WebSocket broadcasting

Pipeline:

Market → Candle → Features → HMM → Stability → Fusion → Strategy

---

### 4️⃣ Decision Pipeline Engine

✔ Pydantic decision model
✔ Strategy → Action mapping
✔ Confidence gating
✔ Cooldown logic
✔ Duplicate protection
✔ MySQL decision storage
✔ REST endpoint `/api/decision/latest`
✔ WebSocket `/ws/decision`

Pipeline:

Market → Regime → Strategy → Decision Policy → MySQL → REST + WebSocket

---

# 🏆 CURRENT SYSTEM CAPABILITIES

✔ Microservice-based architecture
✔ Async multi-market ingestion
✔ Institutional-grade preprocessing
✔ ML-driven regime classification
✔ Strategy switching engine
✔ Signal generation layer
✔ Persistent state storage
✔ Real-time WebSocket broadcasting
✔ Clean service separation (Django / FastAPI / Flask)

---

# 📌 SYSTEM STATE

All core intelligence layers are operational.

Market Engine → Feature Engine → Regime Engine → Strategy Layer → Decision Engine

AETHERION backend is fully functional up to the Decision Intelligence layer.
