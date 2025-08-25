# InvestigatorAI Test Suite

> **📂 Navigation**: [🏠 Home](../../README.md) | [🔧 API Docs](../README.md) | [💻 Frontend](../../frontend/README.md) | [📊 Data](../../data/README.md) | [🚀 Deploy](../../deploy/README.md) | [🧪 Notebooks](../../notebooks/README.md) | [⚙️ GitHub Actions](../../.github/VECTOR_DATABASE_SETUP.md)

Comprehensive test suite for the **modular** InvestigatorAI fraud investigation system, covering API functionality, LangSmith monitoring integration, modular component testing, and enhanced detailed reasoning validation.

## 📋 Test Overview

| Test Type | Files | Coverage | Status |
|-----------|-------|----------|--------|
| **API Functionality** | `test_api.py` | Core API endpoints, search, investigation workflows | ✅ **VERIFIED** |
| **LangSmith Integration** | `test_langsmith_*.py` | Monitoring, tracing, performance tracking | ✅ **ACTIVE** |
| **Circuit Breaker** | `test_circuit_breaker.py` | External API failure handling | ✅ **ACTIVE** |
| **Memory Optimization** | `test_memory_optimizer.py` | Memory management and cleanup | ✅ **ACTIVE** |
| **Unified Investigation** | `test_unified_investigation.py` | Core investigation service | ✅ **ACTIVE** |
| **Test Automation** | `run_langsmith_tests.py` | Automated test execution and reporting | ✅ **ACTIVE** |

## 🎯 Latest API Endpoint Test Results (2025-08-23)

All endpoints tested and verified working:

### ✅ Core Endpoints
- **`GET /health`** - System status and component availability ✅
- **`GET /`** - Root endpoint with API information ✅

### ✅ Cache Management
- **`GET /cache/stats`** - Redis cache statistics ✅
- **`DELETE /cache/clear`** - Clear all cache ✅
- **`DELETE /cache/clear/investigations`** - Clear investigation cache ✅
- **`DELETE /cache/clear/external`** - Clear external API cache ✅

### ✅ Tools & Search
- **`GET /search`** - Vector document search ✅
- **`GET /exchange-rate`** - Currency exchange rates ✅
- **`GET /web-search`** - Web search via Tavily ✅
- **`GET /arxiv-search`** - Academic paper search ✅

### ✅ Investigation Endpoints
- **`POST /investigate`** - Standard fraud investigation ✅
- **`POST /investigate/stream`** - Streaming investigation ✅
- **`POST /investigate/unified`** - Unified investigation service ✅
- **`POST /investigate/unified/stream`** - Streaming unified investigation ✅
- **`GET /investigate/types`** - Available investigation types ✅
- **`GET /investigate/download/{investigation_id}`** - Download investigation report ✅

### ✅ Research Endpoints
- **`POST /research/plan`** - Create research plan ✅
- **`POST /research/investigate`** - Execute research investigation ✅
- **`POST /research/investigate/stream`** - Streaming research ✅
- **`GET /research/status/{research_id}`** - Research status ✅
- **`GET /research/sessions`** - List research sessions ✅
- **`DELETE /research/sessions/{research_id}`** - Delete research session ✅
- **`POST /research/multi-source-search`** - Multi-source search ✅
- **`DELETE /research/cleanup`** - Cleanup research data ✅

## 🗑️ Removed Test Files

The following test files have been removed as they are no longer relevant:

- ~~`test_migration_basic.py`~~ - Migration-specific test, no longer needed after successful migration
- ~~`validate_migration.py`~~ - Migration validation script, no longer needed after successful migration

## 📊 Test File Status Summary

| File | Status | Purpose | Test Type |
|------|--------|---------|-----------|
| `test_api.py` | ✅ **ACTIVE** | Tests all API endpoints and core functionality | Manual Script |
| `test_circuit_breaker.py` | ✅ **ACTIVE** | Tests external API failure handling | Pytest |
| `test_memory_optimizer.py` | ✅ **ACTIVE** | Tests memory management and optimization | Pytest |
| `test_unified_investigation.py` | ✅ **ACTIVE** | Tests unified investigation service | Pytest |
| `test_langsmith_integration.py` | ✅ **ACTIVE** | Tests LangSmith monitoring integration | Manual Script |
| `test_langsmith_api_tracing.py` | ✅ **ACTIVE** | Tests API endpoint tracing | Manual Script |
| `run_langsmith_tests.py` | ✅ **ACTIVE** | Automated test runner for LangSmith tests | Test Runner |

## 🔧 Recent Updates (2025-08-23)

### ✅ Fixed Import Paths
- Updated `test_unified_investigation.py` to use correct import paths:
  - `api.agents.langgraph.multi_agent_system` (was `api.agents.multi_agent_system`)
  - `api.agents.research.specialized_research` (was `api.services.specialized_research`)
- Updated `test_langsmith_api_tracing.py` with correct import paths

### ✅ Updated Test Execution Instructions
- All test commands now include proper `PYTHONPATH` setup
- Added Docker Compose instructions for easier service management
- Updated file paths to reflect current project structure

### ✅ Verified All Imports
- All test file imports have been verified to work correctly
- Test methods align with current API structure
- Endpoint references match current API implementation

## 🚀 Quick Start

### Run All Tests
```bash
# From project root directory
cd /path/to/InvestigatorAI

# API functionality tests (requires running API)
PYTHONPATH=$PWD python api/tests/test_api.py

# LangSmith integration tests
PYTHONPATH=$PWD python api/tests/run_langsmith_tests.py

# Individual LangSmith tests
PYTHONPATH=$PWD python api/tests/test_langsmith_integration.py
PYTHONPATH=$PWD python api/tests/test_langsmith_api_tracing.py

# Circuit breaker tests
PYTHONPATH=$PWD python -m pytest api/tests/test_circuit_breaker.py -v

# Memory optimizer tests
PYTHONPATH=$PWD python -m pytest api/tests/test_memory_optimizer.py -v

# Unified investigation tests
PYTHONPATH=$PWD python -m pytest api/tests/test_unified_investigation.py -v
```

## 🔧 API Functionality Tests (`test_api.py`)

Tests core API functionality and requires a running API server.

### Features Tested
- ✅ **Health Endpoint** - System status and component availability
- ✅ **Document Search** - Vector search with BM25 and dense retrieval
- ✅ **Investigation Workflow** - End-to-end fraud investigation
- ✅ **External APIs** - Exchange rates, web search, ArXiv integration
- ✅ **Performance** - BM25 speed optimization and quality metrics
- ✅ **Configuration** - Search method selection and fallback behavior
- ✅ **Caching** - Redis cache performance and statistics

### Prerequisites
```bash
# 1. Configure environment for Qdrant Cloud
export QDRANT_URL="your_qdrant_cloud_url"
export QDRANT_PROVIDER="cloud"
export OPENAI_API_KEY="your_openai_key"

# 2. Start the API server (from project root)
cd /path/to/InvestigatorAI
docker-compose up -d redis  # Start Redis (Qdrant Cloud is remote)

# OR manually start API
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 3. Ensure services are configured
# - Redis (for caching)
# - Qdrant Cloud (3,312 regulatory documents)
# - External API keys configured

# 4. Run the tests (from project root)
cd /path/to/InvestigatorAI
PYTHONPATH=$PWD python api/tests/test_api.py
```

### Sample Output
```
🔍 Testing health endpoint...
✅ Health check passed!
   Status: healthy
   API Keys Available: True
   Vector Store Initialized: True

🔍 Testing search endpoint...
✅ Search successful! Found 3 results:
   1. FFIEC_BSAAML_Manual_-_Customer_Due_Diligence.pdf (sar_guidance)
      Money laundering is the criminal practice of processing ill-gotten gains...

🔍 Testing BM25 search performance...
✅ BM25 search performance test passed!
   Average latency: 2.1ms (target: <10ms)
   Quality score: 0.95 (target: >0.8)
```

## 📊 LangSmith Integration Tests

Comprehensive monitoring and tracing verification for production deployment.

### Test Files

#### 1. `test_langsmith_integration.py`
**Purpose**: Core integration and configuration testing
- ✅ LangSmith library installation and imports
- ✅ Configuration loading and environment variables
- ✅ API component imports and initialization
- ✅ Basic `@traceable` decorator functionality

#### 2. `test_langsmith_api_tracing.py`
**Purpose**: API-specific tracing and monitoring tests
- ✅ All major API endpoint tracing verification
- ✅ Multi-agent system monitoring coverage
- ✅ Vector store search tracing (BM25, dense, hybrid)
- ✅ Mock investigation workflow testing
- ✅ Decorator coverage analysis across components

#### 3. `run_langsmith_tests.py`
**Purpose**: Automated test runner
- 🚀 Executes all LangSmith tests in sequence
- 📊 Provides comprehensive pass/fail reporting
- 🎯 Returns clear exit codes for CI/CD integration

### Prerequisites

#### Required Environment Variables
```bash
# Add to your config.env file
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=InvestigatorAI-Production
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

#### Required Dependencies
```bash
pip install langsmith==0.4.8
```

### Running LangSmith Tests

```bash
# From project root directory
cd /path/to/InvestigatorAI

# Run all LangSmith tests with comprehensive reporting
PYTHONPATH=$PWD python api/tests/run_langsmith_tests.py

# Run individual tests for debugging
PYTHONPATH=$PWD python api/tests/test_langsmith_integration.py
PYTHONPATH=$PWD python api/tests/test_langsmith_api_tracing.py
```

### Expected Output

#### ✅ Success Case
```
🎉 ALL TESTS PASSED!
✅ LangSmith integration is working correctly
✅ API monitoring is ready for production

🚀 Next Steps:
   1. Start the API: docker-compose up -d (or cd api && python -m uvicorn main:app --reload)
   2. Test endpoints: curl http://localhost:8000/health
   3. Check LangSmith dashboard for traces
```

## 📈 Monitored Components

The test suite verifies monitoring coverage for:

### API Endpoints
- `investigate_fraud_api` - Main investigation endpoint
- `investigate_fraud_stream_api` - Streaming investigation
- `search_documents_api` - Document search endpoint
- `health_check_api` - Health status endpoint

### Multi-Agent System
- `investigate_fraud_multi_agent` - Multi-agent workflow
- `investigate_fraud_stream_multi_agent` - Streaming workflow

### Vector Store
- `vector_store_search` - Main search method with auto-routing
- `bm25_search` - BM25 sparse retrieval (optimized)
- `dense_search` - Dense vector retrieval (fallback)

### Performance Metrics Tracked
- **Latency**: Response times for all endpoints
- **Cost**: Token usage and API costs
- **Quality**: RAGAS metrics and retrieval accuracy
- **Errors**: Exception tracking and debugging info
- **Usage**: Request patterns and user behavior

## 🛠️ Development Workflow

### Adding New Features
1. **Add `@traceable` decorators** to new functions
2. **Update tests** to verify monitoring coverage
3. **Run test suite** to ensure integration works
4. **Check LangSmith dashboard** for traces

### Testing New Components
```python
# Example: Adding monitoring to a new service
from langsmith import traceable

@traceable(name="new_service_method", tags=["service", "feature"])
def new_method(params):
    # Your implementation
    return result

# Add test coverage in test_langsmith_api_tracing.py
def test_new_component():
    from api.services.new_service import NewService
    # Verify @traceable decorator is applied
    # Test functionality works as expected
```

## 🔍 Troubleshooting

### Common Issues

#### 1. API Tests Failing
```bash
# Check if API is running
curl http://localhost:8000/health

# Restart API if needed
docker-compose restart api
# OR manually: cd api && python -m uvicorn main:app --reload

# Check service dependencies
docker ps  # If using Docker for Redis/Qdrant
```

#### 2. LangSmith Tests Failing
```bash
# Check environment variables
echo $LANGSMITH_TRACING
echo $LANGSMITH_API_KEY

# Verify configuration
python -c "from api.core.config import get_settings; print(get_settings().langsmith_available)"

# Test LangSmith connection
python -c "from langsmith import Client; Client().list_datasets(limit=1)"
```

#### 3. Import Errors
```bash
# Ensure you're in the project root
cd /path/to/InvestigatorAI
export PYTHONPATH=$PWD:$PYTHONPATH
python api/tests/test_langsmith_integration.py
```

#### 4. Missing Dependencies
```bash
# Install missing packages
pip install langsmith requests
pip install -e .  # Install project in development mode
```

### Performance Issues

#### Slow Search Performance
- **Target**: BM25 < 10ms, Dense < 1000ms
- **Debug**: Check `test_bm25_search_performance()` output
- **Fix**: Verify BM25 is enabled and initialized

#### High API Latency
- **Monitor**: LangSmith dashboard for detailed metrics
- **Debug**: Check individual component tracing
- **Optimize**: Review retrieval method configuration

## 🚦 CI/CD Integration

### Exit Codes
- **0**: All tests passed
- **1**: Some tests failed
- **2**: Configuration/setup errors

### Example GitHub Actions
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: PYTHONPATH=$PWD python api/tests/run_langsmith_tests.py
        env:
          LANGSMITH_API_KEY: ${{ secrets.LANGSMITH_API_KEY }}
          LANGSMITH_TRACING: true
```

## 📚 Additional Resources

- **API Documentation**: `/docs` endpoint when API is running
- **LangSmith Dashboard**: [https://smith.langchain.com/](https://smith.langchain.com/)
- **Project README**: `../README.md`
- **Configuration Guide**: `../config.env.template`

## 🎯 Success Metrics

### API Tests
- All endpoints return 200 status codes
- Search results are relevant and formatted correctly
- BM25 performance meets latency targets
- Investigation workflows complete successfully

### LangSmith Tests
- All `@traceable` decorators are properly applied
- Configuration is loaded and validated
- Monitoring data flows to LangSmith dashboard
- No import or integration errors

### Production Readiness
- Health checks pass consistently
- Performance metrics are within targets
- Error rates are minimal
- Monitoring covers all critical paths