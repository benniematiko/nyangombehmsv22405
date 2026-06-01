from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_number', 'first_name', 'last_name', 'phone_number', 'created_at')
    search_fields = ('patient_number', 'first_name', 'last_name', 'phone_number')
