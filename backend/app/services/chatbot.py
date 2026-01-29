# backend/app/services/chatbot.py
from openai import OpenAI
from app.services.vector_store import PineconeVectorStore
from app.config import get_settings
from typing import Dict
import uuid

settings = get_settings()

class PolicyChatbot:
    def __init__(self):
        # Initialize OpenAI with custom base URL
        self.openai_client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        
        self.vector_store = PineconeVectorStore()
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        return """You are a Policy Compliance Assistant for TestingXperts. Your job is to answer questions STRICTLY based on the provided policy documents.

CRITICAL RULES:
1.GREETINGS: If the user says "hello", "hi", "thanks", or similar social pleasantries, reply politely and professionally. You do NOT need context for this.
2. ONLY use information from the Context provided below
3. If the answer is not in the Context, respond: "I don't have information about this in our policy documents. Please contact [HR/IT/relevant department] for clarification."
4. When a user asks to do something against policy, clearly state: "This action violates [Policy Name, Section X]" and explain why
5. Always cite the specific policy document, section, and page number
6. Never make assumptions or use general knowledge
7. If policy is ambiguous, indicate uncertainty and cite the relevant section

Format your response as:
- Direct answer to the question
- Citation: [Document Name, Section X, Page Y]
- Confidence level if applicable

Remember: You represent TestingXperts' official policies. Accuracy is critical."""
    
    def _format_context(self, search_results: Dict) -> str:
        """Format search results into context"""
        context_parts = []
        matches = search_results.get('matches', [])
        
        for i, match in enumerate(matches):
            metadata = match['metadata']
            text = metadata.get('text', '')
            source = metadata.get('source', 'Unknown')
            page = metadata.get('page', 'Unknown')
            
            context_parts.append(
                f"[Source {i+1}: {source}, Page {page}]\n{text}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def chat(self, user_query: str, conversation_id: str = None) -> Dict:
        """Main chat function"""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        print(f"\nProcessing query: {user_query}")
        
        try:
            # Step 1: Retrieve relevant documents
            search_results = self.vector_store.search(
                user_query, 
                top_k=settings.TOP_K_RESULTS
            )
            
            # Step 2: Format context
            context = self._format_context(search_results)
            
            if not context.strip():
                return {
                    'answer': "I couldn't find any relevant information in the policy documents. Please contact the appropriate department for assistance.",
                    'sources': [],
                    'conversation_id': conversation_id
                }
            
            # Step 3: Create prompt
            user_prompt = f"""Context from Policy Documents:
{context}

User Question: {user_query}

Please provide an accurate answer based only on the context above. Include proper citations."""
            
            # Step 4: Get response from OpenAI (using custom base URL)
            print("Generating response from custom OpenAI endpoint...")
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            
            answer = response.choices[0].message.content
            print("Response generated successfully")
            
            # Step 5: Extract sources (commented out)
            # sources = [
            #     {
            #         'source': match['metadata'].get('source', 'Unknown'),
            #         'page': match['metadata'].get('page', 'Unknown'),
            #         'score': match['score']
            #     }
            #     for match in search_results.get('matches', [])
            # ]
            
            return {
                'answer': answer,
                # 'sources': sources,
                'sources': [],  # Sources disabled
                'conversation_id': conversation_id
            }
        
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            raise