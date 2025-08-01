"""Configuration service for loading JSON data for fraud investigation"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class ConfigurationService:
    """Service for loading and managing configuration data from JSON files"""
    
    def __init__(self, config_path: str = "data/configs"):
        self.config_path = Path(config_path)
        self._cache = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all configuration files into cache"""
        if not self.config_path.exists():
            print(f"⚠️ Config path not found: {self.config_path}")
            return
        
        config_files = {
            'fatf_jurisdictions': 'fatf_jurisdictions_*.json',
            'fincen_advisories': 'fincen_advisories_*.json', 
            'bsa_requirements': 'bsa_filing_requirements_*.json',
            'gto_orders': 'fincen_gto_orders_*.json',
            'exchange_rates': 'exchange_rates_*.json'
        }
        
        for config_name, pattern in config_files.items():
            files = list(self.config_path.glob(pattern))
            if files:
                # Get the most recent file
                latest_file = max(files, key=lambda f: f.stat().st_mtime)
                try:
                    with open(latest_file, 'r') as f:
                        self._cache[config_name] = json.load(f)
                    print(f"✅ Loaded {config_name} from {latest_file.name}")
                except Exception as e:
                    print(f"❌ Failed to load {config_name}: {e}")
    
    def get_high_risk_jurisdictions(self) -> List[str]:
        """Get high-risk and monitored jurisdictions from FATF data"""
        fatf_data = self._cache.get('fatf_jurisdictions', {})
        bsa_data = self._cache.get('bsa_requirements', {})
        
        high_risk = fatf_data.get('high_risk', [])
        monitored = fatf_data.get('monitored', [])
        bsa_high_risk = bsa_data.get('high_risk_jurisdictions', [])
        
        # Combine all high-risk jurisdictions
        all_high_risk = list(set(high_risk + monitored + bsa_high_risk))
        return all_high_risk
    
    def get_filing_requirements(self) -> Dict[str, Any]:
        """Get BSA filing requirements and thresholds"""
        return self._cache.get('bsa_requirements', {
            'ctr_threshold': 10000,
            'sar_threshold': 5000,
            'filing_deadlines': {
                'sar': '30 days',
                'ctr': '15 days'
            }
        })
    
    def get_fincen_advisories(self) -> List[Dict[str, Any]]:
        """Get FinCEN advisories with risk indicators"""
        return self._cache.get('fincen_advisories', [])
    
    def get_gto_orders(self) -> List[Dict[str, Any]]:
        """Get FinCEN Geographic Targeting Orders"""
        return self._cache.get('gto_orders', [])
    
    def get_exchange_rate(self, from_currency: str, to_currency: str = "USD") -> Optional[float]:
        """Get exchange rate from cached data"""
        exchange_data = self._cache.get('exchange_rates', {})
        rates = exchange_data.get('rates', {})
        
        if from_currency == to_currency:
            return 1.0
        
        # Simple conversion via USD
        from_rate = rates.get(from_currency.upper())
        to_rate = rates.get(to_currency.upper(), 1.0)  # Default to USD
        
        if from_rate and to_rate:
            return to_rate / from_rate
        
        return None
    
    def check_suspicious_indicators(self, transaction_details: Dict[str, Any]) -> List[str]:
        """Check for suspicious activity indicators from FinCEN advisories"""
        advisories = self.get_fincen_advisories()
        found_indicators = []
        
        amount = transaction_details.get('amount', 0)
        description = transaction_details.get('description', '').lower()
        
        for advisory in advisories:
            for indicator in advisory.get('risk_indicators', []):
                indicator_lower = indicator.lower()
                
                # Check for specific patterns
                if 'cash deposits under reporting thresholds' in indicator_lower and amount < 10000:
                    found_indicators.append(f"Below reporting threshold (Advisory: {advisory['title']})")
                elif 'cryptocurrency' in indicator_lower and 'crypto' in description:
                    found_indicators.append(f"Cryptocurrency indicator (Advisory: {advisory['title']})")
                elif 'unusual geographic patterns' in indicator_lower:
                    country = transaction_details.get('country_to', '')
                    if country in self.get_high_risk_jurisdictions():
                        found_indicators.append(f"High-risk jurisdiction (Advisory: {advisory['title']})")
        
        return found_indicators
    
    def calculate_risk_score(self, transaction_details: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive risk score using configuration data"""
        amount = transaction_details.get('amount', 0)
        country = transaction_details.get('country_to', '')
        customer_risk = transaction_details.get('customer_risk_rating', 'Medium')
        account_type = transaction_details.get('account_type', 'Personal')
        
        risk_score = 0.0
        risk_factors = []
        
        # Amount-based risk
        requirements = self.get_filing_requirements()
        ctr_threshold = requirements.get('ctr_threshold', 10000)
        
        if amount >= 100000:
            risk_score += 0.4
            risk_factors.append("Large amount (≥$100K)")
        elif amount >= 50000:
            risk_score += 0.3
            risk_factors.append("Moderate amount ($50K-$100K)")
        elif amount >= ctr_threshold:
            risk_score += 0.2
            risk_factors.append(f"CTR threshold amount (≥${ctr_threshold:,})")
        
        # Country risk using real data
        high_risk_countries = self.get_high_risk_jurisdictions()
        if country in high_risk_countries:
            risk_score += 0.3
            risk_factors.append(f"High-risk jurisdiction ({country})")
        
        # Customer risk
        if customer_risk.upper() == "HIGH" or customer_risk.upper() == "HIGH RISK":
            risk_score += 0.3
            risk_factors.append("High-risk customer rating")
        elif customer_risk.upper() == "MEDIUM":
            risk_score += 0.1
            risk_factors.append("Medium-risk customer rating")
        
        # Account type
        if account_type.upper() == "BUSINESS":
            risk_score += 0.1
            risk_factors.append("Business account complexity")
        
        # Suspicious indicators
        suspicious_indicators = self.check_suspicious_indicators(transaction_details)
        if suspicious_indicators:
            risk_score += 0.2
            risk_factors.extend(suspicious_indicators)
        
        # Cap at 1.0
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "HIGH RISK"
        elif risk_score >= 0.4:
            risk_level = "MEDIUM RISK"
        else:
            risk_level = "LOW RISK"
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'suspicious_indicators': suspicious_indicators
        }
    
    def get_compliance_requirements(self, transaction_details: Dict[str, Any], risk_analysis: Dict[str, Any]) -> List[str]:
        """Get specific compliance requirements based on transaction and risk"""
        requirements = []
        amount = transaction_details.get('amount', 0)
        country = transaction_details.get('country_to', '')
        risk_score = risk_analysis.get('risk_score', 0)
        
        filing_reqs = self.get_filing_requirements()
        ctr_threshold = filing_reqs.get('ctr_threshold', 10000)
        sar_threshold = filing_reqs.get('sar_threshold', 5000)
        
        # CTR requirements
        if amount >= ctr_threshold:
            deadline = filing_reqs.get('filing_deadlines', {}).get('ctr', '15 days')
            requirements.append(f"CTR (Currency Transaction Report) required - file within {deadline}")
        
        # SAR requirements
        if risk_score >= 0.5:
            deadline = filing_reqs.get('filing_deadlines', {}).get('sar', '30 days')
            requirements.append(f"SAR (Suspicious Activity Report) required - file within {deadline}")
        elif amount >= sar_threshold and risk_score >= 0.3:
            requirements.append("SAR (Suspicious Activity Report) recommended for review")
        
        # International requirements
        if country and country.upper() not in ['US', 'USA', 'UNITED STATES']:
            requirements.append("OFAC screening required for international transfer")
            if country in self.get_high_risk_jurisdictions():
                requirements.append("Enhanced due diligence required for high-risk jurisdiction")
        
        # GTO requirements
        gto_orders = self.get_gto_orders()
        for gto in gto_orders:
            if amount >= gto.get('threshold', 0) and 'real estate' in transaction_details.get('description', '').lower():
                requirements.append(f"GTO reporting may be required for {gto['location']}")
        
        requirements.append("Maintain transaction records per BSA requirements (5 years)")
        
        return requirements

# Global instance
_config_service = None

def get_config_service() -> ConfigurationService:
    """Get global configuration service instance"""
    global _config_service
    if _config_service is None:
        _config_service = ConfigurationService()
    return _config_service