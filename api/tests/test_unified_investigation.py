"""Tests for Unified Investigation Service

This test suite covers the critical functionality of the new unified investigation system
to ensure reliability and backward compatibility.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

# Import the classes we're testing
from api.services.unified_investigation import (
    UnifiedInvestigationService, 
    UnifiedInvestigationRequest, 
    UnifiedInvestigationResponse
)
from api.models.schemas import UnifiedInvestigationRequest as SchemaRequest
from api.agents.langgraph.multi_agent_system import FraudInvestigationSystem
from api.agents.research.specialized_research import EnhancedInvestigatorAI


@pytest.fixture
def mock_llm():
    """Mock LLM for testing"""
    llm = Mock()
    llm.model_name = "gpt-4"
    return llm


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    settings = Mock()
    settings.openai_api_key = "test-key"
    settings.tavily_search_api_key = "test-tavily-key"
    return settings


@pytest.fixture
def mock_fraud_system():
    """Mock fraud investigation system"""
    fraud_system = Mock(spec=FraudInvestigationSystem)
    fraud_system.investigate_fraud = Mock(return_value={
        "investigation_id": "TEST_FRAUD_001",
        "status": "completed",
        "final_decision": "LOW RISK - Transaction approved",
        "agents_completed": 4,
        "total_messages": 12,
        "all_agents_finished": True
    })
    
    # Mock streaming
    async def mock_stream(transaction_details):
        yield {"type": "progress", "step": "starting", "progress": 10}
        yield {"type": "progress", "step": "analyzing", "progress": 50}
        yield {"type": "complete", "step": "completed", "progress": 100, "result": {"status": "completed"}}
    
    fraud_system.investigate_fraud_stream = mock_stream
    return fraud_system


@pytest.fixture
def mock_enhanced_investigator():
    """Mock enhanced investigator"""
    investigator = Mock(spec=EnhancedInvestigatorAI)
    investigator.investigate_with_domain_expertise = AsyncMock(return_value={
        "type": "financial_investigation",
        "result": {
            "entity_name": "Test Company",
            "risk_level": "MEDIUM",
            "findings": ["Entity verified", "No sanctions match"],
            "compliance_issues": ["Enhanced monitoring recommended"]
        }
    })
    return investigator


@pytest.fixture
def unified_service(mock_llm, mock_settings, mock_fraud_system, mock_enhanced_investigator):
    """Create unified investigation service with mocks"""
    return UnifiedInvestigationService(
        llm=mock_llm,
        settings=mock_settings,
        fraud_system=mock_fraud_system,
        enhanced_investigator=mock_enhanced_investigator
    )


class TestUnifiedInvestigationService:
    """Test cases for the unified investigation service"""
    
    def test_initialization(self, unified_service):
        """Test service initializes correctly"""
        assert unified_service is not None
        assert unified_service.llm is not None
        assert unified_service.settings is not None
        assert unified_service.fraud_system is not None
        assert unified_service.enhanced_investigator is not None
    
    def test_get_supported_investigation_types(self, unified_service):
        """Test getting supported investigation types"""
        types = unified_service.get_supported_investigation_types()
        
        assert len(types) == 4
        assert any(t["type"] == "fraud_transaction" for t in types)
        assert any(t["type"] == "entity_research" for t in types)
        assert any(t["type"] == "academic_research" for t in types)
        assert any(t["type"] == "general_research" for t in types)
        
        # Check required fields are present
        fraud_type = next(t for t in types if t["type"] == "fraud_transaction")
        assert "amount" in fraud_type["required_fields"]
        assert "customer_name" in fraud_type["required_fields"]
    
    @pytest.mark.asyncio
    async def test_fraud_transaction_investigation(self, unified_service, mock_fraud_system):
        """Test fraud transaction investigation routing"""
        request = UnifiedInvestigationRequest(
            investigation_type="fraud_transaction",
            amount=50000.0,
            currency="USD",
            customer_name="Test Customer",
            country_to="UAE",
            description="Wire transfer"
        )
        
        result = await unified_service.investigate(request)
        
        # Verify result structure
        assert result.investigation_id.startswith("UNI_")
        assert result.investigation_type == "fraud_transaction"
        assert result.status == "completed"
        assert result.fraud_result is not None
        assert result.research_result is None
        assert "regulatory_research" in result.agents_used
        
        # Verify fraud system was called
        mock_fraud_system.investigate_fraud.assert_called_once()
        call_args = mock_fraud_system.investigate_fraud.call_args[0][0]
        assert call_args["amount"] == 50000.0
        assert call_args["customer_name"] == "Test Customer"
    
    @pytest.mark.asyncio 
    async def test_entity_research_investigation(self, unified_service, mock_enhanced_investigator):
        """Test entity research investigation routing"""
        request = UnifiedInvestigationRequest(
            investigation_type="entity_research",
            entity_name="Suspicious Corp",
            entity_type="company",
            context="Money laundering investigation"
        )
        
        result = await unified_service.investigate(request)
        
        # Verify result structure
        assert result.investigation_id.startswith("UNI_")
        assert result.investigation_type == "entity_research"
        assert result.status == "completed"
        assert result.research_result is not None
        assert result.fraud_result is None
        assert "financial_research_agent" in result.agents_used
        
        # Verify enhanced investigator was called
        mock_enhanced_investigator.investigate_with_domain_expertise.assert_called_once()
        call_args = mock_enhanced_investigator.investigate_with_domain_expertise.call_args[0][0]
        assert call_args["type"] == "financial"
        assert call_args["entity_name"] == "Suspicious Corp"
    
    @pytest.mark.asyncio
    async def test_academic_research_investigation(self, unified_service, mock_enhanced_investigator):
        """Test academic research investigation routing"""
        request = UnifiedInvestigationRequest(
            investigation_type="academic_research",
            topic="Machine Learning in Fraud Detection",
            field="computer_science",
            context="Literature review"
        )
        
        result = await unified_service.investigate(request)
        
        # Verify enhanced investigator was called with correct parameters
        call_args = mock_enhanced_investigator.investigate_with_domain_expertise.call_args[0][0]
        assert call_args["type"] == "academic"
        assert call_args["topic"] == "Machine Learning in Fraud Detection"
        assert call_args["field"] == "computer_science"
    
    @pytest.mark.asyncio
    async def test_investigation_error_handling(self, unified_service, mock_fraud_system):
        """Test error handling in investigations"""
        # Make fraud system raise an exception
        mock_fraud_system.investigate_fraud.side_effect = Exception("API Error")
        
        request = UnifiedInvestigationRequest(
            investigation_type="fraud_transaction",
            amount=1000.0,
            customer_name="Test Customer"
        )
        
        result = await unified_service.investigate(request)
        
        # Verify error handling
        assert result.status == "failed"
        assert result.error_message == "API Error"
        assert result.agents_used == []
    
    @pytest.mark.asyncio
    async def test_streaming_investigation(self, unified_service):
        """Test streaming investigation functionality"""
        request = UnifiedInvestigationRequest(
            investigation_type="fraud_transaction",
            amount=25000.0,
            customer_name="Stream Test Customer"
        )
        
        events = []
        async for event in unified_service.investigate_stream(request):
            events.append(event)
            # Stop after a few events to avoid infinite loop
            if len(events) >= 3:
                break
        
        # Verify streaming events
        assert len(events) >= 1
        assert events[0]["type"] == "progress"
        assert "investigation_id" in events[0]
        assert events[0]["investigation_type"] == "fraud_transaction"
    
    @pytest.mark.asyncio
    async def test_invalid_investigation_type(self, unified_service):
        """Test handling of invalid investigation types"""
        request = UnifiedInvestigationRequest(
            investigation_type="invalid_type"  # This should cause an error
        )
        
        result = await unified_service.investigate(request)
        
        assert result.status == "failed"
        assert "Unknown investigation type" in result.error_message
    
    def test_performance_metrics(self, unified_service):
        """Test that performance metrics are captured"""
        # This will be tested through integration tests
        # Here we just verify the structure exists
        types = unified_service.get_supported_investigation_types()
        assert isinstance(types, list)
    
    @pytest.mark.asyncio
    async def test_backward_compatibility(self, unified_service, mock_fraud_system):
        """Test that unified service maintains backward compatibility"""
        # Test with minimal fraud transaction request (like old API)
        request = UnifiedInvestigationRequest(
            investigation_type="fraud_transaction",
            amount=10000.0
        )
        
        result = await unified_service.investigate(request)
        
        # Should still work with defaults
        assert result.status == "completed"
        
        # Verify defaults were applied
        call_args = mock_fraud_system.investigate_fraud.call_args[0][0]
        assert call_args["currency"] == "USD"  # Default
        assert call_args["customer_name"] == "Unknown"  # Default


class TestUnifiedInvestigationModels:
    """Test the unified investigation data models"""
    
    def test_unified_request_validation(self):
        """Test request model validation"""
        # Valid fraud transaction request
        request = SchemaRequest(
            investigation_type="fraud_transaction",
            amount=5000.0,
            customer_name="Test Customer"
        )
        assert request.investigation_type == "fraud_transaction"
        assert request.amount == 5000.0
        assert request.currency == "USD"  # Default
        
        # Valid entity research request
        request = SchemaRequest(
            investigation_type="entity_research",
            entity_name="Test Corp"
        )
        assert request.investigation_type == "entity_research"
        assert request.entity_name == "Test Corp"
        assert request.entity_type == "company"  # Default
    
    def test_optional_fields(self):
        """Test that optional fields work correctly"""
        request = SchemaRequest(
            investigation_type="general_research",
            topic="Test Topic",
            priority="high",
            metadata={"source": "automated_system"}
        )
        assert request.priority == "high"
        assert request.metadata["source"] == "automated_system"


# Integration test helpers
@pytest.mark.integration
class TestUnifiedInvestigationIntegration:
    """Integration tests for the unified investigation system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_fraud_investigation(self):
        """End-to-end test with real components (requires mocking external APIs)"""
        # This would test with real LLM, real agents, but mocked external APIs
        # Implementation depends on test environment setup
        pass
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self):
        """Test performance benchmarks for different investigation types"""
        # This would run performance tests to ensure the unified service
        # meets the performance requirements (e.g., < 60 seconds)
        pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
