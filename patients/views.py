from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Patient
import uuid
from datetime import date


@login_required
def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patients/list.html', {'patients': patients})


@login_required
def get_patients(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    patients = Patient.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(hospital_number__icontains=query)
    )[:10]
    
    patient_list = [{'id': str(p.id), 'name': p.full_name, 'hospital_number': p.hospital_number} for p in patients]
    return JsonResponse(patient_list, safe=False)


@login_required
def get_patient_details(request, patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
        today = date.today()
        age = today.year - patient.date_of_birth.year
        
        data = {
            'success': True,
            'patient': {
                'id': str(patient.id),
                'full_name': patient.full_name,
                'guardian_name': patient.guardian_name,
                'gender': patient.gender,
                'age': f"{age} years",
                'phone_number': patient.phone,
                'email': patient.email,
                'address': patient.address,
                'allergies': patient.allergies,
                'remarks': patient.remarks,
                'insurance': patient.insurance,
                'insurance_id': patient.insurance_id,
                'national_id': patient.national_id,
                'hospital_number': patient.hospital_number,
                'photo_url': patient.photo.url if patient.photo else '',
            }
        }
        return JsonResponse(data)
    except Patient.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Patient not found'}, status=404)


@login_required
def add_patient_ajax(request):
    if request.method == 'POST':
        full_name = request.POST.get('patient_full_name', '').strip()
        name_parts = full_name.split(maxsplit=1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        hospital_number = f"PT-{uuid.uuid4().hex[:8].upper()}"
        
        patient = Patient.objects.create(
            hospital_number=hospital_number,
            first_name=first_name,
            last_name=last_name,
            gender=request.POST.get('gender'),
            date_of_birth=request.POST.get('date_of_birth'),
            phone=request.POST.get('phone_number', ''),
            email=request.POST.get('email', ''),
            address=request.POST.get('address', ''),
            guardian_name=request.POST.get('guardian_full_name', ''),
            allergies=request.POST.get('allergies', ''),
            remarks=request.POST.get('remarks', ''),
            insurance=request.POST.get('insurance', ''),
            insurance_id=request.POST.get('insurance_id', ''),
            national_id=request.POST.get('national_id', ''),
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Patient added successfully',
            'patient': {'id': str(patient.id), 'full_name': patient.full_name}
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
