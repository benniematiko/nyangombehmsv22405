from django.urls import path
from . import views

app_name = 'radiology'

urlpatterns = [
    # Main Dashboard Route
    path('', views.radiology_home, name='radiology_home'),
    
    
]

