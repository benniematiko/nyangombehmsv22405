# annualcalendar/urls.py
from django.urls import path
from . import views

app_name = 'annualcalendar'  # This creates the 'annualcalendar' namespace

urlpatterns = [
    path('', views.annualcalendar_home, name='annualcalendar_home'),  # This creates 'annualcalendar:annualcalendar_home'
    # Add other annualcalendar URLs as needed
    # path('request/', views.request_annualcalendar, name='request'),
    # path('track/<int:annualcalendar_id>/', views.track_annualcalendar, name='track'),
]