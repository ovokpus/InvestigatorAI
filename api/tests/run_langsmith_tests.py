#!/usr/bin/env python3
"""
Test runner for LangSmith integration tests in InvestigatorAI

This script runs all LangSmith-related tests to verify the monitoring
integration is working correctly.
"""

import sys
import subprocess
from pathlib import Path

def run_test(test_file: str, description: str) -> bool:
    """Run a single test file and return success status"""
    print(f"\n🧪 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, 
            str(Path(__file__).parent / test_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(result.stdout)
            print(result.stderr)
            print(f"❌ {description} - FAILED")
            return False
            
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    """Run all LangSmith tests"""
    print("🚀 InvestigatorAI LangSmith Integration Test Suite")
    print("=" * 60)
    print("Running comprehensive tests for LangSmith monitoring integration...")
    
    tests = [
        ("test_langsmith_integration.py", "LangSmith Configuration & Setup Test"),
        ("test_langsmith_api_tracing.py", "LangSmith API Tracing & Decorator Test"),
    ]
    
    results = []
    
    for test_file, description in tests:
        success = run_test(test_file, description)
        results.append((description, success))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {status} - {description}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ LangSmith integration is working correctly")
        print("✅ API monitoring is ready for production")
        print("\n🚀 Next Steps:")
        print("   1. Start the API: cd api && python -m uvicorn main:app --reload")
        print("   2. Test endpoints: curl http://localhost:8000/health")
        print("   3. Check LangSmith dashboard for traces")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("🔧 Please check the error messages above and fix any issues")
        print("\n🛠️  Common Issues:")
        print("   • Missing LANGSMITH_API_KEY environment variable")
        print("   • LANGSMITH_TRACING not set to 'true'")
        print("   • LangSmith package not installed: pip install langsmith")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)