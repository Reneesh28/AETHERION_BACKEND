# 🧠 AETHERION — Backend Architecture

## Day 1: System Bootstrap (MVP Foundation)

---

## 🎯 Objective

Boot a production-style multi-service backend where:

* Django connects to MySQL
* FastAPI connects to MongoDB
* Flask runs independently
* Services communicate via REST
* Each service runs on a separate port

Day 1 goal: Everything runs without errors.

---

# 🏗 System Architecture

Django Core (Port 8000) → MySQL (3306)
FastAPI Market (Port 8001) → MongoDB (27017)
Flask Regime (Port 8002)

FastAPI → Flask (REST Communication)

This establishes a real microservice-style backend separation.

---

# 📂 Project Structure

AETHERION_BACKEND/
│
├── django_core/        # Django + MySQL (Control Tower)
├── fastapi_market/     # FastAPI + MongoDB (Async Market Engine)
├── flask_regime/       # Flask (Regime Engine)
├── shared/             # Shared utilities (future use)
├── requirements.txt
├── .gitignore
└── README.md

---

# ⚙️ Environment Setup

## 1️⃣ Create Virtual Environment

python -m venv venv
venv\Scripts\activate

## 2️⃣ Install Dependencies

pip install -r requirements.txt

---

# 📦 requirements.txt

Django
Django REST framework
djangorestframework
fastapi
uvicorn
flask
mysqlclient
motor
python-dotenv
requests

---

# 🗄 Database Configuration

## MySQL

Create database:

CREATE DATABASE aetherion_core;

Apply Django migrations:

cd django_core
python manage.py migrate

Django ORM manages schema automatically.

---

## MongoDB

MongoDB runs locally as a Windows service on:

mongodb://localhost:27017

FastAPI connects using Motor (async MongoDB driver).

---

# ▶ Running the Services

## Django Core (Port 8000)

cd django_core
python manage.py runserver 8000

Health check:
[http://127.0.0.1:8000/health/](http://127.0.0.1:8000/health/)

---

## FastAPI Market (Port 8001)

cd fastapi_market
uvicorn main:app --port 8001 --reload

Health check:
[http://127.0.0.1:8001/health](http://127.0.0.1:8001/health)

---

## Flask Regime (Port 8002)

cd flask_regime
python app.py

Health check:
[http://127.0.0.1:8002/health](http://127.0.0.1:8002/health)

---

# 🔄 Inter-Service Communication Test

FastAPI calling Flask:

[http://127.0.0.1:8001/check-regime](http://127.0.0.1:8001/check-regime)

Expected response:

{"status":"flask_regime running"}

This confirms service-to-service REST communication.

---

# ✅ Day 1 Completion Checklist

✔ Django connected to MySQL
✔ FastAPI connected to MongoDB
✔ Flask running independently
✔ All services on separate ports
✔ Health endpoints operational
✔ FastAPI → Flask communication working

---

# 🧠 What Day 1 Achieved

You now have:

• Structured storage via MySQL (Django ORM)
• Async unstructured storage via MongoDB (Motor)
• Clean microservice separation
• REST-based inter-service communication
• Production-style backend foundation

This is the base layer for:
Market Intelligence → Regime Detection → Strategy Engine → Risk Layer

---

# 🔜 Day 2 Roadmap (Preview)

Day 2 will focus on:

1. Environment variable management (.env integration across services)
2. Internal API contracts between services
3. Standardized response schemas
4. Logging & structured error handling
5. Base service configuration layer
6. Preparing for deployment (Render / Railway fail-safe setup)

---

# 🚀 Status

AETHERION Backend — Day 1: COMPLETE
System Boot Success
