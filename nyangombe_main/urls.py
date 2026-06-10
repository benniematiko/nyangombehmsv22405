from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),                  # Main landing page
    path('accounts/', include('accounts.urls')),          # Accounts login/logout
    
    # CRITICAL ADDITION: This explicitly registers the 'dashboard' namespace
    path('dashboard/', include('dashboard.urls')),  
    path('pharmacy/', include('pharmacy.urls')), 
    path('billing/', include('billing.urls')),
    path('opd/', include('opd.urls')),
    path('laboratory/', include('laboratory.urls')),    
    path('ipd/', include('ipd.urls')),
    path('appointments/', include('appointments.urls')),
    path('radiology/', include('radiology.urls')),
    path('patients/', include('patients.urls')),  # This creates the /patients/ prefix

    # path('expenses/', include('expenses.urls')),

]










  
    
