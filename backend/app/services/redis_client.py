# backend/app/services/redis_client.py
import redis
import json
import hashlib
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis cache client for caching chatbot responses with metadata support"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, ttl_seconds: int = 3600):
        """
        Initialize Redis connection
        
        Args:
            host: Redis server host (default: localhost)
            port: Redis server port (default: 6379)
            db: Redis database number (default: 0)
            ttl_seconds: Time-to-live for cached entries in seconds (default: 3600 = 1 hour)
        """
        self.ttl = ttl_seconds
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Test connection
            self.client.ping()
            logger.info(f"Redis cache connected successfully at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.client = None
    
    def _generate_cache_key(self, user_query: str) -> str:
        """
        Generate cache key from user query using MD5 hash
        
        Args:
            user_query: The user's question
            
        Returns:
            MD5 hash prefixed with 'chat_cache:' for cache organization
        """
        query_hash = hashlib.md5(user_query.encode()).hexdigest()
        return f"chat_cache:{query_hash}"
    
    def _should_cache(self, user_query: str, response: Dict[str, Any]) -> bool:
        """
        Determine if a response should be cached based on query type and response metadata
        
        Args:
            user_query: The user's question
            response: The chatbot's response dict
            
        Returns:
            True if should be cached, False otherwise
        """
        # Check if metadata explicitly says not to cache
        if response.get('cacheable') is False:
            logger.info(f"Skipping cache - metadata indicates not cacheable")
            return False
        
        query_lower = user_query.lower().strip()
        
        # 1. Don't cache context-dependent questions without context
        context_dependent_keywords = [
            'on which page', 'which page', 'what page',
            'where is it', 'where does it say',
            'where is this', 'where can i find this',
            'it', 'this', 'that',
            'the above', 'mentioned above',
            'refer to', 'reference'
        ]
        
        # If query has context-dependent words but response is asking for clarification
        if any(keyword in query_lower for keyword in context_dependent_keywords):
            answer = response.get('answer', '').lower()
            if any(phrase in answer for phrase in [
                "don't have context",
                "could you please specify",
                "which policy",
                "what are you referring to"
            ]):
                logger.info(f"Skipping cache - context clarification needed: {user_query[:50]}...")
                return False
        
        # 2. Don't cache document location queries (always point to Sahyog Portal)
        location_keywords = [
            'where can i find', 'where is', 'where are',
            'how to access', 'how do i access',
            'how to download', 'can i download',
            'where to find', 'where to get',
            'access the', 'find the document',
            'sahyog portal', 'portal'
        ]
        
        if any(keyword in query_lower for keyword in location_keywords):
            logger.info(f"Skipping cache - document location query: {user_query[:50]}...")
            return False
        
        # 3. Don't cache greetings and casual conversation
        greeting_keywords = [
            'hello', 'hi', 'hey', 'thanks', 'thank you',
            'how are you', 'what is your name', 'who are you'
        ]
        
        if any(keyword in query_lower for keyword in greeting_keywords):
            logger.info(f"Skipping cache - greeting/casual: {user_query[:50]}...")
            return False
        
        # 4. Don't cache "not found" responses
        answer = response.get('answer', '').lower()
        if any(phrase in answer for phrase in [
            "don't have information",
            "couldn't find",
            "no information available",
            "contact the appropriate department"
        ]):
            logger.info(f"Skipping cache - no information found: {user_query[:50]}...")
            return False
        
        # 5. Cache policy content responses
        if response.get('sources') and len(response.get('sources', [])) > 0:
            logger.info(f"Cacheable - policy content with sources: {user_query[:50]}...")
            return True
        
        # Default: cache if it has a substantial answer
        if len(response.get('answer', '')) > 50:
            logger.info(f"Cacheable - substantial answer: {user_query[:50]}...")
            return True
        
        logger.info(f"Skipping cache - default skip: {user_query[:50]}...")
        return False
    
    def get(self, user_query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response for a query
        
        Args:
            user_query: The user's question
            
        Returns:
            Cached response dict if found, None otherwise
        """
        if not self.client:
            return None
        
        try:
            cache_key = self._generate_cache_key(user_query)
            cached_data = self.client.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache HIT for query: {user_query[:50]}...")
                return json.loads(cached_data)
            else:
                logger.info(f"Cache MISS for query: {user_query[:50]}...")
                return None
        
        except Exception as e:
            logger.warning(f"Error retrieving from cache: {str(e)}")
            return None
    
    def set(self, user_query: str, response: Dict[str, Any]) -> bool:
        """
        Store response in cache with TTL (only if cacheable)
        
        Args:
            user_query: The user's question
            response: The chatbot's response dict containing 'answer', 'sources', 'conversation_id'
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
        
        # Check if this response should be cached
        if not self._should_cache(user_query, response):
            return False
        
        try:
            cache_key = self._generate_cache_key(user_query)
            cache_value = json.dumps(response)
            
            # Set with TTL expiration
            self.client.setex(cache_key, self.ttl, cache_value)
            logger.info(f"Cached response for query: {user_query[:50]}... (TTL: {self.ttl}s)")
            return True
        
        except Exception as e:
            logger.warning(f"Error caching response: {str(e)}")
            return False
    
    def delete(self, user_query: str) -> bool:
        """
        Delete specific cache entry
        
        Args:
            user_query: The user's question
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.client:
            return False
        
        try:
            cache_key = self._generate_cache_key(user_query)
            result = self.client.delete(cache_key)
            logger.info(f"Deleted cache entry for query: {user_query[:50]}...")
            return result > 0
        
        except Exception as e:
            logger.warning(f"Error deleting cache entry: {str(e)}")
            return False
    
    def flush_all(self) -> bool:
        """
        Clear all chat cache entries (WARNING: clears entire Redis DB)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            self.client.flushdb()
            logger.info("Flushed all cache entries")
            return True
        
        except Exception as e:
            logger.warning(f"Error flushing cache: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict with cache stats (keys count, memory usage, etc.)
        """
        if not self.client:
            return {"error": "Redis not connected"}
        
        try:
            info = self.client.info('stats')
            keys_count = self.client.dbsize()
            
            return {
                "total_keys": keys_count,
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "hit_rate": f"{(info.get('keyspace_hits', 0) / max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1)) * 100:.2f}%"
            }
        
        except Exception as e:
            logger.warning(f"Error getting cache stats: {str(e)}")
            return {"error": str(e)}
    
    def is_connected(self) -> bool:
        """Check if Redis connection is active"""
        if not self.client:
            return False
        
        try:
            self.client.ping()
            return True
        except:
            return False


# Global cache instance
_cache_instance = None

def get_redis_cache() -> RedisCache:
    """Get or create Redis cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance