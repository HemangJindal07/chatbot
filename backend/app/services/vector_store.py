# backend/app/services/vector_store.py
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from typing import List, Dict
from app.config import get_settings
import time

settings = get_settings()

class PineconeVectorStore:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Initialize OpenAI with custom base URL
        self.openai_client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        
        self.index = self._get_or_create_index()
    
    def _get_or_create_index(self):
        """Create Pinecone index if it doesn't exist"""
        index_name = settings.INDEX_NAME
        
        if index_name not in self.pc.list_indexes().names():
            print(f"Creating new Pinecone index: {index_name}")
            
            self.pc.create_index(
                name=index_name,
                dimension=settings.DIMENSION,
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
            
            while not self.pc.describe_index(index_name).status['ready']:
                print("Waiting for index to be ready...")
                time.sleep(1)
            
            print("Index created successfully!")
        else:
            print(f"Connected to existing index: {index_name}")
        
        return self.pc.Index(index_name)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI with custom base URL"""
        print(f"Generating embeddings for {len(texts)} texts...")
        
        batch_size = 2048
        all_embeddings = []
        
        try:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = self.openai_client.embeddings.create(
                    input=batch,
                    model=settings.EMBEDDING_MODEL
                )
                
                embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(embeddings)
                print(f"   Processed {len(all_embeddings)}/{len(texts)}")
        
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            raise
        
        return all_embeddings
    
    def add_documents(self, chunks: List[Dict]):
        """Add chunked documents to Pinecone"""
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Prepare vectors for upsert
        vectors = []
        for i, (embedding, text, metadata) in enumerate(zip(embeddings, texts, metadatas)):
            vectors.append({
                'id': f"doc_{i}",
                'values': embedding,
                'metadata': {**metadata, 'text': text}
            })
        
        # Upsert in batches
        batch_size = 100
        print(f"\nUploading {len(vectors)} vectors to Pinecone...")
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            print(f"   Uploaded {min(i + batch_size, len(vectors))}/{len(vectors)}")
        
        print("All vectors uploaded successfully!")
    
    def search(self, query: str, top_k: int = 5) -> Dict:
        """Search for relevant documents"""
        try:
            # Generate query embedding
            query_embedding = self.generate_embeddings([query])[0]
            
            # Search
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return results
        
        except Exception as e:
            print(f"Error searching: {str(e)}")
            raise