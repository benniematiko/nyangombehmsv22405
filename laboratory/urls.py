# pharmacy/urls.py
from django.urls import path
from . import views

app_name = 'laboratory'

urlpatterns = [
    path('', views.laboratory_home, name='laboratory_home'),  
    
    
    
]


