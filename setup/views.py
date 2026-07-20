from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


@login_required
def setup_home(request):
    """Setup dashboard landing page."""
    return render(request, 'setup/setup_home.html')


# ============================================================
# CORE ADMINISTRATION
# ============================================================

@login_required
def hospital_settings(request):
    """Manage hospital settings."""
    return render(request, 'setup/hospital_settings.html')


@login_required
def system_settings(request):
    """Manage system-wide settings."""
    return render(request, 'setup/system_settings.html')


@login_required
def staff_list(request):
    """List all staff members."""
    return render(request, 'setup/staff_list.html')


@login_required
def staff_add(request):
    """Add a new staff member."""
    return render(request, 'setup/staff_add.html')


@login_required
def role_list(request):
    """List all roles."""
    return render(request, 'setup/role_list.html')


# ============================================================
# CLINICAL & OPERATIONAL
# ============================================================

@login_required
def department_list(request):
    """List all departments."""
    if request.method == 'POST':
        messages.success(request, "Department added successfully!")
        return redirect('setup:department_list')
    return render(request, 'setup/department_list.html')


@login_required
def department_edit(request, dept_id):
    """Edit a department."""
    return render(request, 'setup/department_edit.html')


@login_required
def department_delete(request, dept_id):
    """Delete a department."""
    if request.method == 'POST':
        messages.success(request, "Department deleted successfully!")
    return redirect('setup:department_list')


@login_required
def symptoms_list(request):
    """List all symptoms."""
    return render(request, 'setup/symptoms_list.html')


# ============================================================
# FINANCE & CHARGE POLICIES
# ============================================================

@login_required
def charge_categories(request):
    """Manage charge categories."""
    return render(request, 'setup/charge_categories.html')


@login_required
def charge_master(request):
    """Manage charge tariffs master."""
    return render(request, 'setup/charge_master.html')


@login_required
def insurance_providers(request):
    """Manage insurance providers."""
    return render(request, 'setup/insurance_providers.html')


# ============================================================
# COMPLIANCE & SYSTEM HEALTH
# ============================================================

@login_required
def audit_logs(request):
    """View audit logs."""
    return render(request, 'setup/audit_logs.html')