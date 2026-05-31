from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Main Dashboard Route
    path('', views.appointments_home, name='appointments_home'),
    
    
]

