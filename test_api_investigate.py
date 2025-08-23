#!/usr/bin/env python3
"""
Test script to verify the /investigate endpoint returns detailed reasoning
"""

import requests
import json
import time

def test_investigate_endpoint():
    """Test the /investigate endpoint to check for detailed reasoning"""
    print("🧪 Testing /investigate endpoint for detailed reasoning")
    print("=" * 60)
    
    # API endpoint
    url = "http://localhost:8000/investigate"
    
    # Test payload
    payload = {
        "amount": 85000.0,
        "currency": "USD",
        "description": "Wire transfer to offshore account for business investment",
        "customer_name": "Test Customer LLC",
        "account_type": "Business",
        "risk_rating": "Medium",
        "country_to": "Cayman Islands"
    }
    
    print(f"📋 Test Transaction:")
    print(f"   💰 Amount: ${payload['amount']} {payload['currency']}")
    print(f"   👤 Customer: {payload['customer_name']}")
    print(f"   🌍 Destination: {payload['country_to']}")
    print(f"   ⚠️  Risk: {payload['risk_rating']}")
    print()
    
    try:
        print("🚀 Sending request to /investigate...")
        start_time = time.time()
        
        response = requests.post(url, json=payload, timeout=300)  # 5 minute timeout
        
        duration = time.time() - start_time
        
        print(f"📡 Response received in {duration:.1f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "=" * 60)
            print("📊 INVESTIGATION RESULTS")
            print("=" * 60)
            
            print(f"🆔 Investigation ID: {result.get('investigation_id', 'N/A')}")
            print(f"📊 Status: {result.get('status', 'N/A')}")
            print(f"⚖️  Final Decision: {result.get('final_decision', 'N/A')}")
            print(f"🤖 Agents Completed: {result.get('agents_completed', 0)}/5")
            print(f"💬 Total Messages: {result.get('total_messages', 0)}")
            print(f"🏁 All Agents Finished: {result.get('all_agents_finished', False)}")
            print(f"🚨 Has Error: {result.get('error') is not None}")
            
            if result.get('error'):
                print(f"❌ Error: {result.get('error')}")
                return False
            
            # Check for detailed reasoning
            print("\n" + "=" * 60)
            print("🔍 DETAILED REASONING CHECK")
            print("=" * 60)
            
            detailed_reasoning = result.get('detailed_reasoning', '')
            investigation_report = result.get('investigation_report', '')
            
            print(f"📝 Detailed Reasoning Length: {len(detailed_reasoning)} characters")
            print(f"📋 Investigation Report Length: {len(investigation_report)} characters")
            
            if detailed_reasoning and len(detailed_reasoning) > 10:
                print("✅ Detailed reasoning present!")
                print(f"📝 Preview: {detailed_reasoning[:200]}...")
            else:
                print("❌ Detailed reasoning missing or empty")
                
            if investigation_report and len(investigation_report) > 10:
                print("✅ Investigation report present!")
                print(f"📋 Preview: {investigation_report[:200]}...")
            else:
                print("❌ Investigation report missing or empty")
            
            # Check ragas_validated_messages for clean content
            print("\n" + "=" * 60)
            print("🔍 RAGAS MESSAGES CHECK")
            print("=" * 60)
            
            ragas_messages = result.get('ragas_validated_messages', [])
            print(f"📨 RAGAS Messages Count: {len(ragas_messages)}")
            
            if ragas_messages:
                # Look for detailed_reasoning agent messages
                detailed_reasoning_msgs = [
                    msg for msg in ragas_messages 
                    if isinstance(msg, dict) and msg.get('name') == 'detailed_reasoning'
                ]
                
                print(f"🔍 Detailed Reasoning Messages: {len(detailed_reasoning_msgs)}")
                
                if detailed_reasoning_msgs:
                    for i, msg in enumerate(detailed_reasoning_msgs):
                        content = msg.get('content', '')
                        print(f"   📝 Message {i+1}: {len(content)} chars")
                        
                        # Check if content is clean (no double-serialization)
                        if content.startswith("content='"):
                            print(f"   ❌ Message {i+1}: Still double-serialized!")
                            print(f"      Preview: {content[:100]}...")
                        else:
                            print(f"   ✅ Message {i+1}: Clean content!")
                            print(f"      Preview: {content[:100]}...")
                
                # Check all message types
                agent_types = {}
                for msg in ragas_messages:
                    if isinstance(msg, dict):
                        agent_name = msg.get('name', 'unknown')
                        agent_types[agent_name] = agent_types.get(agent_name, 0) + 1
                
                print(f"🤖 Agent message counts: {agent_types}")
            
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"💥 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the API server running?")
        print("💡 Try: uvicorn api.main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    print("🧪 InvestigatorAI API Endpoint Test")
    print("Testing /investigate endpoint for detailed reasoning presence")
    print()
    
    success = test_investigate_endpoint()
    
    if success:
        print("\n✅ Test completed successfully")
        print("Check the output above to verify detailed reasoning is present")
    else:
        print("\n❌ Test failed")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
