"""Pydantic models for InvestigatorAI API"""
from typing import Dict, List, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from enum import Enum

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
    ragas_validated_messages: Optional[List[BaseMessage]] = None

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


# Enhanced Research System Models
class ResearchStatus(str, Enum):
    """Research investigation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SearchAPIType(str, Enum):
    """Currently implemented search APIs for fraud investigation"""
    TAVILY = "tavily"    # Real-time web search and news
    ARXIV = "arxiv"      # Academic/regulatory research papers
    # Future APIs (not yet implemented):
    # PUBMED = "pubmed"     # Medical literature (healthcare fraud only)
    # EXA = "exa"           # Neural search (expensive, unclear benefit)
    # PERPLEXITY = "perplexity"  # AI search (overlaps with existing capabilities)


class ResearchSectionRequest(BaseModel):
    """Request model for individual research section"""
    name: str = Field(..., description="Section name")
    description: str = Field(..., description="Section description")
    research: bool = Field(default=True, description="Whether to perform web research")
    queries: Optional[List[str]] = Field(default=None, description="Specific search queries")


class ResearchPlanRequest(BaseModel):
    """Request model for research plan generation"""
    topic: str = Field(..., description="Research topic")
    context: Optional[str] = Field(default="", description="Additional context")
    sections: Optional[List[ResearchSectionRequest]] = Field(default=None, description="Custom sections")
    research_depth: int = Field(default=2, description="Maximum research iterations", ge=1, le=5)
    query_count: int = Field(default=2, description="Queries per iteration", ge=1, le=10)
    sources: Optional[List[SearchAPIType]] = Field(default=["tavily", "arxiv"], description="Search sources")


class ResearchRequest(BaseModel):
    """Request model for enhanced research investigation"""
    type: Literal["financial", "academic", "general"] = Field(default="general", description="Research type")
    topic: Optional[str] = Field(default=None, description="Research topic")
    entity_name: Optional[str] = Field(default=None, description="Entity to investigate (for financial research)")
    entity_type: Optional[str] = Field(default="company", description="Entity type")
    field: Optional[str] = Field(default="general", description="Academic field (for academic research)")
    context: Optional[str] = Field(default="", description="Additional context")
    include_market_analysis: bool = Field(default=False, description="Include market analysis")
    research_plan: Optional[ResearchPlanRequest] = Field(default=None, description="Custom research plan")


class SearchResultResponse(BaseModel):
    """Individual search result"""
    title: str
    url: str
    content: str
    score: float = 0.0
    raw_content: Optional[str] = None
    source: str = ""
    query: str = ""


class SearchResponse(BaseModel):
    """Search response containing multiple results"""
    query: str
    source: str
    results: List[SearchResultResponse] = Field(default_factory=list)
    follow_up_questions: Optional[List[str]] = None
    answer: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class ResearchSectionResponse(BaseModel):
    """Response model for individual research section"""
    name: str
    description: str
    research: bool
    content: str = ""
    queries: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    iteration_count: int = 0
    quality_score: float = 0.0


class ResearchFeedbackResponse(BaseModel):
    """Feedback from quality assessment"""
    grade: Literal["pass", "fail"]
    missing_aspects: List[str] = Field(default_factory=list)
    follow_up_queries: List[str] = Field(default_factory=list)
    quality_score: float = 0.0
    feedback_text: str = ""


class ResearchPlanResponse(BaseModel):
    """Response model for research plan"""
    topic: str
    sections: List[ResearchSectionResponse] = Field(default_factory=list)
    research_depth: int = 2
    query_count: int = 2
    created_at: datetime = Field(default_factory=datetime.now)


class EntityInvestigationResponse(BaseModel):
    """Response from entity investigation"""
    entity_name: str
    entity_type: str
    risk_level: str
    findings: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    compliance_issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    investigation_date: datetime
    confidence_score: float = 0.0


class AcademicResearchResponse(BaseModel):
    """Response from academic research"""
    topic: str
    papers_found: int = 0
    key_findings: List[str] = Field(default_factory=list)
    methodologies: List[str] = Field(default_factory=list)
    future_research: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    research_gaps: List[str] = Field(default_factory=list)


class ResearchStatusResponse(BaseModel):
    """Response model for research status"""
    research_id: str
    topic: str
    status: ResearchStatus
    progress_percentage: float = 0.0
    completed_sections: int = 0
    total_sections: int = 0
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None


class ResearchResponse(BaseModel):
    """Enhanced research response model"""
    research_id: str
    type: Literal["financial", "academic", "general"]
    status: ResearchStatus
    result: Optional[Dict[str, Any]] = None
    financial_result: Optional[EntityInvestigationResponse] = None
    academic_result: Optional[AcademicResearchResponse] = None
    general_result: Optional[ResearchPlanResponse] = None
    timestamp: datetime
    error: Optional[str] = None


class ResearchSessionListResponse(BaseModel):
    """Response for listing research sessions"""
    sessions: List[ResearchStatusResponse] = Field(default_factory=list)
    total_count: int = 0
    page: int = 1
    page_size: int = 20