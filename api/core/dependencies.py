"""FastAPI Dependencies Module"""

from typing import Any
from fastapi import HTTPException, Request, Depends
from api.core.config import Settings
from api.services.external_apis import ExternalAPIService
from api.agents.langgraph.multi_agent_system import FraudInvestigationSystem
from api.services.unified_investigation import UnifiedInvestigationService
import time
from collections import defaultdict, deque

# Global application state
app_state: dict[str, Any] = {
    "fraud_investigation_system": None,
    "vector_store": None,
    "external_api_service": None,
    "settings": None,
    "rate_limiter": None,
    "unified_investigation_service": None
}

# Simple rate limiter implementation
class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        # Clean old requests outside the window
        while self.requests[client_id] and self.requests[client_id][0] < now - self.window_seconds:
            self.requests[client_id].popleft()
        
        # Check if under limit
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        return False

# Dependency functions
def get_fraud_investigation_system() -> Any:
    """Get fraud investigation system dependency"""
    system = app_state.get("fraud_investigation_system")
    if not system:
        raise HTTPException(status_code=503, detail="Fraud investigation system not available")
    return system

def get_vector_store() -> Any:
    """Get vector store dependency"""
    vector_store = app_state.get("vector_store")
    if not vector_store or not vector_store.is_initialized:
        raise HTTPException(status_code=503, detail="Vector store not available")
    return vector_store

def get_external_api_service() -> Any:
    """Get external API service dependency"""
    service = app_state.get("external_api_service")
    if not service:
        raise HTTPException(status_code=503, detail="External API service not available")
    return service

def get_app_settings() -> Any:
    """Get application settings dependency"""
    settings = app_state.get("settings")
    if not settings:
        raise HTTPException(status_code=503, detail="Application settings not available")
    return settings

def check_rate_limit(request: Request) -> None:
    """Rate limiting dependency"""
    rate_limiter = app_state.get("rate_limiter")
    if not rate_limiter:
        return  # No rate limiter configured
    
    client_ip = request.client.host if request.client else 'unknown'
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Maximum 5 requests per minute allowed."
        )

def get_unified_investigation_service() -> Any:
    """Get unified investigation service dependency"""
    service = app_state.get("unified_investigation_service")
    if not service:
        raise HTTPException(status_code=503, detail="Unified investigation service not available")
    return service
