"""
URL configuration for alx_backend_caching_property_listings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin interface - for managing properties through Django admin
    # Why admin is important:
    # 1. Provides easy interface for content management
    # 2. Allows non-technical users to add/edit properties
    # 3. Built-in authentication and authorization
    path('admin/', admin.site.urls),
    
    # Properties app URLs - maps /properties/ to the properties app
    # Why we use include():
    # 1. Delegates URL handling to the app's urls.py
    # 2. Keeps project urls.py clean and organized
    # 3. Allows the app to define its own URL patterns
    # 4. Makes the app more modular and reusable
    path('properties/', include('properties.urls')),
]
