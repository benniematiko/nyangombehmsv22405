from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # This must match name='home' to connect with LOGIN_REDIRECT_URL
    path('', views.home, name='home'), 
]