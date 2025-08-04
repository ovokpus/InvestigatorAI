# LangSmith Integration Tests

This directory contains comprehensive tests for verifying LangSmith monitoring integration in the InvestigatorAI API.

## Test Files

### 1. `test_langsmith_integration.py`
**Purpose**: Basic integration and configuration testing
- ✅ Verifies LangSmith library installation
- ✅ Tests configuration loading and environment variables
- ✅ Validates API component imports
- ✅ Tests basic `@traceable` decorator functionality

### 2. `test_langsmith_api_tracing.py`
**Purpose**: API-specific tracing and monitoring tests
- ✅ Tests all major API endpoint tracing
- ✅ Verifies multi-agent system monitoring
- ✅ Validates vector store search tracing
- ✅ Tests mock investigation workflows
- ✅ Checks decorator coverage across components

### 3. `run_langsmith_tests.py`
**Purpose**: Test runner for executing all LangSmith tests
- 🚀 Runs all tests in sequence
- 📊 Provides comprehensive summary
- 🎯 Returns clear pass/fail status

## Running the Tests

### Quick Start
```bash
# Run all tests
cd tests/
python run_langsmith_tests.py
```

### Individual Tests
```bash
# Test basic integration
python test_langsmith_integration.py

# Test API tracing
python test_langsmith_api_tracing.py
```

## Prerequisites

### Required Environment Variables
```bash
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=InvestigatorAI-Production
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

### Required Dependencies
```bash
pip install langsmith
```

## Expected Output

### ✅ Success Case
```
🎉 ALL TESTS PASSED!
✅ LangSmith integration is working correctly
✅ API monitoring is ready for production
```

### ❌ Failure Cases
- Missing LangSmith API key
- LangSmith package not installed
- Configuration errors
- Import failures

## Monitored Components

The tests verify that these components have LangSmith tracing:

### API Endpoints
- `investigate_fraud_api` - Main investigation endpoint
- `investigate_fraud_stream_api` - Streaming investigation
- `search_documents_api` - Document search endpoint
- `health_check_api` - Health status endpoint

### Multi-Agent System
- `investigate_fraud_multi_agent` - Multi-agent workflow
- `investigate_fraud_stream_multi_agent` - Streaming workflow

### Vector Store
- `vector_store_search` - Main search method
- `bm25_search` - BM25 sparse retrieval
- `dense_search` - Dense vector retrieval

## Production Monitoring

Once tests pass, the following metrics are tracked in LangSmith:

- **Performance**: Latency and response times
- **Cost**: Token usage and API costs
- **Errors**: Exception tracking and debugging
- **Usage**: Request patterns and user behavior
- **Quality**: Investigation accuracy and effectiveness

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the project root
   cd /path/to/InvestigatorAI
   python tests/test_langsmith_integration.py
   ```

2. **Missing Environment Variables**
   ```bash
   # Check your config.env file
   cat config.env
   
   # Or set manually
   export LANGSMITH_TRACING=true
   export LANGSMITH_API_KEY=your_key_here
   ```

3. **LangSmith Package Issues**
   ```bash
   pip install langsmith==0.4.8
   ```

## Integration with Main Tests

These tests can be integrated with your main test suite:

```python
# In your main test runner
from tests.run_langsmith_tests import main as run_langsmith_tests

def test_langsmith_integration():
    """Integration test for LangSmith monitoring"""
    result = run_langsmith_tests()
    assert result == 0, "LangSmith tests failed"
```

## Development

When adding new API endpoints or components:

1. Add `@traceable` decorators
2. Update these tests to verify coverage
3. Run tests to ensure monitoring works
4. Check LangSmith dashboard for traces