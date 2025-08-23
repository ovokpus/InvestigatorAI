"""Enhanced Research API Endpoints

This module provides FastAPI endpoints for the enhanced research capabilities,
including multi-source research, iterative investigation, and domain-specific analysis.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
import json

from langsmith import traceable

from ..models.schemas import (
    ResearchRequest, ResearchResponse, ResearchPlanRequest, ResearchPlanResponse,
    ResearchStatusResponse, ResearchSessionListResponse, EntityInvestigationResponse,
    AcademicResearchResponse, SearchResponse, ResearchStatus, MultiSourceSearchRequest
)
from ..agents.research.multi_source_research import MultiSourceResearchService
from ..agents.research.iterative_research import IterativeResearchAgent, ResearchPlanner
from ..agents.research.specialized_research import EnhancedInvestigatorAI, FinancialResearchAgent, AcademicResearchAgent
from ..agents.research.research_state import ResearchStateManager
from ..core.config import Settings

logger = logging.getLogger(__name__)

# Create router for research endpoints
research_router = APIRouter(prefix="/research", tags=["Enhanced Research"])

# Global state for research services
research_services = {
    "multi_source_service": None,
    "iterative_agent": None,
    "enhanced_investigator": None,
    "state_manager": None,
    "research_planner": None
}


def get_research_services():
    """Get research services dependency"""
    if not research_services["multi_source_service"]:
        raise HTTPException(status_code=503, detail="Research services not initialized")
    return research_services


def initialize_research_services(llm, settings: Settings):
    """Initialize all research services"""
    logger.info("🔬 Initializing enhanced research services...")
    
    try:
        # Initialize multi-source research service
        multi_source_service = MultiSourceResearchService(settings)
        research_services["multi_source_service"] = multi_source_service
        
        # Initialize iterative research agent
        iterative_agent = IterativeResearchAgent(llm, multi_source_service, settings)
        research_services["iterative_agent"] = iterative_agent
        
        # Initialize research planner
        research_planner = ResearchPlanner(llm)
        research_services["research_planner"] = research_planner
        
        # Initialize enhanced investigator with specialized agents
        enhanced_investigator = EnhancedInvestigatorAI(llm, multi_source_service, settings)
        research_services["enhanced_investigator"] = enhanced_investigator
        
        # Initialize state manager
        state_manager = ResearchStateManager()
        research_services["state_manager"] = state_manager
        
        logger.info("✅ Enhanced research services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize research services: {e}")
        raise


@research_router.post("/plan", response_model=ResearchPlanResponse)
@traceable(name="generate_research_plan", tags=["research", "planning"])
async def generate_research_plan(
    request: ResearchPlanRequest,
    services: Dict = Depends(get_research_services)
) -> ResearchPlanResponse:
    """Generate a structured research plan for a given topic"""
    logger.info(f"📋 Generating research plan for: {request.topic}")
    
    try:
        research_planner = services["research_planner"]
        
        # Generate research plan
        research_plan = await research_planner.generate_research_plan(
            topic=request.topic,
            context=request.context
        )
        
        # Convert to response format
        from ..agents.research.iterative_research import ResearchSection
        section_responses = []
        for section in research_plan.sections:
            section_response = {
                "name": section.name,
                "description": section.description,
                "research": section.research,
                "content": section.content,
                "queries": section.queries,
                "sources": section.sources,
                "iteration_count": section.iteration_count,
                "quality_score": section.quality_score
            }
            section_responses.append(section_response)
        
        response = ResearchPlanResponse(
            topic=research_plan.topic,
            sections=section_responses,
            research_depth=research_plan.research_depth,
            query_count=research_plan.query_count,
            created_at=research_plan.created_at
        )
        
        logger.info(f"✅ Research plan generated with {len(section_responses)} sections")
        return response
        
    except Exception as e:
        logger.error(f"❌ Research plan generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Research plan generation failed: {str(e)}")


@research_router.post("/investigate", response_model=ResearchResponse)
@traceable(name="enhanced_research_investigation", tags=["research", "investigation"])
async def conduct_enhanced_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    services: Dict = Depends(get_research_services)
) -> ResearchResponse:
    """Conduct enhanced research investigation with domain expertise"""
    logger.info(f"🔍 Starting enhanced research investigation: {request.type}")
    
    try:
        enhanced_investigator = services["enhanced_investigator"]
        state_manager = services["state_manager"]
        
        # Create research session
        research_id = await state_manager.create_research_session(
            topic=request.topic or request.entity_name or "Unknown",
            metadata={
                "type": request.type,
                "entity_name": request.entity_name,
                "entity_type": request.entity_type,
                "field": request.field,
                "context": request.context
            }
        )
        
        # Update status to in progress
        await state_manager.update_research_progress(
            research_id,
            status=ResearchStatus.IN_PROGRESS
        )
        
        # Prepare investigation request
        investigation_request = {
            "type": request.type,
            "topic": request.topic,
            "entity_name": request.entity_name,
            "entity_type": request.entity_type,
            "field": request.field,
            "context": request.context,
            "include_market_analysis": request.include_market_analysis
        }
        
        # Conduct investigation
        result = await enhanced_investigator.investigate_with_domain_expertise(investigation_request)
        
        # Update state with completion
        await state_manager.update_research_progress(
            research_id,
            status=ResearchStatus.COMPLETED
        )
        
        # Prepare response based on research type
        response = ResearchResponse(
            research_id=research_id,
            type=request.type,
            status=ResearchStatus.COMPLETED,
            result=result.get("result"),
            timestamp=datetime.now().isoformat()
        )
        
        # Add type-specific results
        if request.type == "financial" and "result" in result:
            # Convert to response model if needed
            response.financial_result = result["result"]
        elif request.type == "academic" and "result" in result:
            response.academic_result = result["result"]
        elif request.type == "general" and "result" in result:
            response.general_result = result["result"]
        
        logger.info(f"✅ Enhanced research completed: {research_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Enhanced research failed: {e}")
        
        # Update state with error if research_id exists
        if 'research_id' in locals():
            await state_manager.update_research_progress(
                research_id,
                status=ResearchStatus.FAILED,
                error_message=str(e)
            )
        
        raise HTTPException(status_code=500, detail=f"Enhanced research failed: {str(e)}")


@research_router.post("/investigate/stream")
@traceable(name="enhanced_research_stream", tags=["research", "investigation", "stream"])
async def conduct_enhanced_research_stream(
    request: ResearchRequest,
    services: Dict = Depends(get_research_services)
):
    """Stream real-time progress of enhanced research investigation"""
    
    async def generate_research_stream():
        """Generate Server-Sent Events for research progress"""
        
        # Initial progress event
        yield f"data: {json.dumps({'type': 'progress', 'step': 'initializing', 'message': 'Starting enhanced research...', 'progress': 0})}\n\n"
        
        try:
            enhanced_investigator = services["enhanced_investigator"]
            state_manager = services["state_manager"]
            
            # Create research session
            research_id = await state_manager.create_research_session(
                topic=request.topic or request.entity_name or "Unknown",
                metadata={"type": request.type}
            )
            
            yield f"data: {json.dumps({'type': 'progress', 'step': 'planning', 'message': f'Created research session: {research_id}', 'progress': 10})}\n\n"
            
            # Update status
            await state_manager.update_research_progress(research_id, status=ResearchStatus.IN_PROGRESS)
            
            yield f"data: {json.dumps({'type': 'progress', 'step': 'researching', 'message': 'Conducting specialized research...', 'progress': 30})}\n\n"
            
            # Conduct investigation
            investigation_request = {
                "type": request.type,
                "topic": request.topic,
                "entity_name": request.entity_name,
                "entity_type": request.entity_type,
                "field": request.field,
                "context": request.context,
                "include_market_analysis": request.include_market_analysis
            }
            
            result = await enhanced_investigator.investigate_with_domain_expertise(investigation_request)
            
            yield f"data: {json.dumps({'type': 'progress', 'step': 'analyzing', 'message': 'Analyzing research findings...', 'progress': 80})}\n\n"
            
            # Update completion
            await state_manager.update_research_progress(research_id, status=ResearchStatus.COMPLETED)
            
            # Final completion event
            completion_event = {
                'type': 'complete',
                'step': 'completed',
                'message': 'Enhanced research completed successfully',
                'progress': 100,
                'research_id': research_id,
                'result': result
            }
            yield f"data: {json.dumps(completion_event)}\n\n"
            
        except Exception as e:
            logger.error(f"❌ Research streaming failed: {e}")
            error_event = {
                'type': 'error',
                'step': 'error',
                'message': f"Research failed: {str(e)}",
                'progress': 100,
                'error': True
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        generate_research_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


@research_router.get("/status/{research_id}", response_model=ResearchStatusResponse)
async def get_research_status(
    research_id: str,
    services: Dict = Depends(get_research_services)
) -> ResearchStatusResponse:
    """Get status of a research investigation"""
    logger.info(f"📊 Getting status for research: {research_id}")
    
    try:
        state_manager = services["state_manager"]
        status_data = await state_manager.get_research_status(research_id)
        
        if "error" in status_data:
            raise HTTPException(status_code=404, detail=status_data["error"])
        
        return ResearchStatusResponse(**status_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")


@research_router.get("/sessions", response_model=ResearchSessionListResponse)
async def list_research_sessions(
    limit: int = 20,
    status_filter: Optional[str] = None,
    services: Dict = Depends(get_research_services)
) -> ResearchSessionListResponse:
    """List recent research sessions"""
    logger.info(f"📋 Listing research sessions (limit: {limit})")
    
    try:
        state_manager = services["state_manager"]
        
        # Convert status filter
        status_enum = None
        if status_filter:
            try:
                status_enum = ResearchStatus(status_filter)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")
        
        sessions_data = await state_manager.list_research_sessions(limit, status_enum)
        
        # Convert to response models
        sessions = []
        for session_data in sessions_data:
            session = ResearchStatusResponse(**session_data)
            sessions.append(session)
        
        return ResearchSessionListResponse(
            sessions=sessions,
            total_count=len(sessions),
            page=1,
            page_size=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Session listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Session listing failed: {str(e)}")


@research_router.delete("/sessions/{research_id}")
async def cancel_research_session(
    research_id: str,
    services: Dict = Depends(get_research_services)
):
    """Cancel an ongoing research session"""
    logger.info(f"🛑 Cancelling research session: {research_id}")
    
    try:
        state_manager = services["state_manager"]
        await state_manager.cancel_research(research_id)
        
        return {"message": f"Research session {research_id} cancelled successfully"}
        
    except Exception as e:
        logger.error(f"❌ Session cancellation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Session cancellation failed: {str(e)}")


@research_router.post("/multi-source-search", response_model=List[SearchResponse])
@traceable(name="multi_source_search", tags=["research", "search"])
async def multi_source_search(
    request: MultiSourceSearchRequest,
    services: Dict = Depends(get_research_services)
) -> List[SearchResponse]:
    """Perform multi-source search with specified queries"""
    logger.info(f"🔍 Multi-source search: {len(request.queries)} queries across {request.search_apis}")
    
    try:
        multi_source_service = services["multi_source_service"]
        
        # Perform search
        search_responses = await multi_source_service.search_multiple_sources(
            request.queries, request.search_apis, {"max_results": request.max_results}
        )
        
        # Convert to response format
        response_list = []
        for response in search_responses:
            # Convert SearchResult objects to response format
            result_responses = []
            for result in response.results:
                result_response = {
                    "title": result.title,
                    "url": result.url,
                    "content": result.content,
                    "score": result.score,
                    "raw_content": result.raw_content,
                    "source": result.source,
                    "query": result.query
                }
                result_responses.append(result_response)
            
            search_response = SearchResponse(
                query=response.query,
                source=response.source,
                results=result_responses,
                follow_up_questions=response.follow_up_questions,
                answer=response.answer,
                images=response.images,
                error=response.error
            )
            response_list.append(search_response)
        
        logger.info(f"✅ Multi-source search completed - {len(response_list)} responses")
        return response_list
        
    except Exception as e:
        logger.error(f"❌ Multi-source search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Multi-source search failed: {str(e)}")


@research_router.delete("/cleanup")
async def cleanup_old_research(
    days_old: int = 30,
    services: Dict = Depends(get_research_services)
):
    """Clean up old research sessions"""
    logger.info(f"🧹 Cleaning up research sessions older than {days_old} days")
    
    try:
        state_manager = services["state_manager"]
        cleaned_count = await state_manager.cleanup_old_checkpoints(days_old)
        
        return {
            "message": f"Cleaned up {cleaned_count} old research sessions",
            "days_old": days_old,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
