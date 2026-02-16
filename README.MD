# 🧠 AETHERION — Backend Architecture

---

# 🏁 Current Status

**Day 1: System Bootstrap — ✅ Complete**
**Day 2: Market Data Simulator — ✅ Complete**

AETHERION backend is now running a live async market engine with OHLC aggregation.

---

# 🏗 System Architecture

```
Django Core (Port 8000)   → MySQL (3306)
FastAPI Market (Port 8001) → MongoDB (27017)
Flask Regime (Port 8002)

FastAPI → Flask (REST Communication)
```

This establishes a microservice-style backend separation.

---

# 📂 Project Structure

```
AETHERION_BACKEND/
│
├── django_core/        # Django + MySQL (Control Tower)
├── fastapi_market/     # FastAPI + MongoDB (Async Market Engine)
├── flask_regime/       # Flask (Regime Engine)
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

# 📦 requirements.txt

```
Django
djangorestframework
fastapi
uvicorn
flask
mysqlclient
motor
python-dotenv
requests
loguru
websockets
```

---

# 🗄 Database Configuration

## MySQL (Django Core)

Create database:

```
CREATE DATABASE aetherion_core;
```

Apply migrations:

```
cd django_core
python manage.py migrate
```

---

## MongoDB (FastAPI Market)

Runs locally as Windows service:

```
mongodb://localhost:27017
```

Collections created dynamically:

* `market_ticks`
* `market_candles`

---

# ▶ Running the Services

## Django Core (Port 8000)

```
cd django_core
python manage.py runserver 8000
```

Health check:

```
http://127.0.0.1:8000/health/
```

---

## FastAPI Market (Port 8001)

```
cd fastapi_market
python -m uvicorn main:app --port 8001
```

Health check:

```
http://127.0.0.1:8001/
```

Swagger docs:

```
http://127.0.0.1:8001/docs
```

---

## Flask Regime (Port 8002)

```
cd flask_regime
python app.py
```

Health check:

```
http://127.0.0.1:8002/health
```

---

# 🔄 Inter-Service Communication

FastAPI → Flask REST call:

```
http://127.0.0.1:8001/check-regime
```

Expected response:

```
{"status":"flask_regime running"}
```

---

# 📊 Day 2 — Market Data Simulator

## 🎯 Objective

Generate a live simulated market with:

* Real-time tick generation
* MongoDB persistence
* WebSocket broadcasting
* 10-second OHLC candle aggregation

---

## 🔁 Tick Engine

* Random-walk price simulation
* Volume simulation
* 1-second tick interval
* Logged using `loguru`

Mongo Collection:

```
market_ticks
```

---

## 🌐 WebSocket Endpoint

```
ws://127.0.0.1:8001/ws/market
```

Streams live ticks every second:

```
{
  "price": 101.22,
  "volume": 532,
  "timestamp": 1771230xxx,
  "_id": "..."
}
```

---

## 📈 Candle Aggregation (10-Second OHLC)

Every 10 seconds computes:

* Open
* High
* Low
* Close
* Aggregated Volume

Stored in Mongo:

```
market_candles
```

---

## 📡 REST Endpoints

### Snapshot (Recent Ticks)

```
GET /api/market/snapshot
```

Returns latest stored ticks.

---

### Candle Data

```
GET /api/market/candles
```

Returns recent OHLC candles:

```
{
  "candles": [
    {
      "open": 100.75,
      "high": 102.28,
      "low": 100.75,
      "close": 102.28,
      "volume": 2380,
      "start_time": 1771230349,
      "end_time": 1771230359
    }
  ]
}
```

---

# ✅ Day 1 Completion Checklist

✔ Django connected to MySQL
✔ FastAPI connected to MongoDB
✔ Flask running independently
✔ All services on separate ports
✔ Health endpoints operational
✔ FastAPI → Flask communication working

---

# ✅ Day 2 Completion Checklist

✔ Random-walk price generator
✔ Volume simulation
✔ Tick persistence (MongoDB)
✔ WebSocket real-time streaming
✔ Proper JSON serialization handling
✔ 10-second OHLC candle aggregation
✔ Candle persistence
✔ REST snapshot endpoint
✔ REST candle endpoint

---

# 🧠 What Has Been Achieved

AETHERION now includes:

• Structured storage (MySQL via Django ORM)
• Async unstructured storage (MongoDB via Motor)
• Real-time WebSocket market streaming
• Tick-level data persistence
• OHLC aggregation engine
• Microservice REST communication
• Production-style backend separation

This forms the foundation for:

Market Intelligence → Regime Detection → Strategy Engine → Risk Layer → Surveillance

---

# 🔜 Next Phase (Day 3 Preview)

* Background market engine (single loop, multi-client broadcast)
* Volatility metrics
* Trend detection
* Regime classification engine
* Strategy signal scaffolding

---

# 🚀 Current Status

AETHERION Backend
Day 1: COMPLETE
Day 2: COMPLETE

Live market engine operational.
