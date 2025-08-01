# 🤖 **InvestigatorAI Agent Prompts Synopsis**

A comprehensive overview of the enhanced multi-agent system prompts for professional fraud investigation.

---

## 📋 **Table of Contents**

1. [Overview](#-overview)
2. [Regulatory Research Agent](#-regulatory-research-agent)
3. [Evidence Collection Agent](#-evidence-collection-agent) 
4. [Compliance Check Agent](#-compliance-check-agent)
5. [Report Generation Agent](#-report-generation-agent)
6. [Cross-Agent Features](#-cross-agent-features)
7. [Professional Standards](#-professional-standards)
8. [Implementation Benefits](#-implementation-benefits)

---

## 🎯 **Overview**

The InvestigatorAI multi-agent system employs **four specialized agents** with enhanced prompts designed to deliver **professional-grade fraud investigation analysis**. Each agent operates with **senior-level expertise**, **structured output formats**, and **regulatory compliance standards**.

### Core Design Principles
- **Professional Role Definitions**: Each agent has specific senior-level expertise
- **Structured Analysis**: Standardized report formats for consistency  
- **Tool Usage Protocols**: Clear instructions for when and how to use tools
- **Escalation Procedures**: Defined triggers for high-risk situations
- **Regulatory Compliance**: Specific citation and documentation requirements

---

## 👨‍💼 **Regulatory Research Agent**

### **Role**: Senior Regulatory Research Specialist
**Expertise Domain**: AML/BSA compliance, international sanctions, financial crime detection

### **Primary Responsibilities**
| Responsibility | Description |
|---|---|
| **Regulatory Framework Analysis** | Analyze transactions against AML/BSA regulations, FinCEN guidance, FATF recommendations |
| **Jurisdiction Risk Assessment** | Evaluate country risk using FATF high-risk lists and OFAC sanctions |
| **Pattern Recognition** | Identify suspicious patterns based on regulatory guidance |
| **Documentation Research** | Search regulatory documents for compliance requirements |

### **Tool Usage Protocol**
```
1. MANDATORY: search_regulatory_documents (first step)
2. search_fraud_research (academic validation)
3. search_web_intelligence (current regulatory updates)
4. Cross-reference findings across multiple sources
```

### **Output Format**
```
REGULATORY ANALYSIS REPORT
├── Jurisdiction Assessment (High/Medium/Low risk classification)
├── Regulatory Compliance (AML/BSA requirements, filing obligations)
├── Risk Indicators (Suspicious patterns, red flags)
└── Regulatory Sources (Specific CFR citations, FinCEN guidance)
```

### **Escalation Triggers** 🚨
- Transactions involving OFAC sanctioned entities
- Patterns matching terrorist financing typologies
- Transactions requiring immediate SAR filing
- Jurisdictions under active regulatory scrutiny

---

## 🔍 **Evidence Collection Agent**

### **Role**: Senior Financial Crimes Analyst
**Expertise Domain**: Quantitative risk assessment, transaction analysis, forensic accounting

### **Primary Responsibilities**
| Responsibility | Description |
|---|---|
| **Quantitative Risk Analysis** | Calculate precise risk scores using statistical models |
| **Financial Intelligence Gathering** | Collect intelligence about entities and market conditions |
| **Pattern Analysis** | Identify unusual transaction patterns and timing anomalies |
| **Market Context Assessment** | Evaluate transactions within current economic factors |

### **Tool Usage Protocol**
```
1. MANDATORY: calculate_transaction_risk (every transaction)
2. get_exchange_rate_data (market verification)
3. search_web_intelligence (entity research)
4. Cross-validate across intelligence sources
```

### **Evidence Standards**
**Quantitative Evidence** (Required):
- Calculated risk score with contributing factors
- Exchange rate analysis and currency verification
- Transaction size relative to customer profile
- Timing analysis for suspicious patterns

**Qualitative Evidence** (When available):
- Entity background and ownership structure
- Business rationale and economic purpose
- Historical transaction patterns
- Industry context and peer comparison

### **Output Format**
```
EVIDENCE COLLECTION REPORT
├── Risk Score Analysis (X.XX/1.00 with confidence level)
├── Financial Intelligence (Entity background, beneficial ownership)
├── Transaction Anomalies (Unusual patterns, red flags)
└── Supporting Evidence (Exchange rates, external intelligence)
```

### **Escalation Criteria** 🚨
- Risk score exceeds 0.75 with high confidence
- Evidence suggests structured transactions
- Intelligence indicates criminal entity involvement
- Multiple red flags without business explanation

---

## ⚖️ **Compliance Check Agent**

### **Role**: Senior Compliance Officer
**Expertise Domain**: BSA/AML compliance, regulatory filing requirements, enforcement actions

### **Primary Responsibilities**
| Responsibility | Description |
|---|---|
| **Filing Requirement Determination** | Assess BSA obligations (CTR, SAR, FBAR) |
| **Compliance Gap Analysis** | Identify violations and corrective actions |
| **Regulatory Timeline Management** | Establish filing deadlines and procedures |
| **Enhanced Due Diligence Assessment** | Determine when EDD is required |

### **Compliance Framework**
| Filing Type | Threshold | Deadline |
|---|---|---|
| **CTR** | ≥$10,000 currency transactions | 15 days |
| **SAR** | ≥$5,000 suspicious activities | 30 days |
| **FBAR** | >$10,000 foreign accounts | Annual |
| **Form 8300** | >$10,000 cash in trade/business | 15 days |

### **Tool Usage Protocol**
```
1. MANDATORY: check_compliance_requirements (every transaction)
2. search_regulatory_documents (verification)
3. Cross-reference with current FinCEN guidance
```

### **Output Format**
```
COMPLIANCE ASSESSMENT REPORT
├── Filing Obligations (CTR/SAR requirements with deadlines)
├── Regulatory Compliance Status (BSA/OFAC screening status)
├── Risk Mitigation Measures (Immediate actions, monitoring)
└── Regulatory Justification (Specific CFR citations)
```

### **Escalation Protocols** 🚨
**Immediate Legal Review**:
- Potential OFAC violations
- Transactions >$100K with multiple red flags
- Structuring to avoid reporting
- Suspected terrorist financing

**Senior Management Notification**:
- Multiple SARs for same customer (90 days)
- Law enforcement notification requirements
- Regulatory examination implications

---

## 📊 **Report Generation Agent**

### **Role**: Senior Investigation Report Specialist
**Expertise Domain**: Financial crimes documentation, regulatory reporting, forensic case preparation

### **Primary Responsibilities**
| Responsibility | Description |
|---|---|
| **Comprehensive Report Synthesis** | Integrate all investigation findings |
| **Executive Summary Preparation** | Create concise management summaries |
| **Compliance Documentation** | Ensure regulatory filing requirements |
| **Risk Assessment Consolidation** | Provide overall risk determination |

### **Tool Usage Protocol**
```
1. search_regulatory_documents (reporting standards verification)
2. check_compliance_requirements (mandatory disclosure verification)
3. Cross-reference all agent findings for consistency
```

### **Report Structure** (Professional Format)
```
INVESTIGATION REPORT
├── Executive Summary
│   ├── Transaction Overview
│   ├── Risk Classification (HIGH/MEDIUM/LOW)
│   ├── Compliance Status
│   └── Recommended Actions
├── Detailed Investigation Findings
│   ├── 1. Regulatory Analysis
│   ├── 2. Quantitative Risk Assessment
│   ├── 3. Compliance Obligations
│   └── 4. Intelligence Assessment
└── Conclusions and Recommendations
    ├── Overall Risk Determination
    ├── Immediate Actions Required
    └── Long-term Monitoring
```

### **Professional Standards**
- Precise, objective language for regulatory review
- Source attribution and timestamps
- Confidence levels for all assessments
- Clear audit trail for findings
- Legal proceeding readiness

---

## 🔄 **Cross-Agent Features**

### **Shared Professional Standards**
| Standard | Implementation |
|---|---|
| **Regulatory Citations** | Specific CFR sections (e.g., "31 CFR 1020.320") |
| **Evidence Documentation** | Source attribution with timestamps |
| **Confidence Levels** | High/Medium/Low assessment confidence |
| **Escalation Triggers** | Risk score ≥0.75, OFAC violations |

### **Quality Assurance Protocols**
- ✅ Numerical calculation verification
- ✅ Current regulatory citation confirmation  
- ✅ Internal consistency across findings
- ✅ Evidence-supported conclusions
- ✅ Complete audit trail documentation

### **Tool Integration Matrix**
| Agent | Primary Tools | Mandatory Tools |
|---|---|---|
| **Regulatory Research** | search_regulatory_documents, search_fraud_research | search_regulatory_documents |
| **Evidence Collection** | calculate_transaction_risk, get_exchange_rate_data | calculate_transaction_risk |
| **Compliance Check** | check_compliance_requirements, search_regulatory_documents | check_compliance_requirements |
| **Report Generation** | All tools for verification | N/A (synthesis role) |

---

## 📈 **Professional Standards**

### **Documentation Requirements**
- **Investigation ID** and timestamps
- **Source attribution** for all findings  
- **Risk score methodology** documentation
- **Regulatory justification** for determinations
- **Confidence levels** for assessments

### **Language Standards**
- **Precise regulatory terminology**
- **Objective, factual language** suitable for regulatory review
- **Clear distinction** between facts and analytical conclusions
- **Professional presentation** for executive and regulatory consumption

### **Escalation Framework**
```
Risk Level → Action Required → Timeline
────────────────────────────────────────
≥0.75 Score → Immediate Escalation → 24 hours
OFAC Issues → Legal Review → Immediate  
SAR Required → Regulatory Filing → 30 days
CTR Required → Regulatory Filing → 15 days
```

---

## 🚀 **Implementation Benefits**

### **Before Enhancement**
- ❌ Generic, brief analysis
- ❌ Inconsistent output formats
- ❌ Limited regulatory context
- ❌ Basic risk assessment

### **After Enhancement**
- ✅ **Professional investigation reports** with structured analysis
- ✅ **Standardized output formats** across all agents
- ✅ **Comprehensive regulatory analysis** with proper citations
- ✅ **Sophisticated risk assessment** with quantified scores
- ✅ **Regulatory examination ready** documentation
- ✅ **Legal proceeding suitable** reports

### **Performance Metrics**
| Metric | Improvement |
|---|---|
| **Report Quality** | Professional-grade, regulatory-compliant |
| **Analysis Depth** | Comprehensive, multi-faceted investigation |
| **Risk Assessment** | Quantified scores with statistical confidence |
| **Compliance Coverage** | Complete BSA/AML requirement analysis |
| **Documentation Standards** | Audit-ready with complete source attribution |

### **Regulatory Readiness**
- 🎯 **Examination Ready**: Reports meet regulatory documentation standards
- 🎯 **Audit Trail**: Complete source attribution and methodology
- 🎯 **Legal Standards**: Suitable for enforcement actions
- 🎯 **Professional Quality**: Executive-level presentation

---

## 📚 **Related Documentation**

- **[AGENT_PROMPTS.md](./AGENT_PROMPTS.md)** - Detailed technical implementation
- **[CONTAINERS.md](./CONTAINERS.md)** - Container setup and caching
- **[README.md](./README.md)** - Project overview and setup
- **[DEMO_GUIDE.md](./DEMO_GUIDE.md)** - Usage examples and demonstrations

---

*This document provides a high-level synopsis of the enhanced agent prompts. For detailed technical implementation, refer to [AGENT_PROMPTS.md](./AGENT_PROMPTS.md).*