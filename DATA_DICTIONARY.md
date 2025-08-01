# InvestigatorAI Data Dictionary

> **📂 Navigation**: [🏠 Home](README.md) | [🎓 Certification](CERTIFICATION_CHALLENGE.md) | [📊 Data Dictionary](DATA_DICTIONARY.md) | [🎬 Demo Guide](DEMO_GUIDE.md) | [🔄 Merge Instructions](MERGE.md) | [💻 Frontend Docs](frontend/README.md)

> **Comprehensive catalog of all data sources collected by the InvestigatorAI system**

This document provides a complete reference for all data sources, files, and datasets collected by the three data collection scripts. Each entry includes the source location, data format, content description, and specific relevance to fraud investigation workflows.

---

## 📊 Core Government & Regulatory Data
*Sources from `get_data.py`*

| Data Source | Filename/Format | Description | Fraud Investigation Relevance |
|-------------|-----------------|-------------|------------------------------|
| **OFAC SDN List** | `ofac_sdn_list_YYYYMMDD.csv` | Specially Designated Nationals and blocked persons list with names, aliases, and identifying information | **Sanctions Screening**: Real-time compliance checking against prohibited entities and individuals |
| **FinCEN Geographic Targeting Orders** | `fincen_gto_orders_YYYYMMDD.json` | Geographic areas with enhanced reporting requirements for cash transactions above specified thresholds | **Geographic Risk Assessment**: Identifies high-risk jurisdictions requiring additional due diligence |
| **BSA Filing Requirements** | `bsa_filing_requirements_YYYYMMDD.json` | Bank Secrecy Act thresholds, deadlines, and high-risk jurisdiction lists | **Compliance Framework**: Defines regulatory thresholds and reporting requirements for suspicious activity |
| **World Bank Country Risk** | `world_bank_country_risk_YYYYMMDD.csv` | GDP per capita data with risk level classifications (high/medium/low) for all countries | **Country Risk Scoring**: Economic context for cross-border transaction risk assessment |
| **Exchange Rates** | `exchange_rates_YYYYMMDD_HHMM.json` | Current USD exchange rates for major currencies with timestamps | **Currency Analysis**: Detect unusual currency conversion patterns and pricing anomalies |
| **FinCEN Advisories** | `fincen_advisories_YYYYMMDD.json` | Regulatory alerts on human trafficking, ransomware, and emerging threat typologies | **Pattern Recognition**: Current red flags and suspicious activity indicators from regulators |
| **FATF High-Risk Jurisdictions** | `fatf_jurisdictions_YYYYMMDD.json` | Current lists of high-risk and monitored jurisdictions for money laundering | **Jurisdictional Risk**: Geographic risk factors for enhanced due diligence requirements |

---

## 📈 Economic & Financial Market Data
*Enhanced sources from `get_data.py`*

| Data Source | Filename/Format | Description | Fraud Investigation Relevance |
|-------------|-----------------|-------------|------------------------------|
| **FRED Economic Indicators** | `fred/series_[SERIES_ID]_YYYYMMDD.csv` | Time series data for GDP, unemployment, interest rates, money supply, bank credit | **Economic Context**: Understand economic conditions affecting fraud patterns and financial stress |
| **FRED Banking Indicators** | `fred/series_[BANKING_ID]_YYYYMMDD.csv` | Bank deposits, loans, charge-off rates, delinquency rates, net interest margins | **Banking Health**: Assess financial institution stability and systemic risk factors |
| **Alpha Vantage Company Data** | `alpha_vantage/company_overview_[SYMBOL]_YYYYMMDD.json` | Public company financials, sector information, and market capitalization data | **Corporate Intelligence**: Due diligence on public companies involved in transactions |
| **Alpha Vantage Stock Data** | `alpha_vantage/stock_daily_[SYMBOL]_YYYYMMDD.json` | Daily stock prices for fraud-relevant sectors (financial, crypto, commodities) | **Market Manipulation**: Detect timing relationships between transactions and market movements |
| **Alpha Vantage FX Rates** | `alpha_vantage/fx_rates_[PAIR]_YYYYMMDD.json` | Foreign exchange rates for money laundering currencies (USD/EUR, USD/CNY, etc.) | **Currency Arbitrage**: Identify suspicious currency conversion patterns and rate manipulation |

---

## 🔬 Fraud Training Datasets
*Machine learning sources from `get_data.py`*

| Data Source | Filename/Format | Description | Fraud Investigation Relevance |
|-------------|-----------------|-------------|------------------------------|
| **PaySim Dataset** | `paysim_fraud_dataset_YYYYMMDD.csv` | 6M synthetic mobile money transactions with fraud labels (step, type, amount, balances, isFraud) | **Model Training**: Large-scale labeled dataset for fraud detection algorithm development |
| **Credit Card Fraud Dataset** | `credit_card_fraud_dataset_YYYYMMDD.csv` | 284K European credit card transactions with PCA-transformed features and fraud labels | **Baseline Models**: Industry-standard dataset for fraud detection model benchmarking |
| **PaySim Sample Data** | `paysim_sample_data_YYYYMMDD.csv` | Small sample of PaySim structure when full dataset unavailable | **Schema Reference**: Data structure template for transaction analysis pipelines |
| **Credit Card Sample Data** | `credit_card_sample_data_YYYYMMDD.csv` | Small sample of credit card fraud structure when full dataset unavailable | **Schema Reference**: Feature engineering template for card transaction analysis |

---

## 📄 Regulatory Documents & Manuals
*PDF sources from `get_text_data.py`*

| Data Source | Filename/Format | Description | Fraud Investigation Relevance |
|-------------|-----------------|-------------|------------------------------|
| **FinCEN Advisory PDFs** | `FinCEN_Advisory_[Topic]_YYYYMMDD.pdf` | Human trafficking, ransomware, pig-butchering, bulk cash smuggling alerts | **Typology Guidance**: Detailed red flags and suspicious activity indicators by threat type |
| **FFIEC BSA/AML Manual** | `FFIEC_BSA_AML_Manual_YYYYMMDD.pdf` | Comprehensive examination procedures, control requirements, and compliance frameworks | **Regulatory Standards**: Authoritative guidance on AML controls and risk management |
| **Federal Register Documents** | `Federal_Register_[Topic]_YYYYMMDD.pdf` | Proposed and final rules affecting AML/CFT requirements and enforcement actions | **Regulatory Updates**: Latest compliance requirements and enforcement priorities |
| **Treasury Guidance** | `Treasury_[Topic]_YYYYMMDD.pdf` | Department of Treasury advisories, sanctions guidance, and enforcement actions | **Government Policy**: Official policy positions on sanctions, crypto, and emerging threats |
| **State Documents** | `[State]_[Topic]_YYYYMMDD.pdf` | State-level MSB licensing, regulatory guidance, and enforcement actions | **Jurisdictional Requirements**: State-specific compliance obligations and risk factors |

---

## 📚 Processed Knowledge Base for RAG
*Processed text files from `get_text_data.py`*

| Data Source | Filename/Format | Description | Fraud Investigation Relevance |
|-------------|-----------------|-------------|------------------------------|
| **Knowledge Base Index** | `fraud_knowledge_base/INDEX.txt` | Catalog of all processed documents with metadata, categories, and RAG integration notes | **System Reference**: Document inventory and loading instructions for RAG systems |
| **FinCEN Advisories (Processed)** | `fincen_advisories_[Topic]_[Year].txt` | Extracted and cleaned text from FinCEN PDF advisories, optimized for LLM processing | **RAG Content**: Ready-to-use regulatory guidance for LLM reasoning and pattern matching |
| **FFIEC Manual (Processed)** | `ffiec_examination_manual_[Section].txt` | Processed examination manual sections with structured formatting for compliance queries | **Compliance RAG**: Authoritative examination procedures accessible via natural language queries |
| **Federal Guidance (Processed)** | `federal_guidance_[Agency]_[Topic].txt` | Cleaned text from federal agency guidance documents (Federal Reserve, FDIC, IRS) | **Multi-Agency RAG**: Cross-agency regulatory requirements for comprehensive compliance checking |

---

## 📊 Statistical Workbooks & Trend Data
*Excel sources from `get_additional_data.py`*

| Data Source | Filename/Format | Description | Fraud Investigation Relevance |
|-------------|-----------------|-------------|------------------------------|
| **FinCEN SAR Statistics** | `sar_statistics_YYYY.xlsx` | Multi-sheet workbooks with SAR filings by industry, state, activity type, and filing entity | **Pattern Analysis**: Historical trends in suspicious activity reporting by sector and geography |
| **FinCEN SAR Trends** | `sar_trends_bulk.csv` | Bulk CSV with SAR filing counts, amounts, and trend indicators over time | **Trend Detection**: Quantitative analysis of suspicious activity volumes and emerging patterns |
| **EBA Risk Indicators** | `eba_risk_indicators_YYYYMMDD.xlsx` | 300+ European bank risk metrics including capital ratios, liquidity, and NPL data | **Banking Risk**: Systemic risk indicators for European financial institutions |
| **EBA Stress Test Data** | `eba_stress_test_YYYYMMDD.xlsx` | Bank-by-bank stress test results with adverse scenario modeling | **Financial Stability**: Bank resilience data for counterparty risk assessment |

---

## 🔧 Structured Synthetic Data
*GitHub sources from `get_additional_data.py`*

| Data Source | Filename/Format | Description | Fraud Investigation Relevance |
|-------------|-----------------|-------------|------------------------------|
| **AMLSim Accounts** | `accounts.csv` | Synthetic bank account data with account types, balances, and customer profiles | **Network Analysis**: Account relationship mapping for money laundering pattern detection |
| **AMLSim Alert Patterns** | `alertPatterns.csv` | Predefined suspicious activity patterns and money laundering typologies | **Pattern Library**: Known ML schemes for rule-based detection system development |
| **AMLSim Transactions** | `transactions.csv` | Synthetic transaction data with money laundering flags and pattern classifications | **Training Data**: Labeled synthetic transactions for ML model training and validation |
| **AMLSim Typology** | `AMLTypology.json` | JSON definitions of money laundering schemes, stages, and detection methods | **Scheme Reference**: Structured knowledge base of laundering methodologies |
| **SWIFT MT103 Sample** | `MT103.xml` | XML format single customer credit transfer message with all required fields | **Message Parsing**: Wire transfer format reference for payment message analysis |
| **SWIFT MT202 Sample** | `MT202.xml` | XML format general financial institution transfer for interbank payments | **Interbank Analysis**: Bank-to-bank transfer format for correspondent banking monitoring |
| **SWIFT MT900 Sample** | `MT900.xml` | XML format confirmation of debit message for payment confirmations | **Transaction Confirmation**: Payment confirmation format for transaction verification |

---

## 🌍 International Standards & Assessments
*International sources from `get_additional_data.py`*

| Data Source | Filename/Format | Description | Fraud Investigation Relevance |
|-------------|-----------------|-------------|------------------------------|
| **INTERPOL Fraud Assessment** | `interpol_fraud_assessment_YYYYMMDD.pdf` | Global financial fraud trends, cross-border typologies, and loss statistics | **Global Perspective**: International fraud trends and cross-border investigative approaches |
| **FATF Risk Assessment** | `fatf_risk_assessment_YYYYMMDD.pdf` | National risk assessment methodology and step-by-step scoring frameworks | **Risk Methodology**: Systematic approach to country and sectoral risk assessment |
| **Open Banking Guidelines** | `open_banking_guidelines_YYYYMMDD.pdf` | API standards, consent models, and security frameworks for open banking | **API Security**: Technical standards for secure financial data sharing and fraud prevention |

---

## 🚫 Enhanced Sanctions & Watchlist Data
*Comprehensive sanctions from `get_additional_data.py`*

| Data Source | Filename/Format | Description | Fraud Investigation Relevance |
|-------------|-----------------|-------------|------------------------------|
| **OFAC Consolidated Sanctions** | `consolidated_sanctions_YYYYMMDD.csv` | Complete sanctions list with all programs, consolidated view of restricted parties | **Comprehensive Screening**: Complete sanctions universe for thorough compliance checking |
| **OFAC Alternate Names** | `sdn_alternate_names_YYYYMMDD.csv` | Aliases, alternative spellings, and name variations for sanctioned entities | **Name Matching**: Enhanced entity resolution for fuzzy name matching algorithms |
| **OFAC Addresses** | `sdn_addresses_YYYYMMDD.csv` | Physical addresses, postal codes, and location data for sanctioned parties | **Geographic Screening**: Location-based sanctions screening and address verification |
| **OFAC Programs** | `sanctions_programs_YYYYMMDD.csv` | Sanctions program details, legal authorities, and program-specific restrictions | **Program Analysis**: Understanding sanctions scope and applicable restrictions by program |
| **FATF Risk Indicators** | `risk_indicators_YYYYMMDD.json` | Trade-based ML indicators and jurisdictional risk factors | **Risk Indicators**: Structured red flags for trade finance and jurisdictional risk assessment |

---

## 📋 Data Refresh Schedule

| Data Category | Recommended Refresh | Rationale |
|---------------|-------------------|-----------|
| **Sanctions Lists** | Daily | OFAC updates daily; critical for compliance |
| **Exchange Rates** | Hourly | High volatility; affects transaction analysis |
| **Economic Indicators** | Weekly | FRED data updates weekly; economic context |
| **SAR Statistics** | Monthly | FinCEN publishes monthly; trend analysis |
| **Regulatory Documents** | Weekly | New advisories and guidance published regularly |
| **RAG Knowledge Base** | Weekly | Reprocess when new PDFs are added to maintain current content |
| **Training Datasets** | Annually | Kaggle datasets updated infrequently |
| **International Documents** | Quarterly | Major assessments published quarterly |

---

## 🎯 Integration with InvestigatorAI Workflow

### **Data by Investigation Stage**

| Investigation Stage | Primary Data Sources | Analysis Type |
|-------------------|---------------------|---------------|
| **Initial Screening** | OFAC SDN, Enhanced Sanctions, FATF Jurisdictions | Name matching, geographic risk |
| **Transaction Analysis** | PaySim, Credit Card Fraud, Exchange Rates | Pattern recognition, anomaly detection |
| **Risk Assessment** | World Bank Risk, FRED Indicators, EBA Metrics | Economic context, systemic risk |
| **Typology Matching** | FinCEN Advisories, AMLSim Patterns, SWIFT Samples | Scheme identification, red flag detection |
| **Compliance Verification** | BSA Requirements, FFIEC Manual, Regulatory PDFs | Regulatory requirements, control validation |
| **RAG-Powered Analysis** | Processed Knowledge Base (fraud_knowledge_base) | Natural language queries, regulatory reasoning |
| **Documentation** | SAR Statistics, INTERPOL Assessment, Open Banking | Benchmarking, international best practices |

### **File Organization Structure**
```
data/
├── additional_sources/           # Specialized datasets
│   ├── fincen_sar/              # SAR statistics and trends
│   ├── eba/                     # European banking data
│   ├── github/                  # Synthetic data and samples
│   ├── international/           # Global assessments and standards
│   ├── ofac_enhanced/           # Comprehensive sanctions data
│   └── fatf/                    # Risk indicators and methodology
├── fraud_knowledge_base/        # Processed text files for RAG
│   ├── INDEX.txt               # Document catalog and metadata
│   ├── fincen_advisories_*.txt # Processed FinCEN guidance
│   ├── ffiec_examination_*.txt # Processed FFIEC manuals
│   └── federal_guidance_*.txt  # Processed federal agency docs
├── alpha_vantage/               # Financial market data
├── fred/                        # US economic indicators
├── kaggle/                      # Fraud detection datasets
├── pdf_downloads/               # Original regulatory PDF documents
└── [date-stamped files]         # Core regulatory data (CSV/JSON)
```

---

## 📖 Acronym Glossary

| Acronym | Full Name | Description |
|---------|-----------|-------------|
| **AML** | Anti-Money Laundering | Regulatory framework to prevent money laundering and terrorist financing |
| **API** | Application Programming Interface | Software interface for accessing data from external services |
| **BSA** | Bank Secrecy Act | US law requiring financial institutions to report suspicious activities |
| **CSV** | Comma-Separated Values | Plain text file format for tabular data |
| **EBA** | European Banking Authority | EU regulatory body for banking supervision |
| **EDGAR** | Electronic Data Gathering, Analysis, and Retrieval | SEC's system for corporate filings |
| **FATF** | Financial Action Task Force | International body setting AML/CFT standards |
| **FFIEC** | Federal Financial Institutions Examination Council | US interagency body for uniform examination standards |
| **FinCEN** | Financial Crimes Enforcement Network | US Treasury bureau for financial intelligence |
| **FRED** | Federal Reserve Economic Data | Economic data platform by Federal Reserve Bank of St. Louis |
| **FX** | Foreign Exchange | Currency exchange markets and rates |
| **GTO** | Geographic Targeting Order | FinCEN requirement for enhanced due diligence in specific regions |
| **INTERPOL** | International Criminal Police Organization | Global police cooperation organization |
| **JSON** | JavaScript Object Notation | Lightweight data interchange format |
| **LLM** | Large Language Model | AI models trained on large text datasets for natural language processing |
| **MSB** | Money Services Business | Financial service providers like money transmitters and currency exchanges |
| **OFAC** | Office of Foreign Assets Control | US Treasury office administering economic sanctions |
| **PDF** | Portable Document Format | Document format that preserves formatting across platforms |
| **RAG** | Retrieval-Augmented Generation | AI technique combining information retrieval with language generation |
| **SAR** | Suspicious Activity Report | Mandatory filing for potentially suspicious financial transactions |
| **SDN** | Specially Designated Nationals | OFAC list of blocked persons and entities |
| **SEC** | Securities and Exchange Commission | US federal agency regulating securities markets |
| **SWIFT** | Society for Worldwide Interbank Financial Telecommunication | Global financial messaging network |
| **XML** | eXtensible Markup Language | Structured markup language for data exchange |

---

**Generated**: `2024-12-28 15:30:00`  
**Scripts**: `get_data.py`, `get_text_data.py`, `get_additional_data.py`  
**Total Data Sources**: 45+ distinct datasets and document collections  
**RAG-Ready**: Processed knowledge base with 7+ regulatory documents optimized for LLM reasoning 