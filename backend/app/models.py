# backend/app/models.py
from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    content: str
    isUser: bool
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    conversation_history: Optional[List[Message]] = []  # NEW: Conversation history

class Source(BaseModel):
    source: str
    page: int
    score: float

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    conversation_id: str

class HealthResponse(BaseModel):
    status: str
    message: str