# ambulance/urls.py
from django.urls import path
from . import views

app_name = 'ambulance'  # This creates the 'ambulance' namespace

urlpatterns = [
    path('', views.ambulance_home, name='ambulance'), 
    path('ambulancegeneratebill/', views.ambulancegeneratebill, name='ambulancegeneratebill'),  
    path('ambulancelist/', views.ambulance_list, name='ambulancelist'),  
]