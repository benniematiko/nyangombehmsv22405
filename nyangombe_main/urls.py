from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),                  # Main landing page
    path('accounts/', include('accounts.urls')),          # Accounts login/logout
    
    # CRITICAL ADDITION: This explicitly registers the 'dashboard' namespace
    path('dashboard/', include('dashboard.urls')),   
]