#!/usr/bin/env python3
"""
Comprehensive cache clearing script for InvestigatorAI
"""
import redis
import sys

def clear_all_cache():
    """Clear all Redis cache data"""
    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # Test connection
        r.ping()
        print("✅ Connected to Redis")
        
        # Get all keys
        all_keys = r.keys('*')
        print(f"📊 Found {len(all_keys)} total keys in cache")
        
        if all_keys:
            # Show what's being deleted
            for key in all_keys[:10]:  # Show first 10 keys
                print(f"   🗑️  {key}")
            if len(all_keys) > 10:
                print(f"   ... and {len(all_keys) - 10} more")
            
            # Delete all keys
            deleted = r.delete(*all_keys)
            print(f"🧹 Deleted {deleted} cache keys")
        else:
            print("📭 Cache was already empty")
        
        # Verify cache is empty
        remaining = len(r.keys('*'))
        if remaining == 0:
            print("✅ Cache completely cleared!")
        else:
            print(f"⚠️  {remaining} keys still remain")
            
    except redis.ConnectionError:
        print("❌ Could not connect to Redis")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🧹 CLEARING ALL INVESTIGATORAI CACHE")
    print("=" * 40)
    clear_all_cache()
    print("=" * 40)
    print("🎉 Cache clearing complete!")