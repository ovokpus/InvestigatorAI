#!/usr/bin/env python3
"""
Quick test script for Qdrant Cloud connection
"""

import os
from pathlib import Path

# Load environment variables from .env file using dotenv
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Test Qdrant Cloud connection
def test_qdrant_cloud():
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url or "your-cluster-id" in qdrant_url:
        print("❌ Please update QDRANT_URL in config.env with your actual Qdrant Cloud URL")
        return False
        
    if not qdrant_api_key or "your_qdrant_cloud_api_key" in qdrant_api_key:
        print("❌ Please update QDRANT_API_KEY in config.env with your actual API key")
        return False
    
    try:
        from qdrant_client import QdrantClient
        
        print(f"🔗 Testing connection to: {qdrant_url}")
        client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=30,
            prefer_grpc=False
        )
        
        # Test connection
        collections = client.get_collections()
        print(f"✅ Connected successfully!")
        print(f"📋 Available collections: {len(collections.collections)}")
        
        for collection in collections.collections:
            print(f"   📦 Collection: {collection.name}")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Qdrant Cloud connection...")
    success = test_qdrant_cloud()
    
    if success:
        print("\n🎉 Qdrant Cloud is ready!")
        print("✅ You can now run: python init_vector_db.py")
    else:
        print("\n❌ Please check your Qdrant Cloud credentials")
