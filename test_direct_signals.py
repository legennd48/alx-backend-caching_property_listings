#!/usr/bin/env python3
"""
Direct test of signal integration without HTTP requests
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, '/home/legennd/Software_repos/alx-backend-caching_property_listings')

# Set up Django with test settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_listings.test_settings')
django.setup()

from properties.models import Property
from django.core.cache import cache
from properties.utils import get_all_properties

def test_direct_signal_integration():
    """Test Django signals work directly without HTTP"""
    
    print("🧪 Direct Signal Integration Test")
    print("=" * 40)
    
    # Clear cache
    cache.clear()
    print("✅ Cache cleared")
    
    # Create initial properties if none exist
    if Property.objects.count() == 0:
        Property.objects.create(title="Test 1", description="Test", price=1000, location="Test")
        Property.objects.create(title="Test 2", description="Test", price=2000, location="Test")
        print("✅ Created initial test properties")
    
    # Test 1: Get properties to populate cache
    print("\n1. First call to get_all_properties() - should be cache miss")
    properties1 = get_all_properties()
    print(f"   Retrieved {len(properties1)} properties")
    
    # Test 2: Get properties again - should be cache hit
    print("\n2. Second call to get_all_properties() - should be cache hit")
    properties2 = get_all_properties()
    print(f"   Retrieved {len(properties2)} properties")
    
    # Test 3: Create new property (should trigger signal)
    print("\n3. Creating new property via ORM (should trigger signal)...")
    new_property = Property.objects.create(
        title="Signal Test Direct",
        description="Direct signal test",
        price=99999,
        location="Direct Test City"
    )
    print(f"   Created: {new_property.title}")
    
    # Test 4: Get properties after creation - should be cache miss due to signal
    print("\n4. Call get_all_properties() after creation - should be cache miss")
    properties3 = get_all_properties()
    print(f"   Retrieved {len(properties3)} properties")
    
    # Test 5: Update property (should trigger signal)
    print("\n5. Updating property (should trigger signal)...")
    new_property.price = 88888
    new_property.save()
    print(f"   Updated price to {new_property.price}")
    
    # Test 6: Get properties after update - should be cache miss due to signal
    print("\n6. Call get_all_properties() after update - should be cache miss")
    properties4 = get_all_properties()
    print(f"   Retrieved {len(properties4)} properties")
    
    # Test 7: Delete property (should trigger signal)
    print("\n7. Deleting property (should trigger signal)...")
    new_property.delete()
    print("   Property deleted")
    
    # Test 8: Get properties after deletion - should be cache miss due to signal
    print("\n8. Call get_all_properties() after deletion - should be cache miss")
    properties5 = get_all_properties()
    print(f"   Retrieved {len(properties5)} properties")
    
    print("\n" + "=" * 40)
    print("🎯 Direct Signal Test Complete!")
    print("   Look for 'Cache MISS' vs 'Cache HIT' in the output above")

if __name__ == "__main__":
    test_direct_signal_integration()
