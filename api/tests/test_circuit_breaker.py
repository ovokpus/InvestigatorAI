"""Tests for Circuit Breaker Implementation

This test suite covers the circuit breaker functionality to ensure
external API failures are handled gracefully with fallback responses.
"""

import pytest
import time
from unittest.mock import Mock, patch
import requests

from api.services.external_apis import ExternalAPIService, CircuitBreaker, CircuitBreakerState


class TestCircuitBreaker:
    """Test cases for the circuit breaker implementation"""
    
    def test_initialization(self):
        """Test circuit breaker initializes correctly"""
        cb = CircuitBreaker(failure_threshold=3, timeout_seconds=60)
        
        assert cb.failure_threshold == 3
        assert cb.timeout_seconds == 60
        assert cb.failure_count == 0
        assert cb.last_failure_time is None
        assert cb.state == CircuitBreakerState.CLOSED
    
    def test_successful_call_closed_state(self):
        """Test successful call in closed state"""
        cb = CircuitBreaker(failure_threshold=3, timeout_seconds=60)
        
        def test_func():
            return "success"
        
        result = cb.call(test_func)
        
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
    
    def test_failed_call_records_failure(self):
        """Test that failed calls record failures"""
        cb = CircuitBreaker(failure_threshold=3, timeout_seconds=60)
        
        def failing_func():
            raise Exception("API Error")
        
        # First failure
        with pytest.raises(Exception, match="API Error"):
            cb.call(failing_func)
        
        assert cb.failure_count == 1
        assert cb.state == CircuitBreakerState.CLOSED  # Still closed
    
    def test_circuit_opens_after_threshold(self):
        """Test circuit opens after failure threshold reached"""
        cb = CircuitBreaker(failure_threshold=2, timeout_seconds=60)
        
        def failing_func():
            raise Exception("API Error")
        
        # First failure
        with pytest.raises(Exception):
            cb.call(failing_func)
        assert cb.state == CircuitBreakerState.CLOSED
        
        # Second failure - should open circuit
        with pytest.raises(Exception):
            cb.call(failing_func)
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 2
    
    def test_circuit_rejects_calls_when_open(self):
        """Test circuit rejects calls when open"""
        cb = CircuitBreaker(failure_threshold=1, timeout_seconds=60)
        
        def failing_func():
            raise Exception("API Error")
        
        # Trigger circuit to open
        with pytest.raises(Exception):
            cb.call(failing_func)
        assert cb.state == CircuitBreakerState.OPEN
        
        # Next call should be rejected immediately
        with pytest.raises(Exception, match="Circuit breaker OPEN"):
            cb.call(failing_func)
    
    def test_circuit_transitions_to_half_open(self):
        """Test circuit transitions to half-open after timeout"""
        cb = CircuitBreaker(failure_threshold=1, timeout_seconds=1)  # 1 second timeout
        
        def failing_func():
            raise Exception("API Error")
        
        # Open the circuit
        with pytest.raises(Exception):
            cb.call(failing_func)
        assert cb.state == CircuitBreakerState.OPEN
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Next call should transition to half-open
        with pytest.raises(Exception, match="API Error"):  # Still fails
            cb.call(failing_func)
        
        # Should have attempted the call (half-open state reached)
        assert cb.last_failure_time is not None
    
    def test_circuit_resets_on_success_in_half_open(self):
        """Test circuit resets to closed on success in half-open state"""
        cb = CircuitBreaker(failure_threshold=1, timeout_seconds=1)
        
        def failing_func():
            raise Exception("API Error")
        
        def success_func():
            return "success"
        
        # Open the circuit
        with pytest.raises(Exception):
            cb.call(failing_func)
        
        # Simulate timeout by manually setting state
        cb.state = CircuitBreakerState.HALF_OPEN
        
        # Successful call should reset circuit
        result = cb.call(success_func)
        
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0


class TestExternalAPIServiceWithCircuitBreaker:
    """Test external API service with circuit breaker integration"""
    
    @pytest.fixture
    def api_service(self):
        """Create API service with mock settings"""
        settings = Mock()
        settings.tavily_search_api_key = "test-key"
        return ExternalAPIService(settings)
    
    def test_circuit_breaker_initialization(self, api_service):
        """Test circuit breakers are initialized"""
        assert api_service.tavily_circuit_breaker is not None
        assert api_service.arxiv_circuit_breaker is not None
        assert api_service.exchange_rate_circuit_breaker is not None
        
        assert isinstance(api_service.tavily_circuit_breaker, CircuitBreaker)
    
    @patch('requests.post')
    def test_tavily_search_with_circuit_breaker_success(self, mock_post, api_service):
        """Test successful Tavily search with circuit breaker"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {'title': 'Test Result', 'url': 'http://test.com', 'content': 'Test content'}
            ]
        }
        mock_post.return_value = mock_response
        
        result = api_service.search_web("test query")
        
        assert "Test Result" in result
        assert api_service.tavily_circuit_breaker.state == CircuitBreakerState.CLOSED
    
    @patch('requests.post')
    def test_tavily_search_with_circuit_breaker_failure(self, mock_post, api_service):
        """Test Tavily search failure handling with circuit breaker"""
        # Mock API failure
        mock_post.side_effect = requests.RequestException("Connection error")
        
        result = api_service.search_web("test query")
        
        # Should return fallback response
        assert "Web intelligence temporarily unavailable" in result
        assert "Fallback guidance" in result
        
        # Circuit breaker should record failure
        assert api_service.tavily_circuit_breaker.failure_count > 0
    
    @patch('requests.post')
    def test_circuit_breaker_fallback_responses(self, mock_post, api_service):
        """Test circuit breaker provides appropriate fallback responses"""
        # Mock API failure
        mock_post.side_effect = requests.RequestException("API Error")
        
        # Test sanctions-related query
        result = api_service.search_web("OFAC sanctions check")
        assert "sanctions screening" in result
        assert "OFAC Specially Designated Nationals" in result
        
        # Test fraud-related query
        result = api_service.search_web("suspicious money laundering")
        assert "fraud investigation" in result
        assert "transaction patterns" in result
        
        # Test general query
        result = api_service.search_web("general business information")
        assert "temporarily unavailable" in result
        assert "alternative intelligence sources" in result
    
    def test_circuit_breaker_prevents_repeated_failures(self, api_service):
        """Test circuit breaker prevents repeated API calls after failures"""
        # Manually open the circuit breaker
        api_service.tavily_circuit_breaker.state = CircuitBreakerState.OPEN
        api_service.tavily_circuit_breaker.failure_count = 3
        api_service.tavily_circuit_breaker.last_failure_time = time.time()
        
        # Call should use fallback immediately without hitting API
        with patch('requests.post') as mock_post:
            result = api_service.search_web("test query")
            
            # API should not have been called
            mock_post.assert_not_called()
            
            # Should get fallback response
            assert "temporarily unavailable" in result


class TestCircuitBreakerIntegration:
    """Integration tests for circuit breaker functionality"""
    
    @pytest.mark.integration
    def test_multiple_api_circuit_breakers(self):
        """Test that different APIs have independent circuit breakers"""
        settings = Mock()
        settings.tavily_search_api_key = "test-key"
        api_service = ExternalAPIService(settings)
        
        # Tavily and arXiv should have separate circuit breakers
        assert api_service.tavily_circuit_breaker is not api_service.arxiv_circuit_breaker
        
        # Failures in one shouldn't affect the other
        api_service.tavily_circuit_breaker.record_failure()
        api_service.tavily_circuit_breaker.record_failure()
        api_service.tavily_circuit_breaker.record_failure()
        
        assert api_service.tavily_circuit_breaker.state == CircuitBreakerState.OPEN
        assert api_service.arxiv_circuit_breaker.state == CircuitBreakerState.CLOSED
    
    @pytest.mark.integration  
    @patch('requests.post')
    def test_circuit_breaker_recovery(self, mock_post):
        """Test circuit breaker recovery after API comes back online"""
        settings = Mock()
        settings.tavily_search_api_key = "test-key"
        api_service = ExternalAPIService(settings)
        
        # Simulate API failures
        mock_post.side_effect = requests.RequestException("Connection error")
        
        # Trigger circuit breaker
        for _ in range(3):
            try:
                api_service._search_web_internal("test query")
            except:
                pass
        
        assert api_service.tavily_circuit_breaker.state == CircuitBreakerState.OPEN
        
        # Simulate API recovery
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': []}
        mock_post.side_effect = None
        mock_post.return_value = mock_response
        
        # Manually transition to half-open for testing
        api_service.tavily_circuit_breaker.state = CircuitBreakerState.HALF_OPEN
        
        # Successful call should reset circuit
        result = api_service._search_web_internal("test query")
        assert api_service.tavily_circuit_breaker.state == CircuitBreakerState.CLOSED
    
    def test_fallback_response_quality(self):
        """Test that fallback responses provide useful guidance"""
        settings = Mock()
        api_service = ExternalAPIService(settings)
        
        # Test sanctions fallback
        result = api_service._web_search_fallback("OFAC sanctions entity")
        assert "Check OFAC Specially Designated Nationals" in result
        assert "official channels" in result
        
        # Test fraud fallback
        result = api_service._web_search_fallback("suspicious activity money laundering")
        assert "Review transaction patterns" in result
        assert "customer due diligence" in result
        
        # Fallback should be actionable
        assert "Recommended actions:" in api_service._web_search_fallback("general query")


@pytest.mark.performance
class TestCircuitBreakerPerformance:
    """Performance tests for circuit breaker functionality"""
    
    def test_circuit_breaker_overhead(self):
        """Test that circuit breaker adds minimal overhead"""
        cb = CircuitBreaker()
        
        def fast_func():
            return "result"
        
        # Time normal function call
        start_time = time.time()
        for _ in range(1000):
            fast_func()
        normal_time = time.time() - start_time
        
        # Time with circuit breaker
        start_time = time.time()
        for _ in range(1000):
            cb.call(fast_func)
        cb_time = time.time() - start_time
        
        # Circuit breaker should add minimal overhead (< 50% increase)
        overhead_ratio = cb_time / normal_time
        assert overhead_ratio < 1.5  # Less than 50% overhead
    
    def test_fallback_response_speed(self):
        """Test that fallback responses are generated quickly"""
        settings = Mock()
        api_service = ExternalAPIService(settings)
        
        start_time = time.time()
        result = api_service._web_search_fallback("test query")
        end_time = time.time()
        
        # Fallback should be very fast (< 100ms)
        assert (end_time - start_time) < 0.1
        assert len(result) > 50  # Should provide substantial guidance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
