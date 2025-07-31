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

def main():
    """Run all API tests"""
    print("🧪 InvestigatorAI API Test Suite")
    print("=" * 50)
    
    # Test each endpoint
    tests = [
        test_health_endpoint,
        test_search_endpoint,
        test_exchange_rate_endpoint,
        test_fraud_investigation_endpoint,  # This one takes longest, so run it last
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FastAPI backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()