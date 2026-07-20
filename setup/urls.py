from django.urls import path
from . import views

app_name = 'setup'

urlpatterns = [
    # Dashboard
    path('', views.setup_home, name='setup_home'),
    
    # ============================================================
    # CORE ADMINISTRATION
    # ============================================================
    
    # Hospital Settings
    path('hospital-settings/', views.hospital_settings, name='hospital_settings'),
    
    # System Settings
    path('system-settings/', views.system_settings, name='system_settings'),
    
    # Staff Management
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.staff_add, name='staff_add'),
    
    # Roles & Permissions
    path('roles/', views.role_list, name='role_list'),
    
    # ============================================================
    # CLINICAL & OPERATIONAL
    # ============================================================
    
    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:dept_id>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:dept_id>/delete/', views.department_delete, name='department_delete'),
    
    # Symptoms
    path('symptoms/', views.symptoms_list, name='symptoms_list'),
    
    # ============================================================
    # FINANCE & CHARGE POLICIES
    # ============================================================
    
    # Charge Categories
    path('charge-categories/', views.charge_categories, name='charge_categories'),
    
    # Charge Tariffs Master
    path('charge-master/', views.charge_master, name='charge_master'),
    
    # Insurance Providers
    path('insurance-providers/', views.insurance_providers, name='insurance_providers'),
    path('insurance-setup/', views.insurance_providers, name='insurance_setup'),  # ← ADD THIS ALIAS
    
    # ============================================================
    # COMPLIANCE & SYSTEM HEALTH
    # ============================================================
    
    # Audit Logs
    path('audit-logs/', views.audit_logs, name='audit_logs'),
]