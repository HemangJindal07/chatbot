# backend/app/services/text_chunker.py
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import get_settings

settings = get_settings()

class TextChunker:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """Split documents into chunks with metadata"""
        chunked_docs = []
        
        for doc in documents:
            chunks = self.text_splitter.split_text(doc['text'])
            
            for i, chunk in enumerate(chunks):
                chunked_docs.append({
                    'text': chunk,
                    'metadata': {
                        **doc['metadata'],
                        'chunk_id': i,
                        'total_chunks': len(chunks)
                    }
                })
        
        return chunked_docs