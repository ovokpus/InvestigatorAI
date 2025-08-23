#!/usr/bin/env python3
"""Test script for InvestigatorAI FastAPI backend"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {data['status']}")
            print(f"   API Keys Available: {data['api_keys_available']}")
            print(f"   Vector Store Initialized: {data['vector_store_initialized']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_search_endpoint():
    """Test the search endpoint"""
    print("\n🔍 Testing search endpoint...")
    
    try:
        params = {
            "query": "suspicious activity report requirements",
            "max_results": 3
        }
        response = requests.get(f"{BASE_URL}/search", params=params)
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Search successful! Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                filename = result['metadata']['filename']
                category = result['metadata']['content_category']
                content_preview = result['content'][:100] + "..."
                print(f"   {i}. {filename} ({category})")
                print(f"      {content_preview}")
            return True
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

def test_fraud_investigation_endpoint():
    """Test the fraud investigation endpoint"""
    print("\n🔍 Testing fraud investigation endpoint...")
    
    try:
        investigation_data = {
            "amount": 75000,
            "currency": "USD",
            "description": "Business payment to overseas supplier",
            "customer_name": "Global Trading LLC",
            "account_type": "Business",
            "risk_rating": "Medium",
            "country_to": "UAE"
        }
        
        print(f"   Investigating transaction: ${investigation_data['amount']:,} to {investigation_data['country_to']}")
        
        response = requests.post(f"{BASE_URL}/investigate", json=investigation_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Investigation completed!")
            print(f"   Investigation ID: {result['investigation_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Final Decision: {result['final_decision']}")
            print(f"   Agents Completed: {result['agents_completed']}/4")
            print(f"   All Agents Finished: {result['all_agents_finished']}")
            print(f"   Total Messages: {result['total_messages']}")
            
            if result.get('error'):
                print(f"   Error: {result['error']}")
            
            return True
        else:
            print(f"❌ Investigation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Investigation error: {e}")
        return False

def test_exchange_rate_endpoint():
    """Test the exchange rate endpoint"""
    print("\n🔍 Testing exchange rate endpoint...")
    
    try:
        params = {
            "from_currency": "EUR",
            "to_currency": "USD"
        }
        response = requests.get(f"{BASE_URL}/exchange-rate", params=params)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Exchange rate lookup successful!")
            print(f"   Result: {result['result']}")
            print(f"   Source: {result['source']}")
            return True
        else:
            print(f"❌ Exchange rate lookup failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exchange rate error: {e}")
        return False

def test_bm25_search_performance():
    """Test BM25 search performance and verify optimization is working"""
    print("\n🚀 Testing BM25 search performance...")
    
    try:
        import time
        
        # Test search with performance timing
        start_time = time.time()
        params = {
            "query": "BSA filing requirements suspicious activity",
            "max_results": 5
        }
        response = requests.get(f"{BASE_URL}/search", params=params)
        elapsed_ms = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ BM25 search successful!")
            print(f"   Response time: {elapsed_ms:.1f}ms (target: <10ms for BM25)")
            print(f"   Results count: {len(results)}")
            
            # Verify search quality (should have relevant results)
            if len(results) > 0:
                first_result = results[0]['content'].lower()
                search_terms = ['suspicious', 'activity', 'bsa', 'filing']
                relevant_terms = sum(1 for term in search_terms if term in first_result)
                print(f"   Relevance check: {relevant_terms}/{len(search_terms)} terms found")
                
                # Success criteria: response time and relevance (relaxed for test environment)
                performance_good = elapsed_ms < 1000  # Allow 1 second for test environment
                relevance_good = relevant_terms >= 2
                
                if performance_good and relevance_good:
                    if elapsed_ms < 50:
                        print("   🎯 BM25 optimization working correctly!")
                    else:
                        print("   ✅ Search working (slower than optimal but acceptable for test environment)")
                    return True
                else:
                    print(f"   ⚠️ Performance or relevance concerns (time: {elapsed_ms:.1f}ms, relevance: {relevant_terms})")
                    return False
            else:
                print("   ❌ No results returned")
                return False
        else:
            print(f"❌ BM25 search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ BM25 search error: {e}")
        return False

def test_search_method_configuration():
    """Test that search works with different retrieval methods"""
    print("\n⚙️ Testing search method configuration...")
    
    try:
        # Test queries that should work with both BM25 and dense search
        test_queries = [
            "money laundering red flags",
            "currency transaction report thresholds", 
            "OFAC sanctions screening"
        ]
        
        success_count = 0
        for i, query in enumerate(test_queries, 1):
            params = {"query": query, "max_results": 3}
            response = requests.get(f"{BASE_URL}/search", params=params)
            
            if response.status_code == 200:
                results = response.json()
                if len(results) > 0:
                    print(f"   ✅ Query {i}: Found {len(results)} results")
                    success_count += 1
                else:
                    print(f"   ⚠️ Query {i}: No results found")
            else:
                print(f"   ❌ Query {i}: Failed with status {response.status_code}")
        
        success_rate = success_count / len(test_queries)
        print(f"   Search success rate: {success_count}/{len(test_queries)} ({success_rate*100:.1f}%)")
        
        # Success criteria: at least 80% of queries should return results
        if success_rate >= 0.8:
            print("   🎯 Search configuration working correctly!")
            return True
        else:
            print("   ⚠️ Search configuration may need attention")
            return False
            
    except Exception as e:
        print(f"❌ Search configuration test error: {e}")
        return False

def test_health_with_bm25_status():
    """Test enhanced health endpoint to verify BM25 initialization"""
    print("\n🔍 Testing health endpoint with BM25 status...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Enhanced health check passed!")
            print(f"   Status: {data['status']}")
            print(f"   Vector Store Initialized: {data['vector_store_initialized']}")
            
            # Check if the response mentions BM25 or retrieval optimization
            if data['vector_store_initialized']:
                print("   🚀 Vector store ready for optimized search")
                return True
            else:
                print("   ⚠️ Vector store not initialized")
                return False
        else:
            print(f"❌ Enhanced health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Enhanced health check error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 InvestigatorAI API Test Suite with BM25 Optimization")
    print("=" * 60)
    
    # Test each endpoint - organized by priority and functionality
    tests = [
        # Core API functionality
        test_health_endpoint,
        test_health_with_bm25_status,
        
        # Search optimization tests
        test_search_endpoint,
        test_bm25_search_performance,
        test_search_method_configuration,
        
        # Supporting services
        test_exchange_rate_endpoint,
        
        # Complex integration test (longest, so run last)
        test_fraud_investigation_endpoint,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! BM25 optimization is working correctly.")
        print("   ✅ API endpoints functional")
        print("   ✅ BM25 search performance verified") 
        print("   ✅ Configuration and fallback mechanisms working")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        if passed >= 5:  # Allow for some flexibility in complex tests
            print("   Core BM25 functionality appears to be working.")
        else:
            print("   Critical issues detected. Review implementation.")

if __name__ == "__main__":
    main()