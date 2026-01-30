# backend/test_redis_cache.py
"""
Quick test script to verify Redis caching is working correctly
Run this after starting the backend to test cache functionality
"""

import sys
from app.services.redis_client import get_redis_cache
from app.services.chatbot import PolicyChatbot
import time

def test_redis_connection():
    """Test Redis connection"""
    print("\n=== Testing Redis Connection ===")
    cache = get_redis_cache()
    
    if cache.is_connected():
        print("[PASS] Redis connection successful")
        return True
    else:
        print("[FAIL] Redis connection failed - ensure Redis is running on localhost:6379")
        return False

def test_cache_key_generation():
    """Test MD5 hash key generation"""
    print("\n=== Testing Cache Key Generation ===")
    cache = get_redis_cache()
    
    queries = [
        "What is POSH?",
        "What is POSH?",  # Same query should produce same key
        "What is the process to file a complaint?"
    ]
    
    keys = [cache._generate_cache_key(q) for q in queries]
    print(f"Query 1: {queries[0]}")
    print(f"  Key: {keys[0]}")
    print(f"Query 2: {queries[1]} (same as Query 1)")
    print(f"  Key: {keys[1]}")
    
    if keys[0] == keys[1]:
        print("[PASS] Same queries produce identical keys (as expected)")
    else:
        print("[FAIL] Same queries produced different keys (unexpected)")
        return False
    
    if keys[0] != keys[2]:
        print("[PASS] Different queries produce different keys (as expected)")
        return True
    else:
        print("[FAIL] Different queries produced same keys (unexpected)")
        return False

def test_cache_set_get():
    """Test cache set and get operations"""
    print("\n=== Testing Cache Set/Get Operations ===")
    cache = get_redis_cache()
    
    if not cache.is_connected():
        print("[FAIL] Redis not connected, skipping test")
        return False
    
    test_query = "What is POSH policy?"
    test_response = {
        'answer': 'POSH is the Prevention of Sexual Harassment policy',
        'sources': [{'source': 'POSH_Policy.pdf', 'page': '1', 'score': 0.95}],
        'conversation_id': 'test-id-123'
    }
    
    # Set cache
    print(f"Setting cache for: {test_query}")
    success = cache.set(test_query, test_response)
    if success:
        print("[PASS] Cache set successful")
    else:
        print("[FAIL] Cache set failed")
        return False
    
    # Get cache
    print(f"Getting cache for: {test_query}")
    cached = cache.get(test_query)
    if cached:
        print("[PASS] Cache get successful")
        print(f"  Cached answer: {cached['answer']}")
        return True
    else:
        print("[FAIL] Cache get failed")
        return False

def test_cache_ttl():
    """Test cache TTL expiration"""
    print("\n=== Testing Cache TTL (Short Test) ===")
    from app.services.redis_client import RedisCache
    
    # Create cache with 2-second TTL for testing
    test_cache = RedisCache(ttl_seconds=2)
    
    if not test_cache.is_connected():
        print("[FAIL] Redis not connected, skipping TTL test")
        return False
    
    test_query = "TTL test query"
    test_response = {'answer': 'test', 'sources': [], 'conversation_id': 'test'}
    
    test_cache.set(test_query, test_response)
    print(f"Set cache with 2-second TTL")
    print(f"Checking immediately...")
    
    if test_cache.get(test_query):
        print("[PASS] Cache hit (immediate check)")
    else:
        print("[FAIL] Cache miss (immediate check)")
        return False
    
    print(f"Waiting 3 seconds for TTL expiration...")
    time.sleep(3)
    
    if not test_cache.get(test_query):
        print("[PASS] Cache expired after TTL (as expected)")
        test_cache.delete(test_query)  # Cleanup
        return True
    else:
        print("[FAIL] Cache still valid after TTL (unexpected)")
        test_cache.delete(test_query)  # Cleanup
        return False

def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("REDIS CACHE TESTING SUITE")
    print("="*50)
    
    results = {
        'Connection': test_redis_connection(),
        'Key Generation': test_cache_key_generation(),
        'Set/Get Operations': test_cache_set_get(),
        'TTL Expiration': test_cache_ttl(),
    }
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n[INFO] All tests passed! Redis caching is working correctly.")
    else:
        print("\n[INFO] Some tests failed. Check Redis connection and configuration.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
