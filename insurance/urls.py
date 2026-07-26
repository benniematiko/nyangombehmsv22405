# insurance/urls.py
from django.urls import path
from . import views

app_name = 'insurance'  # This creates the 'insurance' namespace

urlpatterns = [
    path('', views.insurance_home, name='insurance_home'),  # This creates 'insurance:insurance_home'
    # Add other insurance URLs as needed
    # path('request/', views.request_insurance, name='request'),
    # path('track/<int:insurance_id>/', views.track_insurance, name='track'),
]