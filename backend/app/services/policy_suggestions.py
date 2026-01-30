# backend/app/services/policy_suggestions.py
import os
from pypdf import PdfReader
from typing import List, Dict
from openai import OpenAI
from app.config import get_settings
import json
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class PolicySuggestionService:
    def __init__(self, pdf_folder: str = "./data/raw_pdfs"):
        self.pdf_folder = pdf_folder
        self.openai_client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        # Add Redis cache for 24-hour caching
        from app.services.redis_client import get_redis_cache
        self.cache = get_redis_cache()
    
    def extract_comprehensive_text_from_pdf(self, pdf_path: str, max_pages: int = None) -> Dict[str, str]:
        """
        Extract comprehensive text from a PDF document
        
        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to read (None = read all pages)
            
        Returns:
            Dict with filename, full_text, and metadata
        """
        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            pages_to_read = total_pages if max_pages is None else min(max_pages, total_pages)
            
            logger.info(f"📖 Reading {pages_to_read}/{total_pages} pages from {os.path.basename(pdf_path)}")
            
            full_text = []
            for i in range(pages_to_read):
                try:
                    page_text = reader.pages[i].extract_text()
                    if page_text and page_text.strip():
                        full_text.append(page_text.strip())
                except Exception as e:
                    logger.warning(f"⚠️ Could not read page {i+1}: {str(e)}")
                    continue
            
            combined_text = "\n\n".join(full_text)
            
            logger.info(f"✅ Extracted {len(combined_text)} characters from {os.path.basename(pdf_path)}")
            
            return {
                'filename': os.path.basename(pdf_path),
                'text': combined_text,
                'pages_read': pages_to_read,
                'total_pages': total_pages,
                'char_count': len(combined_text)
            }
        
        except Exception as e:
            logger.error(f"❌ Error reading PDF {pdf_path}: {str(e)}")
            return {
                'filename': os.path.basename(pdf_path),
                'text': '',
                'pages_read': 0,
                'total_pages': 0,
                'char_count': 0,
                'error': str(e)
            }
    
    def extract_all_pdfs_comprehensive(self, max_pdfs: int = 5) -> List[Dict[str, str]]:
        """
        Extract comprehensive text from all PDF files
        
        Args:
            max_pdfs: Maximum number of PDFs to process
            
        Returns:
            List of dicts containing PDF content and metadata
        """
        if not os.path.exists(self.pdf_folder):
            logger.error(f"❌ PDF folder not found: {self.pdf_folder}")
            return []
        
        pdf_files = sorted([f for f in os.listdir(self.pdf_folder) if f.endswith('.pdf')])
        
        if not pdf_files:
            logger.warning(f"⚠️ No PDF files found in {self.pdf_folder}")
            return []
        
        logger.info(f"📚 Found {len(pdf_files)} PDF files, processing up to {max_pdfs}")
        
        pdf_contents = []
        for filename in pdf_files[:max_pdfs]:
            pdf_path = os.path.join(self.pdf_folder, filename)
            content = self.extract_comprehensive_text_from_pdf(pdf_path, max_pages=None)  # Read ALL pages
            
            if content['char_count'] > 0:
                pdf_contents.append(content)
            else:
                logger.warning(f"⚠️ Skipping {filename} - no content extracted")
        
        logger.info(f"✅ Successfully processed {len(pdf_contents)} PDF files")
        return pdf_contents
    
    def create_structured_context(self, pdf_contents: List[Dict[str, str]], max_chars_per_doc: int = 4000) -> str:
        """
        Create a structured context from all PDF contents for LLM analysis
        
        Args:
            pdf_contents: List of PDF content dicts
            max_chars_per_doc: Maximum characters per document to include
            
        Returns:
            Structured text context
        """
        context_parts = []
        
        for idx, pdf_data in enumerate(pdf_contents, 1):
            filename = pdf_data['filename']
            text = pdf_data['text']
            pages = pdf_data['pages_read']
            
            # Truncate if too long, but smartly (try to keep complete sections)
            if len(text) > max_chars_per_doc:
                # Take beginning and end to capture intro and conclusion
                half = max_chars_per_doc // 2
                text_sample = text[:half] + "\n\n[...middle content omitted...]\n\n" + text[-half:]
            else:
                text_sample = text
            
            context_parts.append(f"""
============================================================
DOCUMENT {idx}: {filename}
Pages Read: {pages}
============================================================

{text_sample}

""")
        
        return "\n".join(context_parts)
    
    def generate_global_suggestions(self, num_suggestions: int = 5) -> List[Dict]:
        """
        Generate high-quality suggestions by comprehensively analyzing all policy documents
        
        Args:
            num_suggestions: Number of suggestions to generate (default: 5)
            
        Returns:
            List of suggestion dicts with question and category
        """
        # Check Redis cache first (24-hour cache)
        cache_key = f"global_suggestions_v2:{num_suggestions}"
        
        if self.cache.is_connected():
            cached = self.cache.get(cache_key)
            if cached:
                try:
                    cached_data = json.loads(cached) if isinstance(cached, str) else cached
                    suggestions = cached_data.get('suggestions', [])
                    if suggestions:
                        logger.info(f"✅ Returning {len(suggestions)} cached suggestions from Redis")
                        return suggestions
                except Exception as e:
                    logger.warning(f"⚠️ Cache parsing error: {str(e)}")
        
        logger.info(f"🚀 Starting comprehensive PDF analysis for {num_suggestions} suggestions...")
        
        # Extract comprehensive text from all PDFs
        pdf_contents = self.extract_all_pdfs_comprehensive(max_pdfs=5)
        
        if not pdf_contents:
            logger.error("❌ No PDF content extracted - cannot generate suggestions")
            raise Exception("No policy documents found or readable in the data folder")
        
        # Create structured context
        context = self.create_structured_context(pdf_contents, max_chars_per_doc=4000)
        
        # Create comprehensive prompt
        prompt = f"""You are an expert policy analyst analyzing company policy documents for TestingXperts. 

I have provided you with {len(pdf_contents)} complete policy documents. Your task is to generate the {num_suggestions} MOST IMPORTANT and FREQUENTLY ASKED questions that employees would realistically ask about these policies.

ANALYSIS REQUIREMENTS:
1. Read and understand ALL the policy documents provided below
2. Identify the most critical topics that employees need to know
3. Generate questions that are:
   - Simple and conversational (how real employees would ask)
   - Covering different policy areas (IT, HR, Security, Compliance, etc.)
   - Practical and relevant to daily work
   - Clear and specific (no vague terms)
4. Prioritize questions about:
   - Security and access policies (passwords, VPN, data protection)
   - HR policies (harassment, complaints, workplace conduct)
   - Compliance requirements (mandatory training, reporting)
   - Common employee concerns (remote work, email usage, etc.)

POLICY DOCUMENTS CONTENT:
{context}

Generate EXACTLY {num_suggestions} questions in this JSON format:
{{
    "suggestions": [
        {{"question": "What is the password policy?", "category": "IT Security"}},
        {{"question": "What is POSH?", "category": "Workplace Safety"}},
        {{"question": "How do I report harassment?", "category": "HR"}},
        ...
    ]
}}

CRITICAL: Return ONLY valid JSON, no explanation, no markdown formatting.
The questions must be based on the actual content of the documents provided above."""

        try:
            logger.info(f"🤖 Sending {len(context)} characters to LLM for analysis...")
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert policy analyst. You analyze company policy documents and generate the most relevant questions employees would ask. You ONLY return valid JSON format."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Low temperature for consistent, focused results
                max_tokens=800
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean up response - remove markdown formatting
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            # Parse JSON
            result = json.loads(response_text)
            suggestions = result.get('suggestions', [])
            
            if not suggestions:
                logger.error("❌ LLM returned empty suggestions")
                raise Exception("LLM failed to generate suggestions")
            
            # Validate and limit to requested number
            suggestions = suggestions[:num_suggestions]
            
            logger.info(f"✅ Successfully generated {len(suggestions)} high-quality suggestions")
            
            # Cache in Redis for 24 hours
            if self.cache.is_connected():
                cache_data = json.dumps({'suggestions': suggestions})
                self.cache.client.setex(cache_key, 86400, cache_data)  # 24 hours
                logger.info(f"💾 Cached suggestions in Redis for 24 hours")
            
            return suggestions
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {str(e)}")
            logger.error(f"Response was: {response_text[:500]}")
            raise Exception(f"Failed to parse LLM response as JSON: {str(e)}")
        
        except Exception as e:
            logger.error(f"❌ Error generating suggestions: {str(e)}")
            raise Exception(f"Failed to generate policy suggestions: {str(e)}")