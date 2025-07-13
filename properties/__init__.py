# Set the default app config for the properties app
# This ensures that the PropertiesConfig.ready() method is called,
# which registers our signal handlers for automatic cache invalidation
default_app_config = 'properties.apps.PropertiesConfig'