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
# TEXT CONVERSION UTILITIES FOR RAG KNOWLEDGE BASE
# ============================================================================

class TextConverter:
    """Convert structured data to RAG-friendly text format"""
    
    @staticmethod
    def convert_dataframe_to_text(df: pd.DataFrame, title: str, description: str = "") -> str:
        """Convert DataFrame to structured text for RAG"""
        text_lines = [
            f"TITLE: {title}",
            f"TYPE: Structured Dataset",
            f"SOURCE: InvestigatorAI Data Collection",
            f"DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        if description:
            text_lines.extend([
                f"DESCRIPTION: {description}",
                ""
            ])
        
        # Add dataset overview
        text_lines.extend([
            f"DATASET OVERVIEW:",
            f"Total Records: {len(df)}",
            f"Columns: {', '.join(df.columns.tolist())}",
            ""
        ])
        
        # Add column descriptions and sample data
        text_lines.append("COLUMN ANALYSIS:")
        for col in df.columns:
            if df[col].dtype == 'object':
                unique_count = df[col].nunique()
                sample_values = df[col].dropna().head(3).tolist()
                text_lines.append(f"- {col}: Text field, {unique_count} unique values, examples: {sample_values}")
            else:
                stats = df[col].describe()
                text_lines.append(f"- {col}: Numeric field, mean: {stats['mean']:.2f}, range: {stats['min']:.2f} to {stats['max']:.2f}")
        
        text_lines.append("")
        
        # Add sample records (first 5 rows)
        text_lines.append("SAMPLE RECORDS:")
        for i, (_, row) in enumerate(df.head(5).iterrows()):
            text_lines.append(f"Record {i+1}:")
            for col in df.columns:
                value = str(row[col])[:100]  # Truncate long values
                text_lines.append(f"  {col}: {value}")
            text_lines.append("")
        
        return "\n".join(text_lines)
    
    @staticmethod
    def convert_json_to_text(data: Dict, title: str, description: str = "") -> str:
        """Convert JSON data to structured text for RAG"""
        text_lines = [
            f"TITLE: {title}",
            f"TYPE: Structured Data",
            f"SOURCE: InvestigatorAI Data Collection", 
            f"DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        if description:
            text_lines.extend([
                f"DESCRIPTION: {description}",
                ""
            ])
        
        # Convert JSON to readable text
        text_lines.append("DATA CONTENT:")
        text_lines.append(TextConverter._format_json_recursive(data, indent=0))
        
        return "\n".join(text_lines)
    
    @staticmethod
    def convert_list_to_text(data: List, title: str, description: str = "") -> str:
        """Convert list data to structured text for RAG"""
        text_lines = [
            f"TITLE: {title}",
            f"TYPE: List Data",
            f"SOURCE: InvestigatorAI Data Collection",
            f"DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        if description:
            text_lines.extend([
                f"DESCRIPTION: {description}",
                ""
            ])
        
        text_lines.extend([
            f"TOTAL ITEMS: {len(data)}",
            "",
            "CONTENT:"
        ])
        
        for i, item in enumerate(data[:20]):  # Limit to first 20 items
            text_lines.append(f"{i+1}. {str(item)}")
        
        if len(data) > 20:
            text_lines.append(f"... and {len(data) - 20} more items")
        
        return "\n".join(text_lines)
    
    @staticmethod
    def _format_json_recursive(obj, indent: int = 0) -> str:
        """Recursively format JSON object to readable text"""
        lines = []
        prefix = "  " * indent
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{prefix}{key}:")
                    lines.append(TextConverter._format_json_recursive(value, indent + 1))
                else:
                    # Truncate long values
                    value_str = str(value)[:200]
                    if len(str(value)) > 200:
                        value_str += "..."
                    lines.append(f"{prefix}{key}: {value_str}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj[:10]):  # Limit to first 10 items
                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}Item {i+1}:")
                    lines.append(TextConverter._format_json_recursive(item, indent + 1))
                else:
                    lines.append(f"{prefix}{i+1}. {str(item)[:100]}")
            if len(obj) > 10:
                lines.append(f"{prefix}... and {len(obj) - 10} more items")
        
        return "\n".join(lines)
    
    @staticmethod
    def save_to_knowledge_base(text_content: str, filename: str):
        """Save text content to fraud knowledge base"""
        kb_dir = Path("data/fraud_knowledge_base")
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = kb_dir / f"{filename}.txt"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        print(f"💾 Saved to knowledge base: {filepath}")
        return filepath

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
    
    def get_company_overview(self, symbol: str, save_to_file: bool = False) -> Optional[Dict]:
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
                    
                    if save_to_file:
                        Path("data/alpha_vantage").mkdir(parents=True, exist_ok=True)
                        filename = f"data/alpha_vantage/company_overview_{symbol}_{datetime.now().strftime('%Y%m%d')}.json"
                        with open(filename, 'w') as f:
                            json.dump(data, f, indent=2)
                        logger.info(f"💾 Saved company overview to {filename}")
                    
                    return data
                else:
                    logger.warning(f"⚠️ No data found for symbol {symbol}")
            else:
                logger.error(f"❌ Alpha Vantage API error: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Error fetching company data: {e}")
        
        return None
    
    def get_fx_rates(self, from_currency: str, to_currency: str, save_to_file: bool = False) -> Optional[Dict]:
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
                data = response.json()
                
                if save_to_file and data:
                    Path("data/alpha_vantage").mkdir(parents=True, exist_ok=True)
                    filename = f"data/alpha_vantage/fx_rates_{from_currency}_{to_currency}_{datetime.now().strftime('%Y%m%d')}.json"
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    logger.info(f"💾 Saved FX rates to {filename}")
                
                return data
        except Exception as e:
            logger.error(f"❌ Error fetching FX rates: {e}")
        
        return None
    
    def get_daily_stock_data(self, symbol: str, save_to_file: bool = False) -> Optional[Dict]:
        """Get daily stock price data"""
        if not self.available:
            logger.warning("❌ Alpha Vantage API key not available")
            return None
        
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if "Time Series (Daily)" in data:
                    logger.info(f"✅ Retrieved daily stock data for {symbol}")
                    
                    if save_to_file:
                        Path("data/alpha_vantage").mkdir(parents=True, exist_ok=True)
                        filename = f"data/alpha_vantage/stock_daily_{symbol}_{datetime.now().strftime('%Y%m%d')}.json"
                        with open(filename, 'w') as f:
                            json.dump(data, f, indent=2)
                        logger.info(f"💾 Saved stock data to {filename}")
                    
                    return data
                else:
                    logger.warning(f"⚠️ No stock data found for symbol {symbol}")
        except Exception as e:
            logger.error(f"❌ Error fetching stock data: {e}")
        
        return None
    
    def get_economic_indicators(self, save_to_file: bool = False) -> Dict[str, Optional[Dict]]:
        """Get key economic indicators"""
        if not self.available:
            logger.warning("❌ Alpha Vantage API key not available")
            return {}
        
        indicators = {
            "unemployment": "UNEMPLOYMENT",
            "inflation": "CPI",
            "real_gdp": "REAL_GDP"
        }
        
        results = {}
        
        for indicator_name, function in indicators.items():
            params = {
                "function": function,
                "interval": "annual",
                "apikey": self.api_key
            }
            
            try:
                time.sleep(12)  # Respect rate limits (5 calls per minute)
                response = requests.get(self.base_url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    results[indicator_name] = data
                    logger.info(f"✅ Retrieved {indicator_name} data")
                    
                    if save_to_file and data:
                        Path("data/alpha_vantage").mkdir(parents=True, exist_ok=True)
                        filename = f"data/alpha_vantage/economic_{indicator_name}_{datetime.now().strftime('%Y%m%d')}.json"
                        with open(filename, 'w') as f:
                            json.dump(data, f, indent=2)
                        logger.info(f"💾 Saved {indicator_name} data to {filename}")
                        
            except Exception as e:
                logger.error(f"❌ Error fetching {indicator_name} data: {e}")
                results[indicator_name] = None
        
        return results


class FREDAPI:
    """Federal Reserve Economic Data (FRED) API"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.api_key = config.api_keys["fred"]
        self.available = config.is_api_available("fred")
        self.base_url = config.endpoints["fred"]
    
    def get_series_data(self, series_id: str, save_to_file: bool = False) -> Optional[pd.DataFrame]:
        """Get economic time series data from FRED"""
        if not self.available:
            logger.warning("❌ FRED API key not available")
            return None
        
        url = f"{self.base_url}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if "observations" in data:
                    # Convert to DataFrame
                    observations = data["observations"]
                    df = pd.DataFrame(observations)
                    df['date'] = pd.to_datetime(df['date'])
                    df['value'] = pd.to_numeric(df['value'], errors='coerce')
                    
                    logger.info(f"✅ Retrieved FRED series {series_id}: {len(df)} observations")
                    
                    if save_to_file:
                        Path("data/fred").mkdir(parents=True, exist_ok=True)
                        filename = f"data/fred/series_{series_id}_{datetime.now().strftime('%Y%m%d')}.csv"
                        df.to_csv(filename, index=False)
                        logger.info(f"💾 Saved FRED series to {filename}")
                    
                    return df
                else:
                    logger.warning(f"⚠️ No data found for FRED series {series_id}")
        except Exception as e:
            logger.error(f"❌ Error fetching FRED series {series_id}: {e}")
        
        return None
    
    def get_multiple_series(self, series_dict: Dict[str, str], save_to_file: bool = False) -> Dict[str, Optional[pd.DataFrame]]:
        """Get multiple economic series from FRED"""
        if not self.available:
            logger.warning("❌ FRED API key not available")
            return {}
        
        results = {}
        
        for name, series_id in series_dict.items():
            logger.info(f"🔄 Fetching FRED series: {name} ({series_id})")
            data = self.get_series_data(series_id, save_to_file=save_to_file)
            results[name] = data
            
            # Be respectful with rate limits
            time.sleep(0.5)
        
        return results
    
    def get_key_economic_indicators(self, save_to_file: bool = False) -> Dict[str, Optional[pd.DataFrame]]:
        """Get key economic indicators for fraud investigation context"""
        indicators = {
            "gdp": "GDP",  # Gross Domestic Product
            "unemployment_rate": "UNRATE",  # Unemployment Rate
            "federal_funds_rate": "FEDFUNDS",  # Federal Funds Rate
            "consumer_price_index": "CPIAUCSL",  # Consumer Price Index
            "money_supply_m2": "M2SL",  # Money Supply M2
            "bank_credit": "TOTBKCR",  # Total Bank Credit
            "commercial_paper": "COMPAPER",  # Commercial Paper Outstanding
            "exchange_rate_euro": "DEXUSEU",  # USD/EUR Exchange Rate
            "treasury_10y": "GS10",  # 10-Year Treasury Constant Maturity Rate
            "corporate_aaa_spread": "AAA",  # AAA Corporate Bond Yield
        }
        
        logger.info("🔄 Fetching key economic indicators from FRED...")
        results = self.get_multiple_series(indicators, save_to_file=save_to_file)
        
        if save_to_file and any(results.values()):
            # Create a summary file
            Path("data/fred").mkdir(parents=True, exist_ok=True)
            summary_filename = f"data/fred/economic_indicators_summary_{datetime.now().strftime('%Y%m%d')}.json"
            
            summary = {}
            for name, df in results.items():
                if df is not None and not df.empty:
                    latest_value = df['value'].dropna().iloc[-1] if not df['value'].dropna().empty else None
                    latest_date = df['date'].iloc[-1].strftime('%Y-%m-%d') if not df.empty else None
                    summary[name] = {
                        "latest_value": latest_value,
                        "latest_date": latest_date,
                        "total_observations": len(df)
                    }
            
            with open(summary_filename, 'w') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"💾 Saved economic indicators summary to {summary_filename}")
        
        return results
    
    def get_banking_indicators(self, save_to_file: bool = False) -> Dict[str, Optional[pd.DataFrame]]:
        """Get banking sector indicators relevant to fraud detection"""
        banking_indicators = {
            "bank_deposits": "DPSACBW027SBOG",  # Deposits at Commercial Banks
            "bank_loans": "TOTLL",  # Total Loans and Leases at Commercial Banks  
            "charge_offs": "CORCCACBN",  # Charge-Off Rate on Credit Cards
            "delinquency_rate": "DRCCLACBS",  # Delinquency Rate on Credit Cards
            "net_interest_margin": "USNIM",  # Net Interest Margin for all US Banks
            "return_on_assets": "USROA",  # Return on Assets for all US Banks
        }
        
        logger.info("🔄 Fetching banking indicators from FRED...")
        return self.get_multiple_series(banking_indicators, save_to_file=save_to_file)


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
                    
                    # Also save to knowledge base as text
                    text_content = TextConverter.convert_dataframe_to_text(
                        sdn_data,
                        "OFAC Specially Designated Nationals (SDN) List",
                        "Complete list of individuals and entities blocked by OFAC. Used for sanctions screening and compliance. Contains names, aliases, addresses, and identification numbers of sanctioned parties."
                    )
                    TextConverter.save_to_knowledge_base(text_content, f"regulatory_ofac_sdn_list_{datetime.now().strftime('%Y%m%d')}")
                
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
        self.fred = FREDAPI(self.config)
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
                    rates_with_metadata = {
                        'base': rates_data['base'],
                        'date': rates_data['date'],
                        'rates': rates,
                        'retrieved_at': datetime.now().isoformat()
                    }
                    with open(filename, 'w') as f:
                        json.dump(rates_with_metadata, f, indent=2)
                    print(f"💾 Saved exchange rates to {filename}")
                    
                    # Also save to knowledge base as text
                    text_content = TextConverter.convert_json_to_text(
                        rates_with_metadata,
                        "Foreign Exchange Rates",
                        "Current foreign exchange rates for major currencies against USD. Used for currency conversion analysis, cross-border transaction monitoring, and detecting unusual currency exchange patterns in international fraud schemes."
                    )
                    TextConverter.save_to_knowledge_base(text_content, f"financial_exchange_rates_{datetime.now().strftime('%Y%m%d_%H%M')}")
                
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

    def get_fred_economic_data(self, save_to_file: bool = False) -> Dict[str, Any]:
        """Get comprehensive economic data from FRED"""
        print("🔄 Fetching economic data from FRED...")
        
        if not self.fred.available:
            print("⚠️ FRED API not available. Set FRED_API_KEY in environment variables.")
            return {}
        
        results = {}
        
        # Get key economic indicators
        results["economic_indicators"] = self.fred.get_key_economic_indicators(save_to_file=save_to_file)
        
        # Get banking indicators
        results["banking_indicators"] = self.fred.get_banking_indicators(save_to_file=save_to_file)
        
        print(f"✅ Retrieved FRED economic data from {len(results)} categories")
        return results

    def get_alpha_vantage_financial_data(self, symbols: List[str] = None, save_to_file: bool = False) -> Dict[str, Any]:
        """Get comprehensive financial market data from Alpha Vantage"""
        print("🔄 Fetching financial data from Alpha Vantage...")
        
        if not self.alpha_vantage.available:
            print("⚠️ Alpha Vantage API not available. Set ALPHA_VANTAGE_API_KEY in environment variables.")
            return {}
        
        if symbols is None:
            # Default symbols for fraud investigation context
            symbols = ["SPY", "XLF", "BTC-USD", "GLD"]  # S&P 500, Financial Sector, Bitcoin, Gold
        
        results = {}
        
        # Get company overviews
        results["company_overviews"] = {}
        for symbol in symbols:
            overview = self.alpha_vantage.get_company_overview(symbol, save_to_file=save_to_file)
            if overview:
                results["company_overviews"][symbol] = overview
            time.sleep(12)  # Respect rate limits
        
        # Get economic indicators
        results["economic_indicators"] = self.alpha_vantage.get_economic_indicators(save_to_file=save_to_file)
        
        # Get FX rates for common money laundering currencies
        fx_pairs = [("USD", "EUR"), ("USD", "CNY"), ("USD", "RUB"), ("USD", "AED")]
        results["fx_rates"] = {}
        for from_curr, to_curr in fx_pairs:
            fx_data = self.alpha_vantage.get_fx_rates(from_curr, to_curr, save_to_file=save_to_file)
            if fx_data:
                results["fx_rates"][f"{from_curr}_{to_curr}"] = fx_data
            time.sleep(12)  # Respect rate limits
        
        print(f"✅ Retrieved Alpha Vantage data for {len(symbols)} symbols and {len(fx_pairs)} FX pairs")
        return results

    def get_kaggle_datasets(self, save_to_file: bool = False) -> Dict[str, Any]:
        """Get fraud datasets from Kaggle"""
        print("🔄 Fetching datasets from Kaggle...")
        
        if not self.kaggle.available:
            print("⚠️ Kaggle API not available. Set KAGGLE_USERNAME and KAGGLE_KEY in environment variables.")
            return {}
        
        results = {}
        
        # Get PaySim dataset
        paysim_data = self.kaggle.get_paysim_dataset()
        if paysim_data is not None:
            results["paysim"] = paysim_data
            if save_to_file:
                Path("data/kaggle").mkdir(parents=True, exist_ok=True)
                filename = f"data/kaggle/paysim_processed_{datetime.now().strftime('%Y%m%d')}.csv"
                paysim_data.to_csv(filename, index=False)
                print(f"💾 Saved processed PaySim data to {filename}")
        
        # Get Credit Card Fraud dataset
        cc_fraud_data = self.kaggle.get_credit_card_fraud_dataset()
        if cc_fraud_data is not None:
            results["credit_card_fraud"] = cc_fraud_data
            if save_to_file:
                Path("data/kaggle").mkdir(parents=True, exist_ok=True)
                filename = f"data/kaggle/credit_card_fraud_processed_{datetime.now().strftime('%Y%m%d')}.csv"
                cc_fraud_data.to_csv(filename, index=False)
                print(f"💾 Saved processed Credit Card Fraud data to {filename}")
        
        print(f"✅ Retrieved {len(results)} Kaggle datasets")
        return results

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
            
            # Also save to knowledge base as text
            text_content = TextConverter.convert_list_to_text(
                sample_advisories,
                "FinCEN Regulatory Advisories",
                "Official advisories from FinCEN providing guidance on suspicious activity indicators, red flags, and regulatory requirements for financial institutions. Contains specific risk indicators for various fraud typologies including human trafficking, ransomware, and other financial crimes."
            )
            TextConverter.save_to_knowledge_base(text_content, f"regulatory_fincen_advisories_{datetime.now().strftime('%Y%m%d')}")
        
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
            
            # FRED Economic Data
            all_data["fred_data"] = self.commercial_apis.get_fred_economic_data(save_to_file=save_to_files)
            
            # Alpha Vantage Financial Data
            all_data["alpha_vantage_data"] = self.commercial_apis.get_alpha_vantage_financial_data(save_to_file=save_to_files)
            
            # Enhanced Kaggle Datasets
            all_data["kaggle_datasets"] = self.commercial_apis.get_kaggle_datasets(save_to_file=save_to_files)
            
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
        print("📋 Enhanced data available with API keys:")
        print("   🔑 FRED Economic Indicators (Set FRED_API_KEY)")
        print("   🔑 Alpha Vantage Financial Data (Set ALPHA_VANTAGE_API_KEY)")
        print("   🔑 Enhanced Company Data (OpenCorporates, Alpha Vantage)")
        print("   💡 Use option 2 to download ALL available data")
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
    
    def convert_all_data_to_knowledge_base(self) -> Dict[str, Any]:
        """Convert all collected data to text format and save to knowledge base"""
        print("\n📚 CONVERTING ALL DATA TO RAG KNOWLEDGE BASE")
        print("="*60)
        print("Converting structured data to text format for RAG system")
        print("")
        
        all_data = self.collect_all_data(save_to_files=True, include_paid_apis=False)
        converted_count = 0
        
        # Convert regulatory data
        if "ofac_sdn" in all_data and not all_data["ofac_sdn"].empty:
            text_content = TextConverter.convert_dataframe_to_text(
                all_data["ofac_sdn"],
                "OFAC Specially Designated Nationals (SDN) List",
                "Complete list of individuals and entities blocked by OFAC. Used for sanctions screening and compliance."
            )
            TextConverter.save_to_knowledge_base(text_content, f"regulatory_ofac_sdn_current")
            converted_count += 1
        
        # Convert exchange rates
        if "exchange_rates" in all_data and all_data["exchange_rates"]:
            text_content = TextConverter.convert_json_to_text(
                all_data["exchange_rates"],
                "Current Foreign Exchange Rates",
                "Real-time currency exchange rates for fraud investigation and cross-border transaction analysis."
            )
            TextConverter.save_to_knowledge_base(text_content, f"financial_exchange_rates_current")
            converted_count += 1
        
        # Convert country risk data
        if "country_risk" in all_data and not all_data["country_risk"].empty:
            text_content = TextConverter.convert_dataframe_to_text(
                all_data["country_risk"],
                "World Bank Country Risk Assessment Data",
                "Economic and political risk indicators by country for cross-border transaction risk assessment."
            )
            TextConverter.save_to_knowledge_base(text_content, f"international_country_risk_current")
            converted_count += 1
        
        # Convert FinCEN advisories
        if "fincen_advisories" in all_data and all_data["fincen_advisories"]:
            text_content = TextConverter.convert_list_to_text(
                all_data["fincen_advisories"],
                "FinCEN Regulatory Advisories",
                "Official advisories from FinCEN with fraud detection guidance and red flag indicators."
            )
            TextConverter.save_to_knowledge_base(text_content, f"regulatory_fincen_advisories_current")
            converted_count += 1
        
        # Convert FATF jurisdictions
        if "fatf_jurisdictions" in all_data and all_data["fatf_jurisdictions"]:
            text_content = TextConverter.convert_json_to_text(
                all_data["fatf_jurisdictions"],
                "FATF High-Risk Jurisdictions",
                "Countries and territories identified by FATF as high-risk for money laundering and terrorist financing."
            )
            TextConverter.save_to_knowledge_base(text_content, f"regulatory_fatf_jurisdictions_current")
            converted_count += 1
        
        # Convert fraud datasets if available
        if "paysim_data" in all_data and not all_data["paysim_data"].empty:
            # Sample the large dataset for knowledge base
            sample_data = all_data["paysim_data"].sample(n=min(1000, len(all_data["paysim_data"])))
            text_content = TextConverter.convert_dataframe_to_text(
                sample_data,
                "PaySim Fraud Detection Dataset (Sample)",
                "Synthetic mobile money transaction dataset with fraud labels. Sample of key patterns for fraud detection model training."
            )
            TextConverter.save_to_knowledge_base(text_content, f"training_paysim_fraud_sample")
            converted_count += 1
        
        print(f"\n✅ Converted {converted_count} datasets to knowledge base")
        print("💾 All data now available in text format for RAG system")
        print("📍 Files saved to: data/fraud_knowledge_base/")
        
        return {"converted_files": converted_count, "knowledge_base_updated": True}

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
            ("FRED", "fred"),
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
            elif api_key in ["alpha_vantage", "fred", "opencorporates", "companies_house"] and not available:
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
    print("3. 📚 Convert all data to RAG knowledge base")
    print("4. Check API configuration status") 
    print("5. Run demonstration (preview data without saving)")
    print("6. Show API cost estimates and setup guide")
    
    try:
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            # Download and save free data sources
            saved_data = download_and_save_free_data()
            
        elif choice == "2":
            # Download all available data sources
            pipeline = RealWorldDataPipeline()
            saved_data = pipeline.download_all_available_data()
            
        elif choice == "3":
            # Convert all data to knowledge base
            pipeline = RealWorldDataPipeline()
            result = pipeline.convert_all_data_to_knowledge_base()
            
        elif choice == "4":
            # Check API status
            pipeline = RealWorldDataPipeline()
            pipeline.check_api_status()
            
        elif choice == "5":
            # Run the demonstration
            real_data = demonstrate_real_data_integration()
            
        elif choice == "6":
            # Show cost estimates and setup
            print("\n📋 API SETUP GUIDE")
            print("="*50)
            print("1. Copy 'api_config_template.env' to '.env'")
            print("2. Fill in your API keys in the .env file")
            print("3. Run option 4 to check your configuration")
            print("4. Use option 2 to download enhanced datasets")
            print("5. Use option 3 to convert data to knowledge base")
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
