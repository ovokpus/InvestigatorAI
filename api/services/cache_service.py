"""Redis caching service for InvestigatorAI"""
import json
import hashlib
import redis
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import asyncio
from functools import wraps

from ..core.config import Settings

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service for investigation data"""
    
    def __init__(self, settings: Settings):
        logger.info("🗄️  Initializing CacheService")
        logger.info(f"   🎯 Redis Host: {settings.redis_host}:{settings.redis_port}")
        logger.info(f"   📂 Database: {settings.redis_db}")
        logger.info(f"   ⚡ Cache Enabled: {settings.cache_enabled}")
        
        self.settings = settings
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis server"""
        logger.info(f"🔗 Connecting to Redis cache...")
        try:
            self.redis_client = redis.Redis(
                host=self.settings.redis_host,
                port=self.settings.redis_port,
                db=self.settings.redis_db,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            logger.debug("🔍 Testing Redis connection...")
            ping_response = self.redis_client.ping()
            logger.info(f"✅ Connected to Redis successfully - Response: {ping_response}")
            logger.info(f"   🎯 Redis Server: {self.settings.redis_host}:{self.settings.redis_port}")
            logger.info(f"   💾 Database: {self.settings.redis_db}")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            logger.warning("   ⚠️  Cache service disabled - running without caching")
            self.redis_client = None
    
    def _generate_key(self, prefix: str, data: Dict[str, Any]) -> str:
        """Generate a cache key from data"""
        # Create deterministic hash from transaction data
        serialized = json.dumps(data, sort_keys=True)
        hash_object = hashlib.md5(serialized.encode())
        return f"{prefix}:{hash_object.hexdigest()}"
    
    def is_available(self) -> bool:
        """Check if cache is available"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set a value in cache with TTL"""
        if not self.is_available():
            return False
        try:
            serialized_value = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            print(f"❌ Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        if not self.is_available():
            return None
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"❌ Cache get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        if not self.is_available():
            return False
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"❌ Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern"""
        if not self.is_available():
            return 0
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"❌ Cache clear error: {e}")
            return 0
    
    # ======================
    # Investigation-Specific Cache Methods
    # ======================
    
    def cache_risk_analysis(self, transaction_details: Dict[str, Any], risk_data: Dict[str, Any], ttl: int = 1800) -> bool:
        """Cache risk analysis results"""
        key = self._generate_key("risk_analysis", transaction_details)
        cache_data = {
            "risk_data": risk_data,
            "timestamp": datetime.now().isoformat(),
            "transaction_hash": key
        }
        return self.set(key, cache_data, ttl)
    
    def get_cached_risk_analysis(self, transaction_details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached risk analysis"""
        key = self._generate_key("risk_analysis", transaction_details)
        cached = self.get(key)
        if cached:
            print(f"🎯 Cache HIT: Risk analysis for transaction")
            return cached.get("risk_data")
        return None
    
    def cache_web_intelligence(self, query: str, results: str, ttl: int = 3600) -> bool:
        """Cache web search results"""
        key = f"web_intel:{hashlib.md5(query.encode()).hexdigest()}"
        cache_data = {
            "query": query,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        return self.set(key, cache_data, ttl)
    
    def get_cached_web_intelligence(self, query: str) -> Optional[str]:
        """Get cached web intelligence"""
        key = f"web_intel:{hashlib.md5(query.encode()).hexdigest()}"
        cached = self.get(key)
        if cached:
            print(f"🎯 Cache HIT: Web intelligence for '{query[:30]}...'")
            return cached.get("results")
        return None
    
    def cache_arxiv_research(self, query: str, results: str, ttl: int = 7200) -> bool:
        """Cache ArXiv research results"""
        key = f"arxiv:{hashlib.md5(query.encode()).hexdigest()}"
        cache_data = {
            "query": query,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        return self.set(key, cache_data, ttl)
    
    def get_cached_arxiv_research(self, query: str) -> Optional[str]:
        """Get cached ArXiv research"""
        key = f"arxiv:{hashlib.md5(query.encode()).hexdigest()}"
        cached = self.get(key)
        if cached:
            print(f"🎯 Cache HIT: ArXiv research for '{query[:30]}...'")
            return cached.get("results")
        return None
    
    def cache_document_search(self, query: str, results: List[Dict], ttl: int = 1800) -> bool:
        """Cache vector document search results"""
        key = f"doc_search:{hashlib.md5(query.encode()).hexdigest()}"
        cache_data = {
            "query": query,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        return self.set(key, cache_data, ttl)
    
    def get_cached_document_search(self, query: str) -> Optional[List[Dict]]:
        """Get cached document search results"""
        key = f"doc_search:{hashlib.md5(query.encode()).hexdigest()}"
        cached = self.get(key)
        if cached:
            print(f"🎯 Cache HIT: Document search for '{query[:30]}...'")
            return cached.get("results")
        return None
    
    def cache_investigation_result(self, investigation_id: str, results: Dict[str, Any], ttl: int = 86400) -> bool:
        """Cache complete investigation results"""
        key = f"investigation:{investigation_id}"
        cache_data = {
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "investigation_id": investigation_id
        }
        return self.set(key, cache_data, ttl)
    
    def get_cached_investigation(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        """Get cached investigation results"""
        key = f"investigation:{investigation_id}"
        cached = self.get(key)
        if cached:
            print(f"🎯 Cache HIT: Investigation {investigation_id}")
            return cached.get("results")
        return None
    
    # ======================
    # Statistics and Monitoring
    # ======================
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.is_available():
            return {"status": "unavailable"}
        
        try:
            info = self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "Unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": round(info.get("keyspace_hits", 0) / max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)) * 100, 2)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def clear_expired_keys(self) -> int:
        """Clear expired investigation cache keys"""
        patterns = ["risk_analysis:*", "web_intel:*", "arxiv:*", "doc_search:*"]
        total_cleared = 0
        for pattern in patterns:
            total_cleared += self.clear_pattern(pattern)
        return total_cleared

# ======================
# Cache Decorators
# ======================

def cache_result(cache_key_func, ttl: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get cache service from app state or create new one
            try:
                from ..core.config import get_settings
                settings = get_settings()
                cache_service = CacheService(settings)
                
                # Generate cache key
                key = cache_key_func(*args, **kwargs)
                
                # Try to get from cache
                cached_result = cache_service.get(key)
                if cached_result:
                    return cached_result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                cache_service.set(key, result, ttl)
                return result
                
            except Exception as e:
                print(f"⚠️ Cache decorator error: {e}")
                # Fallback to direct execution
                return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                from ..core.config import get_settings
                settings = get_settings()
                cache_service = CacheService(settings)
                
                key = cache_key_func(*args, **kwargs)
                cached_result = cache_service.get(key)
                if cached_result:
                    return cached_result
                
                result = func(*args, **kwargs)
                cache_service.set(key, result, ttl)
                return result
                
            except Exception as e:
                print(f"⚠️ Cache decorator error: {e}")
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Global instance
_cache_service = None

def get_cache_service() -> CacheService:
    """Get global cache service instance"""
    global _cache_service
    if _cache_service is None:
        from ..core.config import get_settings
        settings = get_settings()
        _cache_service = CacheService(settings)
    return _cache_service