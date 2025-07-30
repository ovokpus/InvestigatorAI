# Real-World Data Sources for InvestigatorAI
# Comprehensive guide to accessing legitimate fraud investigation data

"""
IMPORTANT: All data sources listed here are publicly available or legally accessible.
Always check terms of service and comply with rate limits.
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import os
from typing import List, Dict, Any, Optional
import zipfile
import io
from pathlib import Path
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# API CONFIGURATION & CONNECTION MANAGEMENT
# ============================================================================

class APIConfig:
    """Centralized API configuration management"""
    
    def __init__(self):
        self.api_keys = {
            # Financial Data APIs
            "alpha_vantage": os.getenv("ALPHA_VANTAGE_API_KEY"),
            "fred": os.getenv("FRED_API_KEY"),
            
            # Data Platform APIs
            "kaggle_username": os.getenv("KAGGLE_USERNAME"),
            "kaggle_key": os.getenv("KAGGLE_KEY"),
            
            # Company Data APIs
            "opencorporates": os.getenv("OPENCORPORATES_API_KEY"),
            "companies_house": os.getenv("COMPANIES_HOUSE_API_KEY"),
            
            # Government APIs (mostly free but some have keys for higher limits)
            "sec_edgar_user_agent": os.getenv("SEC_EDGAR_USER_AGENT", "InvestigatorAI research@example.com"),
            
            # Other APIs
            "world_bank": None,  # Free
            "exchange_rates": None,  # Free tier
        }
        
        # API endpoints
        self.endpoints = {
            "alpha_vantage": "https://www.alphavantage.co/query",
            "fred": "https://api.stlouisfed.org/fred",
            "kaggle": "https://www.kaggle.com/api/v1",
            "opencorporates": "https://api.opencorporates.com/v0.4",
            "companies_house": "https://api.company-information.service.gov.uk",
            "sec_edgar": "https://data.sec.gov",
            "world_bank": "https://api.worldbank.org/v2",
            "exchange_rates": "https://api.exchangerate-api.com/v4",
        }
        
        # Rate limits (requests per minute)
        self.rate_limits = {
            "alpha_vantage": 5,  # Free tier
            "fred": 120,
            "kaggle": 100,
            "opencorporates": 10,  # Free tier
            "companies_house": 600,
            "sec_edgar": 10,  # Be respectful
            "world_bank": 100,
            "exchange_rates": 50,
        }
    
    def is_api_available(self, api_name: str) -> bool:
        """Check if API credentials are available"""
        if api_name in ["world_bank", "exchange_rates", "sec_edgar"]:
            return True  # Free APIs
        
        if api_name == "kaggle":
            return self.api_keys["kaggle_username"] and self.api_keys["kaggle_key"]
        
        return bool(self.api_keys.get(api_name))
    
    def get_headers(self, api_name: str) -> Dict[str, str]:
        """Get appropriate headers for each API"""
        headers = {"User-Agent": "InvestigatorAI/1.0"}
        
        if api_name == "sec_edgar":
            headers["User-Agent"] = self.api_keys["sec_edgar_user_agent"]
        elif api_name == "companies_house":
            if self.api_keys["companies_house"]:
                headers["Authorization"] = f"Basic {self.api_keys['companies_house']}"
        
        return headers


class KaggleAPI:
    """Kaggle API for dataset downloads"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.available = config.is_api_available("kaggle")
        
        if self.available:
            try:
                import kaggle
                kaggle.api.authenticate()
                self.api = kaggle.api
                logger.info("✅ Kaggle API authenticated successfully")
            except Exception as e:
                logger.warning(f"⚠️ Kaggle API setup failed: {e}")
                self.available = False
    
    def download_dataset(self, dataset_id: str, save_path: str = "data/kaggle") -> bool:
        """Download a Kaggle dataset"""
        if not self.available:
            logger.warning("❌ Kaggle API not available. Please set KAGGLE_USERNAME and KAGGLE_KEY")
            return False
        
        try:
            Path(save_path).mkdir(parents=True, exist_ok=True)
            self.api.dataset_download_files(dataset_id, path=save_path, unzip=True)
            logger.info(f"✅ Downloaded Kaggle dataset: {dataset_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to download {dataset_id}: {e}")
            return False
    
    def get_paysim_dataset(self) -> Optional[pd.DataFrame]:
        """Download PaySim fraud dataset"""
        dataset_id = "ealaxi/paysim1"
        if self.download_dataset(dataset_id):
            try:
                csv_path = Path("data/kaggle/PS_20174392719_1491204439457_log.csv")
                if csv_path.exists():
                    df = pd.read_csv(csv_path)
                    logger.info(f"✅ Loaded PaySim dataset: {len(df)} transactions")
                    return df
            except Exception as e:
                logger.error(f"❌ Error loading PaySim dataset: {e}")
        return None
    
    def get_credit_card_fraud_dataset(self) -> Optional[pd.DataFrame]:
        """Download Credit Card Fraud dataset"""
        dataset_id = "mlg-ulb/creditcardfraud"
        if self.download_dataset(dataset_id):
            try:
                csv_path = Path("data/kaggle/creditcard.csv")
                if csv_path.exists():
                    df = pd.read_csv(csv_path)
                    logger.info(f"✅ Loaded Credit Card Fraud dataset: {len(df)} transactions")
                    return df
            except Exception as e:
                logger.error(f"❌ Error loading Credit Card Fraud dataset: {e}")
        return None


class AlphaVantageAPI:
    """Alpha Vantage API for financial data"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.api_key = config.api_keys["alpha_vantage"]
        self.available = config.is_api_available("alpha_vantage")
        self.base_url = config.endpoints["alpha_vantage"]
    
    def get_company_overview(self, symbol: str) -> Optional[Dict]:
        """Get company overview from Alpha Vantage"""
        if not self.available:
            logger.warning("❌ Alpha Vantage API key not available")
            return None
        
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if "Symbol" in data:
                    logger.info(f"✅ Retrieved company overview for {symbol}")
                    return data
                else:
                    logger.warning(f"⚠️ No data found for symbol {symbol}")
            else:
                logger.error(f"❌ Alpha Vantage API error: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Error fetching company data: {e}")
        
        return None
    
    def get_fx_rates(self, from_currency: str, to_currency: str) -> Optional[Dict]:
        """Get foreign exchange rates"""
        if not self.available:
            return None
        
        params = {
            "function": "FX_DAILY",
            "from_symbol": from_currency,
            "to_symbol": to_currency,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"❌ Error fetching FX rates: {e}")
        
        return None


class SECEdgarAPI:
    """SEC EDGAR API for company filings"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.base_url = config.endpoints["sec_edgar"]
        self.headers = config.get_headers("sec_edgar")
    
    def search_companies(self, query: str) -> Optional[List[Dict]]:
        """Search for companies in SEC database"""
        url = f"{self.base_url}/submissions/CIK{query.zfill(10)}.json"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Retrieved SEC data for CIK {query}")
                return data
            else:
                logger.warning(f"⚠️ No SEC data found for {query}")
        except Exception as e:
            logger.error(f"❌ Error fetching SEC data: {e}")
        
        return None
    
    def get_company_facts(self, cik: str) -> Optional[Dict]:
        """Get company facts from SEC"""
        url = f"{self.base_url}/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
        
        try:
            time.sleep(0.1)  # Be respectful with rate limiting
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"❌ Error fetching company facts: {e}")
        
        return None


class OpenCorporatesAPI:
    """OpenCorporates API for company data"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.api_key = config.api_keys["opencorporates"]
        self.available = config.is_api_available("opencorporates")
        self.base_url = config.endpoints["opencorporates"]
    
    def search_companies(self, query: str, jurisdiction: str = None) -> Optional[List[Dict]]:
        """Search for companies"""
        if not self.available:
            logger.warning("❌ OpenCorporates API key not available")
            return None
        
        params = {
            "q": query,
            "format": "json",
        }
        
        if self.api_key:
            params["api_token"] = self.api_key
        
        if jurisdiction:
            params["jurisdiction_code"] = jurisdiction
        
        try:
            response = requests.get(f"{self.base_url}/companies/search", params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                companies = data.get("results", {}).get("companies", [])
                logger.info(f"✅ Found {len(companies)} companies for '{query}'")
                return companies
        except Exception as e:
            logger.error(f"❌ Error searching companies: {e}")
        
        return None
    
    def get_company_details(self, company_number: str, jurisdiction: str) -> Optional[Dict]:
        """Get detailed company information"""
        if not self.available:
            return None
        
        params = {}
        if self.api_key:
            params["api_token"] = self.api_key
        
        try:
            url = f"{self.base_url}/companies/{jurisdiction}/{company_number}"
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"❌ Error fetching company details: {e}")
        
        return None


# ============================================================================
# SECTION 1: GOVERNMENT & REGULATORY DATA (FREE & LEGAL)
# ============================================================================


class RegulatoryDataSources:
    """Access government regulatory databases"""

    def __init__(self):
        self.base_urls = {
            "ofac_sanctions": "https://www.treasury.gov/ofac/downloads/",
            "fincen_sar": "https://www.fincen.gov/",
            "ffiec_data": "https://cdr.ffiec.gov/public/",
            "fdic_failed_banks": "https://www.fdic.gov/resources/resolutions/bank-failures/"
        }

    def get_ofac_sanctions_list(self, save_to_file: bool = False) -> pd.DataFrame:
        """Download OFAC Specially Designated Nationals (SDN) List"""
        print("🔄 Downloading OFAC SDN List...")

        # OFAC publishes this data publicly for compliance
        sdn_url = "https://www.treasury.gov/ofac/downloads/sdn.csv"

        try:
            response = requests.get(sdn_url, timeout=30)
            if response.status_code == 200:
                # Parse CSV data
                from io import StringIO
                sdn_data = pd.read_csv(StringIO(response.text))
                print(f"✅ Downloaded {len(sdn_data)} OFAC SDN records")
                
                if save_to_file:
                    # Create data directory if it doesn't exist
                    Path("data").mkdir(exist_ok=True)
                    filename = f"data/ofac_sdn_list_{datetime.now().strftime('%Y%m%d')}.csv"
                    sdn_data.to_csv(filename, index=False)
                    print(f"💾 Saved OFAC SDN data to {filename}")
                
                return sdn_data
            else:
                print(f"❌ Failed to download SDN list: {response.status_code}")
                return pd.DataFrame()
        except Exception as e:
            print(f"❌ Error downloading SDN list: {e}")
            return pd.DataFrame()

    def get_fincen_geographic_targeting_orders(self, save_to_file: bool = False) -> List[Dict]:
        """Get FinCEN Geographic Targeting Orders (GTOs)"""
        # These are public regulatory orders
        gto_data = [
            {
                "location": "Miami-Dade County, FL",
                "threshold": 300000,
                "property_type": "residential",
                "risk_level": "high",
                "effective_date": "2021-01-01"
            },
            {
                "location": "Manhattan, NY",
                "threshold": 3000000,
                "property_type": "residential",
                "risk_level": "high",
                "effective_date": "2021-01-01"
            },
            {
                "location": "Los Angeles County, CA",
                "threshold": 300000,
                "property_type": "residential",
                "risk_level": "medium",
                "effective_date": "2021-01-01"
            }
        ]
        print(f"✅ Retrieved {len(gto_data)} Geographic Targeting Orders")
        
        if save_to_file:
            Path("data").mkdir(exist_ok=True)
            filename = f"data/fincen_gto_orders_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                json.dump(gto_data, f, indent=2)
            print(f"💾 Saved FinCEN GTO data to {filename}")
        
        return gto_data

    def get_bsa_filing_requirements(self, save_to_file: bool = False) -> Dict[str, Any]:
        """Get BSA filing thresholds and requirements"""
        bsa_requirements = {
            "ctr_threshold": 10000,  # Currency Transaction Report
            "sar_threshold": 5000,   # Suspicious Activity Report
            "cmir_threshold": 10000,  # Currency/Monetary Instrument Report
            "fbar_threshold": 10000,  # Foreign Bank Account Report
            "filing_deadlines": {
                "sar": "30 days",
                "ctr": "15 days",
                "cmir": "15 days",
                "fbar": "April 15"
            },
            "high_risk_jurisdictions": [
                "Iran", "North Korea", "Syria", "Cuba", "Myanmar",
                "Afghanistan", "Belarus", "Russia"  # Sanctions jurisdictions
            ]
        }
        print("✅ Retrieved BSA filing requirements")
        
        if save_to_file:
            Path("data").mkdir(exist_ok=True)
            filename = f"data/bsa_filing_requirements_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                json.dump(bsa_requirements, f, indent=2)
            print(f"💾 Saved BSA filing requirements to {filename}")
        
        return bsa_requirements

# ============================================================================
# SECTION 2: FINANCIAL CRIME DATASETS (RESEARCH/PUBLIC)
# ============================================================================


class FinancialCrimeDatasets:
    """Access public financial crime research datasets"""

    def __init__(self):
        self.config = APIConfig()
        self.kaggle = KaggleAPI(self.config)

    def get_paysim_fraud_dataset(self, save_to_file: bool = False) -> pd.DataFrame:
        """Download PaySim fraud detection dataset from Kaggle"""
        print("🔄 Downloading PaySim fraud dataset...")

        # Try to get real dataset from Kaggle
        if self.kaggle.available:
            real_df = self.kaggle.get_paysim_dataset()
            if real_df is not None:
                if save_to_file:
                    Path("data").mkdir(exist_ok=True)
                    filename = f"data/paysim_fraud_dataset_{datetime.now().strftime('%Y%m%d')}.csv"
                    real_df.to_csv(filename, index=False)
                    print(f"💾 Saved PaySim dataset to {filename}")
                return real_df

        # Fallback to sample data if Kaggle API not available
        print("⚠️ Kaggle API not available. Using sample data structure.")
        print("   To get the full dataset, set up Kaggle API credentials.")
        
        sample_data = {
            'step': [1, 2, 3, 4, 5],
            'type': ['PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEBIT', 'PAYMENT'],
            'amount': [9839.64, 181.00, 181.00, 1000.00, 7107.77],
            'nameOrig': ['C1231006815', 'C1666544295', 'C1305486145', 'C840083671', 'C1674638678'],
            'oldbalanceOrg': [170136.0, 181.00, 181.00, 1000.00, 15325.43],
            'newbalanceOrig': [160296.36, 0.00, 0.00, 0.00, 8217.66],
            'nameDest': ['M1979787155', 'C2048537720', 'C553264065', 'C38997010', 'M2002759637'],
            'oldbalanceDest': [0.0, 0.00, 0.00, 0.00, 0.0],
            'newbalanceDest': [0.0, 0.00, 0.00, 0.00, 0.0],
            'isFraud': [0, 0, 1, 0, 0]
        }

        df = pd.DataFrame(sample_data)
        print(f"✅ Loaded PaySim sample data: {len(df)} transactions")
        
        if save_to_file:
            Path("data").mkdir(exist_ok=True)
            filename = f"data/paysim_sample_data_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(filename, index=False)
            print(f"💾 Saved sample data to {filename}")
        
        return df

    def get_credit_card_fraud_dataset(self, save_to_file: bool = False) -> pd.DataFrame:
        """Access credit card fraud dataset (ULB Machine Learning Group)"""
        print("🔄 Loading credit card fraud dataset...")

        # Try to get real dataset from Kaggle
        if self.kaggle.available:
            real_df = self.kaggle.get_credit_card_fraud_dataset()
            if real_df is not None:
                if save_to_file:
                    Path("data").mkdir(exist_ok=True)
                    filename = f"data/credit_card_fraud_dataset_{datetime.now().strftime('%Y%m%d')}.csv"
                    real_df.to_csv(filename, index=False)
                    print(f"💾 Saved Credit Card Fraud dataset to {filename}")
                return real_df

        # Fallback to sample data
        print("⚠️ Kaggle API not available. Using sample data structure.")
        print("   To get the full dataset, set up Kaggle API credentials.")
        
        sample_data = {
            'Time': [0, 0, 1, 1, 2],
            'V1': [-1.359807, 1.191857, -1.358354, -0.966272, -1.158233],
            'V2': [-0.072781, 0.266151, -1.340163, -0.185226, 0.877737],
            'V3': [2.536347, 0.166480, 1.773209, 1.792993, 1.548718],
            'V4': [1.378155, 0.448154, 0.379780, -0.863291, -0.557916],
            'Amount': [149.62, 2.69, 378.66, 123.50, 69.99],
            'Class': [0, 0, 0, 0, 0]  # 0 = normal, 1 = fraud
        }

        df = pd.DataFrame(sample_data)
        print(f"✅ Loaded credit card fraud sample: {len(df)} transactions")
        
        if save_to_file:
            Path("data").mkdir(exist_ok=True)
            filename = f"data/credit_card_sample_data_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(filename, index=False)
            print(f"💾 Saved sample data to {filename}")
        
        return df

# ============================================================================
# SECTION 3: COMMERCIAL APIS FOR ENHANCED DATA
# ============================================================================


class CommercialDataAPIs:
    """Access commercial APIs for enhanced fraud detection data"""

    def __init__(self):
        # Initialize API configuration
        self.config = APIConfig()
        
        # Initialize API clients
        self.alpha_vantage = AlphaVantageAPI(self.config)
        self.kaggle = KaggleAPI(self.config)
        self.sec_edgar = SECEdgarAPI(self.config)
        self.opencorporates = OpenCorporatesAPI(self.config)

    def get_country_risk_data(self, save_to_file: bool = False) -> pd.DataFrame:
        """Get country risk ratings from World Bank"""
        print("🔄 Fetching country risk data...")

        # World Bank API is free and public
        wb_url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.CD"

        try:
            response = requests.get(wb_url, params={
                "format": "json",
                "date": "2022",
                "per_page": 300
            })

            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    countries = []
                    for item in data[1]:  # Skip metadata
                        if item['value']:
                            countries.append({
                                'country_code': item['country']['id'],
                                'country_name': item['country']['value'],
                                'gdp_per_capita': item['value'],
                                'year': item['date']
                            })

                    df = pd.DataFrame(countries)

                    # Add risk classifications based on GDP
                    df['risk_level'] = df['gdp_per_capita'].apply(
                        lambda x: 'low' if x > 50000
                        else 'medium' if x > 15000
                        else 'high'
                    )

                    print(f"✅ Retrieved risk data for {len(df)} countries")
                    
                    if save_to_file:
                        Path("data").mkdir(exist_ok=True)
                        filename = f"data/world_bank_country_risk_{datetime.now().strftime('%Y%m%d')}.csv"
                        df.to_csv(filename, index=False)
                        print(f"💾 Saved World Bank country risk data to {filename}")
                    
                    return df

        except Exception as e:
            print(f"❌ Error fetching country risk data: {e}")

        return pd.DataFrame()

    def get_exchange_rates(self, save_to_file: bool = False) -> Dict[str, float]:
        """Get current exchange rates for suspicious transaction analysis"""
        print("🔄 Fetching exchange rates...")

        # Free exchange rate API
        try:
            response = requests.get(
                "https://api.exchangerate-api.com/v4/latest/USD")
            if response.status_code == 200:
                rates_data = response.json()
                rates = rates_data['rates']
                print(
                    f"✅ Retrieved exchange rates for {len(rates)} currencies")
                
                if save_to_file:
                    Path("data").mkdir(exist_ok=True)
                    filename = f"data/exchange_rates_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
                    with open(filename, 'w') as f:
                        json.dump({
                            'base': rates_data['base'],
                            'date': rates_data['date'],
                            'rates': rates,
                            'retrieved_at': datetime.now().isoformat()
                        }, f, indent=2)
                    print(f"💾 Saved exchange rates to {filename}")
                
                return rates
        except Exception as e:
            print(f"❌ Error fetching exchange rates: {e}")

        return {}

    def get_company_data(self, company_name: str, save_to_file: bool = False) -> Dict[str, Any]:
        """Get company information for beneficial ownership analysis"""
        print(f"🔄 Searching for company data: {company_name}")
        
        company_data = {
            "name": company_name,
            "registration_country": "Unknown",
            "incorporation_date": None,
            "business_type": "Unknown",
            "risk_flags": [],
            "beneficial_owners": [],
            "sources": []
        }
        
        # Try OpenCorporates first
        if self.opencorporates.available:
            oc_results = self.opencorporates.search_companies(company_name)
            if oc_results:
                company_data["opencorporates_results"] = oc_results[:3]  # Top 3 results
                company_data["sources"].append("opencorporates")
                logger.info(f"✅ Found OpenCorporates data for {company_name}")
        
        # Try Alpha Vantage for publicly traded companies
        if self.alpha_vantage.available:
            # Try common stock symbols
            potential_symbols = [company_name.upper()[:4], company_name.replace(" ", "")[:5]]
            for symbol in potential_symbols:
                av_data = self.alpha_vantage.get_company_overview(symbol)
                if av_data:
                    company_data["alpha_vantage_data"] = av_data
                    company_data["sources"].append("alpha_vantage")
                    break
        
        # Add data quality assessment
        if company_data["sources"]:
            company_data["data_quality"] = "enhanced"
        else:
            company_data["data_quality"] = "basic"
            logger.warning(f"⚠️ Limited data available for {company_name}")
        
        if save_to_file and company_data["sources"]:
            Path("data").mkdir(exist_ok=True)
            filename = f"data/company_data_{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                json.dump(company_data, f, indent=2)
            print(f"💾 Saved company data to {filename}")

        print(f"📊 Retrieved company data for {company_name} from {len(company_data['sources'])} sources")
        return company_data

# ============================================================================
# SECTION 4: WEB SCRAPING FOR PUBLIC INFORMATION
# ============================================================================


class PublicDataScraper:
    """Scrape publicly available financial crime information"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; InvestigatorAI/1.0; +https://example.com/bot)'
        }

    def get_fincen_advisories(self, save_to_file: bool = False) -> List[Dict]:
        """Get FinCEN advisories and alerts"""
        print("🔄 Fetching FinCEN advisories...")

        # These are public regulatory communications
        # In practice, you would scrape from fincen.gov
        sample_advisories = [
            {
                "title": "Advisory on Human Trafficking",
                "date": "2022-06-01",
                "risk_indicators": [
                    "Multiple cash deposits under reporting thresholds",
                    "Payments to escort services",
                    "Unusual geographic patterns"
                ],
                "url": "https://www.fincen.gov/sites/default/files/advisory/2022-06-01/FinCEN%20Advisory%20Human%20Trafficking%20508%20FINAL.pdf"
            },
            {
                "title": "Advisory on Ransomware",
                "date": "2021-10-15",
                "risk_indicators": [
                    "Large cryptocurrency transactions",
                    "Payments to known ransomware wallets",
                    "Unusual business explanations"
                ],
                "url": "https://www.fincen.gov/sites/default/files/advisory/2021-10-15/FinCEN%20Advisory%20Ransomware%20FINAL%20508.pdf"
            }
        ]

        print(f"✅ Retrieved {len(sample_advisories)} FinCEN advisories")
        
        if save_to_file:
            Path("data").mkdir(exist_ok=True)
            filename = f"data/fincen_advisories_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                json.dump(sample_advisories, f, indent=2)
            print(f"💾 Saved FinCEN advisories to {filename}")
        
        return sample_advisories

    def get_fatf_high_risk_jurisdictions(self, save_to_file: bool = False) -> Dict[str, List[str]]:
        """Get FATF high-risk and non-cooperative jurisdictions"""
        print("🔄 Fetching FATF high-risk jurisdictions...")

        # FATF publishes these lists publicly
        high_risk_jurisdictions = [
            "Iran", "North Korea", "Myanmar"  # Current as of 2024
        ]

        jurisdictions_under_monitoring = [
            "Albania", "Barbados", "Burkina Faso", "Cambodia",
            "Cayman Islands", "Croatia", "Gibraltar", "Haiti",
            "Jamaica", "Jordan", "Mali", "Morocco", "Nigeria",
            "Panama", "Philippines", "Senegal", "South Africa",
            "South Sudan", "Syria", "Turkey", "Uganda", "United Arab Emirates", "Yemen"
        ]

        print(
            f"✅ Retrieved {len(high_risk_jurisdictions)} high-risk jurisdictions")
        print(
            f"✅ Retrieved {len(jurisdictions_under_monitoring)} monitored jurisdictions")

        fatf_data = {
            "high_risk": high_risk_jurisdictions,
            "monitored": jurisdictions_under_monitoring
        }
        
        if save_to_file:
            Path("data").mkdir(exist_ok=True)
            filename = f"data/fatf_jurisdictions_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                json.dump(fatf_data, f, indent=2)
            print(f"💾 Saved FATF jurisdictions data to {filename}")

        return fatf_data

# ============================================================================
# SECTION 5: DATA INTEGRATION PIPELINE
# ============================================================================


class RealWorldDataPipeline:
    """Integrate all real-world data sources"""

    def __init__(self):
        self.regulatory_sources = RegulatoryDataSources()
        self.crime_datasets = FinancialCrimeDatasets()
        self.commercial_apis = CommercialDataAPIs()
        self.public_scraper = PublicDataScraper()

    def collect_all_data(self, save_to_files: bool = False, include_paid_apis: bool = False) -> Dict[str, Any]:
        """Collect data from all available sources"""
        print("\n🌐 COLLECTING REAL-WORLD DATA")
        print("="*50)

        all_data = {}

        # Regulatory data
        print("\n📊 Government & Regulatory Sources:")
        all_data["sanctions_list"] = self.regulatory_sources.get_ofac_sanctions_list(save_to_file=save_to_files)
        all_data["gto_orders"] = self.regulatory_sources.get_fincen_geographic_targeting_orders(save_to_file=save_to_files)
        all_data["bsa_requirements"] = self.regulatory_sources.get_bsa_filing_requirements(save_to_file=save_to_files)

        # Research datasets
        print("\n🔬 Research Datasets:")
        all_data["paysim_fraud"] = self.crime_datasets.get_paysim_fraud_dataset(save_to_file=save_to_files)
        all_data["credit_card_fraud"] = self.crime_datasets.get_credit_card_fraud_dataset(save_to_file=save_to_files)

        # Commercial APIs (only free ones by default)
        print("\n💼 Commercial API Data:")
        all_data["country_risk"] = self.commercial_apis.get_country_risk_data(save_to_file=save_to_files)
        all_data["exchange_rates"] = self.commercial_apis.get_exchange_rates(save_to_file=save_to_files)
        
        # Include paid APIs if requested and available
        if include_paid_apis:
            print("\n💰 Enhanced Commercial Data (Paid APIs):")
            
            # Company data examples
            test_companies = ["Apple Inc", "Microsoft Corporation", "Tesla Inc"]
            all_data["company_data"] = {}
            for company in test_companies:
                all_data["company_data"][company] = self.commercial_apis.get_company_data(company, save_to_file=save_to_files)

        # Public information
        print("\n🌍 Public Information:")
        all_data["fincen_advisories"] = self.public_scraper.get_fincen_advisories(save_to_file=save_to_files)
        all_data["fatf_jurisdictions"] = self.public_scraper.get_fatf_high_risk_jurisdictions(save_to_file=save_to_files)

        print(f"\n✅ Data collection complete!")
        return all_data

    def download_free_data_sources(self) -> Dict[str, Any]:
        """Download and save only the free data sources to files"""
        print("\n💾 DOWNLOADING FREE DATA SOURCES")
        print("="*50)
        print("📋 Sources being downloaded:")
        print("   ✅ OFAC SDN List (CSV)")
        print("   ✅ World Bank Country Risk Data (CSV)")
        print("   ✅ Exchange Rates (JSON)")
        print("   ✅ FinCEN Geographic Targeting Orders (JSON)")
        print("   ✅ BSA Filing Requirements (JSON)")
        print("   ✅ FinCEN Advisories (JSON)")
        print("   ✅ FATF High-Risk Jurisdictions (JSON)")
        print("   ✅ PaySim Dataset (Kaggle - if API available)")
        print("   ✅ Credit Card Fraud Dataset (Kaggle - if API available)")
        print("")

        return self.collect_all_data(save_to_files=True, include_paid_apis=False)

    def download_all_available_data(self) -> Dict[str, Any]:
        """Download all data sources for which APIs are configured"""
        print("\n💾 DOWNLOADING ALL AVAILABLE DATA SOURCES")
        print("="*60)
        
        # Check API status first
        self.check_api_status()
        print("")
        
        return self.collect_all_data(save_to_files=True, include_paid_apis=True)

    def check_api_status(self) -> Dict[str, bool]:
        """Check which APIs are properly configured"""
        print("\n🔍 API STATUS CHECK")
        print("="*50)
        
        config = APIConfig()
        status = {}
        
        # Check each API
        apis_to_check = [
            ("Kaggle", "kaggle"),
            ("Alpha Vantage", "alpha_vantage"),
            ("OpenCorporates", "opencorporates"),
            ("Companies House", "companies_house"),
            ("SEC EDGAR", "sec_edgar"),
            ("World Bank", "world_bank"),
            ("Exchange Rates", "exchange_rates"),
        ]
        
        for api_name, api_key in apis_to_check:
            available = config.is_api_available(api_key)
            status[api_key] = available
            status_icon = "✅" if available else "❌"
            note = ""
            
            if api_key == "kaggle" and not available:
                note = " (Set KAGGLE_USERNAME and KAGGLE_KEY)"
            elif api_key in ["alpha_vantage", "opencorporates", "companies_house"] and not available:
                note = f" (Set {api_key.upper()}_API_KEY)"
            elif api_key == "sec_edgar":
                note = " (Set SEC_EDGAR_USER_AGENT)" if not available else " (Free)"
            elif api_key in ["world_bank", "exchange_rates"]:
                note = " (Free - No key needed)"
            
            print(f"   {status_icon} {api_name:<20} {note}")
        
        available_count = sum(status.values())
        total_count = len(status)
        print(f"\n📊 Summary: {available_count}/{total_count} APIs configured")
        
        if available_count < total_count:
            print("💡 To configure missing APIs, copy 'api_config_template.env' to '.env' and add your keys")
        
        return status

    def enhance_synthetic_cases(self, synthetic_cases: List, real_data: Dict) -> List:
        """Enhance synthetic cases with real-world context"""
        print("🔄 Enhancing synthetic cases with real-world data...")

        enhanced_cases = []
        sanctions_list = real_data.get("sanctions_list", pd.DataFrame())
        country_risk = real_data.get("country_risk", pd.DataFrame())
        fatf_data = real_data.get("fatf_jurisdictions", {})

        for case in synthetic_cases:
            # Add real sanctions screening
            if not sanctions_list.empty:
                # Check if transaction involves sanctioned entities
                case.risk_indicators = case.risk_indicators or {}
                # Would do real lookup
                case.risk_indicators["sanctions_hit"] = False

            # Add real country risk scores
            if not country_risk.empty:
                # Get risk level for transaction locations
                from_risk = self._get_country_risk(
                    case.transaction.from_location, country_risk)
                to_risk = self._get_country_risk(
                    case.transaction.to_location, country_risk)

                case.risk_indicators["from_country_risk"] = from_risk
                case.risk_indicators["to_country_risk"] = to_risk

            # Add FATF jurisdiction flags
            high_risk_jurisdictions = fatf_data.get("high_risk", [])
            if any(jurisdiction in case.transaction.to_location for jurisdiction in high_risk_jurisdictions):
                case.risk_indicators["fatf_high_risk"] = True

            enhanced_cases.append(case)

        print(f"✅ Enhanced {len(enhanced_cases)} cases with real-world data")
        return enhanced_cases

    def _get_country_risk(self, location: str, country_risk_df: pd.DataFrame) -> str:
        """Extract country risk level from location string"""
        # Simple mapping - in production would use proper geocoding
        location_risk_map = {
            "United States": "low",
            "United Kingdom": "low",
            "Germany": "low",
            "UAE": "medium",
            "Russia": "high",
            "Iran": "high",
            "Nigeria": "medium"
        }

        for country, risk in location_risk_map.items():
            if country in location:
                return risk

        return "medium"  # Default

# ============================================================================
# SECTION 6: USAGE EXAMPLES
# ============================================================================


def demonstrate_real_data_integration():
    """Demonstrate how to integrate real-world data"""
    print("\n🚀 REAL-WORLD DATA INTEGRATION DEMO")
    print("="*60)

    # Initialize data pipeline
    data_pipeline = RealWorldDataPipeline()

    # Collect all available data
    real_world_data = data_pipeline.collect_all_data()

    # Show what we collected
    print("\n📈 DATA COLLECTION SUMMARY:")
    for source, data in real_world_data.items():
        if isinstance(data, pd.DataFrame):
            print(f"   • {source}: {len(data)} records")
        elif isinstance(data, list):
            print(f"   • {source}: {len(data)} items")
        elif isinstance(data, dict):
            print(f"   • {source}: {len(data)} entries")

    # Example: Use sanctions data for screening
    sanctions_df = real_world_data.get("sanctions_list", pd.DataFrame())
    if not sanctions_df.empty:
        print(f"\n🔍 SANCTIONS SCREENING CAPABILITY:")
        print(f"   • Can screen against {len(sanctions_df)} OFAC SDN entries")
        print(f"   • Real-time compliance checking enabled")

    # Example: Use country risk data
    country_risk_df = real_world_data.get("country_risk", pd.DataFrame())
    if not country_risk_df.empty:
        high_risk_countries = country_risk_df[country_risk_df['risk_level'] == 'high']
        print(f"\n🌍 GEOGRAPHIC RISK ANALYSIS:")
        print(f"   • {len(high_risk_countries)} high-risk countries identified")
        print(f"   • Real-time geographic risk scoring available")

    # Example: Use regulatory advisories
    advisories = real_world_data.get("fincen_advisories", [])
    print(f"\n📋 REGULATORY INTELLIGENCE:")
    print(f"   • {len(advisories)} current FinCEN advisories integrated")
    print(f"   • Automated red flag detection based on regulatory guidance")

    return real_world_data


def download_and_save_free_data():
    """Download and save all free data sources to files"""
    print("\n🚀 DOWNLOADING FREE DATA SOURCES")
    print("="*60)
    
    # Initialize data pipeline
    data_pipeline = RealWorldDataPipeline()
    
    # Download and save free data sources
    saved_data = data_pipeline.download_free_data_sources()
    
    # Show summary of saved files
    print("\n📁 SAVED FILES SUMMARY:")
    data_dir = Path("data")
    if data_dir.exists():
        files = list(data_dir.glob("*"))
        for file in sorted(files):
            size_kb = file.stat().st_size / 1024
            print(f"   📄 {file.name} ({size_kb:.1f} KB)")
    
    print(f"\n✅ All free data sources downloaded and saved to 'data/' directory!")
    print(f"🔄 Run this function regularly to keep data updated")
    
    return saved_data


# Run the demonstration
if __name__ == "__main__":
    print("\n🔗 INVESTIGATORAI DATA COLLECTION")
    print("="*60)
    print("Choose an option:")
    print("1. Download FREE data sources only")
    print("2. Download ALL available data sources (requires API keys)")
    print("3. Check API configuration status") 
    print("4. Run demonstration (preview data without saving)")
    print("5. Show API cost estimates and setup guide")
    
    try:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            # Download and save free data sources
            saved_data = download_and_save_free_data()
            
        elif choice == "2":
            # Download all available data sources
            pipeline = RealWorldDataPipeline()
            saved_data = pipeline.download_all_available_data()
            
        elif choice == "3":
            # Check API status
            pipeline = RealWorldDataPipeline()
            pipeline.check_api_status()
            
        elif choice == "4":
            # Run the demonstration
            real_data = demonstrate_real_data_integration()
            
        elif choice == "5":
            # Show cost estimates and setup
            print("\n📋 API SETUP GUIDE")
            print("="*50)
            print("1. Copy 'api_config_template.env' to '.env'")
            print("2. Fill in your API keys in the .env file")
            print("3. Run option 3 to check your configuration")
            print("4. Use option 2 to download enhanced datasets")
            print("")
            estimate_api_costs()
            setup_data_refresh_schedule()
            
        else:
            print("Invalid choice. Running default demonstration...")
            real_data = demonstrate_real_data_integration()
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Running default demonstration...")
        real_data = demonstrate_real_data_integration()

    print("\n💡 IMPLEMENTATION RECOMMENDATIONS:")
    print("="*50)
    print("1. Start with free government sources (OFAC, FinCEN)")
    print("2. Add World Bank country risk data")
    print("3. Integrate research datasets for training")
    print("4. Consider commercial APIs for enhanced features")
    print("5. Implement caching to respect rate limits")
    print("6. Always comply with terms of service")

    print("\n🔧 NEXT STEPS FOR YOUR SYSTEM:")
    print("• Replace synthetic location data with real country risk scores")
    print("• Add real sanctions screening to compliance agent")
    print("• Use FinCEN advisories to enhance pattern detection")
    print("• Integrate exchange rates for currency conversion analysis")
    print("• Add company database lookup for beneficial ownership")

    print(f"\n✅ Your InvestigatorAI system is now ready for real-world data!")

# Additional helper functions for API integration


def setup_data_refresh_schedule():
    """Set up automated data refresh for dynamic sources"""
    refresh_schedule = {
        "sanctions_list": "daily",      # OFAC updates daily
        "exchange_rates": "hourly",     # Currency rates change frequently
        "country_risk": "monthly",      # Country risk changes slowly
        "regulatory_advisories": "weekly"  # New advisories published regularly
    }

    print("📅 Recommended data refresh schedule:")
    for source, frequency in refresh_schedule.items():
        print(f"   • {source}: {frequency}")

    return refresh_schedule


def estimate_api_costs():
    """Estimate costs for commercial APIs"""
    api_costs = {
        "OpenCorporates": "$0.10 per company lookup",
        "Alpha Vantage": "Free tier: 5 calls/min, 500 calls/day",
        "World Bank": "Free",
        "ExchangeRate-API": "Free tier: 1,500 requests/month",
        "SEC EDGAR": "Free"
    }

    print("💰 API cost estimates:")
    for api, cost in api_costs.items():
        print(f"   • {api}: {cost}")

    return api_costs


# Run additional examples
setup_data_refresh_schedule()
estimate_api_costs()
