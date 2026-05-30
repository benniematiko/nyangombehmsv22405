# pharmacy/urls.py
from django.urls import path
from . import views

app_name = 'pharmacy'  # This is the namespace string

urlpatterns = [
    path('', views.pharmacy_home, name='pharmacy_home'),
    path('generate-bill/', views.pharmacy_generate_bill_view, name='pharmacygeneratebill'),
    path('medicines/', views.pharmacy_medicines_view, name='pharmacymedicines'),
]



