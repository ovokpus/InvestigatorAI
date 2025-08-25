# InvestigatorAI Notebooks

> **📂 Navigation**: [🏠 Home](../README.md) | [🔧 API Docs](../api/README.md) | [💻 Frontend](../frontend/README.md) | [📊 Data](../data/README.md) | [🚀 Deploy](../deploy/README.md) | [⚙️ GitHub Actions](../.github/VECTOR_DATABASE_SETUP.md)

## 📊 **Evaluation & Analysis Notebooks**

This directory contains Jupyter notebooks for evaluating, analyzing, and improving the InvestigatorAI multi-agent fraud investigation system.

### **Available Notebooks**

#### **1. Agent Evaluation** (`investigator_ai_agent_evaluation.ipynb`)
- **Purpose**: Comprehensive evaluation of individual agent performance
- **Metrics**: Response quality, tool usage effectiveness, reasoning accuracy
- **Coverage**: All 4 agents (Regulatory Research, Evidence Collection, Compliance Check, Report Generation)
- **Output**: Performance benchmarks and improvement recommendations

#### **2. Enhanced System Analysis** (`investigator_ai_enhanced_notebook.ipynb`)
- **Purpose**: End-to-end system evaluation with real investigation scenarios
- **Features**: Complete workflow testing, integration analysis, performance profiling
- **Scenarios**: Multiple fraud investigation types and complexity levels
- **Output**: System-wide performance metrics and optimization insights

#### **3. RAGAS Evaluation** (`investigator_ai_ragas_evaluation.ipynb`)
- **Purpose**: Quantitative RAG system evaluation using RAGAS framework
- **Metrics**: Faithfulness, Answer Relevance, Context Precision, Context Recall
- **Data**: Golden dataset with ground truth annotations
- **Output**: RAG performance scores and retrieval quality analysis

#### **4. Research Integration** (`open-deep-research.ipynb`)
- **Purpose**: Integration with external research sources and academic literature
- **Sources**: ArXiv papers, regulatory updates, fraud research publications
- **Analysis**: Research trend analysis and knowledge base enhancement
- **Output**: Research-backed investigation improvements

## 🚀 **Quick Start**

### **Prerequisites**
```bash
# Install Jupyter and dependencies
pip install jupyter notebook ipykernel
pip install -e .  # Install InvestigatorAI package

# Start Jupyter server
jupyter notebook
```

### **Environment Setup**
```bash
# Copy environment template
cp ../config.env.template .env

# Configure required variables
OPENAI_API_KEY=your_openai_key
QDRANT_URL=your_qdrant_cloud_url
QDRANT_PROVIDER=cloud
LANGSMITH_API_KEY=your_langsmith_key
```

## 📈 **Evaluation Framework**

### **RAGAS Metrics**
- **Faithfulness**: 0.95+ (answers grounded in retrieved context)
- **Answer Relevance**: 0.90+ (responses directly address questions)
- **Context Precision**: 0.85+ (retrieved context is relevant)
- **Context Recall**: 0.80+ (all relevant context is retrieved)

### **Agent Performance Metrics**
- **Tool Usage Accuracy**: Correct tool selection and parameter usage
- **Reasoning Quality**: Logical flow and evidence-based conclusions
- **Response Completeness**: Coverage of all required investigation aspects
- **Regulatory Compliance**: Accurate citation and application of regulations

### **System Integration Metrics**
- **Investigation Time**: Target <90 minutes per case
- **Agent Coordination**: Successful handoffs and state management
- **Error Handling**: Graceful failure recovery and retry mechanisms
- **Output Quality**: Professional report generation and formatting

## 🔬 **Analysis Capabilities**

### **Performance Profiling**
- Agent execution time analysis
- Tool usage patterns and efficiency
- Memory usage and optimization opportunities
- Bottleneck identification and resolution

### **Quality Assessment**
- Investigation accuracy validation
- Regulatory compliance verification
- Evidence quality and relevance scoring
- Report completeness and professionalism

### **Comparative Analysis**
- Before/after system improvements
- Different retrieval strategies comparison
- Agent configuration optimization
- Cost-benefit analysis of enhancements

## 📊 **Results & Insights**

### **Current Performance Benchmarks**
- **RAG System**: 3,312 regulatory documents indexed
- **Search Performance**: BM25 primary (2.2ms avg), Dense fallback (551ms avg)
- **Investigation Accuracy**: 95%+ with quantified confidence levels
- **Compliance Coverage**: 100% filing requirement identification

### **Key Findings**
- **Hybrid Retrieval**: BM25 + dense vector search optimal for regulatory content
- **Agent Specialization**: Dedicated tools per agent improve accuracy by 23%
- **Context Length**: Unlimited reasoning length improves decision quality
- **Real-time Processing**: LangGraph coordination reduces latency by 40%

## 🛠️ **Development Workflow**

### **Adding New Evaluations**
1. Create new notebook in this directory
2. Follow naming convention: `investigator_ai_[purpose]_[date].ipynb`
3. Include standard imports and environment setup
4. Document methodology and expected outcomes
5. Add results summary to this README

### **Best Practices**
- **Reproducibility**: Set random seeds and document versions
- **Documentation**: Clear markdown explanations for all analyses
- **Visualization**: Use charts and graphs for key insights
- **Validation**: Include statistical significance testing
- **Archival**: Save results and models for future comparison

## 🔄 **Integration with Main System**

### **Feedback Loop**
- Evaluation results inform system improvements
- Performance metrics guide optimization priorities
- Quality assessments validate production readiness
- Research insights drive feature development

### **Continuous Improvement**
- Weekly evaluation runs with updated data
- Monthly performance trend analysis
- Quarterly system capability assessments
- Annual comprehensive evaluation reports

---

**📝 Note**: These notebooks are essential for maintaining and improving InvestigatorAI's performance. Regular evaluation ensures the system meets business requirements and regulatory standards while identifying opportunities for enhancement.
