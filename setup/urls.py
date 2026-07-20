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
    # PHARMACY DATA MANAGEMENT (NEW)
    # ============================================================
    
    # Medicine Categories
    path('pharmacy/categories/', views.pharmacy_categories, name='pharmacy_categories'),
    path('pharmacy/categories/add/', views.pharmacy_category_add, name='pharmacy_category_add'),
    path('pharmacy/categories/<int:cat_id>/edit/', views.pharmacy_category_edit, name='pharmacy_category_edit'),
    path('pharmacy/categories/<int:cat_id>/delete/', views.pharmacy_category_delete, name='pharmacy_category_delete'),
    
    # Medicine Groups
    path('pharmacy/groups/', views.pharmacy_groups, name='pharmacy_groups'),
    path('pharmacy/groups/add/', views.pharmacy_group_add, name='pharmacy_group_add'),
    path('pharmacy/groups/<int:group_id>/edit/', views.pharmacy_group_edit, name='pharmacy_group_edit'),
    path('pharmacy/groups/<int:group_id>/delete/', views.pharmacy_group_delete, name='pharmacy_group_delete'),
    
    # Medicine Compositions
    path('pharmacy/compositions/', views.pharmacy_compositions, name='pharmacy_compositions'),
    path('pharmacy/compositions/add/', views.pharmacy_composition_add, name='pharmacy_composition_add'),
    path('pharmacy/compositions/<int:comp_id>/edit/', views.pharmacy_composition_edit, name='pharmacy_composition_edit'),
    path('pharmacy/compositions/<int:comp_id>/delete/', views.pharmacy_composition_delete, name='pharmacy_composition_delete'),
    
    # Suppliers (Medicine Companies)
    path('pharmacy/suppliers/', views.pharmacy_suppliers, name='pharmacy_suppliers'),
    path('pharmacy/suppliers/add/', views.pharmacy_supplier_add, name='pharmacy_supplier_add'),
    path('pharmacy/suppliers/<int:supplier_id>/edit/', views.pharmacy_supplier_edit, name='pharmacy_supplier_edit'),
    path('pharmacy/suppliers/<int:supplier_id>/delete/', views.pharmacy_supplier_delete, name='pharmacy_supplier_delete'),
    
    # ============================================================
    # FINANCE & CHARGE POLICIES
    # ============================================================
    
    # Charge Categories
    path('charge-categories/', views.charge_categories, name='charge_categories'),
    
    # Charge Tariffs Master
    path('charge-master/', views.charge_master, name='charge_master'),
    
    # Insurance Providers
    path('insurance-providers/', views.insurance_providers, name='insurance_providers'),
    path('insurance-setup/', views.insurance_providers, name='insurance_setup'),  # Alias
    
    # ============================================================
    # COMPLIANCE & SYSTEM HEALTH
    # ============================================================
    
    # Audit Logs
    path('audit-logs/', views.audit_logs, name='audit_logs'),
]