# pharmacy/urls.py
from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('', views.pharmacy_home, name='pharmacy_home'),
    path('generate-bill/', views.pharmacy_generate_bill_view, name='pharmacygeneratebill'),
    path('medicines/', views.pharmacy_medicines_view, name='pharmacymedicines'),
    
    
    path('medicines/import/', views.import_medicines, name='importmedicines'),
    path('medicines/add/', views.add_medicines, name='addmedicine'),
    path('medicines/purchase/', views.purchase_medicines, name='purchasemedicines'),
    path('medicines/buy/', views.purchase_medicines_buy, name='purchasemedicinesbuy'),
]


