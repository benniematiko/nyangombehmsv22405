from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

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
    path('finance/', include('finance.urls')),
    path('inventory/', include('inventory.urls')),
    path('bloodbank/', include('bloodbank.urls')),
    path('ambulance/', include('ambulance.urls')),
    path('insurance/', include('insurance.urls')),
    path('frontoffice/', include('frontoffice.urls')),

    path('birthdeath/', include('birthdeath.urls')),
    path('hr/', include('hr.urls')),
    path('dutyroster/', include('dutyroster.urls')),

    path('messaging/', include('messaging.urls')),
    path('download-center/', include('downloadcenter.urls')),
    path('certificates/', include('certificate.urls')),
    path('cms/', include('frontcms.urls')),
    path('live-consultation/', include('liveconsultation.urls')),

    path('referrals/', include('referrals.urls')),
    path('annualcalendar/', include('annualcalendar.urls')),
    path('reports/', include('reports.urls')),
    path('setup/', include('setup.urls')),
    
    

    # path('expenses/', include('expenses.urls')),

]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)