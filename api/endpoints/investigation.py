"""Investigation Endpoints Module"""

import logging
import json
import asyncio
from datetime import datetime
from typing import Any, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse, Response
import openai

from api.models.schemas import (
    InvestigationRequest, UnifiedInvestigationRequest
)
from api.core.dependencies import (
    get_fraud_investigation_system, get_unified_investigation_service, 
    check_rate_limit
)
from api.utils.error_handling import handle_openai_error, serialize_langchain_objects
from api.services.memory_optimizer import get_memory_optimizer

logger = logging.getLogger(__name__)

# Create router
investigation_router = APIRouter(prefix="/investigate", tags=["investigation"])

@investigation_router.post("/stream")
async def investigate_fraud_stream(
    request: InvestigationRequest,
    fraud_system: Any = Depends(get_fraud_investigation_system),
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

@investigation_router.post("")
async def investigate_fraud(
    request: InvestigationRequest,
    fraud_system: Any = Depends(get_fraud_investigation_system),
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

@investigation_router.post("/unified")
async def investigate_unified(
    request: UnifiedInvestigationRequest,
    unified_service: Any = Depends(get_unified_investigation_service),
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

@investigation_router.post("/unified/stream")
async def investigate_unified_stream(
    request: UnifiedInvestigationRequest,
    unified_service: Any = Depends(get_unified_investigation_service),
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

@investigation_router.get("/types")
async def get_investigation_types(
    unified_service: Any = Depends(get_unified_investigation_service)
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

@investigation_router.get("/download/{investigation_id}")
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
