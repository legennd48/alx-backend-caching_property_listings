from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from .models import Property
from .utils import get_all_properties, get_cache_stats

# Dual caching strategy implementation:
# 1. @cache_page(60 * 15) - caches entire HTTP response for 15 minutes
# 2. get_all_properties() - caches queryset data in Redis for 1 hour
#
# Why both caching layers are necessary:
# - HTTP response caching (15 min): Fast response delivery, includes headers/formatting
# - Queryset caching (1 hour): Reusable data across multiple views, longer duration
# - Different expiration times: Response cache refreshes more frequently than data cache
# - Layered performance: Maximum speed with data consistency

@cache_page(60 * 15)  # Cache entire HTTP response for 15 minutes
def property_list(request):
    """
    Returns a JSON list of all properties using dual caching strategy.
    
    Caching layers explained:
    1. HTTP Response Cache (15 minutes):
       - Caches the complete HTTP response including headers
       - Served directly by Django without executing view code
       - Faster delivery since no Python code execution needed
    
    2. Queryset Cache (1 hour):
       - Caches the raw property data from database
       - Shared across multiple views that need property data
       - Longer duration reduces database load
       - More granular control over data caching
    
    Why dual caching works well:
    - First request: Queryset cache miss → Database query → Store in Redis (1h)
    - Response formatted and cached (15min)
    - Next 15 min: Served from HTTP response cache (fastest)
    - After 15 min: HTTP cache expires, queryset still cached (still fast)
    - After 1 hour: Both caches expire, fresh data fetched
    """
    
    # Get properties using low-level cache API (1 hour cache)
    # This handles the queryset caching internally
    properties_list = get_all_properties()
    
    # Get cache statistics for monitoring both cache layers
    cache_stats = get_cache_stats()
    
    # Return JSON response (this entire response will be cached for 15 minutes)
    # JsonResponse automatically sets correct Content-Type header
    return JsonResponse({
        'properties': properties_list,
        'count': len(properties_list),
        'caching_strategy': {
            'http_response_cache': {
                'duration': '15 minutes',
                'decorator': '@cache_page(60 * 15)',
                'purpose': 'Fast HTTP response delivery'
            },
            'queryset_cache': {
                'duration': '1 hour (3600 seconds)',
                'api': 'Low-level cache API',
                'purpose': 'Reusable data across views',
                'is_cached': cache_stats['is_cached'],
                'cache_key': cache_stats['cache_key']
            }
        },
        'performance': {
            'data_source': 'Redis Cache' if cache_stats['is_cached'] else 'PostgreSQL Database',
            'queryset_cache_hit': cache_stats['is_cached'],
            'response_cache_info': 'Check X-Cache headers or response time'
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

def property_list_low_level_only(request):
    """
    Returns a JSON list of all properties using ONLY low-level Redis caching.
    
    This view demonstrates pure low-level cache API without @cache_page decorator.
    
    Difference from property_list view:
    - No @cache_page decorator (no HTTP response caching)
    - Only uses queryset caching (1 hour duration)
    - More control over cache invalidation
    - Better for APIs that need real-time cache management
    
    When to use this approach:
    - When you need manual cache control
    - For APIs with frequent data updates
    - When different views need the same cached data
    - For microservices that share cached data
    """
    
    # Get properties using low-level cache API only
    # This gives us 1-hour queryset caching without HTTP response caching
    properties_list = get_all_properties()
    
    # Get cache statistics for monitoring
    cache_stats = get_cache_stats()
    
    # Return JSON response (this response will NOT be cached by Django)
    return JsonResponse({
        'properties': properties_list,
        'count': len(properties_list),
        'caching_strategy': {
            'type': 'Low-level cache API only',
            'duration': '1 hour (3600 seconds)',
            'http_response_cached': False,
            'queryset_cached': cache_stats['is_cached']
        },
        'cache_info': {
            'is_cached': cache_stats['is_cached'],
            'cache_backend': cache_stats['cache_backend'],
            'cache_timeout': cache_stats['cache_timeout'],
            'cache_key': cache_stats['cache_key']
        },
        'performance': {
            'data_source': 'Redis Cache' if cache_stats['is_cached'] else 'PostgreSQL Database',
            'cache_hit': cache_stats['is_cached'],
            'response_caching': 'Disabled - only queryset caching active'
        }
    })
