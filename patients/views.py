from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Patient
import uuid
from datetime import date


@login_required
def patients_home(request):
    """Patient home/dashboard page - Main patient view"""
    patients = Patient.objects.all().order_by('first_name', 'last_name')
    total_patients = patients.count()
    return render(request, 'patients/home.html', {
        'patients': patients,
        'total_patients': total_patients
    })


@login_required
def patient_list(request):
    """Display list of all patients"""
    patients = Patient.objects.all().order_by('first_name', 'last_name')
    total_patients = patients.count()
    return render(request, 'patients/list.html', {
        'patients': patients,
        'total_patients': total_patients
    })


@login_required
def get_patients(request):
    """API endpoint for patient autocomplete"""
    try:
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse([], safe=False)
        
        patients = Patient.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(patient_number__icontains=query)  # Using patient_number instead of hospital_number
        )[:10]
        
        patient_list = []
        for p in patients:
            patient_list.append({
                'id': str(p.id),
                'name': p.full_name,
                'patient_number': p.patient_number  # Changed from hospital_number
            })
        
        return JsonResponse(patient_list, safe=False)
        
    except Exception as e:
        print(f"Error in get_patients: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_patient_details(request, patient_id):
    """Get detailed patient information"""
    try:
        patient = Patient.objects.get(id=patient_id)
        today = date.today()
        age = today.year - patient.date_of_birth.year
        
        # Adjust age if birthday hasn't occurred yet this year
        if (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day):
            age -= 1
        
        data = {
            'success': True,
            'patient': {
                'id': str(patient.id),
                'full_name': patient.full_name,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'patient_number': patient.patient_number,
                'gender': patient.gender,
                'age': f"{age} years",
                'phone_number': patient.phone_number,
                'email': patient.email or '',
                'national_id': patient.national_id_or_passport or '',
                'next_of_kin_name': patient.next_of_kin_name or '',
                'next_of_kin_phone': patient.next_of_kin_phone or '',
                'next_of_kin_relationship': patient.next_of_kin_relationship or '',
                'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
                'created_at': patient.created_at.strftime('%Y-%m-%d'),
            }
        }
        return JsonResponse(data)
    except Patient.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Patient not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def add_patient_ajax(request):
    """Add a new patient via AJAX"""
    if request.method == 'POST':
        try:
            # Get form data - match your model field names
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            
            if not first_name or not last_name:
                return JsonResponse({'success': False, 'message': 'First name and last name are required'}, status=400)
            
            # Generate unique patient number
            from datetime import datetime
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
            
            # Get date of birth
            dob = request.POST.get('date_of_birth')
            if not dob:
                return JsonResponse({'success': False, 'message': 'Date of birth is required'}, status=400)
            
            # Create patient
            patient = Patient.objects.create(
                patient_number=patient_number,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                gender=request.POST.get('gender', ''),
                phone_number=request.POST.get('phone_number', ''),
                email=request.POST.get('email', ''),
                national_id_or_passport=request.POST.get('national_id', ''),
                next_of_kin_name=request.POST.get('next_of_kin_name', ''),
                next_of_kin_phone=request.POST.get('next_of_kin_phone', ''),
                next_of_kin_relationship=request.POST.get('next_of_kin_relationship', ''),
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Patient added successfully',
                'patient': {
                    'id': str(patient.id),
                    'full_name': patient.full_name,
                    'patient_number': patient.patient_number
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@login_required
def patient_detail(request, patient_id):
    """View single patient details"""
    try:
        patient = Patient.objects.get(id=patient_id)
        return render(request, 'patients/detail.html', {'patient': patient})
    except Patient.DoesNotExist:
        return render(request, '404.html', {'message': 'Patient not found'}, status=404)