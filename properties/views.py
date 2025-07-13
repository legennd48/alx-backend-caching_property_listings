from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from .models import Property
from .utils import get_all_properties, get_cache_stats

# NOTE: Removed @cache_page decorator since we're now using low-level cache API
# cache_page caches entire HTTP response, but we want to cache just the queryset
# Low-level caching gives us more control over what and how we cache

def property_list(request):
    """
    Returns a JSON list of all properties using low-level Redis caching.
    
    Why we switched from @cache_page to low-level cache API:
    - More granular control over cache operations
    - Can cache specific data (queryset) rather than entire HTTP response  
    - Allows custom cache keys and expiration times
    - Better for data reused across multiple views
    - Enables manual cache invalidation when needed
    
    Implementation approach:
    1. Use get_all_properties() which handles Redis caching internally
    2. Cache duration is 1 hour (3600 seconds) as specified
    3. Cache key is 'all_properties' for easy identification
    """
    
    # Get properties from cache or database via utility function
    # get_all_properties() handles all Redis cache logic internally
    properties_list = get_all_properties()
    
    # Get cache statistics for debugging and monitoring
    # Helps track cache performance and hit/miss ratios
    cache_stats = get_cache_stats()
    
    # Return JSON response with enhanced information
    # JsonResponse automatically sets correct Content-Type header
    return JsonResponse({
        'properties': properties_list,
        'count': len(properties_list),
        'cache_info': {
            'is_cached': cache_stats['is_cached'],
            'cache_backend': cache_stats['cache_backend'],
            'cache_timeout': cache_stats['cache_timeout'],
            'cache_key': cache_stats['cache_key']
        },
        'performance': {
            'data_source': 'Redis Cache' if cache_stats['is_cached'] else 'PostgreSQL Database',
            'cache_hit': cache_stats['is_cached']
        }
    })

def cache_stats(request):
    """
    Returns cache statistics for monitoring and debugging.
    
    Why cache monitoring is important:
    - Track cache performance and hit ratios
    - Debug caching issues in development
    - Monitor cache effectiveness in production
    - Optimize cache strategies based on usage patterns
    """
    from .utils import get_cache_stats
    
    stats = get_cache_stats()
    
    return JsonResponse({
        'cache_statistics': stats,
        'message': 'Cache statistics retrieved successfully'
    })

def invalidate_cache(request):
    """
    Manually invalidate the properties cache.
    
    Why manual cache invalidation is needed:
    - Force cache refresh when data changes
    - Clear stale data immediately
    - Testing and debugging purposes
    - Administrative control over cache lifecycle
    
    Security note: In production, this should be restricted to admin users
    """
    from .utils import invalidate_properties_cache
    
    # Only allow POST requests for cache invalidation for security
    if request.method == 'POST':
        invalidate_properties_cache()
        return JsonResponse({
            'message': 'Properties cache invalidated successfully',
            'action': 'cache_cleared',
            'next_request': 'will_fetch_from_database'
        })
    else:
        return JsonResponse({
            'error': 'Only POST method allowed for cache invalidation',
            'current_method': request.method
        }, status=405)
