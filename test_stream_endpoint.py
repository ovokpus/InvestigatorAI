#!/usr/bin/env python3
"""
Test the streaming endpoint to check detailed_reasoning delivery
"""

import requests
import json
import time

def test_streaming_endpoint():
    """Test the /investigate/stream endpoint"""
    print("🧪 Testing /investigate/stream endpoint")
    print("=" * 60)
    
    url = "http://localhost:8000/investigate/stream"
    
    payload = {
        "amount": 85000.0,
        "currency": "USD", 
        "description": "Wire transfer to offshore account",
        "customer_name": "Test Customer LLC",
        "account_type": "Business",
        "risk_rating": "Medium",
        "country_to": "Cayman Islands"
    }
    
    print(f"📋 Request: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        print("🚀 Calling streaming endpoint...")
        response = requests.post(url, json=payload, stream=True, timeout=300)
        
        if response.status_code != 200:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        print("📡 Processing streaming response...")
        
        completion_result = None
        progress_count = 0
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        progress_count += 1
                        
                        print(f"📨 Event {progress_count}: {data.get('type')} - {data.get('step')} - {data.get('progress', 0)}%")
                        
                        if data.get('type') == 'complete':
                            completion_result = data.get('result')
                            print("✅ Completion event received!")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error: {e}")
                        print(f"Line: {line_str}")
        
        if completion_result:
            print("\n" + "=" * 60)
            print("🔍 COMPLETION RESULT ANALYSIS")
            print("=" * 60)
            
            print(f"🆔 Investigation ID: {completion_result.get('investigation_id')}")
            print(f"📊 Status: {completion_result.get('status')}")
            print(f"⚖️  Final Decision: '{completion_result.get('final_decision')}'")
            print(f"🤖 Agents Completed: {completion_result.get('agents_completed')}/5")
            print(f"💬 Total Messages: {completion_result.get('total_messages')}")
            
            # Check detailed reasoning
            detailed_reasoning = completion_result.get('detailed_reasoning', '')
            print(f"\n📝 Detailed Reasoning Present: {bool(detailed_reasoning)}")
            print(f"📝 Detailed Reasoning Length: {len(detailed_reasoning)} characters")
            
            if detailed_reasoning:
                print(f"📝 Preview: {detailed_reasoning[:200]}...")
            else:
                print("❌ No detailed reasoning found")
            
            # Check investigation report
            investigation_report = completion_result.get('investigation_report', '')
            print(f"\n📋 Investigation Report Present: {bool(investigation_report)}")
            print(f"📋 Investigation Report Length: {len(investigation_report)} characters")
            
            if investigation_report:
                print(f"📋 Preview: {investigation_report[:200]}...")
                
            # Check full_results field (needed for frontend)
            full_results = completion_result.get('full_results', {})
            print(f"\n🎯 Full Results Present: {bool(full_results)}")
            print(f"🎯 Full Results Type: {type(full_results)}")
            
            if full_results and isinstance(full_results, dict):
                print(f"🎯 Full Results Keys: {list(full_results.keys())}")
                messages = full_results.get('messages', [])
                print(f"🎯 Full Results Messages Count: {len(messages) if isinstance(messages, list) else 'Not a list'}")
            else:
                print("❌ Frontend will show 'detailed analysis not available' warning!")
                
            # Check frontend condition matching
            final_decision = completion_result.get('final_decision', '').lower()
            print(f"\n🎯 Frontend Condition Check:")
            print(f"   Final decision (lowercase): '{final_decision}'")
            print(f"   Contains 'suspicious': {final_decision.count('suspicious') > 0}")
            print(f"   Contains 'review': {final_decision.count('review') > 0}")
            print(f"   Contains 'not_suspicious': {final_decision.count('not_suspicious') > 0}")
            
            if detailed_reasoning and final_decision.count('suspicious') > 0:
                print("✅ Should display detailed reasoning for suspicious decision")
            elif detailed_reasoning and final_decision.count('review') > 0:
                print("✅ Should display detailed reasoning for review decision")
            elif detailed_reasoning and final_decision.count('not_suspicious') > 0:
                print("✅ Should display detailed reasoning for not suspicious decision")
            else:
                print("❌ Will NOT display detailed reasoning - condition not met")
                
            return True
        else:
            print("❌ No completion result received")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🧪 Streaming Endpoint Test")
    print("Testing /investigate/stream for detailed reasoning")
    print()
    
    success = test_streaming_endpoint()
    
    if success:
        print("\n✅ Test completed")
    else:
        print("\n❌ Test failed")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
