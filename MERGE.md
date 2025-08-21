# 🔬 Enhanced Research Capabilities - Production Deployment Guide

> **📂 Navigation**: [🏠 Home](README.md) | [🔧 API Docs](api/README.md) | [🤖 Agent Architecture](docs/AGENT_PROMPTS.md) | [📈 Advanced Retrievers](docs/ADVANCED_RETRIEVERS.md) | [💼 Business Case](docs/BUSINESS_CASE.md) | [🎓 Certification](docs/CERTIFICATION_CHALLENGE.md) | [🎬 Demo Guide](docs/DEMO_GUIDE.md) | [💻 Frontend](frontend/README.md) | [📊 Data](data/README.md) | [🚀 Deploy](deploy/README.md) | [🧪 Tests](tests/README.md) | [🔄 Merge](MERGE.md)

## 🚀 **Enhanced Research Implementation**

This branch implements sophisticated research capabilities inspired by the Open Deep Research notebook, transforming InvestigatorAI into a comprehensive research platform.

| **Enhancement** | **Before** | **After** | **Improvement** |
|-----------------|------------|-----------|-----------------|
| **Research Sources** | Single (Tavily) | **Multi-source concurrent** | **5x more comprehensive** |
| **Research Quality** | Manual assessment | **Automated quality loops** | **Iterative improvement** |
| **Domain Expertise** | Generic fraud detection | **Financial + Academic specialists** | **Domain-specific insights** |
| **Research State** | Ephemeral | **Persistent with checkpoints** | **Resumable investigations** |
| **Progress Tracking** | None | **Real-time streaming** | **Live progress monitoring** |

---

## 🎯 **What's New**

### **Core Research Enhancements**
- **Multi-Source Concurrent Research**: Simultaneous searches across Tavily, arXiv, PubMed, Exa, and Perplexity
- **Iterative Quality Refinement**: Automated quality assessment with feedback loops
- **Domain-Specific Agents**: Specialized financial and academic research capabilities  
- **Persistent State Management**: Resumable research with checkpoint system
- **Real-Time Streaming**: Server-sent events for live progress tracking

### **New API Endpoints**
- `POST /research/plan` - Generate structured research plans
- `POST /research/investigate` - Enhanced research investigations
- `POST /research/investigate/stream` - Real-time research streaming
- `GET /research/status/{id}` - Research progress tracking
- `GET /research/sessions` - Session management
- `POST /research/multi-source-search` - Direct multi-source access

### **Files Added/Modified**
```
✅ NEW: api/services/multi_source_research.py
✅ NEW: api/services/iterative_research.py  
✅ NEW: api/services/research_state.py
✅ NEW: api/services/specialized_research.py
✅ NEW: api/research_endpoints.py
✅ MODIFIED: api/models/schemas.py (extended with research models)
✅ MODIFIED: api/main.py (integrated research router)
✅ NEW: ENHANCED_RESEARCH_IMPLEMENTATION.md (documentation)
```

---

## 📊 **Deployment Instructions**

### **Option 1: GitHub Pull Request (Recommended)**

1. **Create Pull Request**:
   ```bash
   # Push feature branch to origin
   git push origin feature/enhanced-research-capabilities
   
   # Go to GitHub and create PR:
   # - Base: main
   # - Compare: feature/enhanced-research-capabilities
   # - Title: "feat: implement enhanced research capabilities with multi-source intelligence"
   ```

2. **Review Checklist**:
   - ✅ Multi-source research implementation
   - ✅ Iterative quality assessment system
   - ✅ Domain-specific research agents
   - ✅ Persistent state management
   - ✅ Backward compatibility maintained
   - ✅ Comprehensive API documentation

3. **Merge Strategy**:
   ```bash
   # Use "Squash and merge" for clean history
   # Delete feature branch after merge
   ```

### **Option 2: GitHub CLI (Terminal)**

```bash
# Install GitHub CLI if not available
# brew install gh  # MacOS
# gh auth login     # Authenticate

# Create and merge PR
gh pr create \
  --title "feat: implement enhanced research capabilities with multi-source intelligence" \
  --body "$(cat <<EOF
## 🔬 Enhanced Research Capabilities

### Research Improvements
- **Multi-source intelligence**: Concurrent searches across 5+ APIs
- **Quality assurance**: Automated iterative refinement loops
- **Domain expertise**: Financial crime + academic research specialists
- **State persistence**: Resumable research with checkpointing
- **Real-time tracking**: Live progress streaming

### Key Features
- ✅ Concurrent multi-source research (Tavily, arXiv, PubMed, Exa, Perplexity)
- ✅ Iterative quality assessment with feedback loops
- ✅ Financial entity investigation with AML/compliance focus
- ✅ Academic research with paper analysis and gap identification
- ✅ Persistent research sessions with checkpoint recovery
- ✅ Real-time streaming progress with Server-Sent Events
- ✅ Full backward compatibility with existing fraud investigation

### New API Endpoints
- POST /research/plan - Generate structured research plans
- POST /research/investigate - Enhanced research investigations
- POST /research/investigate/stream - Real-time research streaming
- GET /research/status/{id} - Research progress tracking
- GET /research/sessions - Session management
- POST /research/multi-source-search - Direct multi-source access

### Configuration
- Uses existing environment variables (TAVILY_API_KEY, ANTHROPIC_API_KEY, etc.)
- No database schema changes required
- Creates research_checkpoints/ directory automatically

### Testing
- All existing functionality preserved and tested
- New endpoints provide comprehensive research capabilities
- Full backward compatibility maintained

EOF
)" \
  --base main \
  --head feature/enhanced-research-capabilities

# Review and merge (after team approval)
gh pr merge --squash --delete-branch
```

---

## ⚙️ **Production Configuration**

### **Environment Variables (Existing)**

The enhanced research system uses your existing configuration:

```bash
# ===== Existing API Keys (Required) =====
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here  # Alternative to Anthropic
TAVILY_SEARCH_API_KEY=your_tavily_key_here

# ===== Optional Research Configuration =====
# Maximum research iterations per section (default: 2)
MAX_RESEARCH_ITERATIONS=2

# Queries generated per iteration (default: 2)  
RESEARCH_QUERIES_PER_ITERATION=2

# Token limits for source content (default: 5000)
MAX_TOKENS_PER_SOURCE=5000

# Checkpoint cleanup interval in days (default: 30)
RESEARCH_CHECKPOINT_CLEANUP_DAYS=30
```

### **Deployment Verification Steps**

1. **Test Research Services Initialization**:
   ```bash
   # Check logs for successful research setup
   docker-compose logs api | grep "Enhanced research services initialized"
   ```

2. **Test Basic Research Functionality**:
   ```bash
   # Test research plan generation
   curl -X POST http://localhost:8000/research/plan \
     -H "Content-Type: application/json" \
     -d '{"topic": "Machine Learning in Fraud Detection", "context": "Testing"}'
   ```

3. **Test Multi-Source Search**:
   ```bash
   # Test multi-source search
   curl -X POST http://localhost:8000/research/multi-source-search \
     -H "Content-Type: application/json" \
     -d '{"queries": ["financial crime detection"], "sources": ["tavily"]}'
   ```

4. **Verify Existing Functionality**:
   ```bash
   # Ensure existing fraud investigation still works
   curl -X POST http://localhost:8000/investigate \
     -H "Content-Type: application/json" \
     -d '{
       "amount": 10000,
       "currency": "USD", 
       "description": "Test transaction",
       "customer_name": "Test Customer"
     }'
   ```

---

## 🔧 **Rollback Plan**

If issues arise, rollback safely:

### **Option 1: Disable Research Endpoints (Zero Downtime)**
```bash
# Comment out research router in main.py
# app.include_router(research_router)

# Restart API service
docker-compose restart api
```

### **Option 2: Code Rollback**
```bash
# Revert to previous main branch
git checkout main
git pull origin main

# Redeploy
docker-compose down
docker-compose up -d
```

---

## 📈 **Production Monitoring**

### **Key Metrics to Track**

1. **Research Success Rate** (Target: > 95%)
2. **Research Completion Time** (Target: < 5 minutes)
3. **Multi-Source Search Latency** (Target: < 10 seconds)
4. **Research Session Storage** (Monitor disk usage)
5. **API Rate Limiting** (External service usage)

### **Monitoring Queries**

```bash
# Research session statistics
curl http://localhost:8000/research/sessions | jq '.total_count'

# Check research checkpoint storage
du -sh research_checkpoints/

# Monitor research success rates
docker-compose logs api | grep -E "(Research completed|Research failed)"

# Track multi-source search performance
docker-compose logs api | grep "Multi-source search completed"
```

---

## 🎉 **Success Criteria**

✅ **Deployment Successful When**:
- Research services initialize without errors
- All existing fraud investigation endpoints work unchanged
- New `/research/*` endpoints return 200 status codes
- Multi-source search returns results from configured APIs
- Research sessions can be created, tracked, and resumed
- No memory leaks or excessive resource usage

✅ **Production Benefits**:
- **Comprehensive intelligence**: Multi-source research vs single source
- **Quality assurance**: Automated iterative improvement  
- **Domain expertise**: Specialized financial and academic agents
- **Operational resilience**: Resumable research with checkpointing
- **Real-time insights**: Live progress tracking and streaming
- **Regulatory compliance**: Enhanced AML/BSA investigation capabilities

---

## 🛠️ **Advanced Usage Examples**

### **Financial Entity Investigation**
```bash
curl -X POST http://localhost:8000/research/investigate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "financial",
    "entity_name": "Global Trading LLC",
    "entity_type": "company", 
    "context": "Wire transfer investigation",
    "include_market_analysis": true
  }'
```

### **Academic Research**
```bash
curl -X POST http://localhost:8000/research/investigate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "academic",
    "topic": "Cryptocurrency Money Laundering Detection",
    "field": "computer_science",
    "context": "Literature review for compliance framework"
  }'
```

### **Streaming Research Progress**
```bash
# Use Server-Sent Events for real-time progress
curl -N http://localhost:8000/research/investigate/stream \
  -H "Content-Type: application/json" \
  -d '{
    "type": "general",
    "topic": "FATF Recommendations Implementation"
  }'
```

---

## 📚 **Documentation**

- **Complete Implementation Guide**: [ENHANCED_RESEARCH_IMPLEMENTATION.md](ENHANCED_RESEARCH_IMPLEMENTATION.md)
- **API Documentation**: Available at `/docs` endpoint after deployment
- **Research Endpoint Details**: Full OpenAPI specification in FastAPI docs
- **Usage Examples**: See implementation guide for comprehensive examples

---

## 🆘 **Support Contacts**

**Technical Issues**: Check `ENHANCED_RESEARCH_IMPLEMENTATION.md` for detailed troubleshooting
**Configuration**: Review existing `config.env.template` - no new variables required
**Performance**: Monitor logs for research completion times and success rates
**API Usage**: Use `/docs` endpoint for interactive API documentation

---

*🏆 This enhancement transforms InvestigatorAI into a comprehensive research platform while maintaining full backward compatibility with existing fraud investigation capabilities.*