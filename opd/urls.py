from django.urls import path
from . import views

app_name = 'opd'

urlpatterns = [
    # Main Dashboard Route
    path('', views.opd_home, name='opd_home'),
    
    
]




