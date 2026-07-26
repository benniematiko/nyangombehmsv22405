# frontoffice/urls.py
from django.urls import path
from . import views

app_name = 'frontoffice'  # This creates the 'frontoffice' namespace

urlpatterns = [
    path('', views.frontoffice_home, name='frontoffice_home'),  # This creates 'frontoffice:frontoffice_home'
    # Add other frontoffice URLs as needed
    # path('request/', views.request_frontoffice, name='request'),
    # path('track/<int:frontoffice_id>/', views.track_frontoffice, name='track'),
]