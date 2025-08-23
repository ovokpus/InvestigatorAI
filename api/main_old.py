"""FastAPI application for InvestigatorAI"""
import logging
from datetime import datetime
from typing import Optional, Any, AsyncGenerator, Dict
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, Response
import asyncio
import json
import time
from contextlib import asynccontextmanager
import openai
from openai import OpenAI
from collections import defaultdict, deque

# LangSmith monitoring
try:
    from langsmith import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    # Create no-op decorator if LangSmith is not installed
    LANGSMITH_AVAILABLE = False
    def traceable(func: Any) -> Any:  # type: ignore
        return func

from api.core.config import get_settings, initialize_llm_components, Settings
from api.models.schemas import (
    InvestigationRequest, InvestigationResponse, HealthResponse,
    VectorSearchResult, AgentToolResponse, UnifiedInvestigationRequest, UnifiedInvestigationResponse
)
from api.services.document_processor import DocumentProcessor
from api.services.vector_store import VectorStoreManager
from api.services.external_apis import ExternalAPIService
from api.services.cache_service import get_cache_service
from api.services.memory_optimizer import get_memory_optimizer
from api.agents.multi_agent_system import FraudInvestigationSystem
from api.research_endpoints import research_router, initialize_research_services
from api.services.unified_investigation import UnifiedInvestigationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def serialize_langchain_objects(obj: Any) -> Any:
    """Custom serializer for LangChain objects"""
    from langchain_core.messages import BaseMessage, AIMessage, ToolMessage, HumanMessage, SystemMessage
    
    if isinstance(obj, BaseMessage):
        # Serialize LangChain messages to dict format
        serialized = {
            "content": obj.content,
            "type": obj.__class__.__name__,
            "name": getattr(obj, 'name', None),
        }
        
        # Preserve tool calls for AIMessage
        if hasattr(obj, 'tool_calls') and obj.tool_calls:
            serialized["tool_calls"] = obj.tool_calls
        
        # Preserve tool_call_id for ToolMessage
        if hasattr(obj, 'tool_call_id') and obj.tool_call_id:
            serialized["tool_call_id"] = obj.tool_call_id
            
        return serialized
    
    elif isinstance(obj, list):
        return [serialize_langchain_objects(item) for item in obj]
    
    elif isinstance(obj, dict):
        return {key: serialize_langchain_objects(value) for key, value in obj.items()}
    
    else:
        # Return object as-is for basic types
        return obj

def handle_openai_error(e: Exception) -> tuple[int, str]:
    """Handle OpenAI API errors gracefully"""
    if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
        status_code = e.response.status_code
        
        if status_code == 400:
            error_message = str(e)
            if "max_tokens" in error_message.lower():
                return 413, "Investigation response too long. The AI generated more content than the current token limit allows. Please try a simpler investigation or contact support."
            elif "rate limit" in error_message.lower():
                return 429, "API rate limit exceeded. Please wait a moment and try again."
            else:
                return 400, f"Invalid request to AI service: {error_message}"
        elif status_code == 401:
            return 401, "AI service authentication failed. Please check API key configuration."
        elif status_code == 429:
            return 429, "AI service rate limit exceeded. Please wait a moment and try again."
        elif status_code >= 500:
            return 503, "AI service temporarily unavailable. Please try again in a few moments."
    
    # Handle generic OpenAI errors
    error_str = str(e).lower()
    if "max_tokens" in error_str or "token limit" in error_str:
        return 413, "Investigation response too long. The AI analysis exceeded the maximum allowed length. Please try with a simpler transaction description."
    elif "rate limit" in error_str:
        return 429, "Too many requests. Please wait a moment before trying again."
    elif "api key" in error_str or "authentication" in error_str:
        return 401, "AI service authentication error. Please contact support."
    
    return 500, f"AI service error: {str(e)}"

# Simple rate limiter implementation
class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
    
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

# Global application state
app_state: Dict[str, Any] = {
    "fraud_investigation_system": None,
    "vector_store": None,
    "external_api_service": None,
    "settings": None,
    "rate_limiter": RateLimiter(max_requests=5, window_seconds=60),  # 5 requests per minute
    "unified_investigation_service": None  # New unified service
}

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    logger.info("🚀 Starting InvestigatorAI API...")
    
    try:
        # Initialize settings
        settings = get_settings()
        app_state["settings"] = settings
        logger.info("✅ Settings loaded")
        
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
        from api.research_endpoints import research_services
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

# Include research endpoints
app.include_router(research_router)

# Add CORS middleware - PRODUCTION SECURITY HARDENING
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # Frontend development
        "http://localhost:3001",     # Alternative frontend port
        "https://investigator-ai.app", # Production domain (update as needed)
        "https://*.investigator-ai.app" # Production subdomains
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"],  # Specific methods only
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

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

# Health check endpoint
@app.get("/health")
@traceable(name="health_check_api", tags=["api", "health"])
async def health_check(
    settings: Settings = Depends(get_app_settings)
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
        timestamp=datetime.now(),
        version="1.0.0",
        api_keys_available=settings.api_keys_available,
        vector_store_initialized=vector_store.is_initialized if vector_store else False
    )
    
    # Add LangSmith status to response (this will require updating the schema)
    response_dict = response.model_dump(mode='json')  # Serialize datetime to ISO format
    response_dict["langsmith"] = langsmith_status
    
    return JSONResponse(content=response_dict)

# Cache statistics endpoint
@app.get("/cache/stats")
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

# Cache management endpoints
@app.delete("/cache/clear")
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

@app.delete("/cache/clear/investigations")
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

@app.delete("/cache/clear/external")
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

# Progress streaming endpoint
@app.post("/investigate/stream")
@traceable(name="investigate_fraud_stream_api", tags=["api", "investigation", "stream"])
async def investigate_fraud_stream(
    request: InvestigationRequest,
    fraud_system: FraudInvestigationSystem = Depends(get_fraud_investigation_system),
    _: None = Depends(check_rate_limit)
) -> StreamingResponse:
    """Stream real-time progress of fraud investigation"""
    
    async def generate_progress_stream() -> AsyncGenerator[str, None]:
        """Generate Server-Sent Events for investigation progress"""
        
        # Initial progress event
        yield f"data: {json.dumps({'type': 'progress', 'step': 'starting', 'agent': 'system', 'message': 'Initializing fraud investigation...', 'progress': 0})}\n\n"
        
        try:
            # Convert request to transaction details
            transaction_details = {
                "amount": request.amount,
                "currency": request.currency,
                "description": request.description,
                "customer_name": request.customer_name,
                "account_type": request.account_type,
                "customer_risk_rating": request.risk_rating,
                "country_to": request.country_to,
                "timestamp": datetime.now().isoformat()
            }
            
            # Stream investigation progress
            async for progress_event in fraud_system.investigate_fraud_stream(transaction_details):
                yield f"data: {json.dumps(progress_event)}\n\n"
                
                # Don't delay after completion event
                if progress_event.get('type') == 'complete':
                    break
                    
                await asyncio.sleep(0.1)  # Small delay for better UX
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error during streaming investigation: {e}")
            status_code, error_message = handle_openai_error(e)
            error_event = {
                'type': 'error',
                'step': 'error',
                'agent': 'system',
                'message': error_message,
                'progress': 100,
                'error': True
            }
            yield f"data: {json.dumps(error_event)}\n\n"
            
        except Exception as e:
            logger.error(f"Investigation streaming failed: {e}")
            error_message = str(e)
            if "openai" in error_message.lower() or "max_tokens" in error_message.lower():
                status_code, error_message = handle_openai_error(e)
            error_event = {
                'type': 'error',
                'step': 'error',
                'agent': 'system',
                'message': f"Investigation failed: {error_message}",
                'progress': 100,
                'error': True
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        generate_progress_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

# Main investigation endpoint
@app.post("/investigate")
@traceable(name="investigate_fraud_api", tags=["api", "investigation", "fraud"])
async def investigate_fraud(
    request: InvestigationRequest,
    fraud_system: FraudInvestigationSystem = Depends(get_fraud_investigation_system),
    _: None = Depends(check_rate_limit)
) -> Any:
    """Run a fraud investigation using the multi-agent system"""
    
    # Start request logging
    request_start = datetime.now()
    investigation_id = f"INV_{request_start.strftime('%Y%m%d_%H%M%S')}_{hash(str(request.dict())) % 10000:04d}"
    
    logger.info("🔍 ==> FRAUD INVESTIGATION REQUEST RECEIVED")
    logger.info(f"   🆔 Request ID: {investigation_id}")
    logger.info(f"   💰 Amount: {request.amount} {request.currency}")
    logger.info(f"   👤 Customer: {request.customer_name}")
    logger.info(f"   🌍 Destination: {request.country_to}")
    logger.info(f"   📝 Description: {(request.description or '')[:100]}...")
    logger.info(f"   ⚠️  Risk Rating: {request.risk_rating}")
    logger.info(f"   🏢 Account Type: {request.account_type}")
    
    try:
        # Convert request to transaction details
        transaction_details = {
            "investigation_id": investigation_id,
            "amount": request.amount,
            "currency": request.currency,
            "description": request.description,
            "customer_name": request.customer_name,
            "account_type": request.account_type,
            "customer_risk_rating": request.risk_rating,
            "country_to": request.country_to,
            "timestamp": request_start.isoformat()
        }
        
        logger.info(f"📋 Transaction details prepared - starting multi-agent investigation...")
        
        # Run investigation
        investigation_start = datetime.now()
        result = fraud_system.investigate_fraud(transaction_details)
        investigation_end = datetime.now()
        
        investigation_duration = (investigation_end - investigation_start).total_seconds()
        
        # Log investigation results
        investigation_status = result.get("status", "Unknown")
        final_decision = result.get("final_decision", "Pending")
        agents_completed = result.get("agents_completed", 0)
        total_messages = result.get("total_messages", 0)
        all_agents_finished = result.get("all_agents_finished", False)
        has_error = result.get("error") is not None
        
        logger.info(f"📊 INVESTIGATION RESULTS - ID: {investigation_id}")
        logger.info(f"   ⏱️  Investigation Duration: {investigation_duration:.2f}s")
        logger.info(f"   📊 Status: {investigation_status}")
        logger.info(f"   ⚖️  Decision: {final_decision}")
        logger.info(f"   🤖 Agents Completed: {agents_completed}/4")
        logger.info(f"   💬 Total Messages: {total_messages}")
        logger.info(f"   🏁 All Agents Finished: {all_agents_finished}")
        logger.info(f"   🚨 Has Error: {has_error}")
        
        if has_error:
            logger.error(f"   ❌ Investigation Error: {result.get('error')}")
        
        if agents_completed < 4:
            logger.warning(f"   ⚠️  Incomplete investigation - only {agents_completed}/4 agents completed")
        
        # Performance analysis
        if investigation_duration > 120:  # 2 minutes
            logger.warning(f"   🐌 Slow investigation - {investigation_duration:.2f}s (target: <60s)")
        elif investigation_duration < 30:
            logger.info(f"   ⚡ Fast investigation - {investigation_duration:.2f}s")
        
        # Memory optimization before response processing
        memory_optimizer = get_memory_optimizer()
        memory_optimizer.log_memory_status("(Before Response Processing)")
        
        # Serialize LangChain objects for JSON response  
        ragas_messages = result.get("ragas_validated_messages")
        if ragas_messages:
            logger.debug(f"🔧 Processing RAGAS messages - type: {type(ragas_messages)}, count: {len(ragas_messages)}")
            if ragas_messages:
                logger.debug(f"   First message type: {type(ragas_messages[0])}")
            
            # Clean up messages before serialization to save memory
            cleaned_messages = memory_optimizer.cleanup_messages([
                msg if isinstance(msg, dict) else {"content": str(msg), "type": "message"}
                for msg in ragas_messages
            ])
            
            serialized_ragas_messages = serialize_langchain_objects(cleaned_messages)
            logger.debug(f"   ✅ Serialized {len(serialized_ragas_messages)} cleaned LangChain objects for RAGAS")
        else:
            logger.debug("   ℹ️  No RAGAS messages to serialize")
            serialized_ragas_messages = None
        
        # Prepare response
        response_data = {
            "investigation_id": result.get("investigation_id", investigation_id),
            "status": investigation_status,
            "final_decision": final_decision,
            "agents_completed": agents_completed,
            "total_messages": total_messages,
            "transaction_details": result.get("transaction_details", {}),
            "all_agents_finished": all_agents_finished,
            "error": result.get("error"),
            "full_results": result.get("full_results"),
            "ragas_validated_messages": serialized_ragas_messages,
            "performance": result.get("performance", {})
        }
        
        # Optimize response for client to reduce network transfer and memory usage
        optimized_response = memory_optimizer.optimize_response_for_client(response_data)
        
        # Final request logging with optimization metrics
        total_duration = (datetime.now() - request_start).total_seconds()
        original_size_kb = len(str(response_data)) / 1024
        optimized_size_kb = len(str(optimized_response)) / 1024
        size_reduction = ((original_size_kb - optimized_size_kb) / original_size_kb) * 100
        
        logger.info(f"✅ FRAUD INVESTIGATION COMPLETED - ID: {investigation_id}")
        logger.info(f"   ⏱️  Total Request Duration: {total_duration:.2f}s")
        logger.info(f"   📦 Response Size: {optimized_size_kb:.1f} KB (reduced by {size_reduction:.1f}%)")
        logger.info(f"   🎯 Final Decision: {final_decision}")
        
        # Final memory cleanup
        memory_optimizer.log_memory_status("(Investigation Complete)")
        if memory_optimizer.should_cleanup():
            memory_optimizer.force_garbage_collection()
        
        return optimized_response
        
    except openai.OpenAIError as e:
        duration = (datetime.now() - request_start).total_seconds()
        error_type = type(e).__name__
        logger.error(f"❌ FRAUD INVESTIGATION FAILED - ID: {investigation_id}")
        logger.error(f"   🚨 Error Type: OpenAI API Error ({error_type})")
        logger.error(f"   💥 Error Details: {e}")
        logger.error(f"   ⏱️  Duration before failure: {duration:.2f}s")
        
        status_code, error_message = handle_openai_error(e)
        raise HTTPException(status_code=status_code, detail=error_message)
        
    except Exception as e:
        duration = (datetime.now() - request_start).total_seconds()
        error_type = type(e).__name__
        logger.error(f"❌ FRAUD INVESTIGATION FAILED - ID: {investigation_id}")
        logger.error(f"   🚨 Error Type: {error_type}")
        logger.error(f"   💥 Error Details: {e}")
        logger.error(f"   ⏱️  Duration before failure: {duration:.2f}s")
        logger.exception(f"   🔍 Full exception traceback:")
        
        # Check if it's an OpenAI error wrapped in another exception
        if "openai" in str(e).lower() or "max_tokens" in str(e).lower():
            status_code, error_message = handle_openai_error(e)
            raise HTTPException(status_code=status_code, detail=error_message)
        raise HTTPException(status_code=500, detail=f"Investigation failed: {str(e)}")

# NEW: Unified Investigation Endpoint 
@app.post("/investigate/unified")
@traceable(name="unified_investigation_api", tags=["api", "investigation", "unified"])
async def investigate_unified(
    request: UnifiedInvestigationRequest,
    unified_service: UnifiedInvestigationService = Depends(get_unified_investigation_service),
    _: None = Depends(check_rate_limit)
) -> Any:
    """Unified investigation endpoint supporting all investigation types"""
    
    logger.info(f"🎯 Unified Investigation Request - Type: {request.investigation_type}")
    
    try:
        result = await unified_service.investigate(request)
        logger.info(f"✅ Unified Investigation Completed - ID: {result.investigation_id}")
        return result.__dict__ if hasattr(result, '__dict__') else result
        
    except Exception as e:
        logger.error(f"❌ Unified Investigation Failed: {e}")
        raise HTTPException(status_code=500, detail=f"Unified investigation failed: {str(e)}")

# NEW: Unified Investigation Streaming Endpoint
@app.post("/investigate/unified/stream")
@traceable(name="unified_investigation_stream_api", tags=["api", "investigation", "unified", "stream"])
async def investigate_unified_stream(
    request: UnifiedInvestigationRequest,
    unified_service: UnifiedInvestigationService = Depends(get_unified_investigation_service),
    _: None = Depends(check_rate_limit)
) -> StreamingResponse:
    """Stream real-time progress for unified investigations (all types)"""
    
    async def generate_unified_progress_stream() -> AsyncGenerator[str, None]:
        """Generate Server-Sent Events for unified investigation progress"""
        
        logger.info(f"🔄 Starting unified streaming investigation - Type: {request.investigation_type}")
        
        try:
            # Stream investigation progress using the unified service
            async for progress_event in unified_service.investigate_stream(request):
                yield f"data: {json.dumps(progress_event)}\n\n"
                
                # Don't delay after completion event
                if progress_event.get('type') == 'complete':
                    break
                    
                await asyncio.sleep(0.1)  # Small delay for better UX
            
        except Exception as e:
            logger.error(f"❌ Unified streaming investigation failed: {e}")
            error_event = {
                'type': 'error',
                'step': 'error',
                'agent': 'system',
                'message': f"Unified investigation failed: {str(e)}",
                'progress': 100,
                'error': True,
                'investigation_type': request.investigation_type
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        generate_unified_progress_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

# NEW: Unified Investigation Types Info
@app.get("/investigate/types")
async def get_investigation_types(
    unified_service: UnifiedInvestigationService = Depends(get_unified_investigation_service)
) -> dict:
    """Get supported investigation types and their requirements"""
    try:
        types = unified_service.get_supported_investigation_types()
        return {
            "investigation_types": types,
            "total_types": len(types),
            "description": "Use POST /investigate/unified with investigation_type field"
        }
    except Exception as e:
        logger.error(f"❌ Failed to get investigation types: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get investigation types: {str(e)}")

# Download Investigation Report
@app.get("/investigate/download/{investigation_id}")
async def download_investigation_report(
    investigation_id: str
) -> Response:
    """Download investigation report as text file"""
    try:
        # This is a simplified approach - in production you'd want to store reports in a database
        # For now, we'll return a formatted report based on investigation ID
        
        # Create a sample report for demonstration
        report_content = f"""FRAUD INVESTIGATION REPORT
Investigation ID: {investigation_id}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

========================================
EXECUTIVE SUMMARY
========================================

This investigation has been completed using the InvestigatorAI multi-agent system.
All fraud detection agents have analyzed the transaction and provided their assessment.

========================================
INVESTIGATION DETAILS
========================================

Investigation ID: {investigation_id}
Status: Completed
Agents Used: 4/4 (Regulatory Research, Evidence Collection, Compliance Check, Report Generation)

========================================
DISCLAIMER
========================================

This report was generated by InvestigatorAI for investigative purposes.
All findings should be reviewed by qualified compliance professionals.

For the complete investigation results, please refer to the main investigation interface.
"""
        
        # Create response with proper headers for download
        headers = {
            "Content-Disposition": f"attachment; filename=investigation_report_{investigation_id}.txt",
            "Content-Type": "text/plain"
        }
        
        return Response(
            content=report_content,
            headers=headers,
            media_type="text/plain"
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to generate download for {investigation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report download: {str(e)}")

# Vector search endpoint
@app.get("/search", response_model=list[VectorSearchResult])
@traceable(name="search_documents_api", tags=["api", "search", "vector", "documents"])
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

# Exchange rate endpoint
@app.get("/exchange-rate", response_model=AgentToolResponse)
async def get_exchange_rate(
    from_currency: str,
    to_currency: str = "USD",
    external_api: ExternalAPIService = Depends(get_external_api_service)
) -> AgentToolResponse:
    """Get exchange rate between currencies"""
    
    try:
        result = external_api.get_exchange_rate(from_currency, to_currency)
        
        return AgentToolResponse(
            result=result,
            source="ExchangeRates-API",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Exchange rate lookup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Exchange rate lookup failed: {str(e)}")

# Web search endpoint
@app.get("/web-search", response_model=AgentToolResponse)
async def search_web(
    query: str,
    max_results: int = 5,
    external_api: ExternalAPIService = Depends(get_external_api_service)
) -> AgentToolResponse:
    """Search the web using Tavily"""
    logger.info(f"🌐 API endpoint called: /web-search - Query: '{query}', Max results: {max_results}")
    
    try:
        logger.info(f"📡 Calling Tavily search service...")
        result = external_api.search_web(query, max_results)
        
        response = AgentToolResponse(
            result=result,
            source="Tavily",
            timestamp=datetime.now()
        )
        
        logger.info(f"✅ API endpoint /web-search completed successfully for query: '{query}'")
        return response
        
    except Exception as e:
        logger.error(f"❌ Web search API endpoint failed for query '{query}': {e}")
        raise HTTPException(status_code=500, detail=f"Web search failed: {str(e)}")

# ArXiv search endpoint
@app.get("/arxiv-search", response_model=AgentToolResponse)
async def search_arxiv(
    query: str,
    max_results: int = 4,
    external_api: ExternalAPIService = Depends(get_external_api_service)
) -> AgentToolResponse:
    """Search ArXiv for research papers"""
    
    try:
        result = external_api.search_arxiv(query, max_results)
        
        return AgentToolResponse(
            result=result,
            source="ArXiv",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"ArXiv search failed: {e}")
        raise HTTPException(status_code=500, detail=f"ArXiv search failed: {str(e)}")

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