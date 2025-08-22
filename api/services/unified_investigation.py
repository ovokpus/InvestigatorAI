"""Unified Investigation Service - Single Entry Point for All Investigations

This service consolidates fraud investigation and enhanced research capabilities
into a single, simplified interface while maintaining backward compatibility.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Literal
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langsmith import traceable

from .multi_source_research import MultiSourceResearchService
from .specialized_research import EnhancedInvestigatorAI
from ..agents.multi_agent_system import FraudInvestigationSystem
from ..core.config import Settings
from ..models.schemas import InvestigationRequest, ResearchRequest

logger = logging.getLogger(__name__)


@dataclass
class UnifiedInvestigationRequest:
    """Unified request model supporting both fraud and research investigations"""
    
    # Investigation type routing
    investigation_type: Literal["fraud_transaction", "entity_research", "academic_research", "general_research"]
    
    # Fraud investigation fields (for fraud_transaction type)
    amount: Optional[float] = None
    currency: Optional[str] = "USD"
    description: Optional[str] = None
    customer_name: Optional[str] = None
    account_type: Optional[str] = None
    risk_rating: Optional[str] = None
    country_to: Optional[str] = None
    
    # Research investigation fields (for research types)
    topic: Optional[str] = None
    entity_name: Optional[str] = None
    entity_type: Optional[str] = "company"
    field: Optional[str] = "general"
    context: Optional[str] = ""
    include_market_analysis: bool = False
    
    # Common fields
    priority: str = "normal"  # normal, high, urgent
    metadata: Dict[str, Any] = None


@dataclass
class UnifiedInvestigationResponse:
    """Unified response model for all investigation types"""
    
    investigation_id: str
    investigation_type: str
    status: str
    duration_seconds: float
    
    # Results (one will be populated based on type)
    fraud_result: Optional[Dict[str, Any]] = None
    research_result: Optional[Dict[str, Any]] = None
    
    # Common metadata
    agents_used: List[str] = None
    error_message: Optional[str] = None
    performance_metrics: Dict[str, Any] = None


class UnifiedInvestigationService:
    """Single service for all investigation types with intelligent routing"""
    
    def __init__(self, llm: ChatOpenAI, settings: Settings, 
                 fraud_system: FraudInvestigationSystem,
                 enhanced_investigator: EnhancedInvestigatorAI):
        self.llm = llm
        self.settings = settings
        self.fraud_system = fraud_system
        self.enhanced_investigator = enhanced_investigator
        
        logger.info("🎯 Initialized UnifiedInvestigationService")
        logger.info(f"   ✅ Fraud system: {type(fraud_system).__name__}")
        logger.info(f"   ✅ Enhanced investigator: {type(enhanced_investigator).__name__}")
    
    @traceable(name="unified_investigation", tags=["investigation", "unified"])
    async def investigate(self, request: UnifiedInvestigationRequest) -> UnifiedInvestigationResponse:
        """Route investigation to appropriate service based on type"""
        
        investigation_id = f"UNI_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(request)) % 10000:04d}"
        start_time = datetime.now()
        
        logger.info(f"🎯 Unified Investigation Started - ID: {investigation_id}")
        logger.info(f"   📋 Type: {request.investigation_type}")
        logger.info(f"   ⚡ Priority: {request.priority}")
        
        try:
            # Route to appropriate service
            if request.investigation_type == "fraud_transaction":
                result = await self._investigate_fraud_transaction(request)
                agents_used = ["regulatory_research", "evidence_collection", "compliance_check", "report_generation"]
                
            elif request.investigation_type == "entity_research":
                result = await self._investigate_entity(request)
                agents_used = ["financial_research_agent"]
                
            elif request.investigation_type == "academic_research":
                result = await self._investigate_academic(request)
                agents_used = ["academic_research_agent"]
                
            elif request.investigation_type == "general_research":
                result = await self._investigate_general(request)
                agents_used = ["iterative_research_agent"]
                
            else:
                raise ValueError(f"Unknown investigation type: {request.investigation_type}")
            
            # Calculate performance metrics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Create unified response
            response = UnifiedInvestigationResponse(
                investigation_id=investigation_id,
                investigation_type=request.investigation_type,
                status="completed",
                duration_seconds=duration,
                agents_used=agents_used,
                performance_metrics={
                    "duration_seconds": duration,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                }
            )
            
            # Populate appropriate result
            if request.investigation_type == "fraud_transaction":
                response.fraud_result = result
            else:
                response.research_result = result
            
            logger.info(f"✅ Unified Investigation Completed - ID: {investigation_id}")
            logger.info(f"   ⏱️  Duration: {duration:.2f}s")
            logger.info(f"   🤖 Agents: {len(agents_used)}")
            
            return response
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Unified Investigation Failed - ID: {investigation_id}")
            logger.error(f"   💥 Error: {e}")
            logger.error(f"   ⏱️  Duration before failure: {duration:.2f}s")
            
            return UnifiedInvestigationResponse(
                investigation_id=investigation_id,
                investigation_type=request.investigation_type,
                status="failed",
                duration_seconds=duration,
                error_message=str(e),
                agents_used=[]
            )
    
    async def _investigate_fraud_transaction(self, request: UnifiedInvestigationRequest) -> Dict[str, Any]:
        """Handle fraud transaction investigation using original multi-agent system"""
        logger.info("🚨 Routing to fraud transaction investigation")
        
        # Convert unified request to legacy format
        transaction_details = {
            "amount": request.amount or 0.0,
            "currency": request.currency or "USD",
            "description": request.description or "Wire transfer",
            "customer_name": request.customer_name or "Unknown",
            "account_type": request.account_type or "Personal",
            "customer_risk_rating": request.risk_rating or "Medium",
            "country_to": request.country_to or "Unknown",
            "timestamp": datetime.now().isoformat()
        }
        
        # Use original fraud investigation system
        result = self.fraud_system.investigate_fraud(transaction_details)
        return result
    
    async def _investigate_entity(self, request: UnifiedInvestigationRequest) -> Dict[str, Any]:
        """Handle entity research using enhanced investigation capabilities"""
        logger.info("🏢 Routing to entity research investigation")
        
        # Convert to research request format
        research_request = {
            "type": "financial",
            "entity_name": request.entity_name or request.topic,
            "entity_type": request.entity_type or "company",
            "context": request.context or "",
            "include_market_analysis": request.include_market_analysis
        }
        
        # Use enhanced investigator
        result = await self.enhanced_investigator.investigate_with_domain_expertise(research_request)
        return result
    
    async def _investigate_academic(self, request: UnifiedInvestigationRequest) -> Dict[str, Any]:
        """Handle academic research using enhanced investigation capabilities"""
        logger.info("🎓 Routing to academic research investigation")
        
        research_request = {
            "type": "academic",
            "topic": request.topic or request.entity_name,
            "field": request.field or "general",
            "context": request.context or ""
        }
        
        result = await self.enhanced_investigator.investigate_with_domain_expertise(research_request)
        return result
    
    async def _investigate_general(self, request: UnifiedInvestigationRequest) -> Dict[str, Any]:
        """Handle general research using enhanced investigation capabilities"""
        logger.info("🔍 Routing to general research investigation")
        
        research_request = {
            "type": "general",
            "topic": request.topic or request.entity_name,
            "context": request.context or ""
        }
        
        result = await self.enhanced_investigator.investigate_with_domain_expertise(research_request)
        return result
    
    @traceable(name="unified_investigation_stream", tags=["investigation", "unified", "stream"])
    async def investigate_stream(self, request: UnifiedInvestigationRequest):
        """Stream investigation progress for real-time updates"""
        
        investigation_id = f"STR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(request)) % 10000:04d}"
        
        # Initial progress
        yield {
            "type": "progress",
            "investigation_id": investigation_id,
            "investigation_type": request.investigation_type,
            "step": "routing", 
            "message": f"Routing {request.investigation_type} investigation...",
            "progress": 10
        }
        
        try:
            if request.investigation_type == "fraud_transaction":
                # For fraud investigations, use the existing streaming
                transaction_details = {
                    "amount": request.amount or 0.0,
                    "currency": request.currency or "USD",
                    "description": request.description or "Wire transfer",
                    "customer_name": request.customer_name or "Unknown",
                    "account_type": request.account_type or "Personal",
                    "customer_risk_rating": request.risk_rating or "Medium",
                    "country_to": request.country_to or "Unknown",
                    "timestamp": datetime.now().isoformat()
                }
                
                async for progress in self.fraud_system.investigate_fraud_stream(transaction_details):
                    # Add unified investigation metadata
                    progress["investigation_id"] = investigation_id
                    progress["investigation_type"] = request.investigation_type
                    yield progress
            
            else:
                # For research investigations, provide basic progress updates
                yield {"type": "progress", "investigation_id": investigation_id, "step": "researching", "message": "Conducting enhanced research...", "progress": 50}
                
                # Execute the investigation
                result = await self.investigate(request)
                
                # Final completion
                yield {
                    "type": "complete", 
                    "investigation_id": investigation_id,
                    "step": "completed", 
                    "message": "Investigation completed successfully",
                    "progress": 100,
                    "result": result
                }
                
        except Exception as e:
            yield {
                "type": "error",
                "investigation_id": investigation_id,
                "step": "error",
                "message": f"Investigation failed: {str(e)}",
                "progress": 100,
                "error": True
            }
    
    def get_supported_investigation_types(self) -> List[Dict[str, str]]:
        """Return list of supported investigation types with descriptions"""
        return [
            {
                "type": "fraud_transaction",
                "name": "Fraud Transaction Investigation",
                "description": "Comprehensive fraud analysis using multi-agent system",
                "required_fields": ["amount", "customer_name", "country_to"]
            },
            {
                "type": "entity_research", 
                "name": "Entity Research",
                "description": "Financial entity investigation with AML/compliance focus",
                "required_fields": ["entity_name", "entity_type"]
            },
            {
                "type": "academic_research",
                "name": "Academic Research",
                "description": "Scientific literature analysis and methodology extraction", 
                "required_fields": ["topic", "field"]
            },
            {
                "type": "general_research",
                "name": "General Research",
                "description": "Iterative quality-driven research with multiple sources",
                "required_fields": ["topic"]
            }
        ]


# Factory function for easy initialization
def create_unified_investigation_service(llm: ChatOpenAI, settings: Settings,
                                       fraud_system: FraudInvestigationSystem,
                                       enhanced_investigator: EnhancedInvestigatorAI) -> UnifiedInvestigationService:
    """Factory function to create unified investigation service"""
    return UnifiedInvestigationService(llm, settings, fraud_system, enhanced_investigator)
