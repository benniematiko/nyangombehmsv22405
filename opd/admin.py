from django.contrib import admin
from .models import PatientVisit

@admin.register(PatientVisit)
class PatientVisitAdmin(admin.ModelAdmin):
    list_display = ('case_id', 'patient', 'current_stage', 'created_at')
    list_filter = ('current_stage',)
    search_fields = ('case_id', 'patient__first_name', 'patient__last_name')
