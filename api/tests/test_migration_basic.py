#!/usr/bin/env python3
"""Basic migration functionality test"""

import sys
sys.path.append('.')

def test_migration_functionality():
    """Test that all migration components work"""
    
    try:
        print('🧪 Testing complete migration functionality...')
        
        # Test memory optimizer
        from api.services.memory_optimizer import get_memory_optimizer
        memory_opt = get_memory_optimizer()
        metrics = memory_opt.get_memory_metrics()
        print(f'✅ Memory optimizer: {metrics.process_memory_mb:.1f}MB process memory')
        
        # Test circuit breaker
        from api.services.external_apis import CircuitBreaker
        cb = CircuitBreaker(failure_threshold=2, timeout_seconds=30)
        
        def test_func():
            return 'success'
        
        result = cb.call(test_func)
        print(f'✅ Circuit breaker: {result}, state: {cb.state.value}')
        
        # Test unified service (without actually running investigation)
        from api.services.unified_investigation import UnifiedInvestigationService
        from api.models.schemas import UnifiedInvestigationRequest
        
        # Create mock dependencies for testing
        class MockLLM:
            def __init__(self): 
                self.model_name = 'test'
        
        class MockSettings:
            def __init__(self):
                self.openai_api_key = 'test'
        
        class MockFraudSystem:
            def investigate_fraud(self, details):
                return {'status': 'completed', 'test': True}
        
        class MockEnhancedInvestigator:
            async def investigate_with_domain_expertise(self, request):
                return {'type': 'test', 'result': {'status': 'completed'}}
        
        # Test unified service creation
        unified_service = UnifiedInvestigationService(
            llm=MockLLM(),
            settings=MockSettings(),
            fraud_system=MockFraudSystem(),
            enhanced_investigator=MockEnhancedInvestigator()
        )
        
        types = unified_service.get_supported_investigation_types()
        print(f'✅ Unified service: {len(types)} investigation types supported')
        
        # Test request model
        request = UnifiedInvestigationRequest(
            investigation_type='fraud_transaction',
            amount=25000.0,
            customer_name='Test Customer'
        )
        print(f'✅ Unified request model: {request.investigation_type} with amount ${request.amount:,}')
        
        print('🎉 ALL MIGRATION FUNCTIONALITY TESTS PASSED!')
        return True
        
    except Exception as e:
        print(f'❌ Migration test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_migration_functionality()
    sys.exit(0 if success else 1)
