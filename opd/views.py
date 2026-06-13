from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from patients.models import Patient
from datetime import datetime, timedelta
import uuid


@login_required
def opd_home(request):
    """Renders the main OPD Billing Logs and Records Dashboard"""
    # Your existing dashboard home logic here (fetching logs, querysets, etc.)
    return render(request, 'opd/opd.html')


@login_required
def add_patient_view(request):
    """Renders the full-width clinical case setup for adding a patient"""
    if request.method == 'POST':
        # Handle saving logic here...
        pass
        
    context = {
        'hide_sidebar': True  # Drops the sidebar and triggers full bleed layout rules
    }
    return render(request, 'opd/addpatient.html', context)


@login_required
def add_patient_modal(request):
    """Handle patient registration from modal"""
    if request.method == 'POST':
        try:
            # Generate unique patient number
            year = datetime.now().year
            last_patient = Patient.objects.order_by('-created_at').first()
            if last_patient and last_patient.patient_number:
                try:
                    last_num = int(last_patient.patient_number.split('-')[-1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            
            patient_number = f"EMH-PT-{year}-{new_num:04d}"
            
            # Get form data
            name = request.POST.get('name', '').strip()
            guardian_name = request.POST.get('guardian_name', '')
            gender = request.POST.get('gender', '')
            dob = request.POST.get('dob', '')
            phone = request.POST.get('phone', '')
            email = request.POST.get('email', '')
            address = request.POST.get('address', '')
            remarks = request.POST.get('remarks', '')
            allergies = request.POST.get('allergies', '')
            insurance_provider = request.POST.get('insurance_provider', '')
            insurance_id = request.POST.get('insurance_id', '')
            insurance_validity = request.POST.get('insurance_validity', '')
            national_id = request.POST.get('national_id', '')
            blood_group = request.POST.get('blood_group', '')
            marital_status = request.POST.get('marital_status', '')
            
            # Split name into first and last
            name_parts = name.split(maxsplit=1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Handle age or DOB
            if not dob:
                # Calculate DOB from age
                age_years = int(request.POST.get('age', 0))
                age_months = int(request.POST.get('age_months', 0))
                age_days = int(request.POST.get('age_days', 0))
                dob = datetime.now().date() - timedelta(days=age_years*365 + age_months*30 + age_days)
            
            # Create patient
            patient = Patient.objects.create(
                patient_number=patient_number,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                gender=gender,
                phone_number=phone,
                email=email,
                national_id_or_passport=national_id,
                next_of_kin_name=guardian_name,
                next_of_kin_phone=phone,
                next_of_kin_relationship=guardian_name,
            )
            
            messages.success(request, f'Patient {patient.full_name} registered successfully!')
            return redirect('opd:opd_home')
            
        except Exception as e:
            messages.error(request, f'Error registering patient: {str(e)}')
            return redirect('opd:opd_home')
    
    return redirect('opd:opd_home')