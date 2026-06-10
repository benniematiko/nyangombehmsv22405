# pharmacy/urls.py
from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    # Main Dashboard Panel
    path('', views.pharmacy_home, name='pharmacy_home'),
    
    # Billing & Document Flow
    path('generate-bill/', views.pharmacy_generate_bill_view, name='pharmacygeneratebill'),
    
    # Stock & Inventory Operations
    path('medicines/', views.pharmacy_medicines_view, name='pharmacymedicines'),
    path('medicines/import/', views.import_medicines, name='importmedicines'),
    path('medicines/add/', views.add_medicines, name='addmedicine'),
    
    # Wholesale Purchasing & Procurement Ledger Trackers
    path('medicines/purchase/', views.purchase_medicines_ledger, name='purchasemedicines'),
    path('medicines/buy/', views.purchase_medicines_workspace_view, name='purchasemedicinesbuy'),
    
    # Automated Action Hook: Deducts stock items and pushes rows to the billing app
    path('prescription/<int:prescription_id>/approve/', views.approve_and_dispense_prescription, name='approve_prescription'),
    
    # Async JSON Cascading Select Endpoint API
    path('get-medicines-by-category/', views.get_medicines_by_category, name='get_medicines_by_category'),
]