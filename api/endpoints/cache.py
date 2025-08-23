"""Cache Management Endpoints Module"""

import logging
from datetime import datetime
from typing import Any, Dict
from fastapi import APIRouter, HTTPException

from api.services.cache_service import get_cache_service

logger = logging.getLogger(__name__)

# Create router
cache_router = APIRouter(prefix="/cache", tags=["cache"])

@cache_router.get("/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics and performance metrics"""
    try:
        cache_service = get_cache_service()
        stats = cache_service.get_cache_stats()
        return {
            "cache": stats,
            "timestamp": datetime.now(),
            "endpoints": {
                "clear_cache": "/cache/clear",
                "clear_investigations": "/cache/clear/investigations",
                "clear_external_apis": "/cache/clear/external"
            }
        }
    except Exception as e:
        logger.error(f"Cache stats failed: {e}")
        return {"error": f"Cache stats unavailable: {str(e)}"}

@cache_router.delete("/clear")
async def clear_all_cache() -> Dict[str, Any]:
    """Clear all cache entries"""
    try:
        cache_service = get_cache_service()
        cleared = cache_service.clear_expired_keys()
        return {
            "message": "Cache cleared successfully",
            "keys_cleared": cleared,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")

@cache_router.delete("/clear/investigations")
async def clear_investigation_cache() -> Dict[str, Any]:
    """Clear investigation-related cache entries"""
    try:
        cache_service = get_cache_service()
        patterns = ["risk_analysis:*", "investigation:*"]
        total_cleared = 0
        for pattern in patterns:
            total_cleared += cache_service.clear_pattern(pattern)
        
        return {
            "message": "Investigation cache cleared successfully",
            "keys_cleared": total_cleared,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Investigation cache clear failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")

@cache_router.delete("/clear/external")
async def clear_external_api_cache() -> Dict[str, Any]:
    """Clear external API cache entries"""
    try:
        cache_service = get_cache_service()
        patterns = ["web_intel:*", "arxiv:*", "doc_search:*"]
        total_cleared = 0
        for pattern in patterns:
            total_cleared += cache_service.clear_pattern(pattern)
        
        return {
            "message": "External API cache cleared successfully",
            "keys_cleared": total_cleared,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"External API cache clear failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")
