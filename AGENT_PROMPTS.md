# 🤖 **Enhanced Agent Prompts Documentation**

This document details the sophisticated multi-agent system prompts designed for professional fraud investigation.

## 🎯 **Agent Prompt Enhancement Overview**

### Key Improvements
- **Professional Role Definition**: Each agent has a specific senior-level role with relevant expertise
- **Structured Output Formats**: Standardized, professional report formats for consistency
- **Tool Usage Protocols**: Clear instructions on when and how to use specific tools
- **Escalation Procedures**: Defined triggers for flagging high-risk situations
- **Regulatory Compliance**: Specific citation requirements and compliance standards

## 👨‍💼 **Agent Roles & Responsibilities**

### 1. Regulatory Research Agent
**Role**: Senior Regulatory Research Specialist
**Expertise**: AML/BSA compliance, international sanctions, financial crime detection

**Key Features**:
- **Structured Analysis**: Jurisdiction assessment, regulatory compliance, risk indicators
- **Professional Standards**: Precise regulatory terminology, specific citations (e.g., "31 CFR 1020.320")
- **Escalation Triggers**: OFAC violations, terrorist financing, immediate SAR requirements
- **Tool Protocol**: Always search regulatory documents first, cross-reference multiple sources

**Output Format**:
```
REGULATORY ANALYSIS REPORT
├── Jurisdiction Assessment
├── Regulatory Compliance  
├── Risk Indicators
└── Regulatory Sources (with citations)
```

### 2. Evidence Collection Agent
**Role**: Senior Financial Crimes Analyst
**Expertise**: Quantitative risk assessment, transaction analysis, forensic accounting

**Key Features**:
- **Quantitative Focus**: Mandatory risk score calculation for every transaction
- **Evidence Standards**: Distinction between quantitative and qualitative evidence
- **Statistical Context**: Confidence levels and peer comparisons
- **Professional Standards**: Source documentation, data quality assessment

**Output Format**:
```
EVIDENCE COLLECTION REPORT
├── Risk Score Analysis (with numerical scores)
├── Financial Intelligence
├── Transaction Anomalies
└── Supporting Evidence (with confidence levels)
```

### 3. Compliance Check Agent
**Role**: Senior Compliance Officer
**Expertise**: BSA/AML compliance, regulatory filing, enforcement actions

**Key Features**:
- **Filing Requirements**: Specific CTR, SAR, FBAR determinations
- **Compliance Framework**: Built-in knowledge of BSA filing thresholds
- **Defensive Compliance**: Conservative approach for ambiguous situations
- **Escalation Protocols**: Immediate legal review and senior management notification triggers

**Output Format**:
```
COMPLIANCE ASSESSMENT REPORT
├── Filing Obligations (with deadlines)
├── Regulatory Compliance Status
├── Risk Mitigation Measures
└── Regulatory Justification (with CFR citations)
```

### 4. Report Generation Agent
**Role**: Senior Investigation Report Specialist
**Expertise**: Financial crimes documentation, regulatory reporting, forensic case preparation

**Key Features**:
- **Comprehensive Synthesis**: Integration of all agent findings
- **Professional Format**: Executive summary plus detailed findings
- **Documentation Standards**: Audit trail, source attribution, confidence levels
- **Legal Standards**: Reports suitable for regulatory review and legal proceedings

**Output Format**:
```
INVESTIGATION REPORT
├── Executive Summary
├── Detailed Investigation Findings
│   ├── 1. Regulatory Analysis
│   ├── 2. Quantitative Risk Assessment
│   ├── 3. Compliance Obligations
│   └── 4. Intelligence Assessment
└── Conclusions and Recommendations
```

## 🔧 **Technical Implementation Features**

### Tool Usage Protocols
Each agent has specific tool usage instructions:

**Regulatory Research Agent**:
- `search_regulatory_documents` (mandatory first step)
- `search_fraud_research` (academic validation)
- `search_web_intelligence` (current updates)

**Evidence Collection Agent**:
- `calculate_transaction_risk` (mandatory for every transaction)
- `get_exchange_rate_data` (market verification)
- `search_web_intelligence` (entity research)

**Compliance Check Agent**:
- `check_compliance_requirements` (mandatory filing assessment)
- `search_regulatory_documents` (verification)

**Report Generation Agent**:
- All tools for verification and completeness checking

### Escalation Triggers

**Immediate Escalation** (Risk Score ≥0.75):
- OFAC violations or sanctions evasion
- Terrorist financing indicators
- Structuring to avoid reporting requirements
- Multiple red flags without business justification

**Senior Management Notification**:
- Multiple SAR filings for same customer (90 days)
- Law enforcement notification requirements
- Regulatory examination implications
- Consent order violations

## 📊 **Professional Standards**

### Language and Terminology
- Precise regulatory terminology
- Specific regulation citations (CFR sections)
- Objective, factual language suitable for regulatory review
- Clear distinction between facts and analytical conclusions

### Documentation Requirements
- Investigation ID and timestamps
- Source attribution for all findings
- Risk score methodology documentation
- Regulatory justification for all determinations
- Confidence levels for assessments

### Quality Assurance
- Numerical calculation verification
- Current regulatory citation confirmation
- Internal consistency across findings
- Evidence-supported conclusions

## 🎯 **Expected Improvements**

### Output Quality
- **Professional Format**: Structured reports matching industry standards
- **Regulatory Compliance**: Proper citations and filing requirements
- **Risk Assessment**: Quantified, justified risk determinations
- **Actionable Recommendations**: Clear next steps with timelines

### Investigation Depth
- **Comprehensive Analysis**: All aspects covered by specialized agents
- **Evidence-Based**: Quantitative analysis with supporting documentation
- **Regulatory Accuracy**: Current compliance requirements and deadlines
- **Professional Presentation**: Reports suitable for executive review

### Risk Management
- **Early Warning System**: Escalation triggers for high-risk situations
- **Defensive Compliance**: Conservative approach to regulatory requirements
- **Documentation Standards**: Audit-ready investigation records
- **Legal Preparedness**: Reports suitable for enforcement proceedings

## 🚀 **Performance Benefits**

### Before Enhancement
- Generic, brief analysis
- Inconsistent output formats
- Limited regulatory context
- Basic risk assessment

### After Enhancement
- Professional, detailed investigation reports
- Standardized, structured output
- Comprehensive regulatory analysis
- Sophisticated risk assessment with quantified scores

### Regulatory Readiness
- **Examination Ready**: Reports meet regulatory documentation standards
- **Audit Trail**: Complete source attribution and methodology documentation
- **Legal Standards**: Suitable for enforcement actions and court proceedings
- **Professional Quality**: Executive-level presentation and analysis

---

## 📝 **Usage Examples**

### High-Risk Transaction Analysis
```
Input: $100,000 to British Virgin Islands
Output: 
- Regulatory Research: FATF high-risk jurisdiction analysis
- Evidence Collection: Risk score 0.85 with 6 contributing factors
- Compliance Check: CTR + SAR required, 15/30 day deadlines
- Report Generation: Executive summary + 4-section detailed report
```

### Standard Transaction Analysis
```
Input: $15,000 to Canada
Output:
- Regulatory Research: Standard jurisdiction compliance verified
- Evidence Collection: Risk score 0.25 with 2 contributing factors  
- Compliance Check: CTR required, standard monitoring
- Report Generation: Professional documentation with recommendations
```

The enhanced agent prompts transform InvestigatorAI from a basic analysis tool into a **professional-grade fraud investigation platform** capable of producing **regulatory-quality documentation** and **actionable intelligence**. 🎉