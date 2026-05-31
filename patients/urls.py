from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    # Main Dashboard Route
    path('', views.patients_home, name='patients_home'),
    
    
]

