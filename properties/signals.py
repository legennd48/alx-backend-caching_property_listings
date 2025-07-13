"""
Django signals for automatic cache invalidation on Property model changes.

This module implements automatic cache invalidation using Django's signal system
to ensure data consistency between the database and Redis cache.

Why Django signals are necessary for cache invalidation:
1. Automatic cache refresh - no manual intervention needed
2. Data consistency - ensures cache never contains stale data  
3. Real-time updates - cache reflects database changes immediately
4. Development safety - prevents forgot-to-invalidate bugs
5. Production reliability - handles cache invalidation automatically
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property
import logging

# Set up logging for cache invalidation tracking
# Why logging is important for cache operations:
# - Debug cache invalidation issues in development
# - Monitor cache behavior in production
# - Track when and why cache is being cleared
# - Performance monitoring and optimization
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Property)
def invalidate_property_cache_on_save(sender, instance, created, **kwargs):
    """
    Signal handler that invalidates property cache when a Property is saved.
    
    This function is called automatically by Django after:
    - Creating a new Property (created=True)
    - Updating an existing Property (created=False)
    
    Why post_save signal is used:
    - Triggered after successful database save operation
    - Ensures cache invalidation only happens after data is committed
    - Handles both create and update operations with single handler
    - Prevents cache invalidation on failed save operations
    
    Args:
        sender: The model class that sent the signal (Property)
        instance: The actual Property instance that was saved
        created: Boolean indicating if this was a create (True) or update (False)
        **kwargs: Additional signal arguments
    """
    
    # Define the cache key that needs to be invalidated
    # This must match the cache key used in get_all_properties()
    cache_key = 'all_properties'
    
    try:
        # Delete the cached queryset from Redis
        # cache.delete() removes the key if it exists, does nothing if key doesn't exist
        cache_deleted = cache.delete(cache_key)
        
        # Log the cache invalidation for monitoring
        action = "created" if created else "updated"
        property_info = f"'{instance.title}' (ID: {instance.id})"
        
        if cache_deleted:
            logger.info(f"Cache invalidated: Property {action} - {property_info}")
            print(f"🗑️  Cache invalidated: Property {action} - {property_info}")
        else:
            # Cache key didn't exist, but that's normal behavior
            logger.info(f"Cache invalidation attempted: Property {action} - {property_info} (cache was empty)")
            print(f"ℹ️  Cache invalidation attempted: Property {action} - {property_info} (cache was empty)")
            
    except Exception as e:
        # Log any errors in cache invalidation but don't break the save operation
        # Cache invalidation failures shouldn't prevent database operations
        logger.error(f"Cache invalidation failed for Property {instance.id}: {e}")
        print(f"❌ Cache invalidation failed for Property {instance.id}: {e}")

@receiver(post_delete, sender=Property)
def invalidate_property_cache_on_delete(sender, instance, **kwargs):
    """
    Signal handler that invalidates property cache when a Property is deleted.
    
    This function is called automatically by Django after:
    - Successfully deleting a Property from the database
    
    Why post_delete signal is used:
    - Triggered after successful database delete operation
    - Ensures cache invalidation only happens after data is removed
    - Prevents serving deleted data from cache
    - Maintains data consistency after deletions
    
    Args:
        sender: The model class that sent the signal (Property)
        instance: The Property instance that was deleted
        **kwargs: Additional signal arguments
    """
    
    # Define the cache key that needs to be invalidated
    cache_key = 'all_properties'
    
    try:
        # Delete the cached queryset from Redis
        cache_deleted = cache.delete(cache_key)
        
        # Log the cache invalidation for monitoring
        property_info = f"'{instance.title}' (ID: {instance.id})"
        
        if cache_deleted:
            logger.info(f"Cache invalidated: Property deleted - {property_info}")
            print(f"🗑️  Cache invalidated: Property deleted - {property_info}")
        else:
            # Cache key didn't exist, but that's normal behavior
            logger.info(f"Cache invalidation attempted: Property deleted - {property_info} (cache was empty)")
            print(f"ℹ️  Cache invalidation attempted: Property deleted - {property_info} (cache was empty)")
            
    except Exception as e:
        # Log any errors in cache invalidation but don't break the delete operation
        # Cache invalidation failures shouldn't prevent database operations
        logger.error(f"Cache invalidation failed for deleted Property {instance.id}: {e}")
        print(f"❌ Cache invalidation failed for deleted Property {instance.id}: {e}")

def manual_cache_invalidation():
    """
    Helper function for manual cache invalidation.
    
    This function can be called programmatically when needed:
    - During bulk operations that bypass signals
    - For administrative cache clearing
    - During development and testing
    - For scheduled cache refresh operations
    
    Returns:
        bool: True if cache was cleared, False if cache was already empty
    """
    cache_key = 'all_properties'
    
    try:
        cache_deleted = cache.delete(cache_key)
        
        if cache_deleted:
            logger.info("Manual cache invalidation: all_properties cache cleared")
            print("🗑️  Manual cache invalidation: all_properties cache cleared")
        else:
            logger.info("Manual cache invalidation: cache was already empty")
            print("ℹ️  Manual cache invalidation: cache was already empty")
            
        return cache_deleted
        
    except Exception as e:
        logger.error(f"Manual cache invalidation failed: {e}")
        print(f"❌ Manual cache invalidation failed: {e}")
        return False

# Signal connection verification
# Why verification is important:
# - Ensures signals are properly connected at startup
# - Helps debug signal connection issues
# - Provides startup confirmation in logs
def verify_signal_connections():
    """
    Verify that signals are properly connected.
    
    This function can be called during app startup to ensure
    signal handlers are correctly registered with Django.
    """
    from django.db.models.signals import post_save, post_delete
    
    # Check if our signal handlers are connected
    post_save_receivers = [receiver.__name__ for receiver in post_save._live_receivers()]
    post_delete_receivers = [receiver.__name__ for receiver in post_delete._live_receivers()]
    
    logger.info(f"Property cache invalidation signals connected:")
    logger.info(f"  post_save receivers: {post_save_receivers}")
    logger.info(f"  post_delete receivers: {post_delete_receivers}")
    
    return {
        'post_save_connected': 'invalidate_property_cache_on_save' in str(post_save_receivers),
        'post_delete_connected': 'invalidate_property_cache_on_delete' in str(post_delete_receivers)
    }
