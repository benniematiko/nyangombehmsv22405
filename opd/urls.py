from django.urls import path
from . import views

app_name = 'opd'

urlpatterns = [
    path('', views.opd_home, name='opd_home'),
    path('patient/add/', views.add_patient_view, name='add_patient'),  # Full page template
    path('patient/add-modal/', views.add_patient_modal, name='add_patient_modal'),  # Async API endpoint
]