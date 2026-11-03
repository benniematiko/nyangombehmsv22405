from django.urls import path
from . import views

app_name = 'ipd'

urlpatterns = [
    # Main Dashboard Route
    path('', views.ipd_home, name='ipd_home'),
    path('admit/', views.admit_patient, name='admit_patient'),
    path('discharge/<int:pk>/', views.discharge_patient, name='discharge_patient'),
    path('view/<int:pk>/', views.view_patient, name='view_patient'),
    
    
]