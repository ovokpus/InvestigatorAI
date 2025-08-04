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
    """Extract key regulatory insights from document content, filtering out procedural text"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔍 [DEBUG] _extract_regulatory_insights called with category: {category}")
    logger.info(f"🔍 [DEBUG] Input content length: {len(content)} chars")
    logger.info(f"🔍 [DEBUG] Input content preview: {content[:300]}...")
    
    if not content:
        logger.info("🔍 [DEBUG] No content provided, returning fallback")
        return "No content available"
    
    # Aggressive filtering of procedural and administrative text
    procedural_filters = [
        'days after the date',
        'catalog no.',
        'rev.',
        'draft',
        'detroit computing center',
        'p.o. box',
        'check the box',
        'line 1',
        'part v',
        'description of suspicious activity',
        'if you are correcting',
        'complete the report',
        'include the corrected',
        'for items that do not apply',
        'leave blank',
        'supporting documentation',
        'institution must retain',
        'how to make a report',
        'note: if this report',
        'send each completed',
        'filing institutions must',
        'accomplished by the filing',
        'continuing suspicious activity',
        'calendar days after',
        'previously related sar',
        'robberies and burglaries',
        'savings associations',
        'service corporations',
        'missing, counterfeit',
        'pursuant to the requirements'
    ]
    
    # Split into sentences and find analytical insights
    sentences = content.split('.')
    analytical_sentences = []
    
    # Look for sentences with analytical content, not procedural instructions
    analytical_terms = [
        'must comply with', 'according to', 'requires', 'should ensure',
        'analysis shows', 'indicates that', 'research suggests',
        'findings show', 'evidence suggests', 'study reveals',
        'institutions should', 'banks must', 'regulations require',
        'compliance with', 'violation of', 'enforcement action'
    ]
    
    for sentence in sentences:
        sentence = sentence.strip()
        # Skip short sentences or those with procedural content
        if (len(sentence) > 40 and 
            not any(proc.lower() in sentence.lower() for proc in procedural_filters) and
            any(term.lower() in sentence.lower() for term in analytical_terms) and
            sentence.count(' ') > 7):  # Ensure substantial analytical content
            
            # Additional quality checks
            if not sentence.startswith('•') and not sentence.startswith('-'):
                analytical_sentences.append(sentence)
                if len(analytical_sentences) >= 2:  # Limit to 2 insights
                    break
    
    if analytical_sentences:
        return '. '.join(analytical_sentences) + '.'
    else:
        # Enhanced fallback: return professional summary based on category
        if 'BSA' in category or 'AML' in category:
            return "BSA/AML compliance requirements apply to this transaction type."
        elif 'SAR' in category:
            return "Suspicious Activity Report filing requirements and procedures apply."
        elif 'CTR' in category:
            return "Currency Transaction Report filing requirements for transactions over $10,000."
        elif 'OFAC' in category:
            return "OFAC sanctions screening requirements for international transactions."
        else:
            return "Regulatory compliance analysis completed for transaction review."

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