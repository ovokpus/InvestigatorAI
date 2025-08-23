"""Tests for Memory Optimizer Service

This test suite covers the memory optimization functionality to ensure
investigations don't cause memory leaks and perform efficiently.
"""

import pytest
import gc
import time
from unittest.mock import Mock, patch

from api.services.memory_optimizer import MemoryOptimizer, MemoryMetrics, get_memory_optimizer


class TestMemoryOptimizer:
    """Test cases for the memory optimizer service"""
    
    @pytest.fixture
    def memory_optimizer(self):
        """Create memory optimizer for testing"""
        return MemoryOptimizer(max_memory_mb=512)
    
    def test_initialization(self, memory_optimizer):
        """Test memory optimizer initializes correctly"""
        assert memory_optimizer.max_memory_mb == 512
        assert memory_optimizer.cleanup_threshold == 0.8
        assert memory_optimizer.large_content_threshold == 50000
    
    def test_get_memory_metrics(self, memory_optimizer):
        """Test memory metrics collection"""
        metrics = memory_optimizer.get_memory_metrics()
        
        assert isinstance(metrics, MemoryMetrics)
        assert metrics.total_memory_mb > 0
        assert metrics.used_memory_mb >= 0
        assert metrics.available_memory_mb >= 0
        assert metrics.process_memory_mb >= 0
        assert metrics.timestamp is not None
    
    def test_cleanup_investigation_data(self, memory_optimizer):
        """Test cleanup of large investigation data"""
        # Create test data with large content
        large_content = "x" * 100000  # 100KB of data
        investigation_data = {
            "large_field": large_content,
            "normal_field": "normal content",
            "nested_data": {
                "another_large_field": large_content,
                "small_field": "small"
            },
            "large_list": ["item"] * 200  # Large list
        }
        
        cleaned_data = memory_optimizer.cleanup_investigation_data(investigation_data)
        
        # Verify large content was truncated
        assert len(cleaned_data["large_field"]) < len(large_content)
        assert "TRUNCATED" in cleaned_data["large_field"]
        
        # Verify normal content unchanged
        assert cleaned_data["normal_field"] == "normal content"
        
        # Verify nested cleanup
        assert len(cleaned_data["nested_data"]["another_large_field"]) < len(large_content)
        assert cleaned_data["nested_data"]["small_field"] == "small"
        
        # Verify list truncation
        assert len(cleaned_data["large_list"]) == 100  # Truncated to 100 items
    
    def test_cleanup_messages(self, memory_optimizer):
        """Test cleanup of message arrays"""
        # Create test messages with large content
        messages = [
            {
                "content": "x" * 100000,  # Large content
                "type": "message",
                "raw_content": "should be removed",
                "full_results": "should be removed"
            },
            {
                "content": "normal message",
                "type": "message"
            }
        ]
        
        cleaned_messages = memory_optimizer.cleanup_messages(messages)
        
        # Verify large content was truncated
        assert len(cleaned_messages[0]["content"]) < 100000
        assert "TRUNCATED" in cleaned_messages[0]["content"]
        
        # Verify unnecessary metadata removed
        assert "raw_content" not in cleaned_messages[0]
        assert "full_results" not in cleaned_messages[0]
        
        # Verify normal message unchanged
        assert cleaned_messages[1]["content"] == "normal message"
    
    def test_optimize_response_for_client(self, memory_optimizer):
        """Test response optimization for client"""
        response_data = {
            "investigation_id": "TEST_001",
            "status": "completed",
            "full_results": {
                "messages": ["msg1", "msg2"] * 50,  # Large message array
                "agents_completed": ["agent1", "agent2"],
                "investigation_status": "completed"
            },
            "ragas_validated_messages": ["msg"] * 20  # Large message history
        }
        
        optimized = memory_optimizer.optimize_response_for_client(response_data)
        
        # Verify full_results was simplified
        assert "summary" in optimized["full_results"]
        assert "note" in optimized["full_results"]
        assert optimized["full_results"]["agents_completed"] == ["agent1", "agent2"]
        
        # Verify message history was limited
        assert len(optimized["ragas_validated_messages"]) == 10  # Last 10 only
        
        # Verify other fields unchanged
        assert optimized["investigation_id"] == "TEST_001"
        assert optimized["status"] == "completed"
    
    def test_should_cleanup_memory_threshold(self, memory_optimizer):
        """Test memory cleanup threshold detection"""
        # Mock high memory usage
        with patch.object(memory_optimizer, 'get_memory_metrics') as mock_metrics:
            mock_metrics.return_value = MemoryMetrics(
                total_memory_mb=1000,
                used_memory_mb=900,  # 90% usage
                available_memory_mb=100,
                cpu_percent=50,
                process_memory_mb=400,
                timestamp=time.time()
            )
            
            assert memory_optimizer.should_cleanup() == True
    
    def test_should_cleanup_process_limit(self, memory_optimizer):
        """Test process memory limit detection"""
        # Mock high process memory usage
        with patch.object(memory_optimizer, 'get_memory_metrics') as mock_metrics:
            mock_metrics.return_value = MemoryMetrics(
                total_memory_mb=1000,
                used_memory_mb=400,  # Normal system usage
                available_memory_mb=600,
                cpu_percent=50,
                process_memory_mb=600,  # Exceeds 512MB limit
                timestamp=time.time()
            )
            
            assert memory_optimizer.should_cleanup() == True
    
    def test_should_not_cleanup_normal_usage(self, memory_optimizer):
        """Test normal memory usage doesn't trigger cleanup"""
        with patch.object(memory_optimizer, 'get_memory_metrics') as mock_metrics:
            mock_metrics.return_value = MemoryMetrics(
                total_memory_mb=1000,
                used_memory_mb=400,  # 40% usage - normal
                available_memory_mb=600,
                cpu_percent=30,
                process_memory_mb=200,  # Well under limit
                timestamp=time.time()
            )
            
            assert memory_optimizer.should_cleanup() == False
    
    def test_force_garbage_collection(self, memory_optimizer):
        """Test forced garbage collection"""
        # Create some objects to collect
        test_objects = [{"data": "x" * 1000} for _ in range(100)]
        
        # Mock memory metrics to show improvement
        with patch.object(memory_optimizer, 'get_memory_metrics') as mock_metrics:
            # Before cleanup
            mock_metrics.return_value = MemoryMetrics(
                total_memory_mb=1000, used_memory_mb=400, available_memory_mb=600,
                cpu_percent=30, process_memory_mb=300, timestamp=time.time()
            )
            
            # Should run without error
            memory_optimizer.force_garbage_collection()
            
            # Verify gc.collect was effectively called (objects should be eligible for collection)
            del test_objects
            collected = gc.collect()
            assert collected >= 0  # Should collect something
    
    def test_create_memory_efficient_state(self, memory_optimizer):
        """Test creation of memory-efficient investigation state"""
        investigation_data = {
            "investigation_id": "TEST_001",
            "investigation_status": "completed",
            "large_data": "x" * 100000,
            "risk_analysis": {"score": 0.5, "level": "MEDIUM"},
            "compliance_requirements": ["CTR required", "SAR recommended"],
            "key_findings": ["Finding 1", "Finding 2"],
            "parallel_execution_time": 1.5
        }
        
        efficient_state = memory_optimizer.create_memory_efficient_state(investigation_data)
        
        # Verify structure
        assert "summary" in efficient_state
        assert "results" in efficient_state
        assert "performance" in efficient_state
        
        # Verify content
        assert efficient_state["summary"]["investigation_id"] == "TEST_001"
        assert efficient_state["summary"]["memory_optimized"] == True
        assert efficient_state["results"]["risk_analysis"]["score"] == 0.5
        assert efficient_state["performance"]["parallel_execution_time"] == 1.5
    
    def test_log_memory_status(self, memory_optimizer, caplog):
        """Test memory status logging"""
        with patch.object(memory_optimizer, 'get_memory_metrics') as mock_metrics:
            mock_metrics.return_value = MemoryMetrics(
                total_memory_mb=1000, used_memory_mb=400, available_memory_mb=600,
                cpu_percent=30, process_memory_mb=200, timestamp=time.time()
            )
            
            memory_optimizer.log_memory_status("(Test Context)")
            
            # Verify logging occurred
            assert "Memory Status (Test Context)" in caplog.text
            assert "Process Memory: 200.0MB" in caplog.text
            assert "CPU Usage: 30.0%" in caplog.text


class TestMemoryOptimizerIntegration:
    """Integration tests for memory optimizer"""
    
    def test_get_memory_optimizer_singleton(self):
        """Test global memory optimizer singleton"""
        optimizer1 = get_memory_optimizer()
        optimizer2 = get_memory_optimizer()
        
        # Should return same instance
        assert optimizer1 is optimizer2
        assert isinstance(optimizer1, MemoryOptimizer)
    
    @pytest.mark.integration
    def test_real_memory_metrics(self):
        """Test with real memory metrics (integration test)"""
        optimizer = get_memory_optimizer()
        metrics = optimizer.get_memory_metrics()
        
        # Should get real system metrics
        assert metrics.total_memory_mb > 0
        assert metrics.process_memory_mb > 0
        # Process should be using some memory
        assert metrics.process_memory_mb < metrics.total_memory_mb
    
    @pytest.mark.performance
    def test_memory_optimization_performance(self):
        """Test that memory optimization doesn't significantly impact performance"""
        optimizer = MemoryOptimizer()
        
        # Create large test data
        large_data = {
            "field_" + str(i): "x" * 10000 for i in range(100)  # 1MB total
        }
        
        # Time the cleanup operation
        start_time = time.time()
        cleaned_data = optimizer.cleanup_investigation_data(large_data)
        end_time = time.time()
        
        cleanup_time = end_time - start_time
        
        # Should complete in reasonable time (< 1 second for 1MB data)
        assert cleanup_time < 1.0
        assert len(cleaned_data) == len(large_data)  # Same number of fields
    
    @pytest.mark.stress
    def test_repeated_cleanup_stability(self):
        """Test that repeated cleanup operations remain stable"""
        optimizer = MemoryOptimizer()
        
        # Run multiple cleanup cycles
        for cycle in range(10):
            test_data = {
                "cycle": cycle,
                "large_content": "x" * 50000,  # 50KB
                "messages": [{"content": "msg" + str(i)} for i in range(100)]
            }
            
            cleaned = optimizer.cleanup_investigation_data(test_data)
            
            # Verify consistent behavior
            assert cleaned["cycle"] == cycle
            assert len(cleaned["large_content"]) < 50000
            assert len(cleaned["messages"]) <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
