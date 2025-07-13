#!/usr/bin/env python3
"""
Simple test to verify signal integration with test settings
"""

import os
import sys
import django
import requests
import time

# Add the project directory to Python path
sys.path.insert(0, '/home/legennd/Software_repos/alx-backend-caching_property_listings')

# Set up Django with test settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_listings.test_settings')
django.setup()

from properties.models import Property
from django.core.cache import cache

def test_signal_integration():
    """Test that signals automatically invalidate cache"""
    
    print("🧪 Testing Signal-Based Cache Invalidation")
    print("=" * 50)
    
    base_url = "http://localhost:8002"
    
    # Clear existing cache
    cache.clear()
    print("✅ Cache cleared")
    
    # Create initial property via Django ORM
    print("\n1. Creating property via Django ORM...")
    property1 = Property.objects.create(
        title="Signal Test Property 1",
        description="Testing automatic cache invalidation",
        price=150000,
        location="Test City"
    )
    print(f"✅ Created property: {property1.title}")
    
    # Wait for server to be ready
    print("\n2. Waiting for server...")
    time.sleep(2)
    
    # Make first request to populate cache
    print("\n3. Making first request to populate cache...")
    try:
        response = requests.get(f"{base_url}/properties/low-level/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received: {len(data['properties'])} properties")
            print(f"   Cache status: {data['cache_status']}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return
    
    # Create another property via ORM (should invalidate cache)
    print("\n4. Creating second property (should invalidate cache)...")
    property2 = Property.objects.create(
        title="Signal Test Property 2", 
        description="This should invalidate the cache",
        price=200000,
        location="Another City"
    )
    print(f"✅ Created property: {property2.title}")
    
    # Make second request (should be cache miss due to signal invalidation)
    print("\n5. Making second request (should be cache miss)...")
    try:
        response = requests.get(f"{base_url}/properties/low-level/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received: {len(data['properties'])} properties")
            print(f"   Cache status: {data['cache_status']}")
            
            if data['cache_status'] == 'Cache miss - data fetched from database':
                print("🎉 SUCCESS: Cache was automatically invalidated by signal!")
            else:
                print("⚠️  Note: Cache status was: " + data['cache_status'])
        else:
            print(f"❌ Request failed: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return
    
    # Clean up
    print("\n6. Cleaning up...")
    Property.objects.all().delete()
    print("✅ Cleaned up test data")
    
    print("\n" + "=" * 50)
    print("🎯 Signal Integration Test Complete!")

if __name__ == "__main__":
    test_signal_integration()
