from django.contrib import admin
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    # Simple list display - only use fields that exist
    list_display = ('id', 'get_doctor_name', 'specialization', 'license_number', 'phone', 'is_available')
    list_filter = ('specialization', 'is_available')
    search_fields = ('user__first_name', 'user__last_name', 'license_number', 'phone')
    list_per_page = 20
    
    # Only use fields that exist in your model
    fields = ('user', 'specialization', 'license_number', 'phone', 'email', 'address', 'consultation_fee', 'is_available')
    
    def get_doctor_name(self, obj):
        return obj.full_name
    get_doctor_name.short_description = 'Doctor Name'
    get_doctor_name.admin_order_field = 'user__first_name'