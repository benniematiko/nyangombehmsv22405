# birthdeath/urls.py
from django.urls import path
from . import views

app_name = 'birthdeath'  # This creates the 'birthdeath' namespace

urlpatterns = [
    path('', views.birthdeath_home, name='birthdeath_home'),  # This creates 'birthdeath:birthdeath_home'
    # Add other birthdeath URLs as needed
    # path('request/', views.request_birthdeath, name='request'),
    # path('track/<int:birthdeath_id>/', views.track_birthdeath, name='track'),
]