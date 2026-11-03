from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.inventory_home, name='inventory_home'),    
    path('stock/', views.item_stock_list, name='item_stock_list'),
    
   
    
    
]