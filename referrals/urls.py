# referrals/urls.py
from django.urls import path
from . import views

app_name = 'referrals'  # This creates the 'referrals' namespace

urlpatterns = [
    path('', views.referrals_home, name='referrals_home'),  # This creates 'referrals:referrals_home'
    # Add other referrals URLs as needed
    # path('request/', views.request_referrals, name='request'),
    # path('track/<int:referrals_id>/', views.track_referrals, name='track'),
]