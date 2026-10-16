from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import BUSINESS_DB
from app.db import app_db, seed
from app.routes import chat, data


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not BUSINESS_DB.exists():
        seed.seed()
    app_db.init()
    yield


app = FastAPI(title="SQL Chatbot API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"],
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(chat.router, prefix="/api")
app.include_router(data.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
