# ambulance/urls.py
from django.urls import path
from . import views

app_name = 'ambulance'  # This creates the 'ambulance' namespace

urlpatterns = [
    path('', views.ambulance_home, name='ambulance_home'),  # This creates 'ambulance:ambulance_home'
    # Add other ambulance URLs as needed
    # path('request/', views.request_ambulance, name='request'),
    # path('track/<int:ambulance_id>/', views.track_ambulance, name='track'),
]