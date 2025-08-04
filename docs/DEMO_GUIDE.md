# InvestigatorAI Demo Guide

> **📂 Navigation**: [🏠 Home](../README.md) | [🤖 Agent Prompts](AGENT_PROMPTS.md) | [🎓 Certification](CERTIFICATION_CHALLENGE.md) | [🎬 Demo Guide](DEMO_GUIDE.md) | [🔄 Merge Instructions](../MERGE.md) | [💻 Frontend Docs](../frontend/README.md) | [📊 Data Docs](../data/README.md) | [🚀 Deploy Docs](../deploy/README.md)

## 🎯 Live Demo Instructions

### Prerequisites
- API running on `http://localhost:8000` ✅
- Frontend running on `http://localhost:3000` ✅
- Both services health status shows "Ready" ✅

## 🎬 Demo Scenarios - Real World Cases

### Scenario 1: "The Shell Company Equipment Purchase"
**Based on**: Real-world procurement fraud patterns

```json
{
  "amount": 85000,
  "currency": "USD",
  "description": "Large equipment purchase from overseas supplier through shell company",
  "customer_name": "Rapid Industries LLC",
  "account_type": "Business",
  "risk_rating": "High", 
  "country_to": "British Virgin Islands"
}
```

**Why This Is Suspicious:**
- High-value transaction to known tax haven
- Shell company with minimal business history
- Equipment purchase without proper documentation
- BVI is flagged jurisdiction for money laundering

**Expected Investigation Results:**
- Regulatory flags for offshore jurisdiction
- SAR filing recommendations
- Enhanced due diligence requirements

---

### Scenario 2: "The Cryptocurrency Exchange Transfer"
**Based on**: Emerging crypto-related fraud trends

```json
{
  "amount": 125000,
  "currency": "USD", 
  "description": "Investment transfer to cryptocurrency exchange platform",
  "customer_name": "Digital Assets Management Co",
  "account_type": "Corporate",
  "risk_rating": "Medium",
  "country_to": "Estonia"
}
```

**Why This Is Suspicious:**
- Large crypto investment without proper KYC
- Estonia has emerging crypto regulations
- Corporate structure for individual trading
- Potential sanctions evasion risk

---

### Scenario 3: "The Structured Cash Deposits"
**Based on**: Classic structuring patterns

```json
{
  "amount": 9500,
  "currency": "USD",
  "description": "Business cash deposit from daily operations",
  "customer_name": "Corner Market Express",
  "account_type": "Business", 
  "risk_rating": "Low",
  "country_to": "United States"
}
```

**Why This Is Suspicious:**
- Amount just under $10K CTR threshold
- Pattern suggests structuring to avoid reporting
- Cash-intensive business model
- Potential BSA compliance issues

---

### Scenario 4: "The Wire Transfer to High-Risk Country"
**Based on**: Sanctions and money laundering patterns

```json
{
  "amount": 75000,
  "currency": "USD",
  "description": "Business payment to overseas supplier for industrial equipment", 
  "customer_name": "Global Trading LLC",
  "account_type": "Business",
  "risk_rating": "Medium",
  "country_to": "UAE"
}
```

**Why This Is Suspicious:**
- UAE is higher-risk jurisdiction for money laundering
- Industrial equipment can be dual-use (civilian/military)
- Large payment without proper documentation
- Potential sanctions screening required

---

### Scenario 5: "The Politically Exposed Person Transaction"
**Based on**: PEP compliance requirements

```json
{
  "amount": 250000,
  "currency": "EUR",
  "description": "Real estate investment through trust structure",
  "customer_name": "International Holdings Trust",
  "account_type": "Corporate",
  "risk_rating": "High",
  "country_to": "Switzerland"
}
```

**Why This Is Suspicious:**
- High-value real estate transaction
- Trust structure obscures beneficial ownership
- Switzerland requires enhanced PEP monitoring
- Potential for corruption proceeds

---

### Scenario 6: "The Trade Finance Manipulation"
**Based on**: Import/export fraud schemes

```json
{
  "amount": 180000,
  "currency": "USD",
  "description": "Import payment for agricultural commodities from emerging market",
  "customer_name": "Agri-Trade International",
  "account_type": "Corporate",
  "risk_rating": "Medium",
  "country_to": "Nigeria"
}
```

**Why This Is Suspicious:**
- Nigeria on FATF grey list for AML deficiencies
- Agricultural commodities often used for trade-based money laundering
- Large payment without proper trade documentation
- Potential for invoice manipulation and value transfer

---

### Scenario 7: "The Charity Front Operation"
**Based on**: Nonprofit fraud and terrorist financing

```json
{
  "amount": 45000,
  "currency": "USD",
  "description": "Humanitarian aid transfer to international relief organization",
  "customer_name": "Global Relief Foundation",
  "account_type": "Nonprofit",
  "risk_rating": "Low",
  "country_to": "Turkey"
}
```

**Why This Is Suspicious:**
- Turkey border region with conflict zones
- Nonprofit sector vulnerable to terrorist financing
- Humanitarian aid can mask illicit fund transfers
- Requires enhanced due diligence for NPO accounts

---

### Scenario 8: "The Professional Services Laundering"
**Based on**: Service-based money laundering schemes

```json
{
  "amount": 95000,
  "currency": "USD",
  "description": "Consulting fees for business development and market analysis",
  "customer_name": "Strategic Consulting Group",
  "account_type": "Professional Services",
  "risk_rating": "Low",
  "country_to": "Panama"
}
```

**Why This Is Suspicious:**
- Panama known for offshore financial services
- Consulting services difficult to verify and value
- Professional services commonly used for laundering
- High fees for vague service descriptions

---

### Scenario 9: "The Gaming Platform Deposit"
**Based on**: Online gambling money laundering

```json
{
  "amount": 35000,
  "currency": "USD",
  "description": "Gaming platform deposit for online casino and sports betting",
  "customer_name": "Digital Entertainment LLC",
  "account_type": "Gaming/Entertainment",
  "risk_rating": "High",
  "country_to": "Malta"
}
```

**Why This Is Suspicious:**
- Online gambling high-risk for money laundering
- Malta gaming jurisdiction with regulatory challenges
- Digital platforms enable rapid fund movement
- Entertainment entities used to obscure beneficial ownership

---

### Scenario 10: "The Precious Metals Investment"
**Based on**: Alternative asset money laundering

```json
{
  "amount": 220000,
  "currency": "USD",
  "description": "Investment in precious metals and rare earth commodities",
  "customer_name": "Precious Assets Holdings",
  "account_type": "Investment",
  "risk_rating": "Medium",
  "country_to": "Hong Kong"
}
```

**Why This Is Suspicious:**
- Precious metals traditional money laundering vehicle
- Hong Kong financial hub with complex regulations
- Investment entities may obscure true ownership
- Alternative assets used to transfer value across borders

## 🛠️ Investigation Tools Deep Dive

### Tool 1: Regulatory Document Search
**Purpose**: Access real-time regulatory guidance and compliance requirements

**Example Usage**:
```
Query: "SAR filing threshold suspicious activity"
Agent: Regulatory Research Agent
Tool: search_regulatory_documents
Result: FinCEN guidance on $5,000 SAR threshold and filing requirements
Business Value: Instant access to current regulations vs. 2-hour manual research
```

**Advanced Queries**:
- `"beneficial ownership requirements CDD rule"`
- `"AML program requirements small banks"`
- `"wire transfer recordkeeping BSA requirements"`

### Tool 2: Transaction Risk Calculation
**Purpose**: Quantitative risk assessment using multiple factors

**Example Usage**:
```
Input: amount=75000, currency=USD, country=UAE, customer_risk=Medium
Agent: Evidence Collection Agent
Tool: calculate_transaction_risk
Result: Risk Score: 7.2/10 (High Risk)
Factors: Geographic risk (3.5), Amount threshold (2.1), Customer profile (1.6)
```

**Risk Factors Analyzed**:
- Geographic jurisdiction risk levels
- Transaction amount thresholds
- Customer risk profile weighting
- Historical pattern analysis

### Tool 3: Exchange Rate Verification
**Purpose**: Detect unusual currency movements and pricing anomalies

**Example Usage**:
```
Query: EUR to USD conversion for €180,000 transaction
Agent: Evidence Collection Agent
Tool: get_exchange_rate_data
Result: Current rate: 1.0875, Historical variance: Normal
Red Flag: None detected for current transaction
```

**Anomaly Detection**:
- Unusual exchange rate timing
- Off-market rate transactions
- Currency arbitrage schemes
- Cross-border value transfer analysis

### Tool 4: Compliance Requirements Checker
**Purpose**: Automated regulatory requirement determination

**Example Usage**:
```
Transaction: $125,000 to cryptocurrency exchange
Agent: Compliance Check Agent
Tool: check_compliance_requirements
Result: 
- SAR Filing: Recommended (crypto high-risk)
- CTR Filing: Required (>$10,000 cash equivalent)
- Enhanced Due Diligence: Required (VASP transaction)
- Recordkeeping: 5-year BSA requirement
```

### Tool 5: Web Intelligence Gathering
**Purpose**: Current threat intelligence and entity verification

**Example Usage**:
```
Entity: "Global Trading LLC"
Agent: Evidence Collection Agent
Tool: search_web_intelligence
Result: 
- No significant adverse media
- Business registration: Delaware (2023)
- Industry: Import/Export (general)
- Risk Indicators: New entity, minimal web presence
```

**Intelligence Sources**:
- Adverse media screening
- Business registration verification
- Sanctions list checking
- Corporate structure analysis

## 🎯 Agent Coordination Examples

### Multi-Agent Investigation Flow
**Scenario**: $85,000 payment to British Virgin Islands shell company

1. **Regulatory Research Agent**:
   - Searches BVI regulatory status
   - Identifies offshore jurisdiction risks
   - Locates relevant FinCEN advisories

2. **Evidence Collection Agent**:
   - Calculates transaction risk score
   - Gathers exchange rate data
   - Performs entity intelligence gathering

3. **Compliance Check Agent**:
   - Determines SAR filing requirements
   - Checks CTR thresholds
   - Reviews EDD requirements

4. **Report Generation Agent**:
   - Synthesizes findings from all agents
   - Generates regulatory-compliant documentation
   - Provides investigation recommendations

### Agent Tool Specialization
```
Regulatory Research Agent:
├── search_regulatory_documents (Primary)
├── search_fraud_research (Secondary)
└── search_web_intelligence (Supplementary)

Evidence Collection Agent:
├── calculate_transaction_risk (Primary)
├── get_exchange_rate_data (Primary)
└── search_web_intelligence (Primary)

Compliance Check Agent:
├── check_compliance_requirements (Primary)
└── search_regulatory_documents (Secondary)

Report Generation Agent:
├── search_regulatory_documents (Documentation)
└── check_compliance_requirements (Verification)
```

## 🧪 Testing Workflow

### Step 1: System Health Check
1. Navigate to `http://localhost:3000`
2. Verify green status indicators:
   - ✅ API Status: healthy
   - ✅ AI Models: Ready
   - ✅ Vector DB: Ready

### Step 2: Advanced Document Search Tests
1. Click "Tools & Search"
2. **Basic Regulatory Search**: 
   - Query: `"suspicious activity report requirements"`
   - Expected: FinCEN SAR filing instructions and regulatory guidance
   
3. **Specific Compliance Query**:
   - Query: `"currency transaction report threshold BSA"`
   - Expected: FFIEC CTR requirements and $10,000 threshold documentation
   
4. **International Standards Search**:
   - Query: `"FATF recommendations money laundering"`
   - Expected: International regulatory standards and compliance frameworks
   
5. **Sanctions Screening Query**:
   - Query: `"OFAC sanctions screening requirements"`
   - Expected: Treasury department guidance and prohibited parties information

### Step 3: Investigation Tools Testing

#### Exchange Rate Tool
1. In Tools page, test EUR → USD conversion
2. Expected: "Exchange rate API key not available" (graceful handling)
3. Note: Shows proper error handling for missing API keys

#### Advanced Search Techniques Testing
4. **Complex Regulatory Query**:
   - Query: `"customer due diligence enhanced requirements high risk"`
   - Expected: CDD rule documentation and enhanced due diligence procedures
   
5. **Cross-Reference Testing**:
   - Query: `"wire transfer $3000 threshold recordkeeping"`
   - Expected: BSA recordkeeping requirements for wire transfers
   
6. **Industry-Specific Search**:
   - Query: `"money services business MSB registration requirements"`
   - Expected: FinCEN MSB registration and compliance guidance

### Step 4: Main Investigation Demo

#### Quick Test (2-3 minutes):
Use **Scenario 4** (Global Trading LLC to UAE):
1. Fill form with provided data
2. Click "Start Investigation"
3. Watch real-time processing:
   - Health status updates
   - Multiple OpenAI API calls in terminal
   - 4 agents processing sequentially

#### Full Demo (5-10 minutes):
Use **Scenario 1** (Shell Company):
1. Complete investigation workflow
2. Show results display:
   - Investigation ID generation
   - Agent completion status (4/4)
   - Final decision classification
   - Transaction details summary
   - Agent progress tracking

### Step 5: Advanced Features Demo
1. **Navigation**: Switch between Investigation and Tools
2. **Real-time Updates**: Show 30-second health checks
3. **Responsive Design**: Test mobile view
4. **Error Handling**: Show API disconnection handling

## 📊 Expected Demo Outcomes

### Investigation Processing Times
- **Health Check**: < 1 second
- **Document Search**: 2-3 seconds  
- **Exchange Rate**: < 1 second
- **Full Investigation**: 30-90 seconds (depending on complexity)

### Investigation Results Format
```json
{
  "investigation_id": "INV_20250731_XXXXXX_XXXX",
  "status": "completed", 
  "final_decision": "requires_review | suspicious_activity | proceed_with_caution",
  "agents_completed": 4,
  "total_messages": 8-12,
  "all_agents_finished": true
}
```

### Multi-Agent Processing Evidence
Watch terminal for:
- Multiple `POST https://api.openai.com/v1/chat/completions` calls
- Embedding generation for document search
- Vector database queries
- Agent coordination messages

## 🎤 Demo Script

### Opening (30 seconds)
*"InvestigatorAI transforms fraud investigation from a 6-hour manual process into a 90-minute AI-assisted workflow. Let me show you how fraud analysts can investigate suspicious transactions using our multi-agent system."*

### Health Check Demo (30 seconds)
*"First, notice our real-time system monitoring - all components are healthy and ready. The green indicators show our AI models and vector database are operational."*

### Search Capabilities (1 minute)
*"Analysts often need regulatory guidance. Watch as I search for suspicious activity report requirements... The system returns real INTERPOL and regulatory content in seconds rather than hours of manual research."*

### Main Investigation (3-4 minutes)
*"Now the core functionality. I'll investigate a suspicious $85,000 payment to a shell company in the British Virgin Islands..."*

1. **Form Entry**: *"I enter the transaction details - amount, customer, destination..."*
2. **Processing**: *"Notice the system processing - 4 specialized AI agents are analyzing this transaction simultaneously"*
3. **Results**: *"Within 60 seconds, we have a complete investigation with regulatory compliance checks, risk assessment, and documentation ready for review."*

### Conclusion (30 seconds)
*"This demonstrates how InvestigatorAI provides fraud analysts with AI-powered investigation assistance while maintaining human oversight and regulatory compliance."*

## 🔍 Technical Demonstration Points

### Multi-Agent Architecture
- **Evidence Collection Agent**: Analyzes transaction patterns
- **Regulatory Compliance Agent**: Checks AML/BSA requirements  
- **Historical Case Agent**: Searches similar fraud patterns
- **Investigation Report Agent**: Generates compliance documentation

### Real-Time Processing
- Watch OpenAI API calls in terminal
- Vector database queries for regulatory documents
- State management through LangGraph
- Error handling and recovery

### Production-Ready Features
- Health monitoring and status updates
- Responsive design for mobile investigators
- Real-time API status tracking
- Comprehensive error handling

## 📋 Demo Checklist

**Pre-Demo Setup:**
- [ ] API server running (`python -m api.main`)
- [ ] Frontend running (`npm run dev`)
- [ ] Browser open to `http://localhost:3000`
- [ ] Terminal visible for backend logs
- [ ] Demo scenarios ready

**During Demo:**
- [ ] Show system health status
- [ ] Demonstrate search functionality
- [ ] Run complete investigation workflow
- [ ] Highlight real-time processing
- [ ] Show professional UI/UX
- [ ] Explain business value

**Key Messages:**
- [ ] Transforms 6-hour process to 90 minutes
- [ ] Maintains regulatory compliance
- [ ] Uses real government documents
- [ ] Production-ready architecture
- [ ] Human oversight preserved

## 🎯 Success Metrics

A successful demo should show:
- ✅ All system components operational
- ✅ Sub-second response times for basic queries
- ✅ Complete investigation workflow in under 2 minutes
- ✅ Professional, accessible user interface
- ✅ Real regulatory content in search results
- ✅ Multi-agent processing evidence in logs
- ✅ Appropriate error handling and user feedback