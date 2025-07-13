#!/usr/bin/env python3
"""
Focused test to verify Django signals are working for cache invalidation
"""

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.insert(0, '/home/legennd/Software_repos/alx-backend-caching_property_listings')

# Set up Django with test settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_listings.test_settings')
django.setup()

from properties.models import Property
from django.core.cache import cache

def test_signal_cache_invalidation():
    """Test that Django signals invalidate cache automatically"""
    
    print("🧪 Testing Signal-Based Cache Invalidation")
    print("=" * 55)
    
    base_url = "http://localhost:8003"
    
    # Step 1: Clear cache and check current state
    cache.clear()
    print("✅ Cache cleared manually")
    
    # Step 2: Get current property count
    initial_count = Property.objects.count()
    print(f"📊 Initial property count: {initial_count}")
    
    # Step 3: Make first request to populate cache
    print("\n🔄 Making first request to populate cache...")
    response = requests.get(f"{base_url}/properties/low-level/")
    data = response.json()
    print(f"📥 Response: {len(data['properties'])} properties")
    print(f"💾 Cache status: Hit={data['performance']['cache_hit']}")
    
    # Step 4: Create new property via Django ORM (should trigger signal)
    print(f"\n➕ Creating new property via Django ORM...")
    new_property = Property.objects.create(
        title="Signal Test Property - Auto Invalidation",
        description="This creation should trigger signal to invalidate cache",
        price=999999,
        location="Signal Test City"
    )
    print(f"✅ Created property: {new_property.title} (ID: {new_property.id})")
    
    # Step 5: Make second request (should be cache miss due to signal)
    print(f"\n🔄 Making second request (should be cache miss due to signal)...")
    response = requests.get(f"{base_url}/properties/low-level/")
    data = response.json()
    print(f"📥 Response: {len(data['properties'])} properties")
    print(f"💾 Cache status: Hit={data['performance']['cache_hit']}")
    
    if not data['performance']['cache_hit']:
        print("🎉 SUCCESS: Cache was automatically invalidated by CREATE signal!")
    else:
        print("❌ FAILED: Expected cache miss, but got cache hit")
    
    # Step 6: Make third request to repopulate cache
    print(f"\n🔄 Making third request to repopulate cache...")
    response = requests.get(f"{base_url}/properties/low-level/")
    data = response.json()
    print(f"📥 Response: {len(data['properties'])} properties")
    print(f"💾 Cache status: Hit={data['performance']['cache_hit']}")
    
    # Step 7: Update property (should trigger signal again)
    print(f"\n✏️ Updating property price (should trigger UPDATE signal)...")
    new_property.price = 888888
    new_property.save()
    print(f"✅ Updated property price to ${new_property.price}")
    
    # Step 8: Make fourth request (should be cache miss due to update signal)
    print(f"\n🔄 Making fourth request (should be cache miss due to UPDATE signal)...")
    response = requests.get(f"{base_url}/properties/low-level/")
    data = response.json()
    print(f"📥 Response: {len(data['properties'])} properties")
    print(f"💾 Cache status: Hit={data['performance']['cache_hit']}")
    
    if not data['performance']['cache_hit']:
        print("🎉 SUCCESS: Cache was automatically invalidated by UPDATE signal!")
    else:
        print("❌ FAILED: Expected cache miss after update, but got cache hit")
    
    # Step 9: Delete property (should trigger signal)
    print(f"\n🗑️ Deleting property (should trigger DELETE signal)...")
    property_id = new_property.id
    new_property.delete()
    print(f"✅ Deleted property ID: {property_id}")
    
    # Step 10: Make fifth request (should be cache miss due to delete signal)
    print(f"\n🔄 Making fifth request (should be cache miss due to DELETE signal)...")
    response = requests.get(f"{base_url}/properties/low-level/")
    data = response.json()
    print(f"📥 Response: {len(data['properties'])} properties")
    print(f"💾 Cache status: Hit={data['performance']['cache_hit']}")
    
    if not data['performance']['cache_hit']:
        print("🎉 SUCCESS: Cache was automatically invalidated by DELETE signal!")
    else:
        print("❌ FAILED: Expected cache miss after delete, but got cache hit")
    
    print("\n" + "=" * 55)
    print("🎯 Signal Integration Test Complete!")
    print("   All cache invalidations should have been automatic via Django signals")

if __name__ == "__main__":
    test_signal_cache_invalidation()
