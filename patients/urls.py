from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patients_home, name='patients_home'),
    path('list/', views.patient_list, name='list'),
    path('detail/<uuid:patient_id>/', views.patient_detail, name='detail'),
    path('api/get-patients/', views.get_patients, name='get_patients'),
    path('api/patient/<uuid:patient_id>/', views.get_patient_details, name='get_patient_details'),
    path('api/add-patient/', views.add_patient_ajax, name='add_patient_ajax'),
]