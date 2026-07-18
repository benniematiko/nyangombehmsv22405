from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
# Import your real models here (e.g., from .models import Appointment)

def appointments_home(request):
    """
    Renders the active scheduling log with support for search terms 
    and customizable entries per page parameters.
    """
    # Placeholder/Mock data logic (Replace with your actual ORM query)
    # appointments_list = Appointment.objects.all().order_by('-scheduled_date')
    appointments_list = [] 
    
    per_page = request.GET.get('per_page', 20)
    paginator = Paginator(appointments_list, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'appointments': page_obj,
        'total_records': paginator.count,
    }
    return render(request, 'appointments/appointments.html', context)

def book_appointment(request):
    # Process or serve standard scheduling intake forms
    return render(request, 'appointments/book_appointment.html')

def doctor_rosters(request):
    # Serve availability calendars/shifts
    return render(request, 'appointments/doctor_rosters.html')

def appointment_detail(request, appointment_id):
    # Detailed full sheet profile canvas view
    return render(request, 'appointments/appointment_detail.html', {'id': appointment_id})

def print_appointment_slip(request, appointment_id):
    # Direct PDF streaming/print layout window target view
    return render(request, 'appointments/print_slip.html', {'id': appointment_id})

def edit_appointment(request, appointment_id):
    # Entry modifier routing target logic
    return redirect('appointments:appointments_home')

def confirm_appointment(request, appointment_id):
    # Alter specific booking states directly
    return redirect('appointments:appointments_home')

def delete_appointment(request, appointment_id):
    """
    Handles secure async post requests targeting booking cancellation.
    """
    if request.method == 'POST':
        # Your ORM model deletion here
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid Request Pattern Method.'})

def appointment_modal_details(request, appointment_id):
    """
    Asynchronously queries appointment context details and structures 
    a payload mapping to the template's JSON structure.
    """
    try:
        # Replace this placeholder logic with true database queries:
        # appt_obj = get_object_or_404(Appointment, id=appointment_id)
        
        data = {
            'success': True,
            'appointment': {
                'id': appointment_id,
                'appointment_number': f"APT-{appointment_id:04d}",
                'date': "2026-06-26",
                'time_slot': "10:30 AM",
                'patient_name': "Example Patient Case",
                'patient_phone': "+254 700 000000",
                'doctor': "Dr. Jane Doe",
                'department': "Outpatient Clinic",
                'notes': "Routine general review consultation tracking follow-up.",
                'consultation_fee': 1500.00,
                'total_amount': 1500.00,
                'discount_amount': 0.00,
                'net_amount': 1500.00,
                'status': "Pending",
                'created_by': request.user.get_full_name() or request.user.username,
                'services': [
                    {
                        'category': "Consultation Clinic",
                        'name': "Specialist Consultation Fee",
                        'code': "CNS-01",
                        'price': 1500.00,
                        'quantity': 1,
                        'row_total': 1500.00
                    }
                ]
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})