"""LangChain tools for InvestigatorAI agents"""
from langchain_core.tools import tool
from typing import Optional
import logging

from ..services.vector_store import VectorStoreManager
from ..services.external_apis import ExternalAPIService, RiskCalculator, ComplianceChecker
from ..core.config import get_settings

logger = logging.getLogger(__name__)

# Global instances for tools
_external_api_service: Optional[ExternalAPIService] = None
_settings = get_settings()

def initialize_tools(external_api_service: ExternalAPIService):
    """Initialize tools with dependencies"""
    global _external_api_service
    _external_api_service = external_api_service

@tool
def search_regulatory_documents(query: str, max_results: int = 5) -> str:
    """Search regulatory documents for fraud investigation guidance."""
    vector_store = VectorStoreManager.get_instance()
    
    if not vector_store or not vector_store.is_initialized:
        return "Vector database not available. Cannot search regulatory documents."
    
    try:
        results = vector_store.search(query, k=max_results)
        
        if not results:
            return f"No regulatory documents found for query: {query}"
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            filename = result.metadata.filename
            category = result.metadata.content_category
            content_preview = result.content  # Show full content for comprehensive analysis
            
            formatted_results.append(
                f"{i}. {filename} ({category})\n   {content_preview}"
            )
        
        return "\n\n".join(formatted_results)
        
    except Exception as e:
        return f"Error searching regulatory documents: {e}"

@tool
def calculate_transaction_risk(amount: float, country_to: str = "", 
                             customer_risk_rating: str = "Medium", 
                             account_type: str = "Personal") -> str:
    """Calculate risk score for a transaction based on amount, destination, and customer factors."""
    return RiskCalculator.calculate_transaction_risk(
        amount=amount,
        country_to=country_to,
        customer_risk_rating=customer_risk_rating,
        account_type=account_type
    )

@tool
def get_exchange_rate_data(from_currency: str, to_currency: str = "USD") -> str:
    """Retrieve currency exchange rates."""
    if not _external_api_service:
        return "External API service not initialized"
    
    return _external_api_service.get_exchange_rate(from_currency, to_currency)

@tool  
def search_fraud_research(query: str, max_results: int = 2) -> str:
    """Search ArXiv for research papers on fraud detection and financial crime."""
    if not _external_api_service:
        return "External API service not initialized"
    
    return _external_api_service.search_arxiv(query, max_results)

@tool
def check_compliance_requirements(amount: float, risk_score: float, country_to: str = "") -> str:
    """Check SAR/CTR and other compliance obligations for a transaction."""
    return ComplianceChecker.check_compliance_requirements(amount, risk_score, country_to)

@tool
def search_web_intelligence(query: str, max_results: int = 2) -> str:
    """Search the web using Tavily for current fraud intelligence and news."""
    logger.info(f"🔧 Tool called: search_web_intelligence - Query: '{query}', Max results: {max_results}")
    
    if not _external_api_service:
        logger.error("❌ External API service not initialized for web intelligence search")
        return "External API service not initialized"
    
    logger.info(f"📡 Forwarding to Tavily API service...")
    result = _external_api_service.search_web(query, max_results)
    logger.info(f"✅ Web intelligence search completed for query: '{query}'")
    
    return result

# Tool groups for different agent types
REGULATORY_TOOLS = [search_regulatory_documents, search_fraud_research, search_web_intelligence]
EVIDENCE_TOOLS = [calculate_transaction_risk, get_exchange_rate_data, search_web_intelligence]
COMPLIANCE_TOOLS = [check_compliance_requirements, search_regulatory_documents]
REPORT_TOOLS = [search_regulatory_documents, check_compliance_requirements]