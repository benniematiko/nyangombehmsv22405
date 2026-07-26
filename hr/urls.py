# hr/urls.py
from django.urls import path
from . import views

app_name = 'hr'  # This creates the 'hr' namespace

urlpatterns = [
    path('', views.hr_home, name='hr_home'),  # This creates 'hr:hr_home'
    # Add other hr URLs as needed
    # path('request/', views.request_hr, name='request'),
    # path('track/<int:hr_id>/', views.track_hr, name='track'),
]