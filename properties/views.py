from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from .models import Property

# Cache the property list for 15 minutes (60 * 15 = 900 seconds)
# Why caching is necessary:
# 1. Reduces database queries - avoids hitting the database on every request
# 2. Improves response time - Redis is much faster than PostgreSQL for read operations
# 3. Reduces server load - cached responses require less CPU and memory
# 4. Better user experience - faster page loads
@cache_page(60 * 15)  # Cache for 15 minutes in Redis
def property_list(request):
    """
    Returns a JSON list of all properties.
    
    Why we return JSON:
    - API-ready format for frontend consumption
    - Easier to test and debug
    - Lightweight compared to full HTML rendering
    - Can be easily consumed by mobile apps or other services
    """
    # Get all properties from database
    # This query will only run once every 15 minutes due to caching
    properties = Property.objects.all().values(
        'id', 'title', 'description', 'price', 'location', 'created_at'
    )
    
    # Convert QuerySet to list for JSON serialization
    # Why we use .values(): It's more efficient than serializing full model instances
    properties_list = list(properties)
    
    # Return JSON response
    # Why JsonResponse: Automatically sets correct Content-Type header
    return JsonResponse({
        'properties': properties_list,
        'count': len(properties_list),
        'cached': True  # Indicates this response comes from cache after first request
    })
