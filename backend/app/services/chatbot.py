# backend/app/services/chatbot.py
from openai import OpenAI
from app.services.vector_store import PineconeVectorStore
from app.services.redis_client import get_redis_cache
from app.config import get_settings
from typing import Dict, List
import uuid
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class PolicyChatbot:
    def __init__(self):
        self.openai_client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.vector_store = PineconeVectorStore()
        self.cache = get_redis_cache()
        self.system_prompt = self._create_system_prompt()
    
#     def _create_system_prompt(self) -> str:
#         return """You are a Policy Compliance Assistant for TestingXperts. Answer questions STRICTLY based on provided policy documents and conversation history.
# GREETINGS: If the user says "hello", "hi", "thanks", or similar social pleasantries, reply politely and professionally. You do NOT need context for this.
# CRITICAL RULES:
# 1. ONLY use information from the Context provided
# 2. Check conversation history to understand "it", "this", "that" references
# 3. When user asks "where did I ask about X?", verify in conversation history
# 4. If answer not in Context: "I don't have information about this in our policy documents."
# 5. if the user asks any vague question example how are you, tell me a joke, what is your name, etc. respond with proper answer fetched from the llm

# RESPONSE FORMAT (MANDATORY):
# - ALWAYS use bullet points (•) 
# - NO paragraphs or long text
# - Be EXTREMELY CONCISE

# ANSWER TYPES:

# 1. SIMPLE QUESTIONS (which page, what section, who, when, etc.):
#    → Give DIRECT answer in 1 bullet point only
   
#    Example:
#    User: "On which page is it?"
#    Workaround for you should be check the session history to find the previous topic discussed.
#    if found then respond with the page number only else respond with "I don't have information about this in our policy documents."
#    Response:
#    • Page 5 of POSH Policy 

# 2. WHAT/EXPLAIN QUESTIONS (what is X, explain Y, etc.):
#    → Brief intro (1 line) + 3-5 key bullet points
   
#    Example:
#    User: "What is POSH?"
#    Response:
#    POSH protects women from workplace sexual harassment.
   
#    • Enacted in 2013 by Parliament of India
#    • Mandates Internal Complaints Committee (ICC)
#    • Covers prevention, prohibition, and redressal
#    • Applies to all workplaces
   

# 3. HOW/PROCESS QUESTIONS (how to X, process for Y):
#    → Steps in bullet points
   
#    Example:
#    User: "How to file a complaint?"
#    Response:
#    Complaint Filing Process:
   
#    • Submit written complaint to ICC
#    • Include details of incident
#    • Provide supporting evidence if available
#    • ICC will investigate within 90 days
   

# FOLLOW-UP QUESTION HANDLING:
# - "on which page?" → Check previous message, state page only
# - "what section?" → Check previous message, state section only
# - "references?" → List references from previous topic
# - "where did I ask?" → Check conversation history, answer truthfully

# FORMATTING RULES:
# ✓ Always use bullets (•)
# ✓ Each bullet = ONE key point
# ✓ Maximum 5 bullets for complex answers
# ✓ Maximum 1 bullet for simple questions

# NEVER:
# ✗ Write long paragraphs
# ✗ Repeat information
# ✗ Add unnecessary details
# ✗ Use multiple sentences per bullet"""

    def _create_system_prompt(self) -> str:
        return """You are a Policy Compliance Assistant for TestingXperts. Answer questions STRICTLY based on provided policy documents and conversation history.

    GREETINGS: If the user says "hello", "hi", "thanks", or similar social pleasantries, reply politely and professionally. You do NOT need context for this.

    DOCUMENT LOCATION QUERIES:
    When users ask WHERE to find documents, HOW to access policies, or WHERE policies are located, respond with:
    "You can access all company policy documents through the Sahyog Portal. Please navigate to the Policies section to view and download the complete documents."

    Trigger phrases for this response:
    - "Where can I find this document?"
    - "How do I access this policy?"
    - "Where is this document located?"
    - "Can I download this policy?"
    - "Where are the policies stored?"
    - "How to access the full document?"
    - "Where can I read the complete policy?"

    CRITICAL RULES:
    1. ONLY use information from the Context provided for policy content questions
    2. Check conversation history to understand "it", "this", "that" references
    3. When user asks "where did I ask about X?", verify in conversation history
    4. If answer not in Context: "I don't have information about this in our policy documents."
    5. If the user asks any vague question (how are you, tell me a joke, what is your name), respond appropriately and professionally

    RESPONSE FORMAT RULES:

    TYPE 1: SIMPLE DIRECT ANSWERS (page numbers, yes/no, single facts)
    → NO bullet points needed
    → Just state the answer naturally

    Examples:
    Q: "On which page is it?"
    A: Page 5 of POSH Policy

    Q: "Where can i reference it from the document?"
    A: Page 5 of POSH Policy

    Q: "Is this correct?"
    A: Yes, that information is accurate based on the policy documents.

    Q: "Who handles complaints?"
    A: The Internal Complaints Committee (ICC) handles all sexual harassment complaints.

    TYPE 2: POLICY EXPLANATIONS (What is X? Explain Y)
    → USE bullet points for policy details
    → Brief intro + bullet points for key information

    Examples:
    Q: "What is POSH?"
    A: POSH protects women from workplace sexual harassment.

    - Enacted in 2013 by Parliament of India
    - Mandates Internal Complaints Committee (ICC)
    - Covers prevention, prohibition, and redressal
    - Applies to all workplaces

    Q: "What is the password policy?"
    A: The password policy ensures secure account access.

    - Minimum 12 characters long
    - Must include uppercase, lowercase, numbers, special characters
    - Change every 90 days
    - Cannot reuse last 5 passwords

    TYPE 3: PROCESS/PROCEDURE QUESTIONS (How to X?)
    → USE bullet points for steps

    Example:
    Q: "How to file a complaint?"
    A: To file a sexual harassment complaint:

    - Submit written complaint to ICC
    - Include details of incident and witnesses
    - Provide supporting evidence if available
    - ICC will investigate within 90 days
    - Maintain confidentiality throughout process

    TYPE 4: DOCUMENT ACCESS/LOCATION QUESTIONS
    → Direct users to Sahyog Portal
    → NO bullet points needed

    Examples:
    Q: "Where can I find this document?"
    A: You can access all company policy documents through the Sahyog Portal. Please navigate to the Policies section to view and download the complete documents.

    Q: "How do I download the IT Policy?"
    A: You can access all company policy documents through the Sahyog Portal. Please navigate to the Policies section to view and download the complete documents.

    FORMATTING RULES:
    ✓ Use bullet points ONLY for listing policy details, requirements, or steps
    ✓ Use natural sentences for confirmations, simple answers, page numbers, document locations
    ✓ Each bullet = ONE distinct point
    ✓ Maximum 5 bullets for any answer
    ✓ NO bullets for: yes/no answers, page numbers, single fact confirmations, document location queries

    NEVER:
    ✗ Use bullets for generic confirmations like "Yes, it's accurate"
    ✗ Use bullets for page number answers
    ✗ Use bullets for document location responses
    ✗ Write long paragraphs
    ✗ Repeat information unnecessarily
    ✗ List obvious statements in bullet form

    Remember: 
    - Bullets are for LISTING policy information, NOT for wrapping every sentence
    - Document location queries ALWAYS point to Sahyog Portal → Policies section""" 
    
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
        """Main chat function with conversation history support and Redis caching"""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        print(f"\nProcessing query: {user_query}")
        print(f"Conversation history length: {len(conversation_history) if conversation_history else 0}")
        
        # CACHE CHECK
        cached_response = self.cache.get(user_query)
        if cached_response:
            logger.info(f"[CACHE HIT] Returning cached response for: {user_query[:50]}...")
            cached_response['conversation_id'] = conversation_id
            return cached_response
        
        try:
            # Detect question type
            is_simple = self._is_simple_question(user_query)
            is_followup = self._is_followup_question(user_query)
            
            print(f"[QUESTION TYPE] Simple: {is_simple}, Follow-up: {is_followup}")
            
            # CHECK: If it's a follow-up question but no conversation history exists
            if is_followup and (not conversation_history or len(conversation_history) <= 1):
                # Questions that REQUIRE prior context
                requires_context_keywords = [
                    'on which page', 'which page', 'what page',
                    'where is it', 'where does it say',
                    'reference', 'that policy', 'this policy',
                    'it', 'this', 'that',
                    'the above', 'mentioned above'
                ]
                
                query_lower = user_query.lower()
                needs_context = any(keyword in query_lower for keyword in requires_context_keywords)
                
                if needs_context:
                    return {
                        'answer': "I don't have context about what you're referring to. Could you please specify which policy or topic you'd like to know about?",
                        'sources': [],
                        'conversation_id': conversation_id
                    }
            
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
                print(f"🔍 Enhanced search query: {search_query[:100]}...")
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
                    'answer': "I don't have information about this in our policy documents. Please contact the appropriate department for assistance.",
                    'sources': [],
                    'conversation_id': conversation_id
                }
            
            # Format conversation history
            history_context = ""
            if conversation_history and len(conversation_history) > 0:
                history_context = self._format_conversation_history(conversation_history)
                print(f"📝 Including conversation history with {len(conversation_history)} messages")
            
            # Create prompt based on question type
            if is_simple and is_followup:
                # Simple follow-up (e.g., "which page?")
                user_prompt = f"""{history_context}

    Context from Policy Documents:
    {document_context}

    Current User Question: {user_query}

    This is a SIMPLE FOLLOW-UP question. Look at the conversation history to understand what the user is asking about.

    IMPORTANT: If the conversation history is empty or doesn't provide context for what "it" refers to, respond with:
    "I don't have context about what you're referring to. Could you please specify which policy or topic?"

    Otherwise, provide a direct answer in natural language. NO bullet points needed for simple answers.

    Example format:
    "Page 5 of POSH Policy"

    Just answer the question naturally and concisely."""

            elif is_followup:
                # Complex follow-up
                user_prompt = f"""{history_context}

    Context from Policy Documents:
    {document_context}

    Current User Question: {user_query}

    This is a FOLLOW-UP question. Check conversation history to understand context.

    IMPORTANT: If the conversation history doesn't provide clear context for what the user is referring to, ask for clarification.

    If asking for confirmation or simple fact: Answer naturally without bullets.
    If asking for policy details: Use bullet points for listing information.

    Format for policy details:
    Brief intro (1 line)

    - Key point 1
    - Key point 2
    - Key point 3
    (Maximum 5 bullets)

    Format for confirmations:
    Just answer naturally: "Yes, that's correct..." or "No, actually..."
    """

            else:
                # New question - determine if it needs bullets
                user_prompt = f"""{history_context}

    Context from Policy Documents:
    {document_context}

    Current User Question: {user_query}

    Analyze the question type:
    - If asking for a single fact, page number, or yes/no: Answer naturally without bullets
    - If asking about policy details (What is X?): Use brief intro + bullet points
    - If asking for process (How to X?): Use bullet points for steps

    Format for policy details:
    Brief intro (1 line)

    - Key point 1
    - Key point 2
    - Key point 3
    (Maximum 5 bullets)

    Format for simple answers:
    Just state the information naturally without bullets."""
            
            # Get response from OpenAI
            print("🤖 Generating response...")
            
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
            print("✅ Response generated successfully")
            
            # Extract sources
            sources = [
                {
                    'source': match['metadata'].get('source', 'Unknown'),
                    'page': match['metadata'].get('page', 'Unknown'),
                    'score': match['score']
                }
                for match in search_results.get('matches', [])
            ]
            
            # CACHE STORE
            response_data = {
                'answer': answer,
                'sources': sources,
                'conversation_id': conversation_id
            }
            self.cache.set(user_query, response_data)
            
            return response_data
        
        except Exception as e:
            print(f"❌ Error in chat: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise
