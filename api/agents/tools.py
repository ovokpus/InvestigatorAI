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
    """Search regulatory documents for fraud investigation guidance and return summarized insights."""
    vector_store = VectorStoreManager.get_instance()
    
    if not vector_store or not vector_store.is_initialized:
        return "Vector database not available. Cannot search regulatory documents."
    
    try:
        results = vector_store.search(query, k=max_results)
        
        if not results:
            return f"No regulatory documents found for query: {query}"
        
        # Process and summarize results instead of returning raw content
        summarized_insights = []
        seen_insights = set()
        
        for i, result in enumerate(results, 1):
            filename = result.metadata.filename
            category = result.metadata.content_category
            content = result.content
            
            # Extract key insights instead of showing full content
            key_insights = _extract_regulatory_insights(content, category)
            
            # Avoid duplicates
            insight_key = key_insights[:100]  # First 100 chars for deduplication
            if insight_key not in seen_insights:
                seen_insights.add(insight_key)
                summarized_insights.append(
                    f"{i}. {filename} ({category}):\n   {key_insights}"
                )
        
        if not summarized_insights:
            return "Found documents but could not extract relevant insights."
            
        return "\n\n".join(summarized_insights)
        
    except Exception as e:
        return f"Error searching regulatory documents: {e}"

def _extract_regulatory_insights(content: str, category: str) -> str:
    """Extract key regulatory insights from document content"""
    if not content:
        return "No content available"
    
    # Split into sentences and find key regulatory information
    sentences = content.split('.')
    key_sentences = []
    
    # Look for sentences containing key regulatory terms
    important_terms = [
        'SAR', 'CTR', 'suspicious activity', 'filing', 'required', 'within', 'days',
        'threshold', 'report', 'compliance', 'violation', 'penalty', 'must',
        'shall', 'CFR', 'FinCEN', 'OFAC', 'sanction', 'high-risk', 'enhanced due diligence'
    ]
    
    for sentence in sentences[:10]:  # Check first 10 sentences
        sentence = sentence.strip()
        if (len(sentence) > 30 and 
            any(term.lower() in sentence.lower() for term in important_terms) and
            sentence.count(' ') > 5):  # Ensure it's a substantial sentence
            key_sentences.append(sentence)
            if len(key_sentences) >= 2:  # Limit to 2 key insights per document
                break
    
    if key_sentences:
        return '. '.join(key_sentences) + '.'
    else:
        # Fallback: return first coherent part of content (max 200 chars)
        clean_content = content.replace('\n', ' ').strip()
        if len(clean_content) > 200:
            # Find a good breaking point near 200 chars
            break_point = clean_content.rfind(' ', 0, 200)
            if break_point > 100:
                return clean_content[:break_point] + '...'
        return clean_content[:200] + '...' if len(clean_content) > 200 else clean_content

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