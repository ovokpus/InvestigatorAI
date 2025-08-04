"""External API integrations for InvestigatorAI"""
import os
import json
import requests
import urllib.parse
import xml.etree.ElementTree as ET
import logging
from typing import Dict, Any
from datetime import datetime

from ..core.config import Settings

logger = logging.getLogger(__name__)

class ExternalAPIService:
    """Service for handling external API calls"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def get_exchange_rate(self, from_currency: str, to_currency: str = "USD") -> str:
        """Get exchange rate from local JSON configuration file"""
        logger.info(f"💱 Exchange Rate Request - From: {from_currency} → To: {to_currency}")
        
        try:
            # Path to the exchange rates JSON file
            exchange_rates_file = "data/configs/exchange_rates_20250731_1954.json"
            
            logger.debug(f"📂 Loading exchange rates from: {exchange_rates_file}")
            
            # Check if file exists
            if not os.path.exists(exchange_rates_file):
                logger.error(f"❌ Exchange rates file not found: {exchange_rates_file}")
                return f"Exchange rates configuration file not available"
            
            # Load exchange rates from JSON file
            with open(exchange_rates_file, 'r') as file:
                exchange_data = json.load(file)
            
            base_currency = exchange_data.get('base', 'USD')
            rates = exchange_data.get('rates', {})
            rate_date = exchange_data.get('date', 'Unknown')
            
            logger.debug(f"📊 Loaded exchange rates - Base: {base_currency}, Date: {rate_date}, Currencies: {len(rates)}")
            
            # Normalize currency codes to uppercase
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            
            # Check if currencies are available in the rates
            if from_currency not in rates:
                logger.warning(f"⚠️  Currency '{from_currency}' not found in exchange rates data")
                return f"Currency '{from_currency}' not supported. Available currencies: {', '.join(sorted(rates.keys())[:10])}..."
            
            if to_currency not in rates:
                logger.warning(f"⚠️  Currency '{to_currency}' not found in exchange rates data")
                return f"Currency '{to_currency}' not supported. Available currencies: {', '.join(sorted(rates.keys())[:10])}..."
            
            # Calculate exchange rate (both currencies are relative to USD base)
            from_rate = rates[from_currency]
            to_rate = rates[to_currency]
            
            # Convert: amount_in_from_currency * (1/from_rate) * to_rate = amount_in_to_currency
            # So the rate from_currency -> to_currency is: to_rate / from_rate
            conversion_rate = to_rate / from_rate
            
            logger.info(f"✅ Exchange rate calculated successfully")
            logger.info(f"   💱 {from_currency} → {to_currency}: {conversion_rate:.6f}")
            logger.info(f"   📅 Rate Date: {rate_date}")
            logger.info(f"   📊 Base Currency: {base_currency}")
            
            # Format result with precision
            if conversion_rate >= 1:
                formatted_rate = f"{conversion_rate:.4f}"
            else:
                formatted_rate = f"{conversion_rate:.6f}"
                
            return f"Exchange rate {from_currency} to {to_currency}: {formatted_rate} (as of {rate_date})"
                
        except FileNotFoundError:
            logger.error(f"❌ Exchange rates configuration file not found")
            return f"Exchange rates configuration file not available"
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in exchange rates file: {e}")
            return f"Exchange rates configuration file is corrupted"
        except KeyError as e:
            logger.error(f"❌ Missing required field in exchange rates data: {e}")
            return f"Exchange rates configuration file has invalid structure"
        except ZeroDivisionError:
            logger.error(f"❌ Invalid exchange rate data - division by zero for {from_currency}")
            return f"Invalid exchange rate data for {from_currency}"
        except Exception as e:
            logger.error(f"❌ Exchange rate lookup failed: {e}")
            logger.exception(f"   🔍 Full exception details:")
            return f"Exchange rate lookup failed: {e}"
    
    def search_web(self, query: str, max_results: int = 3) -> str:
        """Search web using Tavily API"""
        logger.info(f"🌐 Tavily Search initiated - Query: '{query}', Max results: {max_results}")
        
        try:
            api_key = self.settings.tavily_search_api_key
            if not api_key:
                logger.warning("❌ Tavily API key not available")
                return "Tavily API key not available"
            
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic"
            }
            
            logger.info(f"🔍 Calling Tavily API: {url}")
            start_time = datetime.now()
            
            response = requests.post(url, json=payload, timeout=30)
            
            end_time = datetime.now()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                logger.info(f"✅ Tavily API success - Retrieved {len(results)} results in {latency_ms:.1f}ms")
                
                if results:
                    formatted_results = []
                    for i, result in enumerate(results, 1):
                        title = result.get('title', 'No title')
                        content = result.get('content', 'No content')  # Show full content
                        url_result = result.get('url', 'No URL')
                        formatted_results.append(f"{i}. {title}\n   {content}\n   Source: {url_result}")
                        logger.debug(f"   Result {i}: {title[:50]}...")
                    
                    result_text = "\n\n".join(formatted_results)
                    logger.info(f"📝 Tavily search completed - {len(results)} results formatted")
                    return result_text
                else:
                    logger.warning(f"🔍 Tavily API returned no results for query: {query}")
                    return f"No results found for query: {query}"
            else:
                logger.error(f"❌ Tavily API error - Status: {response.status_code}, Response: {response.text[:200]}")
                return f"Tavily API error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error(f"⏰ Tavily API timeout after 30s for query: {query}")
            return f"Tavily API timeout for query: {query}"
        except Exception as e:
            logger.error(f"❌ Tavily search failed for query '{query}': {e}")
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