from django.contrib import admin
from .models import IPDPatient

@admin.register(IPDPatient)
class IPDPatientAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'admission_date', 'status', 'ward', 'bed_number']
    list_filter = ['status', 'admission_date']
    search_fields = ['patient__full_name', 'diagnosis', 'admission_reason']
    date_hierarchy = 'admission_date'
    
    readonly_fields = ['admission_date', 'updated_at']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient', 'doctor', 'diagnosis', 'admission_reason')
        }),
        ('Admission Details', {
            'fields': ('ward', 'bed_number', 'status', 'admission_date', 'discharge_date')
        }),
        ('Notes & Metadata', {
            'fields': ('notes', 'created_by', 'updated_at')
        }),
    )