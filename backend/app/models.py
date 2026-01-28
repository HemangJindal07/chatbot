# backend/app/models.py
from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

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