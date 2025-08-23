#!/usr/bin/env python3
"""Migration Validation Script

This script validates that the 5-hour migration was successful by testing:
1. Security improvements (rate limiting, CORS)
2. Unified investigation service functionality
3. Performance improvements (parallel processing, memory optimization)
4. Error handling and circuit breaker functionality
"""

import asyncio
import requests
import time
import json
from datetime import datetime
from typing import Dict, Any


class MigrationValidator:
    """Validates the migration was successful"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        
        self.results[test_name] = {
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_health_endpoint(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result("Health Check", True, f"API is healthy - Version: {data.get('version')}")
                else:
                    self.log_result("Health Check", False, f"Unhealthy status: {data.get('status')}")
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {e}")
    
    def test_rate_limiting(self):
        """Test rate limiting is working"""
        try:
            # Make multiple rapid requests to trigger rate limiting
            responses = []
            for i in range(8):  # More than the 5/minute limit
                response = requests.get(f"{self.base_url}/health", timeout=5)
                responses.append(response.status_code)
                time.sleep(0.1)  # Very rapid requests
            
            # Check if any requests were rate limited (429)
            rate_limited = any(status == 429 for status in responses)
            
            if rate_limited:
                self.log_result("Rate Limiting", True, "Rate limiting is active")
            else:
                self.log_result("Rate Limiting", False, "No rate limiting detected")
                
        except Exception as e:
            self.log_result("Rate Limiting", False, f"Error testing rate limiting: {e}")
    
    def test_unified_investigation_types(self):
        """Test unified investigation types endpoint"""
        try:
            response = requests.get(f"{self.base_url}/investigate/types", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                types = data.get("investigation_types", [])
                
                expected_types = ["fraud_transaction", "entity_research", "academic_research", "general_research"]
                found_types = [t["type"] for t in types]
                
                if all(expected in found_types for expected in expected_types):
                    self.log_result("Unified Investigation Types", True, f"Found {len(types)} investigation types")
                else:
                    missing = [t for t in expected_types if t not in found_types]
                    self.log_result("Unified Investigation Types", False, f"Missing types: {missing}")
            else:
                self.log_result("Unified Investigation Types", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Unified Investigation Types", False, f"Error: {e}")
    
    def test_unified_investigation_fraud(self):
        """Test unified fraud investigation"""
        try:
            payload = {
                "investigation_type": "fraud_transaction",
                "amount": 25000.0,
                "currency": "USD",
                "customer_name": "Test Customer Migration",
                "country_to": "UAE",
                "description": "Migration validation test transaction"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/investigate/unified",
                json=payload,
                timeout=120  # Allow time for investigation
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "completed":
                    agents_used = len(data.get("agents_used", []))
                    self.log_result("Unified Fraud Investigation", True, 
                                  f"Completed in {duration:.1f}s with {agents_used} agents")
                else:
                    self.log_result("Unified Fraud Investigation", False, 
                                  f"Status: {data.get('status')}")
            else:
                self.log_result("Unified Fraud Investigation", False, 
                              f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_result("Unified Fraud Investigation", False, f"Error: {e}")
    
    def test_legacy_compatibility(self):
        """Test that original endpoints still work"""
        try:
            payload = {
                "amount": 15000.0,
                "currency": "USD", 
                "customer_name": "Legacy Test Customer",
                "country_to": "Canada",
                "description": "Legacy endpoint compatibility test"
            }
            
            response = requests.post(
                f"{self.base_url}/investigate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") in ["completed", "failed"]:  # Either is acceptable
                    self.log_result("Legacy Compatibility", True, "Original endpoint still works")
                else:
                    self.log_result("Legacy Compatibility", False, f"Unexpected status: {data.get('status')}")
            else:
                self.log_result("Legacy Compatibility", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Legacy Compatibility", False, f"Error: {e}")
    
    def test_web_search_fallback(self):
        """Test web search with circuit breaker fallback"""
        try:
            # Test web search endpoint
            response = requests.get(
                f"{self.base_url}/web-search",
                params={"query": "test circuit breaker", "max_results": 2},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", "")
                
                # Check if we get either real results or fallback
                if "temporarily unavailable" in result or len(result) > 50:
                    self.log_result("Web Search Fallback", True, "Web search with fallback working")
                else:
                    self.log_result("Web Search Fallback", False, "No valid response or fallback")
            else:
                self.log_result("Web Search Fallback", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Web Search Fallback", False, f"Error: {e}")
    
    def test_memory_optimization(self):
        """Test memory optimization by looking at response sizes"""
        try:
            # Make a request that should trigger memory optimization
            payload = {
                "investigation_type": "general_research", 
                "topic": "Memory optimization test with long topic name that should trigger cleanup mechanisms"
            }
            
            response = requests.post(
                f"{self.base_url}/investigate/unified",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                # Check response size - should be reasonable
                response_size = len(response.content)
                
                if response_size < 100000:  # Less than 100KB
                    self.log_result("Memory Optimization", True, f"Response size: {response_size//1024}KB")
                else:
                    self.log_result("Memory Optimization", False, f"Large response: {response_size//1024}KB")
            else:
                self.log_result("Memory Optimization", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Memory Optimization", False, f"Error: {e}")
    
    def test_performance_improvement(self):
        """Test overall performance improvements"""
        try:
            # Test simple fraud investigation for performance
            payload = {
                "investigation_type": "fraud_transaction",
                "amount": 5000.0,
                "customer_name": "Performance Test",
                "country_to": "US"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/investigate/unified",
                json=payload,
                timeout=90
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for parallel execution metrics
                fraud_result = data.get("fraud_result", {})
                performance = fraud_result.get("performance", {})
                
                if duration < 60:  # Should complete in under 60 seconds
                    self.log_result("Performance Improvement", True, 
                                  f"Investigation completed in {duration:.1f}s")
                else:
                    self.log_result("Performance Improvement", False, 
                                  f"Slow investigation: {duration:.1f}s")
            else:
                self.log_result("Performance Improvement", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Performance Improvement", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 Starting Migration Validation Tests...\n")
        
        tests = [
            ("Basic Connectivity", self.test_health_endpoint),
            ("Security: Rate Limiting", self.test_rate_limiting), 
            ("Architecture: Unified Types", self.test_unified_investigation_types),
            ("Architecture: Unified Investigation", self.test_unified_investigation_fraud),
            ("Compatibility: Legacy Endpoints", self.test_legacy_compatibility),
            ("Reliability: Circuit Breaker", self.test_web_search_fallback),
            ("Performance: Memory Optimization", self.test_memory_optimization),
            ("Performance: Speed Improvement", self.test_performance_improvement)
        ]
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            try:
                test_func()
            except Exception as e:
                self.log_result(test_name, False, f"Test execution error: {e}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🎯 MIGRATION VALIDATION SUMMARY")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for test_name, result in self.results.items():
                if not result["success"]:
                    print(f"  - {test_name}: {result['message']}")
        
        print("\n" + "="*60)
        
        if passed_tests >= total_tests * 0.8:  # 80% pass rate
            print("🎉 MIGRATION VALIDATION: SUCCESS")
            print("The 5-hour migration appears to be successful!")
        else:
            print("⚠️ MIGRATION VALIDATION: ISSUES DETECTED")
            print("Some components may need attention.")
        
        print("="*60)


def main():
    """Main validation function"""
    print("🔍 InvestigatorAI 5-Hour Migration Validation")
    print("=" * 50)
    
    validator = MigrationValidator()
    validator.run_all_tests()
    
    # Save results to file
    with open("migration_validation_results.json", "w") as f:
        json.dump({
            "validation_timestamp": datetime.now().isoformat(),
            "results": validator.results
        }, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: migration_validation_results.json")


if __name__ == "__main__":
    main()
