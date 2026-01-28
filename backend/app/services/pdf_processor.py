# backend/app/services/pdf_processor.py
import os
from pypdf import PdfReader
from typing import List, Dict

class PDFProcessor:
    def __init__(self, pdf_folder: str):
        self.pdf_folder = pdf_folder
        
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract text from PDF with metadata"""
        reader = PdfReader(pdf_path)
        documents = []
        filename = os.path.basename(pdf_path)
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():
                documents.append({
                    'text': text,
                    'metadata': {
                        'source': filename,
                        'page': page_num + 1,
                        'total_pages': len(reader.pages)
                    }
                })
        return documents
    
    def process_all_pdfs(self) -> List[Dict]:
        """Process all PDFs in folder"""
        all_documents = []
        pdf_files = [f for f in os.listdir(self.pdf_folder) if f.endswith('.pdf')]
        
        for filename in pdf_files:
            pdf_path = os.path.join(self.pdf_folder, filename)
            docs = self.extract_text_from_pdf(pdf_path)
            all_documents.extend(docs)
        
        return all_documents