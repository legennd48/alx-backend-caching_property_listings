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
    # Property list endpoint - maps to /properties/
    # Why this URL pattern:
    # 1. RESTful design - GET /properties/ returns list of properties
    # 2. Clean URLs - easy to remember and type
    # 3. Follows Django conventions for list views
    path('', views.property_list, name='property_list'),
]
