from django.contrib import admin
from .models import (
    HospitalSetting, 
    Department, 
    Role, 
    StaffProfile, 
    SystemSetting, 
    AuditLog
)

@admin.register(HospitalSetting)
class HospitalSettingAdmin(admin.ModelAdmin):
    list_display = ['hospital_name', 'registration_number', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'staff_type', 'department', 'is_active', 'is_available']
    list_filter = ['staff_type', 'department', 'is_active', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']
    raw_id_fields = ['user', 'department', 'role']


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'setting_type', 'is_active']
    list_filter = ['setting_type', 'is_active']
    search_fields = ['key']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'created_at']
    list_filter = ['action', 'model_name']
    search_fields = ['user__username', 'model_name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']