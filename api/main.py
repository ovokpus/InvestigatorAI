"""FastAPI application for InvestigatorAI - Modular Version"""

import logging
import os
from datetime import datetime
from typing import Any, AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# LangSmith monitoring
try:
    from langsmith import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    # Create no-op decorator if LangSmith is not installed
    LANGSMITH_AVAILABLE = False
    def traceable(func: Any) -> Any:  # type: ignore
        return func

from api.core.config import get_settings, initialize_llm_components
from api.models.schemas import HealthResponse
from api.services.document_processor import DocumentProcessor
from api.services.vector_store import VectorStoreManager
from api.services.external_apis import ExternalAPIService
from api.agents.langgraph.multi_agent_system import FraudInvestigationSystem
from api.endpoints.research import research_router, initialize_research_services
from api.services.unified_investigation import UnifiedInvestigationService
from api.core.dependencies import app_state, RateLimiter, get_app_settings
from api.endpoints.investigation import investigation_router
from api.endpoints.tools import tools_router
from api.endpoints.cache import cache_router
from api.middleware.logging_middleware import LoggingMiddleware, StreamingLoggingMiddleware
# Configure comprehensive logging
from api.utils.logging_config import setup_logging, get_logger

# Setup logging based on environment
log_level = os.getenv("LOG_LEVEL", "INFO")
log_to_file = os.getenv("LOG_TO_FILE", "true").lower() == "true"
json_logging = os.getenv("JSON_LOGGING", "false").lower() == "true"

setup_logging(
    log_level=log_level,
    log_to_file=log_to_file,
    json_logging=json_logging,
    enable_performance_logging=True
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    logger.info("🚀 Starting InvestigatorAI API...")
    
    try:
        # Initialize settings
        settings = get_settings()
        app_state["settings"] = settings
        logger.info("✅ Settings loaded")
        
        # Initialize rate limiter
        app_state["rate_limiter"] = RateLimiter(max_requests=5, window_seconds=60)
        
        # Initialize LLM components
        llm, embeddings = initialize_llm_components(settings)
        logger.info("✅ LLM and embeddings initialized")
        
        # Initialize external API service
        external_api_service = ExternalAPIService(settings)
        app_state["external_api_service"] = external_api_service
        logger.info("✅ External API service initialized")
        
        # Connect to existing vector store (documents pre-loaded by init service)
        logger.info("🔗 Connecting to pre-initialized vector store...")
        vector_store = VectorStoreManager.connect_existing(embeddings, settings)
        app_state["vector_store"] = vector_store
        
        if vector_store and vector_store.is_initialized:
            logger.info("✅ Vector store connected successfully")
        else:
            logger.warning("⚠️  Vector store not ready - API will start but document search may be limited")
            logger.info("💡 Ensure the init-docs service has completed successfully")
        
        # Initialize fraud investigation system
        fraud_investigation_system = FraudInvestigationSystem(llm, external_api_service)
        app_state["fraud_investigation_system"] = fraud_investigation_system
        logger.info("✅ Fraud investigation system initialized")
        
        # Initialize enhanced research services
        logger.info("🔬 Initializing enhanced research services...")
        initialize_research_services(llm, settings)
        logger.info("✅ Enhanced research services initialized")
        
        # Initialize unified investigation service (NEW)
        logger.info("🎯 Initializing unified investigation service...")
        from api.endpoints.research import research_services
        enhanced_investigator = research_services.get("enhanced_investigator")
        
        if enhanced_investigator:
            unified_service = UnifiedInvestigationService(  # type: ignore
                llm=llm,
                settings=settings,
                fraud_system=fraud_investigation_system,
                enhanced_investigator=enhanced_investigator
            )
            app_state["unified_investigation_service"] = unified_service
            logger.info("✅ Unified investigation service initialized")
        else:
            logger.warning("⚠️ Enhanced investigator not available for unified service")
        
        logger.info("🎉 InvestigatorAI API ready!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize application: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down InvestigatorAI API...")

# Create FastAPI app
app = FastAPI(
    title="InvestigatorAI",
    description="Multi-Agent Fraud Investigation System API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://investigator-ai.app",
        "https://*.investigator-ai.app",
        "https://investigator-ai-ochre.vercel.app",
        "https://investigator-ai-ovo-okpubulukus-projects.vercel.app",
        "https://investigator-ai-ovokpus-ovo-okpubulukus-projects.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware, exclude_paths=["/health", "/docs", "/openapi.json", "/favicon.ico"])
app.add_middleware(StreamingLoggingMiddleware)

# Include routers
app.include_router(investigation_router)
app.include_router(tools_router)
app.include_router(cache_router)
app.include_router(research_router)

# Health check endpoint
@app.get("/health")
@traceable(name="health_check_api", tags=["api", "health"])
async def health_check(
    settings: Any = Depends(get_app_settings)
) -> Any:
    """Health check endpoint"""
    vector_store = app_state.get("vector_store")
    
    # Check LangSmith status
    langsmith_status = {
        "available": LANGSMITH_AVAILABLE and settings.langsmith_available,
        "configured": settings.langsmith_available,
        "project": settings.langsmith_project if settings.langsmith_available else None
    }
    
    response = HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        api_keys_available=settings.api_keys_available,
        vector_store_initialized=vector_store.is_initialized if vector_store else False
    )
    
    # Add LangSmith status to response
    response_dict = response.model_dump(mode='json')
    response_dict["langsmith"] = langsmith_status
    
    return JSONResponse(content=response_dict)

# Root endpoint
@app.get("/")
async def root() -> dict:
    """Root endpoint"""
    return {
        "message": "InvestigatorAI Multi-Agent Fraud Investigation System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
