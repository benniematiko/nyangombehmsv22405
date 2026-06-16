from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Main Dashboard Route
    path('', views.billing_home, name='billing_home'),

    # Charge Catalogue API — powers cascading dropdowns on addpatient.html
    path('api/charge-categories/', views.get_charge_categories, name='get_charge_categories'),
    path('api/charges/', views.get_charges_by_category, name='get_charges_by_category'),
]