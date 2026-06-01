from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Main Dashboard Route
    path('', views.billing_home, name='billing_home'),
    
    
]



