# InvestigatorAI Test Suite

Comprehensive test suite for the InvestigatorAI fraud investigation system, covering API functionality, LangSmith monitoring integration, and BM25 retrieval optimization.

## 📋 Test Overview

| Test Type | Files | Coverage |
|-----------|-------|----------|
| **API Functionality** | `test_api.py` | Core API endpoints, search, investigation workflows |
| **LangSmith Integration** | `test_langsmith_*.py` | Monitoring, tracing, performance tracking |
| **Test Automation** | `run_langsmith_tests.py` | Automated test execution and reporting |

## 🚀 Quick Start

### Run All Tests
```bash
# API functionality tests (requires running API)
python test_api.py

# LangSmith integration tests
python run_langsmith_tests.py

# Individual LangSmith tests
python test_langsmith_integration.py
python test_langsmith_api_tracing.py
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
# 1. Start the API server
cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 2. Ensure all services are running
# - Redis (for caching)
# - Qdrant (for vector storage)
# - External API keys configured

# 3. Run the tests
cd ../tests
python test_api.py
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
# Run all LangSmith tests with comprehensive reporting
python run_langsmith_tests.py

# Run individual tests for debugging
python test_langsmith_integration.py
python test_langsmith_api_tracing.py
```

### Expected Output

#### ✅ Success Case
```
🎉 ALL TESTS PASSED!
✅ LangSmith integration is working correctly
✅ API monitoring is ready for production

🚀 Next Steps:
   1. Start the API: cd api && python -m uvicorn main:app --reload
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
cd api
python -m uvicorn main:app --reload

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
python tests/test_langsmith_integration.py
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
      - run: python tests/run_langsmith_tests.py
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