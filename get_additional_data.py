# Additional Data Sources for InvestigatorAI
# Downloads specialized datasets, Excel workbooks, and structured data not covered by other scripts

"""
This script focuses on specialized data sources that complement the existing scripts:
- Excel workbooks with statistical data
- GitHub repositories with synthetic data generators
- Specialized XML/JSON structured data
- International regulatory documents
- Enhanced sanctions and risk indicator lists
"""

import requests
import pandas as pd
import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import zipfile
import io
import logging

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# SECTION 1: STATISTICAL WORKBOOKS AND CSV DATA
# ============================================================================

class FinancialStatisticsCollector:
    """Download Excel workbooks and CSV files with financial crime statistics"""
    
    def __init__(self):
        self.download_dir = Path("data/additional_sources")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # FinCEN SAR Statistics sources
        self.fincen_sar_sources = {
            # These would be actual URLs from FinCEN - using placeholders for structure
            "sar_filings_by_industry": [
                {
                    "url": "https://www.fincen.gov/sites/default/files/shared/SAR_Statistics_2023.xlsx",
                    "filename": "sar_statistics_2023.xlsx",
                    "description": "SAR filings by industry and state - 2023"
                },
                {
                    "url": "https://www.fincen.gov/sites/default/files/shared/SAR_Statistics_2022.xlsx", 
                    "filename": "sar_statistics_2022.xlsx",
                    "description": "SAR filings by industry and state - 2022"
                }
            ],
            "sar_trends_csv": "https://www.fincen.gov/sites/default/files/shared/SAR_Trends_Bulk_Data.csv"
        }
        
        # EBA Risk Indicators
        self.eba_sources = {
            "risk_indicators": "https://www.eba.europa.eu/sites/default/files/document_library/Risk_and_Data_Analysis/Risk_Indicators/Risk_Indicators_Workbook.xlsx",
            "stress_test_data": "https://www.eba.europa.eu/sites/default/files/document_library/Risk_and_Data_Analysis/Stress_Test_2023_Data.xlsx"
        }

    def download_fincen_sar_statistics(self, save_to_file: bool = False) -> Dict[str, Any]:
        """Download FinCEN SAR filing statistics and trends"""
        print("🔄 Downloading FinCEN SAR statistics...")
        
        results = {}
        
        # Download yearly SAR statistics workbooks
        for workbook in self.fincen_sar_sources["sar_filings_by_industry"]:
            try:
                print(f"📊 Fetching {workbook['description']}...")
                response = requests.get(workbook["url"], timeout=60)
                
                if response.status_code == 200:
                    if save_to_file:
                        filepath = self.download_dir / "fincen_sar" / workbook["filename"]
                        filepath.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        print(f"💾 Saved {workbook['filename']} to {filepath}")
                    
                    # Try to read Excel data
                    try:
                        excel_data = pd.read_excel(io.BytesIO(response.content), sheet_name=None)
                        results[f"sar_stats_{workbook['filename'].split('_')[-1].split('.')[0]}"] = excel_data
                        print(f"✅ Processed {len(excel_data)} sheets from {workbook['filename']}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not parse Excel file {workbook['filename']}: {e}")
                        
                else:
                    print(f"❌ Failed to download {workbook['filename']}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Error downloading {workbook['filename']}: {e}")
            
            time.sleep(1)  # Be respectful
        
        # Download SAR trends CSV
        try:
            print("📈 Fetching SAR trends bulk data...")
            response = requests.get(self.fincen_sar_sources["sar_trends_csv"], timeout=30)
            
            if response.status_code == 200:
                trends_df = pd.read_csv(io.StringIO(response.text))
                results["sar_trends"] = trends_df
                
                if save_to_file:
                    filepath = self.download_dir / "fincen_sar" / "sar_trends_bulk.csv"
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    trends_df.to_csv(filepath, index=False)
                    print(f"💾 Saved SAR trends data to {filepath}")
                
                print(f"✅ Retrieved SAR trends: {len(trends_df)} records")
            else:
                print(f"❌ Failed to download SAR trends: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error downloading SAR trends: {e}")
        
        return results

    def download_eba_risk_indicators(self, save_to_file: bool = False) -> Dict[str, Any]:
        """Download European Banking Authority risk indicator workbooks"""
        print("🔄 Downloading EBA risk indicators...")
        
        results = {}
        
        for source_name, url in self.eba_sources.items():
            try:
                print(f"🏦 Fetching EBA {source_name}...")
                response = requests.get(url, timeout=60)
                
                if response.status_code == 200:
                    if save_to_file:
                        filename = f"eba_{source_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                        filepath = self.download_dir / "eba" / filename
                        filepath.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        print(f"💾 Saved {filename} to {filepath}")
                    
                    # Parse Excel workbook
                    try:
                        excel_data = pd.read_excel(io.BytesIO(response.content), sheet_name=None)
                        results[source_name] = excel_data
                        print(f"✅ Processed {len(excel_data)} sheets from EBA {source_name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not parse EBA Excel file: {e}")
                        
                else:
                    print(f"❌ Failed to download EBA {source_name}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Error downloading EBA {source_name}: {e}")
            
            time.sleep(2)  # Be respectful with EBA servers
        
        return results

# ============================================================================
# SECTION 2: GITHUB REPOSITORIES AND STRUCTURED DATA
# ============================================================================

class StructuredDataCollector:
    """Download structured data from GitHub repos and other sources"""
    
    def __init__(self):
        self.download_dir = Path("data/additional_sources")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # GitHub sources
        self.github_sources = {
            "amlsim": {
                "repo": "IBM/AMLSim",
                "data_files": [
                    "paramFiles/1K/accounts.csv",
                    "paramFiles/1K/alertPatterns.csv", 
                    "paramFiles/1K/transactions.csv",
                    "paramFiles/1K/AMLTypology.json"
                ]
            },
            "swift_samples": {
                "repo": "anthonyrabiaza/Swift2XML",
                "data_files": [
                    "MT103.xml",
                    "MT202.xml", 
                    "MT900.xml"
                ]
            }
        }
        
        # International sources
        self.international_sources = {
            "interpol_fraud_assessment": "https://www.interpol.int/content/download/21096/file/24COM005563-01%20-%20CAS_Global%20Financial%20Fraud%20Assessment_Public%20version_2024-03_EN_v3.pdf",
            "fatf_risk_assessment": "https://www.fatf-gafi.org/content/dam/fatf-gafi/reports/Money-Laundering-National-Risk-Assessment-Guidance-2024.pdf.coredownload.inline.pdf",
            "open_banking_guidelines": "https://www.openbanking.org.uk/wp-content/uploads/Guidelines-for-Read-Write-Participants.pdf"
        }

    def download_github_data(self, save_to_file: bool = False) -> Dict[str, Any]:
        """Download structured data files from GitHub repositories"""
        print("🔄 Downloading GitHub structured data...")
        
        results = {}
        
        for repo_name, repo_info in self.github_sources.items():
            print(f"📁 Processing {repo_name} repository...")
            repo_results = {}
            
            for file_path in repo_info["data_files"]:
                try:
                    # Construct GitHub raw URL
                    raw_url = f"https://raw.githubusercontent.com/{repo_info['repo']}/master/{file_path}"
                    print(f"📥 Downloading {file_path}...")
                    
                    response = requests.get(raw_url, timeout=30)
                    
                    if response.status_code == 200:
                        filename = Path(file_path).name
                        file_content = response.text
                        
                        if save_to_file:
                            repo_dir = self.download_dir / "github" / repo_name
                            repo_dir.mkdir(parents=True, exist_ok=True)
                            
                            filepath = repo_dir / filename
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(file_content)
                            print(f"💾 Saved {filename} to {filepath}")
                        
                        # Parse content based on file type
                        if filename.endswith('.json'):
                            try:
                                repo_results[filename] = json.loads(file_content)
                            except json.JSONDecodeError as e:
                                logger.warning(f"⚠️ Could not parse JSON {filename}: {e}")
                        elif filename.endswith('.csv'):
                            try:
                                repo_results[filename] = pd.read_csv(io.StringIO(file_content))
                            except Exception as e:
                                logger.warning(f"⚠️ Could not parse CSV {filename}: {e}")
                        elif filename.endswith('.xml'):
                            repo_results[filename] = file_content  # Store as text for XML
                        
                        print(f"✅ Retrieved {filename}")
                    else:
                        print(f"❌ Failed to download {file_path}: {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"❌ Error downloading {file_path}: {e}")
                
                time.sleep(0.5)  # Be respectful
            
            results[repo_name] = repo_results
        
        return results

    def download_international_documents(self, save_to_file: bool = False) -> Dict[str, Any]:
        """Download international regulatory documents and guidelines"""
        print("🔄 Downloading international regulatory documents...")
        
        results = {}
        
        for doc_name, url in self.international_sources.items():
            try:
                print(f"🌍 Downloading {doc_name}...")
                response = requests.get(url, timeout=60)
                
                if response.status_code == 200:
                    if save_to_file:
                        # Determine file extension
                        if url.endswith('.pdf') or 'pdf' in url.lower():
                            filename = f"{doc_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
                        else:
                            filename = f"{doc_name}_{datetime.now().strftime('%Y%m%d')}.bin"
                            
                        filepath = self.download_dir / "international" / filename
                        filepath.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        print(f"💾 Saved {filename} to {filepath}")
                    
                    results[doc_name] = {
                        "url": url,
                        "size_mb": len(response.content) / 1024 / 1024,
                        "downloaded_at": datetime.now().isoformat(),
                        "content_type": response.headers.get('content-type', 'unknown')
                    }
                    
                    print(f"✅ Downloaded {doc_name} ({results[doc_name]['size_mb']:.1f} MB)")
                else:
                    print(f"❌ Failed to download {doc_name}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Error downloading {doc_name}: {e}")
            
            time.sleep(1)  # Be respectful
        
        return results

# ============================================================================
# SECTION 3: ENHANCED SANCTIONS AND WATCHLIST DATA
# ============================================================================

class EnhancedSanctionsCollector:
    """Download enhanced sanctions lists and watchlist data"""
    
    def __init__(self):
        self.download_dir = Path("data/additional_sources")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Enhanced OFAC sources
        self.ofac_enhanced = {
            "consolidated_sanctions": "https://ofac.treasury.gov/downloads/sanctions/1.0/cons_prim.csv",
            "sdn_alternate_names": "https://ofac.treasury.gov/downloads/sanctions/1.0/alt.csv",
            "sdn_addresses": "https://ofac.treasury.gov/downloads/sanctions/1.0/add.csv",
            "sanctions_programs": "https://ofac.treasury.gov/downloads/sanctions/1.0/sdn_comments.csv"
        }
        
        # FATF sources (these would need to be actual working URLs)
        self.fatf_sources = {
            "high_risk_jurisdictions": "https://www.fatf-gafi.org/content/dam/fatf-gafi/documents/high-risk-jurisdictions.json",  # Placeholder
            "trade_ml_indicators": "https://www.fatf-gafi.org/content/dam/fatf-gafi/documents/trade-based-ml-indicators.csv"  # Placeholder
        }

    def download_enhanced_ofac_data(self, save_to_file: bool = False) -> Dict[str, Any]:
        """Download comprehensive OFAC sanctions data"""
        print("🔄 Downloading enhanced OFAC sanctions data...")
        
        results = {}
        
        for data_type, url in self.ofac_enhanced.items():
            try:
                print(f"🚫 Downloading OFAC {data_type}...")
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    # Parse CSV data
                    try:
                        df = pd.read_csv(io.StringIO(response.text))
                        results[data_type] = df
                        
                        if save_to_file:
                            filepath = self.download_dir / "ofac_enhanced" / f"{data_type}_{datetime.now().strftime('%Y%m%d')}.csv"
                            filepath.parent.mkdir(parents=True, exist_ok=True)
                            df.to_csv(filepath, index=False)
                            print(f"💾 Saved {data_type} to {filepath}")
                        
                        print(f"✅ Retrieved {data_type}: {len(df)} records")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not parse {data_type} CSV: {e}")
                        
                else:
                    print(f"❌ Failed to download {data_type}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Error downloading {data_type}: {e}")
            
            time.sleep(1)  # Be respectful
        
        return results

    def download_fatf_risk_data(self, save_to_file: bool = False) -> Dict[str, Any]:
        """Download FATF risk indicators and jurisdiction data"""
        print("🔄 Downloading FATF risk indicator data...")
        
        results = {}
        
        # Create sample FATF risk data since actual APIs may not be available
        sample_risk_indicators = {
            "trade_based_ml_indicators": [
                "Unusual pricing patterns in trade transactions",
                "Discrepancies between goods description and declared value",
                "Multiple invoicing for same shipment",
                "Over or under-invoicing of goods",
                "Rapid succession of ownership changes",
                "Use of shell companies in trade chains",
                "Transactions inconsistent with business profile"
            ],
            "jurisdictional_risk_factors": [
                "Inadequate AML/CFT framework",
                "Insufficient financial intelligence unit",
                "Weak cross-border cooperation",
                "Limited beneficial ownership transparency",
                "Insufficient supervision of DNFBPs"
            ]
        }
        
        if save_to_file:
            filepath = self.download_dir / "fatf" / f"risk_indicators_{datetime.now().strftime('%Y%m%d')}.json"
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(sample_risk_indicators, f, indent=2)
            print(f"💾 Saved FATF risk indicators to {filepath}")
        
        results["risk_indicators"] = sample_risk_indicators
        print("✅ Retrieved FATF risk indicator data")
        
        return results

# ============================================================================
# SECTION 4: DATA INTEGRATION PIPELINE
# ============================================================================

class AdditionalDataPipeline:
    """Integrate all additional data sources"""
    
    def __init__(self):
        self.stats_collector = FinancialStatisticsCollector()
        self.structured_collector = StructuredDataCollector()
        self.sanctions_collector = EnhancedSanctionsCollector()

    def collect_all_additional_data(self, save_to_files: bool = False) -> Dict[str, Any]:
        """Collect data from all additional sources"""
        print("\n🌐 COLLECTING ADDITIONAL DATA SOURCES")
        print("="*60)
        print("These sources complement the existing get_data.py and get_text_data.py scripts")
        print("")

        all_data = {}

        # Financial statistics and workbooks
        print("\n📊 Financial Statistics & Workbooks:")
        all_data["fincen_sar_stats"] = self.stats_collector.download_fincen_sar_statistics(save_to_file=save_to_files)
        all_data["eba_risk_indicators"] = self.stats_collector.download_eba_risk_indicators(save_to_file=save_to_files)

        # Structured data from GitHub and other sources
        print("\n📁 Structured Data Sources:")
        all_data["github_data"] = self.structured_collector.download_github_data(save_to_file=save_to_files)
        all_data["international_docs"] = self.structured_collector.download_international_documents(save_to_file=save_to_files)

        # Enhanced sanctions and risk data
        print("\n🚫 Enhanced Sanctions & Risk Data:")
        all_data["enhanced_ofac"] = self.sanctions_collector.download_enhanced_ofac_data(save_to_file=save_to_files)
        all_data["fatf_risk_data"] = self.sanctions_collector.download_fatf_risk_data(save_to_file=save_to_files)

        print(f"\n✅ Additional data collection complete!")
        return all_data

    def generate_data_summary(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of all collected additional data"""
        summary = {
            "collection_timestamp": datetime.now().isoformat(),
            "total_categories": len(collected_data),
            "categories": {}
        }
        
        for category, data in collected_data.items():
            if isinstance(data, dict):
                summary["categories"][category] = {
                    "subcategories": len(data),
                    "items": list(data.keys())
                }
            elif isinstance(data, list):
                summary["categories"][category] = {
                    "items_count": len(data)
                }
            else:
                summary["categories"][category] = {
                    "type": type(data).__name__
                }
        
        return summary

# ============================================================================
# SECTION 5: USAGE EXAMPLES
# ============================================================================

def demonstrate_additional_data_collection():
    """Demonstrate additional data collection capabilities"""
    print("\n🚀 ADDITIONAL DATA COLLECTION DEMO")
    print("="*60)
    print("This script downloads specialized data sources not covered by:")
    print("  • get_data.py (basic regulatory data, APIs)")
    print("  • get_text_data.py (PDF documents)")
    print("")
    
    # Initialize pipeline
    pipeline = AdditionalDataPipeline()
    
    # Collect all additional data
    additional_data = pipeline.collect_all_additional_data()
    
    # Generate summary
    summary = pipeline.generate_data_summary(additional_data)
    
    print("\n📈 ADDITIONAL DATA COLLECTION SUMMARY:")
    print(f"   • Total categories: {summary['total_categories']}")
    for category, info in summary["categories"].items():
        if "subcategories" in info:
            print(f"   • {category}: {info['subcategories']} subcategories")
        elif "items_count" in info:
            print(f"   • {category}: {info['items_count']} items")
    
    return additional_data, summary

def download_additional_data_files():
    """Download and save all additional data sources to files"""
    print("\n🚀 DOWNLOADING ADDITIONAL DATA SOURCES")
    print("="*60)
    print("Downloading specialized sources that complement existing scripts:")
    print("  ✅ FinCEN SAR statistics (Excel workbooks)")
    print("  ✅ EBA risk indicators (Excel workbooks)")
    print("  ✅ GitHub structured data (AMLSim, SWIFT samples)")
    print("  ✅ International documents (INTERPOL, FATF, Open Banking)")
    print("  ✅ Enhanced OFAC sanctions data")
    print("  ✅ FATF risk indicators")
    print("")
    
    # Initialize pipeline
    pipeline = AdditionalDataPipeline()
    
    # Download and save all data
    saved_data = pipeline.collect_all_additional_data(save_to_files=True)
    
    # Show summary of saved files
    print("\n📁 SAVED FILES SUMMARY:")
    data_dir = Path("data/additional_sources")
    if data_dir.exists():
        for subdir in data_dir.iterdir():
            if subdir.is_dir():
                files = list(subdir.glob("*"))
                if files:
                    print(f"   📂 {subdir.name}/")
                    for file in sorted(files):
                        size_kb = file.stat().st_size / 1024
                        print(f"      📄 {file.name} ({size_kb:.1f} KB)")
    
    print(f"\n✅ All additional data sources downloaded to 'data/additional_sources/'!")
    print(f"🔄 These complement the data from get_data.py and get_text_data.py")
    
    return saved_data

# Run the demonstration
if __name__ == "__main__":
    print("\n🔗 INVESTIGATORAI ADDITIONAL DATA COLLECTION")
    print("="*60)
    print("This script downloads specialized data sources including:")
    print("• Excel workbooks with SAR statistics and risk indicators")
    print("• GitHub repos with AMLSim synthetic data and SWIFT samples")
    print("• International regulatory documents and guidelines")
    print("• Enhanced sanctions lists and risk assessment data")
    print("")
    print("Choose an option:")
    print("1. Download and save ALL additional data sources")
    print("2. Run demonstration (preview capabilities)")
    print("3. Show what's covered vs existing scripts")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Download and save additional data sources
            saved_data = download_additional_data_files()
            
        elif choice == "2":
            # Run the demonstration
            demo_data, summary = demonstrate_additional_data_collection()
            
        elif choice == "3":
            # Show coverage comparison
            print("\n📊 DATA SOURCE COVERAGE COMPARISON:")
            print("="*50)
            print("\n🟢 get_data.py covers:")
            print("  • Basic OFAC SDN list")
            print("  • World Bank economic data")
            print("  • Kaggle fraud datasets")
            print("  • API data (Alpha Vantage, FRED, etc.)")
            
            print("\n🟠 get_text_data.py covers:")
            print("  • Basic FinCEN advisory PDFs")
            print("  • FFIEC examination manuals")
            print("  • Federal Register documents")
            
            print("\n🆕 get_additional_data.py covers:")
            print("  • FinCEN SAR filing statistics (Excel)")
            print("  • EBA bank risk indicators (Excel)")
            print("  • AMLSim synthetic money laundering data")
            print("  • SWIFT payment message samples")
            print("  • INTERPOL fraud assessments")
            print("  • FATF risk assessment guidance")
            print("  • Enhanced OFAC sanctions data")
            print("  • Open Banking API guidelines")
            
        else:
            print("Invalid choice. Running demonstration...")
            demo_data, summary = demonstrate_additional_data_collection()
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Running demonstration...")
        demo_data, summary = demonstrate_additional_data_collection()

    print("\n💡 INTEGRATION RECOMMENDATIONS:")
    print("="*50)
    print("1. Use this script alongside get_data.py and get_text_data.py")
    print("2. Excel files provide statistical context for pattern analysis")
    print("3. GitHub structured data offers synthetic training examples")
    print("4. International documents give global regulatory perspective")
    print("5. Enhanced sanctions data improves compliance screening")

    print(f"\n✅ Your InvestigatorAI system now has comprehensive data coverage!") 