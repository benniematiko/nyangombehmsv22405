from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'patient_number', 
        'first_name', 
        'last_name', 
        'phone_number',
        'blood_group',
        'insurance_provider',
        'created_at'
    )
    
    search_fields = (
        'patient_number', 
        'first_name', 
        'last_name', 
        'phone_number',
        'national_id_or_passport',
        'insurance_id'
    )
    
    list_filter = ('gender', 'blood_group', 'marital_status', 'created_at')
    
    # Include all fields in the edit form
    fields = (
        'patient_number', 'first_name', 'last_name', 'date_of_birth', 'gender',
        'blood_group', 'marital_status', 'phone_number', 'email', 'address',
        'national_id_or_passport', 'allergies', 'remarks', 'insurance_provider',
        'insurance_id', 'insurance_validity', 'next_of_kin_name', 
        'next_of_kin_phone', 'next_of_kin_relationship', 'patient_photo',
        'created_at', 'updated_at'
    )
    
    readonly_fields = ('created_at', 'updated_at')