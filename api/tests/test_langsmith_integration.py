#!/usr/bin/env python3
"""Test script to verify LangSmith integration in InvestigatorAI"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_langsmith_integration():
    """Test LangSmith configuration and integration"""
    print("🧪 Testing LangSmith Integration in InvestigatorAI API")
    print("=" * 60)
    
    # Test 1: Import LangSmith
    print("\n1. Testing LangSmith Import:")
    try:
        from langsmith import traceable
        print("   ✅ LangSmith import successful")
        langsmith_available = True
    except ImportError as e:
        print(f"   ❌ LangSmith import failed: {e}")
        langsmith_available = False
    
    # Test 2: Load Configuration
    print("\n2. Testing Configuration:")
    try:
        from api.core.config import get_settings
        settings = get_settings()
        print(f"   ✅ Settings loaded successfully")
        print(f"   📊 LangSmith Project: {settings.langsmith_project}")
        print(f"   🔧 LangSmith Tracing: {settings.langsmith_tracing}")
        print(f"   🌐 LangSmith Endpoint: {settings.langsmith_endpoint}")
        print(f"   🔑 LangSmith API Key: {'✅ SET' if settings.langsmith_api_key else '❌ NOT SET'}")
        print(f"   ✨ LangSmith Available: {settings.langsmith_available}")
    except Exception as e:
        print(f"   ❌ Configuration failed: {e}")
        return False
    
    # Test 3: Test Decorated Functions
    print("\n3. Testing Traceable Decorators:")
    
    @traceable(name="test_function", tags=["test", "langsmith"])
    def test_function(message: str) -> str:
        """Test function with LangSmith tracing"""
        return f"Processed: {message}"
    
    try:
        result = test_function("Hello LangSmith!")
        print(f"   ✅ Traceable function executed: {result}")
    except Exception as e:
        print(f"   ❌ Traceable function failed: {e}")
    
    # Test 4: Test API Components
    print("\n4. Testing API Component Imports:")
    components = [
        ("Main API", "api.main"),
        ("Multi-Agent System", "api.agents.langgraph.multi_agent_system"),
        ("Vector Store", "api.services.vector_store"),
    ]
    
    for name, module_path in components:
        try:
            __import__(module_path)
            print(f"   ✅ {name} import successful")
        except Exception as e:
            print(f"   ❌ {name} import failed: {e}")
    
    # Test 5: Environment Variables
    print("\n5. Checking Environment Variables:")
    env_vars = [
        "LANGSMITH_API_KEY",
        "LANGSMITH_PROJECT", 
        "LANGSMITH_TRACING",
        "LANGSMITH_ENDPOINT"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            display_value = "***" if "KEY" in var else value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ⚠️  {var}: Not set")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 LANGSMITH INTEGRATION SUMMARY:")
    print(f"   LangSmith Library: {'✅ Available' if langsmith_available else '❌ Not Available'}")
    print(f"   Configuration: {'✅ Loaded' if 'settings' in locals() else '❌ Failed'}")
    print(f"   API Integration: {'✅ Ready' if langsmith_available and settings.langsmith_available else '⚠️ Needs Configuration'}")
    
    if langsmith_available and settings.langsmith_available:
        print("\n🎉 LangSmith integration is ready for production monitoring!")
        print(f"📊 Traces will be sent to project: {settings.langsmith_project}")
    elif langsmith_available:
        print("\n⚠️  LangSmith is installed but not configured.")
        print("   Set LANGSMITH_API_KEY and LANGSMITH_TRACING=true to enable monitoring.")
    else:
        print("\n❌ LangSmith is not installed. Install with: pip install langsmith")
    
    return True

if __name__ == "__main__":
    test_langsmith_integration()