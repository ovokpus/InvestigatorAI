"""Pydantic models for InvestigatorAI API"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

# LangGraph State Management
class FraudInvestigationState(TypedDict):
    """State for fraud investigation workflow"""
    messages: List[BaseMessage]
    investigation_id: str
    transaction_details: Dict[str, Any]
    agents_completed: List[str]
    investigation_status: str
    final_decision: str
    next: str

# API Request Models
class InvestigationRequest(BaseModel):
    """Request model for fraud investigation"""
    amount: float = Field(..., description="Transaction amount", gt=0)
    currency: str = Field(default="USD", description="Currency code")
    description: Optional[str] = Field(default="Wire transfer", description="Transaction description")
    customer_name: str = Field(default="Unknown", description="Customer name")
    account_type: str = Field(default="Personal", description="Account type (Personal/Business)")
    risk_rating: str = Field(default="Medium", description="Customer risk rating")
    country_to: str = Field(default="Unknown", description="Destination country")

# API Response Models  
class InvestigationResponse(BaseModel):
    """Response model for fraud investigation"""
    investigation_id: str
    status: str
    final_decision: str
    agents_completed: int
    total_messages: int
    transaction_details: Dict[str, Any]
    all_agents_finished: bool
    error: Optional[str] = None
    full_results: Optional[Dict[str, Any]] = None
    ragas_validated_messages: Optional[List[Dict[str, Any]]] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    api_keys_available: bool
    vector_store_initialized: bool

class AgentToolResponse(BaseModel):
    """Response from agent tools"""
    result: str
    source: str
    timestamp: datetime

# Document Processing Models
class DocumentMetadata(BaseModel):
    """Metadata for processed documents"""
    filename: str
    content_category: str
    source_type: str
    document_type: str
    last_updated: Optional[str] = None

class ProcessedDocument(BaseModel):
    """Processed document with content and metadata"""
    page_content: str
    metadata: DocumentMetadata

class VectorSearchResult(BaseModel):
    """Result from vector similarity search"""
    content: str
    metadata: DocumentMetadata
    similarity_score: Optional[float] = None