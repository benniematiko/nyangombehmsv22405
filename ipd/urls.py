from django.urls import path
from . import views

app_name = 'ipd'

urlpatterns = [
    # Main Dashboard Route
    path('', views.ipd_home, name='ipd_home'),
    
    
]