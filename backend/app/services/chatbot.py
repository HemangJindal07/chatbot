# backend/app/services/chatbot.py
from openai import OpenAI
from app.services.vector_store import PineconeVectorStore
from app.config import get_settings
from typing import Dict, List
import uuid

settings = get_settings()

class PolicyChatbot:
    def __init__(self):
        self.openai_client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.vector_store = PineconeVectorStore()
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        return """You are a Policy Compliance Assistant for TestingXperts. Answer questions STRICTLY based on provided policy documents and conversation history.

CRITICAL RULES:
1. ONLY use information from the Context provided
2. Check conversation history to understand "it", "this", "that" references
3. When user asks "where did I ask about X?", verify in conversation history
4. If answer not in Context: "I don't have information about this in our policy documents."


RESPONSE FORMAT (MANDATORY):
- ALWAYS use bullet points (•) 
- NO paragraphs or long text
- Be EXTREMELY CONCISE

ANSWER TYPES:

1. SIMPLE QUESTIONS (which page, what section, who, when, etc.):
   → Give DIRECT answer in 1 bullet point only
   
   Example:
   User: "On which page is it?"
   Response:
   • Page 5 of POSH Policy

2. WHAT/EXPLAIN QUESTIONS (what is X, explain Y, etc.):
   → Brief intro (1 line) + 3-5 key bullet points
   
   Example:
   User: "What is POSH?"
   Response:
   POSH protects women from workplace sexual harassment.
   
   • Enacted in 2013 by Parliament of India
   • Mandates Internal Complaints Committee (ICC)
   • Covers prevention, prohibition, and redressal
   • Applies to all workplaces
   

3. HOW/PROCESS QUESTIONS (how to X, process for Y):
   → Steps in bullet points
   
   Example:
   User: "How to file a complaint?"
   Response:
   Complaint Filing Process:
   
   • Submit written complaint to ICC
   • Include details of incident
   • Provide supporting evidence if available
   • ICC will investigate within 90 days
   

FOLLOW-UP QUESTION HANDLING:
- "on which page?" → Check previous message, state page only
- "what section?" → Check previous message, state section only
- "references?" → List references from previous topic
- "where did I ask?" → Check conversation history, answer truthfully

FORMATTING RULES:
✓ Always use bullets (•)
✓ Each bullet = ONE key point
✓ Maximum 5 bullets for complex answers
✓ Maximum 1 bullet for simple questions

NEVER:
✗ Write long paragraphs
✗ Repeat information
✗ Add unnecessary details
✗ Use multiple sentences per bullet"""
    
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
    
    def _format_conversation_history(self, messages: List) -> str:
        """Format conversation history for context"""
        if not messages:
            return ""
        
        history = ["=== CONVERSATION HISTORY (Most Recent Last) ==="]
        
        for msg in messages:
            if hasattr(msg, 'isUser'):
                role = "USER" if msg.isUser else "ASSISTANT"
                content = msg.content
            elif isinstance(msg, dict):
                role = "USER" if msg.get('isUser') else "ASSISTANT"
                content = msg.get('content', '')
            else:
                continue
            
            history.append(f"\n{role}: {content}")
        
        history.append("\n=== END OF CONVERSATION HISTORY ===\n")
        return "\n".join(history)
    
    def _is_simple_question(self, query: str) -> bool:
        """Detect if question needs only a short direct answer"""
        simple_keywords = [
            'which page', 'what page', 'on which page', 'page number',
            'which section', 'what section', 'where is it', 
            'who', 'when', 'how many', 'how much'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in simple_keywords)
    
    def _is_followup_question(self, query: str) -> bool:
        """Detect if question is a follow-up requiring conversation context"""
        followup_keywords = [
            'it', 'this', 'that', 'which page', 'what page', 'reference', 
            'where', 'how', 'why', 'when did i', 'where did i', 'what did i',
            'tell me more', 'explain', 'clarify', 'elaborate', 'details'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in followup_keywords)
    
    def chat(self, user_query: str, conversation_id: str = None, conversation_history: List = None) -> Dict:
        """Main chat function with conversation history support"""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        print(f"\nProcessing query: {user_query}")
        print(f"Conversation history length: {len(conversation_history) if conversation_history else 0}")
        
        try:
            # Detect question type
            is_simple = self._is_simple_question(user_query)
            is_followup = self._is_followup_question(user_query)
            
            print(f"Question type - Simple: {is_simple}, Follow-up: {is_followup}")
            
            # For follow-up questions, use previous context
            if is_followup and conversation_history and len(conversation_history) >= 2:
                last_messages = conversation_history[-2:]
                last_topic = ""
                for msg in last_messages:
                    if hasattr(msg, 'content'):
                        last_topic += msg.content + " "
                    elif isinstance(msg, dict):
                        last_topic += msg.get('content', '') + " "
                
                search_query = f"{last_topic} {user_query}"
                print(f"Enhanced search query: {search_query[:100]}...")
            else:
                search_query = user_query
            
            # Retrieve relevant documents
            search_results = self.vector_store.search(
                search_query, 
                top_k=settings.TOP_K_RESULTS
            )
            
            # Format context from documents
            document_context = self._format_context(search_results)
            
            if not document_context.strip():
                return {
                    'answer': "• I don't have information about this in our policy documents.\n\nPlease contact the appropriate department for assistance.",
                    'sources': [],
                    'conversation_id': conversation_id
                }
            
            # Format conversation history
            history_context = ""
            if conversation_history and len(conversation_history) > 0:
                history_context = self._format_conversation_history(conversation_history)
                print(f"Including conversation history with {len(conversation_history)} messages")
            
            # Create prompt based on question type
            if is_simple and is_followup:
                # Simple follow-up (e.g., "which page?")
                user_prompt = f"""{history_context}

Context from Policy Documents:
{document_context}

Current User Question: {user_query}

This is a SIMPLE FOLLOW-UP question. Look at the conversation history to understand what the user is asking about.

Provide ONLY:
- Direct answer no bullet point just the information requested

Example:
Page 5 of POSH Policy


DO NOT add extra information. Just the direct answer."""

            elif is_followup:
                # Complex follow-up
                user_prompt = f"""{history_context}

Context from Policy Documents:
{document_context}

Current User Question: {user_query}

This is a FOLLOW-UP question. Check conversation history to understand context.

Format:
Brief intro (1 line)

- Key point 1
- Key point 2
- Key point 3
(Maximum 5 bullets)
"""

            else:
                # New question
                user_prompt = f"""{history_context}

Context from Policy Documents:
{document_context}

Current User Question: {user_query}

Format your answer in BULLET POINTS only:
Brief intro (1 line if needed)

- Key point 1
- Key point 2
- Key point 3
(Maximum 5 bullets)"""
            
            # Get response from OpenAI
            print("Generating bullet-formatted response...")
            
            response = self.openai_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=400
            )
            
            answer = response.choices[0].message.content
            print("Response generated successfully")
            
            # Extract sources
            sources = [
                {
                    'source': match['metadata'].get('source', 'Unknown'),
                    'page': match['metadata'].get('page', 'Unknown'),
                    'score': match['score']
                }
                for match in search_results.get('matches', [])
            ]
            
            return {
                'answer': answer,
                'sources': sources,
                'conversation_id': conversation_id
            }
        
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise