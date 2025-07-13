#!/usr/bin/env python3
"""
Comprehensive test script to verify automatic cache invalidation via Django signals.
This script tests that cache is automatically invalidated when Property objects
are created, updated, or deleted through Django signals.
"""

import os
import sys
import django
import requests
import time
import json

# Add the project directory to Python path
sys.path.insert(0, '/home/legennd/Software_repos/alx-backend-caching_property_listings')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_listings.settings')
django.setup()

from properties.models import Property
from django.core.cache import cache

def test_signal_integration():
    """Test that signals automatically invalidate cache"""
    
    print("🧪 Testing Signal-Based Cache Invalidation")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Clear existing cache
    cache.clear()
    print("✅ Cache cleared")
    
    # Create initial property via Django ORM (should trigger signal)
    print("\n1. Creating property via Django ORM...")
    property1 = Property.objects.create(
        title="Signal Test Property 1",
        description="Testing automatic cache invalidation",
        price=150000,
        location="Test City"
    )
    print(f"✅ Created property: {property1.title}")
    
    # Make first request to populate cache
    print("\n2. Making first request to populate cache...")
    try:
        response = requests.get(f"{base_url}/properties/low-level/")
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
    print("\n3. Creating second property (should invalidate cache)...")
    property2 = Property.objects.create(
        title="Signal Test Property 2",
        description="This should invalidate the cache",
        price=200000,
        location="Another City"
    )
    print(f"✅ Created property: {property2.title}")
    
    # Make second request (should be cache miss due to signal invalidation)
    print("\n4. Making second request (should be cache miss)...")
    try:
        response = requests.get(f"{base_url}/properties/low-level/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received: {len(data['properties'])} properties")
            print(f"   Cache status: {data['cache_status']}")
            
            if data['cache_status'] == 'Cache miss - data fetched from database':
                print("🎉 SUCCESS: Cache was automatically invalidated by signal!")
            else:
                print("⚠️  WARNING: Expected cache miss, but got cache hit")
        else:
            print(f"❌ Request failed: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return
    
    # Update property (should invalidate cache again)
    print("\n5. Updating property (should invalidate cache)...")
    property1.price = 175000
    property1.save()
    print(f"✅ Updated property price to ${property1.price}")
    
    # Make third request (should be cache miss due to update signal)
    print("\n6. Making third request (should be cache miss after update)...")
    try:
        response = requests.get(f"{base_url}/properties/low-level/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received: {len(data['properties'])} properties")
            print(f"   Cache status: {data['cache_status']}")
            
            if data['cache_status'] == 'Cache miss - data fetched from database':
                print("🎉 SUCCESS: Cache was automatically invalidated by update signal!")
            else:
                print("⚠️  WARNING: Expected cache miss after update, but got cache hit")
        else:
            print(f"❌ Request failed: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return
    
    # Delete property (should invalidate cache)
    print("\n7. Deleting property (should invalidate cache)...")
    property2.delete()
    print("✅ Deleted property2")
    
    # Make fourth request (should be cache miss due to delete signal)
    print("\n8. Making fourth request (should be cache miss after delete)...")
    try:
        response = requests.get(f"{base_url}/properties/low-level/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received: {len(data['properties'])} properties")
            print(f"   Cache status: {data['cache_status']}")
            
            if data['cache_status'] == 'Cache miss - data fetched from database':
                print("🎉 SUCCESS: Cache was automatically invalidated by delete signal!")
            else:
                print("⚠️  WARNING: Expected cache miss after delete, but got cache hit")
        else:
            print(f"❌ Request failed: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return
    
    # Clean up
    print("\n9. Cleaning up...")
    property1.delete()
    print("✅ Cleaned up test data")
    
    print("\n" + "=" * 50)
    print("🎯 Signal Integration Test Complete!")
    print("   All cache invalidations should have been automatic")
    print("   Check the output above for 'Cache miss' confirmations")

if __name__ == "__main__":
    test_signal_integration()
