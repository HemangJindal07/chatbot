# # backend/app/services/policy_suggestions.py
# import os
# from pypdf import PdfReader
# from typing import List, Dict
# from openai import OpenAI
# from app.config import get_settings
# import json

# settings = get_settings()

# class PolicySuggestionService:
#     def __init__(self, pdf_folder: str = "./data/raw_pdfs"):
#         self.pdf_folder = pdf_folder
#         self.openai_client = OpenAI(
#             api_key=settings.OPENAI_API_KEY,
#             base_url=settings.OPENAI_BASE_URL
#         )
    
#     def get_available_policies(self) -> List[Dict]:
#         """Get list of all available PDF policies"""
#         policies = []
        
#         if not os.path.exists(self.pdf_folder):
#             return policies
        
#         pdf_files = [f for f in os.listdir(self.pdf_folder) if f.endswith('.pdf')]
        
#         # Icon mapping based on keywords in filename
#         icon_mapping = {
#             'IT': '',
#             'POSH': '',
#             'Sexual': '',
#             'Harassment': '',
#             'HR': '',
#             'Security': '',
#             'Data': '',
#             'Password': '',
#             'Network': '',
#             'Cloud': '',
#             'Email': '',
#             'VPN': '',
#             'Access': '',
#             'Mobile': '',
#             'Compliance': '',
#             'Privacy': '',
#         }
        
#         for filename in pdf_files:
#             # Determine icon based on filename keywords
#             icon = ''  # Default icon
#             for keyword, emoji in icon_mapping.items():
#                 if keyword.lower() in filename.lower():
#                     icon = emoji
#                     break
            
#             # Clean filename for display
#             display_name = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
            
#             policies.append({
#                 'filename': filename,
#                 'display_name': display_name,
#                 'icon': icon,
#                 'path': os.path.join(self.pdf_folder, filename)
#             })
        
#         return policies
    
#     def extract_text_sample_from_pdf(self, pdf_path: str, max_pages: int = 5) -> str:
#         """Extract text from first few pages to understand document content"""
#         try:
#             reader = PdfReader(pdf_path)
#             text_sample = ""
            
#             # Get text from first N pages (or all if less than N)
#             pages_to_read = min(max_pages, len(reader.pages))
            
#             for i in range(pages_to_read):
#                 page_text = reader.pages[i].extract_text()
#                 text_sample += page_text + "\n"
            
#             # Limit to ~3000 characters to avoid token limits
#             return text_sample[:3000]
        
#         except Exception as e:
#             print(f"Error extracting text from {pdf_path}: {str(e)}")
#             return ""
    
#     def generate_suggestions_with_ai(self, filename: str, text_sample: str, max_suggestions: int = 4) -> List[Dict]:
#         """Use AI to generate natural, relevant questions from document content"""
        
#         prompt = f"""You are analyzing a policy document. Based on the content below, generate {max_suggestions} natural questions that a user might ask about this policy.

# REQUIREMENTS:
# 1. Questions should be simple and conversational (like "What is ICC?", "What is the password policy?")
# 2. Questions should cover the MAIN topics in this document
# 3. Questions should be clear and specific to this policy
# 4. Do NOT use vague terms like "Removed", "MR A", or incomplete sentences
# 5. Focus on the most important/useful information users would want to know

# Document Title: {filename}

# Document Content Sample:
# {text_sample}

# Generate exactly {max_suggestions} questions in this JSON format:
# {{
#     "suggestions": [
#         {{"question": "What is the password policy?", "topic": "Password Security"}},
#         {{"question": "What is ICC?", "topic": "Internal Complaints Committee"}},
#         ...
#     ]
# }}

# Return ONLY the JSON, no explanation."""

#         try:
#             print(f"Generating AI suggestions for: {filename}")
            
#             response = self.openai_client.chat.completions.create(
#                 model=settings.LLM_MODEL,
#                 messages=[
#                     {
#                         "role": "system", 
#                         "content": "You are a helpful assistant that analyzes policy documents and generates clear, natural questions users might ask."
#                     },
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.3,  # Low temperature for consistent results
#                 max_tokens=500
#             )
            
#             response_text = response.choices[0].message.content.strip()
            
#             # Remove markdown code blocks if present
#             if response_text.startswith("```json"):
#                 response_text = response_text.replace("```json", "").replace("```", "").strip()
#             elif response_text.startswith("```"):
#                 response_text = response_text.replace("```", "").strip()
            
#             # Parse JSON response
#             result = json.loads(response_text)
#             suggestions = result.get('suggestions', [])
            
#             print(f"Generated {len(suggestions)} suggestions")
#             return suggestions
        
#         except Exception as e:
#             print(f"Error generating AI suggestions: {str(e)}")
#             # Fallback to generic suggestions
#             return self._generate_generic_suggestions(filename)
    
#     def generate_suggestions(self, filename: str, max_suggestions: int = 4) -> List[Dict]:
#         """Generate suggestion questions using AI analysis"""
#         pdf_path = os.path.join(self.pdf_folder, filename)
        
#         if not os.path.exists(pdf_path):
#             return []
        
#         # Extract text sample from PDF
#         text_sample = self.extract_text_sample_from_pdf(pdf_path, max_pages=5)
        
#         if not text_sample or len(text_sample) < 100:
#             # If we can't extract enough text, use generic suggestions
#             return self._generate_generic_suggestions(filename)
        
#         # Use AI to generate contextual suggestions
#         return self.generate_suggestions_with_ai(filename, text_sample, max_suggestions)
    
#     def _generate_generic_suggestions(self, filename: str) -> List[Dict]:
#         """Generate generic suggestions if AI fails or PDF can't be read"""
#         display_name = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
        
#         # Smart generic suggestions based on filename
#         if 'posh' in filename.lower() or 'harassment' in filename.lower():
#             return [
#                 {'question': 'What is POSH?', 'topic': 'Policy Overview'},
#                 {'question': 'What is ICC?', 'topic': 'Internal Complaints Committee'},
#                 {'question': 'How to file a complaint?', 'topic': 'Complaint Process'},
#                 {'question': 'What are the penalties for violations?', 'topic': 'Enforcement'},
#             ]
#         elif 'it' in filename.lower() or 'security' in filename.lower():
#             return [
#                 {'question': 'What is the password policy?', 'topic': 'Password Security'},
#                 {'question': 'What is the VPN policy?', 'topic': 'VPN Access'},
#                 {'question': 'What is the email usage policy?', 'topic': 'Email Guidelines'},
#                 {'question': 'What is the data security policy?', 'topic': 'Data Protection'},
#             ]
#         else:
#             return [
#                 {'question': f'What is the {display_name}?', 'topic': 'Overview'},
#                 {'question': f'What are the key requirements?', 'topic': 'Requirements'},
#                 {'question': f'Who does this policy apply to?', 'topic': 'Scope'},
#                 {'question': f'What are the consequences of violations?', 'topic': 'Enforcement'},
#             ]


# backend/app/services/policy_suggestions.py
import os
from pypdf import PdfReader
from typing import List, Dict
from openai import OpenAI
from app.config import get_settings
import json

settings = get_settings()

class PolicySuggestionService:
    def __init__(self, pdf_folder: str = "./data/raw_pdfs"):
        self.pdf_folder = pdf_folder
        self.openai_client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    def extract_text_from_all_pdfs(self, max_chars_per_pdf: int = 2000) -> str:
        """Extract text samples from all PDFs to understand available policies"""
        all_text = []
        
        if not os.path.exists(self.pdf_folder):
            return ""
        
        pdf_files = [f for f in os.listdir(self.pdf_folder) if f.endswith('.pdf')]
        
        for filename in pdf_files[:5]:  # Process up to 5 PDFs
            pdf_path = os.path.join(self.pdf_folder, filename)
            try:
                reader = PdfReader(pdf_path)
                text_sample = ""
                
                # Get text from first 3 pages
                for i in range(min(3, len(reader.pages))):
                    page_text = reader.pages[i].extract_text()
                    text_sample += page_text + "\n"
                
                # Add document title and sample
                all_text.append(f"Document: {filename}\n{text_sample[:max_chars_per_pdf]}")
            
            except Exception as e:
                print(f"Error reading {filename}: {str(e)}")
                continue
        
        return "\n\n---\n\n".join(all_text)
    
    def generate_global_suggestions(self, num_suggestions: int = 5) -> List[Dict]:
        """Generate 4-5 most common/useful questions across all policy documents"""
        
        # Extract content from all PDFs
        all_content = self.extract_text_from_all_pdfs()
        
        if not all_content or len(all_content) < 100:
            # Fallback to common policy questions
            return self._get_common_policy_questions(num_suggestions)
        
        prompt = f"""You are analyzing multiple company policy documents. Based on the content below, generate {num_suggestions} of the MOST FREQUENTLY ASKED questions that employees would ask about company policies.

REQUIREMENTS:
1. Questions should be simple, conversational, and commonly asked (like "What is the password policy?", "Can I work from home?")
2. Focus on the MOST COMMON employee concerns across all policies
3. Questions should be practical and useful for day-to-day work
4. Cover different policy areas (IT, HR, Security, etc.)
5. Make questions natural - how real employees would ask

Policy Documents Content:
{all_content[:8000]}

Generate exactly {num_suggestions} questions in this JSON format:
{{
    "suggestions": [
        {{"question": "What is the password policy?", "category": "IT Security"}},
        {{"question": "Can I work from home?", "category": "Remote Work"}},
        {{"question": "What is POSH?", "category": "Workplace Safety"}},
        ...
    ]
}}

Return ONLY the JSON, no explanation."""

        try:
            print(f"🤖 Generating {num_suggestions} global suggestions from all policies...")
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant that understands company policies and generates the most commonly asked employee questions."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean up response
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            # Parse JSON
            result = json.loads(response_text)
            suggestions = result.get('suggestions', [])
            
            print(f"✅ Generated {len(suggestions)} global suggestions")
            return suggestions[:num_suggestions]
        
        except Exception as e:
            print(f"❌ Error generating global suggestions: {str(e)}")
            return self._get_common_policy_questions(num_suggestions)
    
    def _get_common_policy_questions(self, num_suggestions: int = 5) -> List[Dict]:
        """Fallback common policy questions"""
        common_questions = [
            {'question': 'What is the password policy?', 'category': 'IT Security'},
            {'question': 'What is POSH?', 'category': 'Workplace Safety'},
            {'question': 'Can I work from home?', 'category': 'Remote Work'},
            {'question': 'What is the VPN policy?', 'category': 'Network Access'},
            {'question': 'How do I report harassment?', 'category': 'HR'},
            {'question': 'What is the email usage policy?', 'category': 'IT Policy'},
            {'question': 'What is the data security policy?', 'category': 'Security'},
        ]
        return common_questions[:num_suggestions]