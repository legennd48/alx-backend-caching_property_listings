"""
Utility functions for properties app with Redis caching implementation.

This module provides low-level caching functionality for Property querysets
using Django's cache framework with Redis backend.
"""
from django.core.cache import cache
from django.core import serializers
from .models import Property
import json

def get_all_properties():
    """
    Retrieves all properties with Redis caching for 1 hour.
    
    Implementation approach:
    1. Check Redis cache first for existing data
    2. If cache miss, fetch from database
    3. Store result in Redis for future requests
    4. Return the data
    
    Why low-level cache API is necessary:
    - More granular control over cache operations
    - Can cache specific data (queryset) rather than entire HTTP response
    - Allows custom cache keys and expiration times
    - Better for data that's used across multiple views
    - Enables cache invalidation strategies
    """
    
    # Define cache key for all properties
    # cache key must be descriptive and unique to avoid conflicts
    cache_key = 'all_properties'
    
    # Step 1: Try to get data from Redis cache
    # cache.get() returns None if key doesn't exist or has expired
    cached_properties = cache.get(cache_key)
    
    if cached_properties is not None:
        # Cache hit - data found in Redis
        print(f"Cache HIT: Retrieved {len(cached_properties)} properties from Redis")
        return cached_properties
    
    # Cache miss - data not found in Redis, fetch from database
    print("Cache MISS: Fetching properties from database")
    
    # Step 2: Fetch all properties from PostgreSQL database
    # Using .values() for better JSON serialization and performance
    # values() returns dictionaries instead of model instances
    properties_queryset = Property.objects.all().values(
        'id', 'title', 'description', 'price', 'location', 'created_at'
    )
    
    # Convert QuerySet to list for JSON serialization
    # QuerySets are not directly serializable, so convert to list
    properties_list = list(properties_queryset)
    
    # Step 3: Store in Redis cache for 1 hour (3600 seconds)
    # cache.set() stores the data with specified expiration time
    # 3600 seconds = 1 hour as required
    cache.set(cache_key, properties_list, 3600)
    
    print(f"Cache SET: Stored {len(properties_list)} properties in Redis for 1 hour")
    
    # Step 4: Return the properties data
    return properties_list

def invalidate_properties_cache():
    """
    Manually invalidate (clear) the properties cache.
    
    Why cache invalidation is important:
    - Ensures data consistency when properties are added/updated/deleted
    - Prevents serving stale data to users
    - Allows immediate reflection of database changes
    
    Usage: Call this function after create/update/delete operations
    """
    cache_key = 'all_properties'
    
    # Delete the cache entry
    cache.delete(cache_key)
    print("Cache INVALIDATED: Properties cache cleared")

def get_cache_stats():
    """
    Get cache statistics for monitoring purposes.
    
    Why cache monitoring is important:
    - Track cache hit/miss ratios
    - Monitor cache performance
    - Debug caching issues
    - Optimize cache strategies
    """
    cache_key = 'all_properties'
    
    # Check if data exists in cache
    cached_data = cache.get(cache_key)
    
    stats = {
        'cache_key': cache_key,
        'is_cached': cached_data is not None,
        'cached_count': len(cached_data) if cached_data else 0,
        'database_count': Property.objects.count(),
        'cache_backend': 'Redis',
        'cache_timeout': '1 hour (3600 seconds)'
    }
    
    return stats
