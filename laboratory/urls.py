# pharmacy/urls.py
from django.urls import path
from . import views

app_name = 'laboratory'

urlpatterns = [
    path('', views.laboratory_home, name='laboratory_home'),  
    path('generatebill/', views.laboratory_generate_bill_view, name='laboratorygeneratebill'),  
    path('tests/list/', views.laboratory_tests_list_view, name='laboratorytestslist'),
    
    
    
]







