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

## 🧪 Testing Workflow

### Step 1: System Health Check
1. Navigate to `http://localhost:3000`
2. Verify green status indicators:
   - ✅ API Status: healthy
   - ✅ AI Models: Ready
   - ✅ Vector DB: Ready

### Step 2: Document Search Test
1. Click "Tools & Search"
2. Search for: `"suspicious activity report requirements"`
3. Expected: INTERPOL and regulatory document results
4. Verify: Regulatory guidance from real documents

### Step 3: Exchange Rate Test
1. In Tools page, test EUR → USD conversion
2. Expected: "Exchange rate API key not available" (graceful handling)
3. Note: Shows proper error handling for missing API keys

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