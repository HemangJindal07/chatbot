# backend/test_connection.py
"""
Test script to verify connection to custom OpenAI endpoint
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from openai import OpenAI
from app.config import get_settings

settings = get_settings()

def test_openai_connection():
    """Test connection to custom OpenAI endpoint"""
    print("Testing connection to custom OpenAI endpoint...")
    print(f"Base URL: {settings.OPENAI_BASE_URL}")
    
    try:
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        
        # Test chat completion
        print("\n1. Testing chat completion...")
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "user", "content": "Hello, this is a test message."}
            ],
            temperature=0.1
        )
        
        print(f"Chat completion successful!")
        print(f"Response: {response.choices[0].message.content}")
        
        # Test embeddings
        print("\n2. Testing embeddings generation...")
        embedding_response = client.embeddings.create(
            input=["Test text for embedding"],
            model=settings.EMBEDDING_MODEL
        )
        
        print(f"Embeddings generation successful!")
        print(f"Embedding dimension: {len(embedding_response.data[0].embedding)}")
        
        print("\nAll tests passed! Your custom OpenAI endpoint is working correctly.")
        return True
    
    except Exception as e:
        print(f"\nConnection test failed: {str(e)}")
        print("\nPlease check:")
        print("1. Your API key is correct")
        print("2. The base URL is accessible")
        print("3. The endpoint supports the required models")
        return False

if __name__ == "__main__":
    test_openai_connection()