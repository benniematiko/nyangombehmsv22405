# dutyroster/urls.py
from django.urls import path
from . import views

app_name = 'dutyroster'  # This creates the 'dutyroster' namespace

urlpatterns = [
    path('', views.dutyroster_home, name='dutyroster_home'),  # This creates 'dutyroster:dutyroster_home'
    # Add other dutyroster URLs as needed
    # path('request/', views.request_dutyroster, name='request'),
    # path('track/<int:dutyroster_id>/', views.track_dutyroster, name='track'),
]