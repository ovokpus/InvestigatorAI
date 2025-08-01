#!/usr/bin/env python3
"""Test script for Redis and Qdrant container integration"""

import sys
import time
import json
import redis
import requests
from qdrant_client import QdrantClient
from datetime import datetime

def test_redis():
    """Test Redis connection and basic operations"""
    print("🔍 Testing Redis connection...")
    
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # Test ping
        pong = r.ping()
        if not pong:
            raise Exception("Redis ping failed")
        
        # Test set/get
        test_key = f"test:{int(time.time())}"
        test_value = {"message": "Hello Redis!", "timestamp": datetime.now().isoformat()}
        
        r.setex(test_key, 60, json.dumps(test_value))
        retrieved = json.loads(r.get(test_key))
        
        if retrieved["message"] != test_value["message"]:
            raise Exception("Redis set/get test failed")
        
        # Test deletion
        r.delete(test_key)
        
        print("✅ Redis: Connection and operations successful")
        
        # Get Redis info
        info = r.info()
        print(f"   📊 Memory used: {info.get('used_memory_human', 'Unknown')}")
        print(f"   🔗 Connected clients: {info.get('connected_clients', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis: {e}")
        return False

def test_qdrant():
    """Test Qdrant connection and basic operations"""
    print("🔍 Testing Qdrant connection...")
    
    try:
        client = QdrantClient(host="localhost", port=6333, timeout=10)
        
        # Test health
        health_response = requests.get("http://localhost:6333/health", timeout=5)
        if health_response.status_code != 200:
            raise Exception(f"Qdrant health check failed: {health_response.status_code}")
        
        # Get collections
        collections = client.get_collections()
        print(f"✅ Qdrant: Connection successful")
        print(f"   📊 Collections: {len(collections.collections)}")
        
        for collection in collections.collections:
            try:
                info = client.get_collection(collection.name)
                print(f"   📋 {collection.name}: {info.points_count} points")
            except:
                print(f"   📋 {collection.name}: Info unavailable")
        
        return True
        
    except Exception as e:
        print(f"❌ Qdrant: {e}")
        return False

def test_api_integration():
    """Test API integration with cache services"""
    print("🔍 Testing API cache integration...")
    
    try:
        # Test cache stats endpoint
        response = requests.get("http://localhost:8000/cache/stats", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ API Cache Integration: Successful")
            
            cache_stats = stats.get("cache", {})
            if cache_stats.get("status") == "connected":
                print(f"   📊 Cache hit rate: {cache_stats.get('hit_rate', 0)}%")
                print(f"   💾 Memory usage: {cache_stats.get('used_memory', 'Unknown')}")
            else:
                print(f"   ⚠️ Cache status: {cache_stats.get('status', 'Unknown')}")
            
            return True
        else:
            print(f"❌ API Cache Integration: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API Cache Integration: {e}")
        return False

def test_investigation_caching():
    """Test investigation caching functionality"""
    print("🔍 Testing investigation caching...")
    
    try:
        # Test investigation endpoint with caching
        investigation_data = {
            "amount": 50000,
            "currency": "USD",
            "description": "Test transaction for caching",
            "customer_name": "Test Customer",
            "account_type": "Business",
            "risk_rating": "Medium",
            "country_to": "Canada"
        }
        
        print("   📤 Running first investigation (should cache results)...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/investigate",
            json=investigation_data,
            timeout=60
        )
        
        first_duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ First investigation completed in {first_duration:.2f}s")
            
            # Run same investigation again (should use cache)
            print("   📤 Running second investigation (should use cache)...")
            start_time = time.time()
            
            response2 = requests.post(
                "http://localhost:8000/investigate",
                json=investigation_data,
                timeout=60
            )
            
            second_duration = time.time() - start_time
            
            if response2.status_code == 200:
                print(f"   ✅ Second investigation completed in {second_duration:.2f}s")
                
                if second_duration < first_duration * 0.8:  # Should be faster due to caching
                    print(f"   🚀 Cache effectiveness: {((first_duration - second_duration) / first_duration * 100):.1f}% faster")
                else:
                    print(f"   ⚠️ Cache may not be working optimally")
                
                return True
            else:
                print(f"   ❌ Second investigation failed: HTTP {response2.status_code}")
                return False
        else:
            print(f"   ❌ First investigation failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Investigation Caching: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 InvestigatorAI Container Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Redis", test_redis),
        ("Qdrant", test_qdrant),
        ("API Cache Integration", test_api_integration),
        ("Investigation Caching", test_investigation_caching)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Container integration is working correctly.")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()