"""External API integrations for InvestigatorAI"""
import os
import requests
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Dict, Any
from datetime import datetime

from ..core.config import Settings

class ExternalAPIService:
    """Service for handling external API calls"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def get_exchange_rate(self, from_currency: str, to_currency: str = "USD") -> str:
        """Get exchange rate from ExchangeRates-API"""
        try:
            api_key = self.settings.exchange_rate_api_key
            if not api_key:
                return f"Exchange rate API key not available"
            
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data['result'] == 'success':
                    rate = data['conversion_rate']
                    return f"Exchange rate {from_currency} to {to_currency}: {rate}"
                else:
                    return f"Error: {data.get('error-type', 'Unknown error')}"
            else:
                return f"HTTP Error: {response.status_code}"
                
        except Exception as e:
            return f"Exchange rate lookup failed: {e}"
    
    def search_web(self, query: str, max_results: int = 3) -> str:
        """Search web using Tavily API"""
        try:
            api_key = self.settings.tavily_search_api_key
            if not api_key:
                return "Tavily API key not available"
            
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic"
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results:
                    formatted_results = []
                    for i, result in enumerate(results, 1):
                        title = result.get('title', 'No title')
                        content = result.get('content', 'No content')  # Show full content
                        formatted_results.append(f"{i}. {title}\n   {content}")
                    
                    return "\n\n".join(formatted_results)
                else:
                    return f"No results found for query: {query}"
            else:
                return f"Tavily API error: {response.status_code}"
                
        except Exception as e:
            return f"Web search failed: {e}"
    
    def search_arxiv(self, query: str, max_results: int = 2) -> str:
        """Search ArXiv for research papers"""
        try:
            # Format query for ArXiv API
            encoded_query = urllib.parse.quote_plus(query)
            url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}"
            
            response = requests.get(url)
            
            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.content)
                
                # Extract entries
                entries = root.findall('{http://www.w3.org/2005/Atom}entry')
                
                if entries:
                    formatted_results = []
                    for i, entry in enumerate(entries, 1):
                        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()  # Show full summary
                        
                        formatted_results.append(f"{i}. {title}\n   Summary: {summary}")
                    
                    return "\n\n".join(formatted_results)
                else:
                    return f"No ArXiv papers found for query: {query}"
            else:
                return f"ArXiv API error: {response.status_code}"
                
        except Exception as e:
            return f"ArXiv search failed: {e}"

class RiskCalculator:
    """Service for calculating transaction risk scores"""
    
    @staticmethod
    def calculate_transaction_risk(amount: float, country_to: str = "", 
                                 customer_risk_rating: str = "Medium", 
                                 account_type: str = "Personal") -> str:
        """Calculate risk score for a transaction"""
        try:
            risk_score = 0.0
            factors = []
            
            # Amount-based risk
            if amount >= 100000:
                risk_score += 0.4
                factors.append("Large amount (≥$100K)")
            elif amount >= 50000:
                risk_score += 0.3
                factors.append("Moderate amount ($50K-$100K)")
            elif amount >= 10000:
                risk_score += 0.2
                factors.append("CTR threshold amount ($10K+)")
            
            # Country risk (simplified)
            high_risk_countries = ['UAE', 'IRAN', 'RUSSIA', 'CHINA', 'AFGHANISTAN', 'SYRIA']
            if country_to.upper() in high_risk_countries:
                risk_score += 0.3
                factors.append("High-risk destination country")
            
            # Customer risk rating
            if customer_risk_rating.upper() == "HIGH":
                risk_score += 0.3
                factors.append("High-risk customer rating")
            elif customer_risk_rating.upper() == "MEDIUM":
                risk_score += 0.1
                factors.append("Medium-risk customer rating")
            
            # Account type risk
            if account_type.upper() == "BUSINESS":
                risk_score += 0.1
                factors.append("Business account (higher complexity)")
            
            # Cap risk score at 1.0
            risk_score = min(risk_score, 1.0)
            
            risk_level = "LOW" if risk_score < 0.3 else "MEDIUM" if risk_score < 0.6 else "HIGH"
            
            return f"Risk Score: {risk_score:.2f} ({risk_level})\nRisk Factors: {', '.join(factors) if factors else 'None identified'}"
            
        except Exception as e:
            return f"Risk calculation failed: {e}"

class ComplianceChecker:
    """Service for checking compliance requirements"""
    
    @staticmethod
    def check_compliance_requirements(amount: float, risk_score: float, country_to: str = "") -> str:
        """Check SAR/CTR and other compliance obligations"""
        requirements = []
        
        if amount >= 10000:
            requirements.append("CTR (Currency Transaction Report) required for transactions ≥$10,000")
        
        if risk_score >= 0.5:
            requirements.append("SAR (Suspicious Activity Report) recommended due to high risk score")
        elif amount >= 5000 and risk_score >= 0.3:
            requirements.append("Consider SAR filing for medium-risk transaction ≥$5,000")
        
        if country_to and country_to.upper() not in ['US', 'USA', 'UNITED STATES']:
            requirements.append("OFAC screening required for international transfers")
            requirements.append("Enhanced due diligence may be required")
        
        requirements.append("Maintain transaction records per BSA requirements")
        
        return "Compliance Requirements:\n" + "\n".join(f"• {req}" for req in requirements)