from django.urls import path
from . import views

app_name = 'opd'

urlpatterns = [
    path('', views.opd_home, name='opd_home'),
    
    # Main OPD Registration + Billing Form
    path('addpatient/', views.add_patient_view, name='add_patient'),
    
    # Quick Add Patient Modal (AJAX)
    path('addmodal/', views.add_patient_modal, name='add_patient_modal'),
    
    # Generate page (if you still need it)
    path('generate/', views.generate_consultation, name='generate_consultation'),
    
    # Invoice & Other actions
    path('print/<int:visit_id>/', views.print_invoice, name='print_invoice'),
    path('pdf/<int:visit_id>/', views.download_pdf_invoice, name='download_pdf_invoice'),  # PDF Download
    path('api/visit/<int:visit_id>/', views.get_visit_details, name='get_visit_details'),
    path('api/patient/<int:patient_id>/', views.get_patient_details_api, name='get_patient_details_api'),
    path('delete/<int:visit_id>/', views.delete_visit, name='delete_visit'),

    # action section such as add prescription, show, print bill
    
    path('prescription/<int:visit_id>/', views.add_prescription, name='add_prescription'),
    path('manual-prescription/<int:visit_id>/', views.manual_prescription, name='manual_prescription'),
    path('move-to-ipd/<int:visit_id>/', views.move_to_ipd, name='move_to_ipd'),
]