# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Policy Chatbot API",
    description="API for TestingXperts Policy Compliance Chatbot",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)

@app.get("/")
async def root():
    return {
        "message": "Policy Chatbot API",
        "docs": "/docs",
        "health": "/api/health"
    }