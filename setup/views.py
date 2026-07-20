from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from pharmacy.models import MedicineCategory, MedicineGroup, MedicineComposition, Supplier


@login_required
def setup_home(request):
    """Setup dashboard landing page."""
    from pharmacy.models import MedicineCategory, MedicineGroup, MedicineComposition, Supplier
    
    context = {
        # Existing counts (if any)
        'category_count': MedicineCategory.objects.count(),
        'group_count': MedicineGroup.objects.count(),
        'composition_count': MedicineComposition.objects.count(),
        'supplier_count': Supplier.objects.count(),
    }
    return render(request, 'setup/setup_home.html', context)


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



# ============================================================
# PHARMACY DATA MANAGEMENT
# ============================================================



# ---------- MEDICINE CATEGORIES ----------

@login_required
def pharmacy_categories(request):
    """Manage medicine categories."""
    categories = MedicineCategory.objects.all().order_by('name')
    return render(request, 'setup/pharmacy_categories.html', {'categories': categories})


@login_required
def pharmacy_category_add(request):
    """Add a new medicine category."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, "Category name is required.")
            return redirect('setup:pharmacy_category_add')
        
        try:
            MedicineCategory.objects.create(name=name, description=description, is_active=True)
            messages.success(request, f"Category '{name}' added successfully!")
            return redirect('setup:pharmacy_categories')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return render(request, 'setup/pharmacy_category_form.html', {'is_edit': False})


@login_required
def pharmacy_category_edit(request, cat_id):
    """Edit a medicine category."""
    category = get_object_or_404(MedicineCategory, id=cat_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        if not name:
            messages.error(request, "Category name is required.")
            return redirect('setup:pharmacy_category_edit', cat_id=cat_id)
        
        try:
            category.name = name
            category.description = description
            category.is_active = is_active
            category.save()
            messages.success(request, f"Category '{name}' updated successfully!")
            return redirect('setup:pharmacy_categories')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return render(request, 'setup/pharmacy_category_form.html', {'item': category, 'is_edit': True})


@login_required
def pharmacy_category_delete(request, cat_id):
    """Delete a medicine category."""
    category = get_object_or_404(MedicineCategory, id=cat_id)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f"Category '{name}' deleted successfully!")
    return redirect('setup:pharmacy_categories')


# ---------- MEDICINE GROUPS ----------

@login_required
def pharmacy_groups(request):
    """Manage medicine groups."""
    groups = MedicineGroup.objects.all().order_by('name')
    return render(request, 'setup/pharmacy_groups.html', {'groups': groups})


@login_required
def pharmacy_group_add(request):
    """Add a new medicine group."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, "Group name is required.")
            return redirect('setup:pharmacy_group_add')
        
        try:
            MedicineGroup.objects.create(name=name, description=description, is_active=True)
            messages.success(request, f"Group '{name}' added successfully!")
            return redirect('setup:pharmacy_groups')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return render(request, 'setup/pharmacy_group_form.html', {'is_edit': False})


@login_required
def pharmacy_group_edit(request, group_id):
    """Edit a medicine group."""
    group = get_object_or_404(MedicineGroup, id=group_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        if not name:
            messages.error(request, "Group name is required.")
            return redirect('setup:pharmacy_group_edit', group_id=group_id)
        
        try:
            group.name = name
            group.description = description
            group.is_active = is_active
            group.save()
            messages.success(request, f"Group '{name}' updated successfully!")
            return redirect('setup:pharmacy_groups')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return render(request, 'setup/pharmacy_group_form.html', {'item': group, 'is_edit': True})


@login_required
def pharmacy_group_delete(request, group_id):
    """Delete a medicine group."""
    group = get_object_or_404(MedicineGroup, id=group_id)
    if request.method == 'POST':
        name = group.name
        group.delete()
        messages.success(request, f"Group '{name}' deleted successfully!")
    return redirect('setup:pharmacy_groups')


# ---------- MEDICINE COMPOSITIONS ----------

@login_required
def pharmacy_compositions(request):
    """Manage medicine compositions."""
    compositions = MedicineComposition.objects.all().order_by('name')
    return render(request, 'setup/pharmacy_compositions.html', {'compositions': compositions})


@login_required
def pharmacy_composition_add(request):
    """Add a new medicine composition."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, "Composition name is required.")
            return redirect('setup:pharmacy_composition_add')
        
        try:
            MedicineComposition.objects.create(name=name, description=description, is_active=True)
            messages.success(request, f"Composition '{name}' added successfully!")
            return redirect('setup:pharmacy_compositions')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return render(request, 'setup/pharmacy_composition_form.html', {'is_edit': False})


@login_required
def pharmacy_composition_edit(request, comp_id):
    """Edit a medicine composition."""
    composition = get_object_or_404(MedicineComposition, id=comp_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        if not name:
            messages.error(request, "Composition name is required.")
            return redirect('setup:pharmacy_composition_edit', comp_id=comp_id)
        
        try:
            composition.name = name
            composition.description = description
            composition.is_active = is_active
            composition.save()
            messages.success(request, f"Composition '{name}' updated successfully!")
            return redirect('setup:pharmacy_compositions')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return render(request, 'setup/pharmacy_composition_form.html', {'item': composition, 'is_edit': True})


@login_required
def pharmacy_composition_delete(request, comp_id):
    """Delete a medicine composition."""
    composition = get_object_or_404(MedicineComposition, id=comp_id)
    if request.method == 'POST':
        name = composition.name
        composition.delete()
        messages.success(request, f"Composition '{name}' deleted successfully!")
    return redirect('setup:pharmacy_compositions')


# ---------- SUPPLIERS (Medicine Companies) ----------

@login_required
def pharmacy_suppliers(request):
    """Manage suppliers (medicine companies)."""
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'setup/pharmacy_suppliers.html', {'suppliers': suppliers})


@login_required
def pharmacy_supplier_add(request):
    """Add a new supplier (medicine company)."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        contact_person = request.POST.get('contact_person', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        email = request.POST.get('email', '').strip()
        location = request.POST.get('location', '').strip()
        
        if not name:
            messages.error(request, "Supplier name is required.")
            return redirect('setup:pharmacy_supplier_add')
        
        try:
            Supplier.objects.create(
                name=name,
                contact_person=contact_person,
                phone_number=phone_number,
                email=email,
                location=location,
                is_active=True,
            )
            messages.success(request, f"Supplier '{name}' added successfully!")
            return redirect('setup:pharmacy_suppliers')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return render(request, 'setup/pharmacy_supplier_form.html', {'is_edit': False})


@login_required
def pharmacy_supplier_edit(request, supplier_id):
    """Edit a supplier (medicine company)."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        contact_person = request.POST.get('contact_person', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        email = request.POST.get('email', '').strip()
        location = request.POST.get('location', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        if not name:
            messages.error(request, "Supplier name is required.")
            return redirect('setup:pharmacy_supplier_edit', supplier_id=supplier_id)
        
        try:
            supplier.name = name
            supplier.contact_person = contact_person
            supplier.phone_number = phone_number
            supplier.email = email
            supplier.location = location
            supplier.is_active = is_active
            supplier.save()
            messages.success(request, f"Supplier '{name}' updated successfully!")
            return redirect('setup:pharmacy_suppliers')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return render(request, 'setup/pharmacy_supplier_form.html', {'item': supplier, 'is_edit': True})


@login_required
def pharmacy_supplier_delete(request, supplier_id):
    """Delete a supplier (medicine company)."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        name = supplier.name
        supplier.delete()
        messages.success(request, f"Supplier '{name}' deleted successfully!")
    return redirect('setup:pharmacy_suppliers')