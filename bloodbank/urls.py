from django.urls import path
from . import views

app_name = 'bloodbank'

urlpatterns = [
    # Dashboard
    path('', views.bloodbank_home, name='bloodbank_home'),
    
    # Donor URLs
    path('donors/', views.donor_list, name='donor_list'),
    path('donors/<int:donor_id>/', views.donor_detail, name='donor_detail'),
    path('donors/create/', views.donor_create, name='donor_create'),
    path('donors/<int:donor_id>/edit/', views.donor_edit, name='donor_edit'),
    path('donors/<int:donor_id>/delete/', views.donor_delete, name='donor_delete'),
    
    # Blood Stock URLs
    path('stock/', views.blood_stock, name='blood_stock'),
    
    # Donation URLs
    path('donations/', views.donation_list, name='donation_list'),
    path('donations/create/', views.donation_create, name='donation_create'),
    
    # Blood Request URLs
    path('requests/', views.blood_request_list, name='request_list'),
    path('requests/create/', views.blood_request_create, name='request_create'),
    path('requests/<int:request_id>/update/', views.blood_request_update, name='request_update'),
]