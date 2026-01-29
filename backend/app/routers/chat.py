# backend/app/routers/chat.py
from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse, HealthResponse
from app.services.chatbot import PolicyChatbot
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

# Initialize chatbot (singleton)
try:
    chatbot = PolicyChatbot()
    logger.info("Chatbot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize chatbot: {str(e)}")
    chatbot = None

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if chatbot is None:
        raise HTTPException(
            status_code=503, 
            detail="Chatbot service unavailable"
        )
    
    return {
        "status": "healthy",
        "message": "Policy Chatbot API is running"
    }

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint"""
    if chatbot is None:
        raise HTTPException(
            status_code=503, 
            detail="Chatbot service unavailable"
        )
    
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        response = chatbot.chat(
            user_query=request.message,
            conversation_id=request.conversation_id
        )
        logger.info("Chat response generated successfully")
        return response
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process chat request: {str(e)}"
        )