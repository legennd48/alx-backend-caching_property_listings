from django.apps import AppConfig


class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        This ensures that signals are registered and will be triggered
        when Property model instances are created, updated, or deleted.
        """
        import properties.signals
