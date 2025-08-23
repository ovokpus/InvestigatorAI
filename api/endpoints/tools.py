"""Tools and Search Endpoints Module"""

import logging
from datetime import datetime
from typing import Any
from fastapi import APIRouter, HTTPException, Depends

from api.models.schemas import VectorSearchResult, AgentToolResponse
from api.core.dependencies import get_vector_store, get_external_api_service

logger = logging.getLogger(__name__)

# Create router
tools_router = APIRouter(tags=["tools"])

@tools_router.get("/search")
async def search_documents(
    query: str,
    max_results: int = 5,
    vector_store: Any = Depends(get_vector_store)
) -> list[VectorSearchResult]:
    """Search regulatory documents"""
    
    try:
        results = vector_store.search(query, k=max_results)
        return results or []
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@tools_router.get("/exchange-rate")
async def get_exchange_rate(
    from_currency: str,
    to_currency: str = "USD",
    external_api: Any = Depends(get_external_api_service)
) -> AgentToolResponse:
    """Get exchange rate between currencies"""
    
    try:
        result = external_api.get_exchange_rate(from_currency, to_currency)
        
        return AgentToolResponse(
            result=result,
            source="ExchangeRates-API",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Exchange rate lookup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Exchange rate lookup failed: {str(e)}")

@tools_router.get("/web-search")
async def search_web(
    query: str,
    max_results: int = 5,
    external_api: Any = Depends(get_external_api_service)
) -> AgentToolResponse:
    """Search the web using Tavily"""
    logger.info(f"🌐 API endpoint called: /web-search - Query: '{query}', Max results: {max_results}")
    
    try:
        logger.info(f"📡 Calling Tavily search service...")
        result = external_api.search_web(query, max_results)
        
        response = AgentToolResponse(
            result=result,
            source="Tavily",
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✅ API endpoint /web-search completed successfully for query: '{query}'")
        return response
        
    except Exception as e:
        logger.error(f"❌ Web search API endpoint failed for query '{query}': {e}")
        raise HTTPException(status_code=500, detail=f"Web search failed: {str(e)}")

@tools_router.get("/arxiv-search")
async def search_arxiv(
    query: str,
    max_results: int = 4,
    external_api: Any = Depends(get_external_api_service)
) -> AgentToolResponse:
    """Search ArXiv for research papers"""
    
    try:
        result = external_api.search_arxiv(query, max_results)
        
        return AgentToolResponse(
            result=result,
            source="ArXiv",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"ArXiv search failed: {e}")
        raise HTTPException(status_code=500, detail=f"ArXiv search failed: {str(e)}")
