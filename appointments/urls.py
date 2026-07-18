from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Main Dashboard / Scheduling Log
    path('', views.appointments_home, name='appointments_home'),
    
    # Navigation Targets requested by layout actions
    path('book/', views.book_appointment, name='book_appointment'),
    path('rosters/', views.doctor_rosters, name='doctor_rosters'),
    
    # Detail Profiles, Printing engine & Actions
    path('booking/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('booking/<int:appointment_id>/print/', views.print_appointment_slip, name='print_appointment_slip'),
    path('booking/<int:appointment_id>/details/', views.appointment_modal_details, name='appointment_modal_details'),
    path('booking/<int:appointment_id>/edit/', views.edit_appointment, name='edit_appointment'),
    path('booking/<int:appointment_id>/delete/', views.delete_appointment, name='delete_appointment'),
    path('booking/<int:appointment_id>/confirm/', views.confirm_appointment, name='confirm_appointment'),
]