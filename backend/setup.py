# backend/setup.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.services.pdf_processor import PDFProcessor
from app.services.text_chunker import TextChunker
from app.services.vector_store import PineconeVectorStore
from test_connection import test_openai_connection

def main():
    print("Starting Policy Chatbot Setup\n")
    
    # Test connection first
    print("="*60)
    print("STEP 0: Testing Custom OpenAI Endpoint Connection")
    print("="*60)
    if not test_openai_connection():
        print("\nSetup aborted due to connection failure.")
        return
    
    print("\n" + "="*60)
    print("STEP 1: Processing PDF Documents")
    print("="*60)
    processor = PDFProcessor("./data/raw_pdfs")
    docs = processor.process_all_pdfs()
    
    if not docs:
        print("No documents found. Add PDFs to ./data/raw_pdfs/")
        return
    
    print(f"Processed {len(docs)} pages")
    
    print("\n" + "="*60)
    print("STEP 2: Chunking Documents")
    print("="*60)
    chunker = TextChunker()
    chunks = chunker.chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")
    
    print("\n" + "="*60)
    print("STEP 3: Uploading to Pinecone")
    print("="*60)
    vector_store = PineconeVectorStore()
    vector_store.add_documents(chunks)
    
    print("\n" + "="*60)
    print("STEP 4: Testing Search")
    print("="*60)
    test_query = "What is the password policy?"
    print(f"Test query: {test_query}")
    results = vector_store.search(test_query)
    
    if results['matches']:
        print(f"Search test successful! Found {len(results['matches'])} results")
        print(f"\nTop result preview:")
        print(results['matches'][0]['metadata']['text'][:200] + "...")
    else:
        print("No results found. Please check your setup.")
    
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start backend: uvicorn app.main:app --reload --port 8000")
    print("2. Start frontend: cd frontend && npm run dev")

if __name__ == "__main__":
    main()