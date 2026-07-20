from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.inventory_home, name='inventory_home'),
    
    # Items
    path('items/', views.item_list, name='item_list'),
    path('items/add/', views.item_add, name='item_add'),
    path('items/<int:item_id>/edit/', views.item_edit, name='item_edit'),
    path('items/<int:item_id>/delete/', views.item_delete, name='item_delete'),
    path('items/<int:item_id>/', views.item_detail, name='item_detail'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    
    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_add, name='supplier_add'),
    
    # Stock Movements
    path('stock/transactions/', views.stock_transactions, name='stock_transactions'),
    path('stock/add/', views.stock_add, name='stock_add'),
    path('stock/issue/', views.stock_issue, name='stock_issue'),
    path('stock/adjust/', views.stock_adjust, name='stock_adjust'),
    
    # Purchase Orders
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/add/', views.purchase_order_add, name='purchase_order_add'),
    path('purchase-orders/<int:po_id>/', views.purchase_order_detail, name='purchase_order_detail'),
    
    # Stock Counts
    path('stock-counts/', views.stock_count_list, name='stock_count_list'),
    path('stock-counts/add/', views.stock_count_add, name='stock_count_add'),
    
    # Reports
    path('reports/low-stock/', views.low_stock_report, name='low_stock_report'),
    path('reports/expiring/', views.expiring_items_report, name='expiring_items_report'),
]