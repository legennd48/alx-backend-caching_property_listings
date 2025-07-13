"""
Utility functions for properties app with Redis caching implementation.

This module provides low-level caching functionality for Property querysets
using Django's cache framework with Redis backend.
"""
from django.core.cache import cache
from django.core import serializers
from .models import Property
import json
import logging

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

def get_redis_cache_metrics():
    """
    Retrieves and analyzes Redis cache hit/miss metrics for performance monitoring.
    
    This function connects directly to the Redis instance to gather comprehensive
    cache performance statistics that are essential for optimization and monitoring.
    
    Why Redis cache metrics are important:
    1. Performance optimization - identify cache efficiency bottlenecks
    2. Memory usage monitoring - track Redis memory consumption patterns
    3. Hit ratio analysis - measure cache effectiveness (target: >80% hit ratio)
    4. Capacity planning - determine when to scale Redis infrastructure
    5. Troubleshooting - diagnose cache-related performance issues
    6. Cost optimization - optimize cache size based on actual usage patterns
    
    Technical approach:
    1. Connect to Redis using django_redis connection
    2. Execute INFO command to get keyspace statistics
    3. Parse keyspace_hits and keyspace_misses metrics
    4. Calculate hit ratio percentage
    5. Log metrics for monitoring/alerting systems
    6. Return structured data for API consumption
    
    Returns:
        dict: Comprehensive cache metrics including hit ratio, raw stats, and analysis
    """
    
    try:
        # Import django_redis to get direct Redis connection
        # Why django_redis instead of redis-py directly:
        # - Uses same connection pool as Django cache framework
        # - Respects Django cache configuration settings
        # - Maintains connection consistency across application
        # - Handles Redis authentication and connection parameters automatically
        from django_redis import get_redis_connection
        
        # Get the Redis connection from django_redis
        # Uses 'default' cache backend configuration from settings.py
        # This ensures we're monitoring the same Redis instance used for caching
        redis_connection = get_redis_connection("default")
        
        # Execute Redis INFO command to get server statistics
        # INFO command returns comprehensive Redis server information including:
        # - Memory usage statistics
        # - Client connection information  
        # - Keyspace hit/miss statistics
        # - Server configuration details
        # - Replication information (if applicable)
        redis_info = redis_connection.info()
        
        # Extract keyspace hit/miss statistics
        # keyspace_hits: Total number of successful key lookups
        # keyspace_misses: Total number of failed key lookups
        # These are cumulative counters since Redis server startup
        keyspace_hits = redis_info.get('keyspace_hits', 0)
        keyspace_misses = redis_info.get('keyspace_misses', 0)
        
        # Calculate total requests for hit ratio computation
        total_requests = keyspace_hits + keyspace_misses
        
        # Calculate hit ratio percentage
        # Hit ratio is the key performance indicator for cache effectiveness
        # Formula: (hits / total_requests) * 100
        # Good hit ratios: >80% excellent, 60-80% good, <60% needs optimization
        hit_ratio = (keyspace_hits / total_requests) * 100 if total_requests > 0 else 0
        
        # Get additional Redis metrics for comprehensive monitoring
        # used_memory: Current memory usage in bytes
        # used_memory_human: Human-readable memory usage
        # connected_clients: Number of active client connections
        # total_commands_processed: Total commands executed since startup
        used_memory = redis_info.get('used_memory', 0)
        used_memory_human = redis_info.get('used_memory_human', '0B')
        connected_clients = redis_info.get('connected_clients', 0)
        total_commands = redis_info.get('total_commands_processed', 0)
        
        # Determine cache performance classification
        # This helps with quick performance assessment and alerting
        if hit_ratio >= 80:
            performance_status = "Excellent"
            performance_color = "green"
        elif hit_ratio >= 60:
            performance_status = "Good"
            performance_color = "yellow"
        elif hit_ratio >= 40:
            performance_status = "Fair"
            performance_color = "orange"
        else:
            performance_status = "Poor"
            performance_color = "red"
        
        # Create comprehensive metrics dictionary
        # This structure provides both raw data and computed insights
        metrics = {
            # Raw Redis statistics
            'raw_metrics': {
                'keyspace_hits': keyspace_hits,
                'keyspace_misses': keyspace_misses,
                'total_requests': total_requests,
                'used_memory_bytes': used_memory,
                'used_memory_human': used_memory_human,
                'connected_clients': connected_clients,
                'total_commands_processed': total_commands
            },
            
            # Computed performance indicators
            'performance_analysis': {
                'hit_ratio_percentage': round(hit_ratio, 2),
                'miss_ratio_percentage': round(100 - hit_ratio, 2),
                'performance_status': performance_status,
                'performance_color': performance_color,
                'operations_per_second': 'N/A'  # Would need time-series data for accurate calculation
            },
            
            # Cache efficiency insights
            'efficiency_insights': {
                'is_cache_effective': hit_ratio >= 60,
                'needs_optimization': hit_ratio < 60,
                'memory_efficiency': 'Normal' if used_memory < 100 * 1024 * 1024 else 'High',  # 100MB threshold
                'recommendation': (
                    'Cache performing well' if hit_ratio >= 80 else
                    'Consider cache optimization' if hit_ratio >= 60 else
                    'Cache strategy needs review'
                )
            },
            
            # Metadata for monitoring systems
            'metadata': {
                'timestamp': redis_info.get('server_time_usec', 0),
                'redis_version': redis_info.get('redis_version', 'unknown'),
                'cache_backend': 'Redis',
                'monitoring_source': 'django_redis_connection'
            }
        }
        
        # Log metrics for monitoring and alerting systems
        # This enables external monitoring tools to track cache performance
        logger = logging.getLogger(__name__)
        
        logger.info(
            f"Redis Cache Metrics: Hit Ratio: {hit_ratio:.2f}%, "
            f"Hits: {keyspace_hits}, Misses: {keyspace_misses}, "
            f"Memory: {used_memory_human}, Status: {performance_status}"
        )
        
        # Console output for development debugging
        print(f"📊 Redis Cache Metrics:")
        print(f"   Hit Ratio: {hit_ratio:.2f}% ({performance_status})")
        print(f"   Hits: {keyspace_hits:,}, Misses: {keyspace_misses:,}")
        print(f"   Memory Usage: {used_memory_human}")
        print(f"   Connected Clients: {connected_clients}")
        
        return metrics
        
    except ImportError as e:
        # Handle case where django_redis is not installed
        error_msg = "django_redis not available for direct Redis connection"
        logger = logging.getLogger(__name__)
        logger.error(f"Redis metrics error: {error_msg} - {e}")
        
        return {
            'error': error_msg,
            'status': 'unavailable',
            'message': 'Install django_redis for Redis metrics functionality',
            'fallback_recommendation': 'Use Django cache framework stats instead'
        }
        
    except Exception as e:
        # Handle Redis connection errors, authentication issues, etc.
        error_msg = f"Failed to retrieve Redis cache metrics: {str(e)}"
        logger = logging.getLogger(__name__)
        logger.error(f"Redis metrics error: {error_msg}")
        
        return {
            'error': error_msg,
            'status': 'error',
            'message': 'Check Redis connection and configuration',
            'troubleshooting': [
                'Verify Redis server is running',
                'Check Django CACHES configuration',
                'Verify Redis authentication credentials',
                'Ensure network connectivity to Redis instance'
            ]
        }
