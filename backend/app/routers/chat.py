# backend/app/routers/chat.py
from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse, HealthResponse
from app.services.chatbot import PolicyChatbot
from app.services.policy_suggestions import PolicySuggestionService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

# Initialize services
try:
    chatbot = PolicyChatbot()
    suggestion_service = PolicySuggestionService()
    logger.info("Chatbot and Suggestion Service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    chatbot = None
    suggestion_service = None

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

@router.get("/suggestions")
async def get_suggestions(num: int = 5):
    """Get AI-generated smart suggestions from all policies"""
    if suggestion_service is None:
        raise HTTPException(
            status_code=503,
            detail="Suggestion service unavailable"
        )
    
    try:
        logger.info(f"Generating {num} global suggestions...")
        suggestions = suggestion_service.generate_global_suggestions(num_suggestions=num)
        
        if not suggestions:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate suggestions - no content extracted from PDFs"
            )
        
        return {
            "suggestions": suggestions,
            "count": len(suggestions)
        }
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate suggestions: {str(e)}"
        )

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with conversation history support"""
    if chatbot is None:
        raise HTTPException(
            status_code=503, 
            detail="Chatbot service unavailable"
        )
    
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        logger.info(f"Conversation history: {len(request.conversation_history) if request.conversation_history else 0} messages")
        
        response = chatbot.chat(
            user_query=request.message,
            conversation_id=request.conversation_id,
            conversation_history=request.conversation_history or []
        )
        
        logger.info("Chat response generated successfully")
        return response
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process chat request: {str(e)}"
        )