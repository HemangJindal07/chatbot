# backend/app/services/redis_client.py
import redis
import json
import hashlib
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis cache client for caching chatbot responses"""
    
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
        Store response in cache with TTL
        
        Args:
            user_query: The user's question
            response: The chatbot's response dict containing 'answer', 'sources', 'conversation_id'
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
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
