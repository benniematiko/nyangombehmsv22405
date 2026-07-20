# pharmacy/urls.py
from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    # ====================== MAIN DASHBOARD ======================
    path('', views.pharmacy_home, name='pharmacy_home'),

    # ====================== BILLING & PAYMENT ======================
    path('generate-bill/', views.pharmacy_generate_bill_view, name='pharmacygeneratebill'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:invoice_id>/print/', views.invoice_print, name='invoice_print'),
    path('invoice/<int:invoice_id>/details/', views.get_invoice_details, name='invoice_details'),
    path('invoice/<int:invoice_id>/delete/', views.delete_invoice, name='delete_invoice'),
    path('payment/', views.pharmacy_payment_view, name='pharmacypayment'),
    path('payment/save/', views.save_payment, name='save_payment'),

    # ====================== INVENTORY & MEDICINES ======================
    path('medicines/', views.pharmacy_medicines_view, name='pharmacymedicines'),
    path('medicines/add/', views.add_medicines, name='addmedicine'),
    path('medicines/import/', views.import_medicines, name='importmedicines'),

    # Wholesale / Purchase Ledger
    path('medicines/purchase/', views.purchase_medicines_ledger, name='purchasemedicines'),
    path('medicines/buy/', views.purchase_medicines_workspace_view, name='purchasemedicinesbuy'),

    # ====================== PRESCRIPTION & ACTIONS ======================
    path('prescription/<int:prescription_id>/approve/', 
         views.approve_and_dispense_prescription, 
         name='approve_prescription'),

    # ====================== AJAX / JSON ENDPOINTS ======================
    path('search-patients/', views.search_patients, name='search_patients'),
    path('get-medicines-by-category/', views.get_medicines_by_category, name='get_medicines_by_category'),
    path('get-patient/<int:patient_id>/', views.get_patient_by_id, name='get_patient_by_id'),
    path('get-transactions/', views.get_transactions, name='get_transactions'),
    path('delete-transaction/', views.delete_transaction, name='delete_transaction'),
    path('add-patient-modal/', views.add_patient_modal, name='add_patient_modal'),

    # ====================== API ENDPOINTS FOR MEDICINE DROPDOWNS ======================
    path('api/medicine-categories/', views.get_medicine_categories, name='api_medicine_categories'),
    path('api/medicine-companies/', views.get_medicine_companies, name='api_medicine_companies'),
    path('api/medicine-compositions/', views.get_medicine_compositions, name='api_medicine_compositions'),
    path('api/medicine-groups/', views.get_medicine_groups, name='api_medicine_groups'),  # ← ADD THIS
]