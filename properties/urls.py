"""
URL configuration for properties app.

Why we need a separate urls.py for the app:
1. Separation of concerns - keeps app URLs isolated
2. Reusability - this app can be used in other projects
3. Maintainability - easier to manage app-specific URLs
4. Django best practice - follows the standard project structure
"""
from django.urls import path
from . import views

# Define the app namespace
# Why app_name is important:
# 1. Prevents URL name conflicts between different apps
# 2. Allows reverse URL lookup with namespacing (e.g., 'properties:property_list')
# 3. Makes URL names more explicit and readable
app_name = 'properties'

urlpatterns = [
    # Property list endpoint with dual caching - maps to /properties/
    # Uses both @cache_page (15 min) and low-level cache API (1 hour)
    # Why this URL pattern:
    # 1. RESTful design - GET /properties/ returns list of properties
    # 2. Clean URLs - easy to remember and type
    # 3. Follows Django conventions for list views
    path('', views.property_list, name='property_list'),
    
    # Property list with low-level cache only - maps to /properties/low-level/
    # Uses only low-level cache API (1 hour), no HTTP response caching
    # Why this endpoint is useful:
    # 1. Demonstrates pure low-level caching without @cache_page
    # 2. Better for APIs that need manual cache control
    # 3. Useful for testing different caching strategies
    path('low-level/', views.property_list_low_level_only, name='property_list_low_level'),
    
    # Cache statistics endpoint - maps to /properties/cache/stats/
    # Why cache stats endpoint is useful:
    # 1. Monitor cache performance and hit ratios
    # 2. Debug caching issues in development
    # 3. Administrative monitoring in production
    path('cache/stats/', views.cache_stats, name='cache_stats'),
    
    # Cache invalidation endpoint - maps to /properties/cache/invalidate/
    # Why cache invalidation endpoint is needed:
    # 1. Manual cache refresh when needed
    # 2. Testing and debugging purposes
    # 3. Administrative control over cache lifecycle
    # 4. Force immediate data refresh
    path('cache/invalidate/', views.invalidate_cache, name='invalidate_cache'),
]
