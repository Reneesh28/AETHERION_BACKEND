from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import requests

app = FastAPI()

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.aetherion_market

@app.get("/health")
async def health():
    await db.test.insert_one({"check": "ok"})
    return {"status": "fastapi_market running"}

@app.get("/check-regime")
def check_regime():
    response = requests.get("http://localhost:8002/health")
    return response.json()