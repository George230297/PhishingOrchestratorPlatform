from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(title="Phishing Simulator API")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Phishing Simulator Backend is running", "env": settings.POSTGRES_DB}
