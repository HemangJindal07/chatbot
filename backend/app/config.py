# backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = "http://agenticqe.ai/v1"  # Your custom base URL
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str = "gcp-starter"
    
    # Models
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o-mini"

    # Chunking
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 200
    
    # Pinecone
    INDEX_NAME: str = "policy-docs"
    DIMENSION: int = 1536
    
    # Retrieval
    TOP_K_RESULTS: int = 5
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()