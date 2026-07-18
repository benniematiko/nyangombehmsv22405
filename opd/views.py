from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.template.loader import get_template
from django.utils import timezone
from patients.models import Patient
from .models import PatientVisit
from .forms import PatientVisitForm
from datetime import datetime
from doctors.models import Doctor
from billing.models import InsuranceProvider
from io import BytesIO

# Try to import xhtml2pdf, fallback to print view if not installed
try:
    from xhtml2pdf import pisa
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


# ==============================================================================
# OPD HOME — Main Billing Logs & Records Dashboard
# ==============================================================================
@login_required
def opd_home(request):
    """Renders the main OPD Billing Logs and Records Dashboard"""
    visits = PatientVisit.objects.all().select_related('patient', 'created_by').order_by('-created_at')

    search_query = request.GET.get('search', '')
    if search_query:
        visits = visits.filter(
            models.Q(case_id__icontains=search_query) |
            models.Q(patient__first_name__icontains=search_query) |
            models.Q(patient__last_name__icontains=search_query) |
            models.Q(casualty_doctor__icontains=search_query) |
            models.Q(reference__icontains=search_query)
        )

    paginator = Paginator(visits, 10)
    page = request.GET.get('page', 1)

    try:
        visits_page = paginator.page(page)
    except PageNotAnInteger:
        visits_page = paginator.page(1)
    except EmptyPage:
        visits_page = paginator.page(paginator.num_pages)

    context = {
        'visits': visits_page,
        'total_count': paginator.count,
        'search_query': search_query,
    }
    return render(request, 'opd/opd.html', context)


# ==============================================================================
# ADD PATIENT VIEW — Full-width OPD consultation & billing entry form
# ==============================================================================
@login_required
def add_patient_view(request):
    """
    Renders and processes the OPD patient consultation + billing entry form.
    """
    patients = Patient.objects.all().order_by('first_name', 'last_name')
    doctors = Doctor.objects.filter(is_available=True).select_related('user').order_by('user__first_name')
    insurance_providers = InsuranceProvider.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        # ------------------------------------------------------------------ #
        # Extract form data
        # ------------------------------------------------------------------ #
        patient_id          = request.POST.get('patient')
        symptoms_type       = request.POST.get('symptoms_type', '').strip()
        symptoms_title      = request.POST.get('symptoms_title', '').strip()
        symptoms_description= request.POST.get('symptoms_description', '').strip()
        notes               = request.POST.get('notes', '').strip()
        known_allergies     = request.POST.get('known_allergies', '').strip()
        appointment_date    = request.POST.get('appointment_date')
        casualty            = request.POST.get('casualty', 'No')
        old_patient         = request.POST.get('old_patient', 'No')
        reference           = request.POST.get('reference', '').strip()
        casualty_doctor     = request.POST.get('casualty_doctor', '').strip()
        apply_insurance     = request.POST.get('apply_insurance') == 'true'
        charge_category     = request.POST.get('charge_category', '').strip()
        charge_selection    = request.POST.get('charge_selection', '').strip()
        payment_mode        = request.POST.get('payment_mode', 'Cash')
        live_consultation   = request.POST.get('live_consultation', 'No')
        action              = request.POST.get('action', 'save')

        # Financial fields
        def safe_float(val):
            try:
                return float(val or 0)
            except (ValueError, TypeError):
                return 0.0

        standard_charge = safe_float(request.POST.get('standard_charge'))
        applied_charge  = safe_float(request.POST.get('applied_charge'))
        discount        = safe_float(request.POST.get('discount'))
        tax_total       = safe_float(request.POST.get('tax_total'))

        subtotal_base = applied_charge - discount + tax_total
        subtotal_base = max(0.0, subtotal_base)

        if payment_mode == 'Insurance Claim':
            paid_amount = 0.0
        else:
            paid_amount = subtotal_base

        # ------------------------------------------------------------------ #
        # Validation
        # ------------------------------------------------------------------ #
        errors = []
        if not patient_id:
            errors.append('Please select a patient before saving.')
        if not symptoms_type:
            errors.append('Symptoms Type is required.')
        if not symptoms_title:
            errors.append('Symptoms Title is required.')
        if not appointment_date:
            errors.append('Appointment Date is required.')

        patient = None
        if patient_id:
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                errors.append('Selected patient was not found.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'opd/addpatient.html', {
                'patients': patients,
                'doctors': doctors,
                'insurance_providers': insurance_providers,
                'hide_sidebar': True,
            })

        # ------------------------------------------------------------------ #
        # Create PatientVisit
        # ------------------------------------------------------------------ #
        try:
            visit = PatientVisit(
                patient=patient,
                symptoms_type=symptoms_type,
                symptoms_title=symptoms_title,
                symptoms_description=symptoms_description,
                notes=notes,
                known_allergies=known_allergies,
                appointment_date=appointment_date,
                casualty=casualty,
                old_patient=old_patient,
                reference=reference,
                casualty_doctor=casualty_doctor,
                apply_insurance=apply_insurance,
                charge_category=charge_category,
                charge_selection=charge_selection,
                standard_charge=standard_charge,
                applied_charge=applied_charge,
                discount=discount,
                tax_total=tax_total,
                subtotal_base=subtotal_base,
                payment_mode=payment_mode,
                paid_amount=paid_amount,
                live_consultation=live_consultation,
                created_by=request.user,
                current_stage='Triage',
            )
            visit.save()

            messages.success(request, f'Consultation saved successfully! Case ID: {visit.case_id}')

            if action == 'save_print':
                return redirect('opd:print_invoice', visit_id=visit.id)
            else:
                return redirect('opd:opd_home')

        except Exception as e:
            messages.error(request, f'Error saving consultation: {str(e)}')
            return render(request, 'opd/addpatient.html', {
                'patients': patients,
                'doctors': doctors,
                'insurance_providers': insurance_providers,
                'hide_sidebar': True,
            })

    # GET request
    return render(request, 'opd/addpatient.html', {
        'patients': patients,
        'doctors': doctors,
        'insurance_providers': insurance_providers,
        'hide_sidebar': True,
    })


# ==============================================================================
# ADD PATIENT MODAL — Async AJAX registration
# ==============================================================================
@login_required
def add_patient_modal(request):
    """Handle patient registration from modal with AJAX support"""
    if request.method == 'POST':
        try:
            # Generate patient number
            year = datetime.now().year
            last_patient = Patient.objects.order_by('-created_at').first()
            last_num = int(last_patient.patient_number.split('-')[-1]) if last_patient and last_patient.patient_number else 0
            new_num = last_num + 1
            patient_number = f"EMH-PT-{year}-{new_num:04d}"

            # Extract data
            name = request.POST.get('name', '').strip()
            name_parts = name.split(maxsplit=1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            # Insurance data
            insurance_provider_id = request.POST.get('insurance_provider')
            insurance_id = request.POST.get('insurance_id', '')
            insurance_validity = request.POST.get('insurance_validity')

            patient = Patient.objects.create(
                patient_number=patient_number,
                first_name=first_name,
                last_name=last_name,
                date_of_birth=request.POST.get('dob') or datetime.now().date(),
                gender=request.POST.get('gender', ''),
                phone_number=request.POST.get('phone', ''),
                email=request.POST.get('email', ''),
                national_id_or_passport=request.POST.get('national_id', ''),
                next_of_kin_name=request.POST.get('guardian_name', ''),
                next_of_kin_phone=request.POST.get('phone', ''),
                next_of_kin_relationship=request.POST.get('guardian_name', '') or 'Self',
                blood_group=request.POST.get('blood_group', ''),
                marital_status=request.POST.get('marital_status', ''),
                address=request.POST.get('address', ''),
                remarks=request.POST.get('remarks', ''),
                allergies=request.POST.get('allergies', ''),
                insurance_provider_id=insurance_provider_id if insurance_provider_id else None,
                insurance_id=insurance_id,
                insurance_validity=insurance_validity or None,
            )

            patient_data = {
                'success': True,
                'message': f'{patient.full_name} registered successfully!',
                'patient': {
                    'id': patient.id,
                    'name': patient.full_name,
                    'patient_number': patient.patient_number,
                }
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(patient_data)
            else:
                messages.success(request, patient_data['message'])
                return redirect('opd:opd_home')

        except Exception as e:
            error_message = f'Error registering patient: {str(e)}'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message}, status=400)
            messages.error(request, error_message)
            return redirect('opd:opd_home')

    return redirect('opd:opd_home')


# ==============================================================================
# GET PATIENT DETAILS API — For displaying patient info on selection
# ==============================================================================
@login_required
def get_patient_details_api(request, patient_id):
    """Get detailed patient information for AJAX request to display in the info panel"""
    try:
        patient = Patient.objects.get(id=patient_id)
        
        # Calculate age
        today = datetime.now().date()
        age = today.year - patient.date_of_birth.year
        if (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day):
            age -= 1
        
        # Get insurance provider name
        insurance_name = None
        if patient.insurance_provider:
            insurance_name = patient.insurance_provider.name
        
        data = {
            'success': True,
            'patient': {
                'id': patient.id,
                'full_name': patient.full_name,
                'patient_number': patient.patient_number,
                'guardian_name': patient.next_of_kin_name or 'N/A',
                'gender': patient.gender or 'N/A',
                'age': age,
                'blood_group': patient.blood_group or 'N/A',
                'marital_status': patient.marital_status or 'N/A',
                'phone_number': patient.phone_number or 'N/A',
                'email': patient.email or 'N/A',
                'address': patient.address or 'N/A',
                'allergies': patient.allergies or 'None reported',
                'remarks': patient.remarks or 'N/A',
                'insurance_provider': insurance_name or 'None',
                'insurance_id': patient.insurance_id or '',
                'national_id': patient.national_id_or_passport or 'N/A',
                'patient_photo': patient.patient_photo.url if patient.patient_photo else None,
            }
        }
        return JsonResponse(data)
        
    except Patient.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Patient not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==============================================================================
# PDF GENERATION HELPER FUNCTION
# ==============================================================================
def render_to_pdf(template_src, context_dict={}):
    """Convert HTML template to PDF using xhtml2pdf"""
    if not PDF_SUPPORT:
        return None
    
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


# ==============================================================================
# DOWNLOAD PDF INVOICE — Generate and download PDF
# ==============================================================================
@login_required
def download_pdf_invoice(request, visit_id):
    """Generate and download PDF invoice for a consultation"""
    visit = get_object_or_404(PatientVisit, id=visit_id)
    
    # Calculate age
    today = datetime.now().date()
    age = today.year - visit.patient.date_of_birth.year
    if (today.month, today.day) < (visit.patient.date_of_birth.month, visit.patient.date_of_birth.day):
        age -= 1
    
    # Get insurance provider name
    insurance_name = None
    if visit.patient.insurance_provider:
        insurance_name = visit.patient.insurance_provider.name
    
    context = {
        'visit': visit,
        'patient': visit.patient,
        'age': age,
        'insurance_name': insurance_name,
        'generated_date': timezone.now(),
        'hospital_name': 'Eagles Mission Hospital',
        'hospital_address': 'Nairobi, Kenya',
        'hospital_phone': '+254 700 000 000',
        'hospital_email': 'info@eagleshospital.co.ke',
    }
    
    # Check if PDF support is available
    if not PDF_SUPPORT:
        messages.warning(request, 'PDF library not installed. Using print view instead.')
        return render(request, 'opd/print_invoice.html', context)
    
    pdf = render_to_pdf('opd/pdf_invoice.html', context)
    
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Invoice_{visit.case_id}_{visit.patient.patient_number}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    messages.error(request, 'Error generating PDF. Please try again.')
    return redirect('opd:opd_home')


# ==============================================================================
# PRINT INVOICE — Print-friendly HTML version
# ==============================================================================
@login_required
def print_invoice(request, visit_id):
    """Print OPD Consultation Invoice (print-friendly HTML)"""
    visit = get_object_or_404(PatientVisit, id=visit_id)
    
    # Calculate age
    today = datetime.now().date()
    age = today.year - visit.patient.date_of_birth.year
    if (today.month, today.day) < (visit.patient.date_of_birth.month, visit.patient.date_of_birth.day):
        age -= 1
    
    # Get insurance provider name
    insurance_name = None
    if visit.patient.insurance_provider:
        insurance_name = visit.patient.insurance_provider.name
    
    context = {
        'visit': visit,
        'patient': visit.patient,
        'age': age,
        'insurance_name': insurance_name,
        'generated_date': timezone.now(),
        'hospital_name': 'Eagles Mission Hospital',
        'hospital_address': 'Nairobi, Kenya',
        'hospital_phone': '+254 700 000 000',
        'hospital_email': 'info@eagleshospital.co.ke',
    }
    return render(request, 'opd/print_invoice.html', context)


# ==============================================================================
# GET VISIT DETAILS — AJAX endpoint
# ==============================================================================
@login_required
def get_visit_details(request, visit_id):
    """Get visit details for AJAX requests"""
    visit = get_object_or_404(PatientVisit, id=visit_id)
    data = {
        'id': visit.id,
        'case_id': visit.case_id,
        'patient_name': visit.patient.full_name,
        'appointment_date': visit.appointment_date.strftime('%Y-%m-%d %H:%M'),
        'casualty_doctor': visit.casualty_doctor or '-',
        'reference': visit.reference or '-',
        'symptoms': f"{visit.symptoms_type or ''} - {visit.symptoms_title or ''}" if visit.symptoms_type else '-',
        'total_amount': str(visit.subtotal_base),
        'payment_mode': visit.payment_mode,
        'status': visit.live_consultation,
        'temperature': str(visit.temperature) if visit.temperature else '-',
        'bp': f"{visit.bp_systolic}/{visit.bp_diastolic}" if visit.bp_systolic else '-',
        'weight': str(visit.weight) if visit.weight else '-',
    }
    return JsonResponse(data)


# ==============================================================================
# GENERATE CONSULTATION — Backward compatibility
# ==============================================================================
@login_required
def generate_consultation(request):
    """Backward compatibility for generate.html"""
    patients = Patient.objects.all().order_by('first_name', 'last_name')
    doctors = Doctor.objects.filter(is_available=True).select_related('user')
    return render(request, 'opd/generate.html', {
        'patients': patients,
        'doctors': doctors,
        'hide_sidebar': True,
    })


# ==============================================================================
# DELETE VISIT — Remove consultation record
# ==============================================================================
@login_required
def delete_visit(request, visit_id):
    """Delete an OPD consultation record"""
    if request.method == 'POST':
        visit = get_object_or_404(PatientVisit, id=visit_id)
        visit.delete()
        messages.success(request, 'Consultation record deleted successfully!')
        return redirect('opd:opd_home')
    return redirect('opd:opd_home')



    # added views for actions

    # ==============================================================================
# ADD PRESCRIPTION — Redirects to pharmacy bill generation with visit context
# ==============================================================================
# ==============================================================================
# ADD PRESCRIPTION — Render prescription form within OPD app
# ==============================================================================
@login_required
def add_prescription(request, visit_id):
    """Render prescription form for a specific OPD visit"""
    visit = get_object_or_404(PatientVisit, id=visit_id)
    
    # Get the patient
    patient = visit.patient
    
    # Calculate age
    from datetime import datetime
    today = datetime.now().date()
    age = today.year - patient.date_of_birth.year
    if (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day):
        age -= 1
    
    context = {
        'visit': visit,
        'patient': patient,
        'age': age,
        'case_id': visit.case_id,
    }
    
    return render(request, 'opd/addprescription.html', context)


# ==============================================================================
# SAVE PRESCRIPTION — Save prescription from OPD prescription form
# ==============================================================================
@login_required
def save_prescription(request, visit_id):
    """Save prescription from the OPD prescription form"""
    visit = get_object_or_404(PatientVisit, id=visit_id)
    
    if request.method == 'POST':
        # Get form data
        drug_name = request.POST.get('drug_name', '').strip()
        dosage = request.POST.get('dosage', '').strip()
        frequency = request.POST.get('frequency', '').strip()
        duration = request.POST.get('duration', '').strip()
        instructions = request.POST.get('instructions', '').strip()
        clinical_notes = request.POST.get('clinical_notes', '').strip()
        
        # Validate
        if not drug_name or not dosage or not frequency:
            messages.error(request, 'Please fill in all required fields: Drug Name, Dosage, and Frequency.')
            return redirect('opd:add_prescription', visit_id=visit_id)
        
        # Build prescription text
        from django.utils import timezone
        prescription_text = f"""
=== PRESCRIPTION ===
Patient: {visit.patient.full_name}
Patient ID: {visit.patient.patient_number}
Case ID: {visit.case_id}
Date: {timezone.now().strftime('%Y-%m-%d %H:%M')}
Prescribed by: {request.user.get_full_name() or request.user.username}

Medication:
  Drug: {drug_name}
  Dosage: {dosage}
  Frequency: {frequency}
  Duration: {duration if duration else 'As prescribed'}

Special Instructions:
{instructions if instructions else 'None'}

Clinical Notes:
{clinical_notes if clinical_notes else 'None'}
"""
        
        # Save to visit notes
        if visit.notes:
            visit.notes = f"{visit.notes}\n\n{prescription_text}"
        else:
            visit.notes = prescription_text
        
        visit.save(update_fields=['notes'])
        
        messages.success(request, f'Prescription for {drug_name} saved successfully!')
        return redirect('opd:opd_home')
    
    return redirect('opd:add_prescription', visit_id=visit_id)

# ==============================================================================
# MANUAL PRESCRIPTION — Simple notes form saved to PatientVisit.notes
# ==============================================================================
@login_required
def manual_prescription(request, visit_id):
    """Save a manual prescription note to the visit record"""
    visit = get_object_or_404(PatientVisit, id=visit_id)

    if request.method == 'POST':
        prescription_notes = request.POST.get('prescription_notes', '').strip()
        if prescription_notes:
            visit.notes = prescription_notes
            visit.save(update_fields=['notes'])
            return JsonResponse({'success': True, 'message': 'Prescription saved successfully.'})
        return JsonResponse({'success': False, 'message': 'Prescription notes cannot be empty.'}, status=400)

    # GET — return current notes for the modal
    return JsonResponse({
        'success': True,
        'visit_id': visit.id,
        'case_id': visit.case_id,
        'patient_name': visit.patient.full_name,
        'notes': visit.notes or '',
    })


# ==============================================================================
# MOVE TO IPD — Updates visit stage to signal IPD admission
# ==============================================================================
@login_required
def move_to_ipd(request, visit_id):
    """Mark OPD visit as transferred to IPD"""
    visit = get_object_or_404(PatientVisit, id=visit_id)

    if request.method == 'POST':
        visit.current_stage = 'Discharged'  # OPD stage ends
        visit.save(update_fields=['current_stage'])
        messages.success(
            request,
            f'Patient {visit.patient.full_name} (Case: {visit.case_id}) transferred to IPD successfully.'
        )
        return JsonResponse({'success': True, 'message': 'Patient transferred to IPD.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)