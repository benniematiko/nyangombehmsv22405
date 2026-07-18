from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal

from .models import LaboratoryTest, LaboratoryInvoice, LaboratoryInvoiceItem, LaboratoryPayment
from billing.models import Charge, ChargeCategory
from patients.models import Patient
from doctors.models import Doctor


from decimal import Decimal, InvalidOperation

@login_required
def laboratory_home(request):
    """Laboratory dashboard - shows invoices"""
    
    search_query = request.GET.get('search', '')
    invoices_qs = LaboratoryInvoice.objects.select_related(
        'patient', 'created_by'
    ).order_by('-issue_date')

    if search_query:
        invoices_qs = invoices_qs.filter(
            Q(invoice_number__icontains=search_query) |
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(case_id__icontains=search_query) |
            Q(doctor_name__icontains=search_query)
        )

    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(invoices_qs, per_page)
    invoices = paginator.get_page(request.GET.get('page', 1))

    context = {
        'invoices': invoices,
        'total_records': paginator.count,
        'search_query': search_query,
    }
    return render(request, 'laboratory/laboratory.html', context)




@login_required
def laboratory_generate_bill_view(request):
    """Generate bill for laboratory services"""

    patients         = Patient.objects.all().order_by('first_name')
    hospital_doctors = Doctor.objects.filter(is_available=True)

    # ── Pull test names from billing Charge catalogue ──
    lab_category = ChargeCategory.objects.filter(
        name__icontains='lab'
    ).first()

    if lab_category:
        lab_tests = Charge.objects.filter(
            category=lab_category,
            is_active=True
        ).order_by('name')
    else:
        lab_tests = Charge.objects.filter(is_active=True).order_by('name')

    # ── Next invoice number ──
    last_invoice  = LaboratoryInvoice.objects.order_by('-id').first()
    next_id       = (last_invoice.id + 1) if last_invoice else 1
    next_invoice_no = f"LAB-{timezone.now().year}-{next_id:04d}"

    if request.method == 'POST':
        try:
            patient_id  = request.POST.get('patient')
            patient     = get_object_or_404(Patient, id=patient_id)
            case_id     = request.POST.get('case_id', '').strip()
            doctor_name = request.POST.get('doctor_name', '').strip()

            subtotal = Decimal(request.POST.get('total_amount', 0) or 0)
            discount = Decimal(request.POST.get('discount_amount', 0) or 0)
            tax      = Decimal(request.POST.get('tax_summary', 0) or 0)
            total    = Decimal(request.POST.get('net_amount', 0) or 0)
            paid     = Decimal(request.POST.get('payment_amount', 0) or 0)

            invoice = LaboratoryInvoice.objects.create(
                invoice_number=request.POST.get('bill_number') or next_invoice_no,
                patient=patient,
                case_id=case_id,
                doctor_name=doctor_name,
                subtotal=subtotal,
                discount_amount=discount,
                tax_amount=tax,
                total_amount=total,
                amount_paid=paid,
                balance_due=total - paid,
                status='issued',
                notes=request.POST.get('bill_notes', ''),
                created_by=request.user
            )

            # ── Create invoice items from form ──
            test_ids     = request.POST.getlist('test_name[]')
            row_amounts  = request.POST.getlist('row_amount[]')
            tax_percents = request.POST.getlist('tax_percent[]')

            for i in range(len(test_ids)):
                if test_ids[i] and row_amounts[i]:
                    amount      = Decimal(row_amounts[i] or 0)
                    tax_pct     = Decimal(tax_percents[i] or 0)

                    charge_obj  = Charge.objects.filter(id=test_ids[i]).first()
                    description = charge_obj.name if charge_obj else f"Test #{test_ids[i]}"

                    LaboratoryInvoiceItem.objects.create(
                        invoice=invoice,
                        test=None,
                        description=description,
                        quantity=1,
                        unit_price=amount,
                        tax_percent=tax_pct,
                        total=amount + (amount * tax_pct / 100)
                    )

            messages.success(request, f"Invoice {invoice.invoice_number} created successfully!")
            
            # ── Handle action (Save or Save & Print) ──
            action = request.POST.get('action', 'save')
            if action == 'save_print':
                return redirect('laboratory:invoice_print', invoice_id=invoice.id)
            return redirect('laboratory:laboratory_home')  # Save button goes to dashboard

        except Exception as e:
            messages.error(request, f"Error generating bill: {str(e)}")
            return redirect('laboratory:laboratory_home')

    context = {
        'patients':         patients,
        'lab_tests':        lab_tests,
        'hospital_doctors': hospital_doctors,
        'next_bill_no':     next_invoice_no,
    }
    return render(request, 'laboratory/laboratorygeneratebill.html', context)





@login_required
def add_test(request):
    """Add a new laboratory test"""
    if request.method == 'POST':
        try:
            # Safely convert numbers with fallback to 0
            def safe_decimal(value, default=0):
                if not value or value.strip() == '':
                    return Decimal(default)
                try:
                    return Decimal(value)
                except (InvalidOperation, ValueError):
                    return Decimal(default)

            test = LaboratoryTest.objects.create(
                test_name=request.POST.get('test_name', '').strip(),
                test_category=request.POST.get('category_name', '').strip(),
                specimen_type=request.POST.get('test_type', '').strip(),
                notes=request.POST.get('test_parameter', '').strip(),
                
                # Safe Decimal conversion
                cost=safe_decimal(request.POST.get('standard_charge')),
                tax_percent=safe_decimal(request.POST.get('tax')),
                
                ordered_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Test "{test.test_name}" added successfully!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)






@login_required
def test_detail(request, test_id):
    test    = get_object_or_404(LaboratoryTest, id=test_id)
    context = {'test': test}
    return render(request, 'laboratory/test_detail.html', context)


@login_required
def update_test_result(request, test_id):
    test = get_object_or_404(LaboratoryTest, id=test_id)

    if request.method == 'POST':
        try:
            test.result       = request.POST.get('result')
            test.normal_range = request.POST.get('normal_range')
            test.status       = 'completed'
            test.performed_by = request.user
            test.performed_at = timezone.now()
            test.save()
            messages.success(request, "Test results updated successfully!")
            return redirect('laboratory:test_detail', test_id=test.id)
        except Exception as e:
            messages.error(request, f"Error updating results: {str(e)}")

    context = {'test': test}
    return render(request, 'laboratory/update_result.html', context)


@login_required
def create_invoice(request, test_id):
    test = get_object_or_404(LaboratoryTest, id=test_id)

    if request.method == 'POST':
        try:
            last_invoice   = LaboratoryInvoice.objects.order_by('-id').first()
            next_id        = (last_invoice.id + 1) if last_invoice else 1
            invoice_number = f"LAB-{timezone.now().year}-{next_id:04d}"

            subtotal = Decimal(request.POST.get('subtotal', 0))
            discount = Decimal(request.POST.get('discount', 0))
            tax      = Decimal(request.POST.get('tax', 0))
            total    = subtotal - discount + tax

            invoice = LaboratoryInvoice.objects.create(
                invoice_number=invoice_number,
                patient=test.patient,
                subtotal=subtotal,
                discount_amount=discount,
                tax_amount=tax,
                total_amount=total,
                balance_due=total,
                status='issued',
                notes=request.POST.get('notes', ''),
                created_by=request.user
            )

            LaboratoryInvoiceItem.objects.create(
                invoice=invoice,
                test=test,
                description=test.test_name,
                quantity=1,
                unit_price=subtotal,
                total=subtotal
            )

            messages.success(request, f"Invoice {invoice_number} created successfully!")
            return redirect('laboratory:laboratory_home')

        except Exception as e:
            messages.error(request, f"Error creating invoice: {str(e)}")

    context = {'test': test}
    return render(request, 'laboratory/create_invoice.html', context)


@login_required
def invoice_detail(request, invoice_id):
    invoice  = get_object_or_404(LaboratoryInvoice, id=invoice_id)
    items    = invoice.items.all()
    payments = invoice.payments.all()

    context = {
        'invoice':  invoice,
        'items':    items,
        'payments': payments,
    }
    return render(request, 'laboratory/invoice_detail.html', context)


@login_required
def invoice_print(request, invoice_id):
    """Print invoice view"""
    invoice = get_object_or_404(LaboratoryInvoice, id=invoice_id)
    items = invoice.items.all()
    payments = invoice.payments.all()
    
    context = {
        'invoice': invoice,
        'items': items,
        'payments': payments,
    }
    return render(request, 'laboratory/invoice_print.html', context)


@login_required
def record_payment(request, invoice_id):
    invoice = get_object_or_404(LaboratoryInvoice, id=invoice_id)

    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', 0))
            if amount <= 0:
                messages.error(request, "Amount must be greater than 0")
                return redirect('laboratory:invoice_detail', invoice_id=invoice.id)

            LaboratoryPayment.objects.create(
                invoice=invoice,
                amount=amount,
                payment_method=request.POST.get('payment_method', 'cash'),
                reference=request.POST.get('reference', ''),
                notes=request.POST.get('notes', ''),
                received_by=request.user
            )

            invoice.amount_paid += amount
            invoice.balance_due  = invoice.total_amount - invoice.amount_paid
            if invoice.balance_due <= 0:
                invoice.status = 'paid'
            invoice.save()

            messages.success(request, f"Payment of {amount} recorded successfully!")
            return redirect('laboratory:invoice_detail', invoice_id=invoice.id)

        except Exception as e:
            messages.error(request, f"Error recording payment: {str(e)}")

    context = {'invoice': invoice}
    return render(request, 'laboratory/record_payment.html', context)


@login_required
def delete_test(request, test_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        test      = get_object_or_404(LaboratoryTest, id=test_id)
        test_name = test.test_name
        test.delete()
        return JsonResponse({'success': True, 'message': f'Test {test_name} deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def delete_invoice(request, invoice_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        invoice        = get_object_or_404(LaboratoryInvoice, id=invoice_id)
        invoice_number = invoice.invoice_number
        invoice.delete()
        return JsonResponse({'success': True, 'message': f'Invoice {invoice_number} deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def search_patients(request):
    """Search patients by name or patient number (AJAX)"""
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse([], safe=False)

    patients = Patient.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(patient_number__icontains=query) |
        Q(phone_number__icontains=query)
    ).select_related()[:20]

    results = []
    for patient in patients:
        try:
            age = patient.age
        except Exception:
            age = None

        results.append({
            'id':         patient.id,
            'name':       patient.full_name,
            'opd_number': patient.patient_number,
            'gender':     patient.gender or '',
            'age':        age,
            'phone':      patient.phone_number or '',
        })

    return JsonResponse(results, safe=False)


@login_required
def add_patient_modal(request):
    """Register a new patient via AJAX modal"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        full_name = request.POST.get('name', '').strip()
        if not full_name:
            return JsonResponse({'success': False, 'error': 'Patient name is required'})

        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name  = name_parts[1] if len(name_parts) > 1 else ''

        last_patient   = Patient.objects.order_by('-id').first()
        next_id        = (last_patient.id + 1) if last_patient else 1
        patient_number = f"EMH-PT-{timezone.now().year}-{next_id:04d}"

        patient = Patient.objects.create(
            patient_number=patient_number,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=request.POST.get('dob') or None,
            gender=request.POST.get('gender', ''),
            blood_group=request.POST.get('blood_group', ''),
            marital_status=request.POST.get('marital_status', ''),
            phone_number=request.POST.get('phone', ''),
            email=request.POST.get('email', ''),
            address=request.POST.get('address', ''),
            national_id_or_passport=request.POST.get('national_id', ''),
            allergies=request.POST.get('allergies', ''),
            remarks=request.POST.get('remarks', ''),
            next_of_kin_name=request.POST.get('guardian_name', ''),
            next_of_kin_phone='',
            next_of_kin_relationship='',
            insurance_id=request.POST.get('insurance_id', ''),
            insurance_validity=request.POST.get('insurance_validity') or None,
        )

        return JsonResponse({
            'success':      True,
            'patient_id':   patient.id,
            'patient_name': patient.full_name,
            'opd_number':   patient.patient_number,
            'message':      f'Patient {patient.full_name} registered successfully!',
            'patient': {
                'id':             patient.id,
                'name':           patient.full_name,
                'patient_number': patient.patient_number,
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def laboratorytestslist(request):
    """Display list of laboratory tests and handle adding new tests"""
    
    # ── Handle POST request (form submission from modal) ──
    if request.method == 'POST':
        try:
            test_name = request.POST.get('test_name', '').strip()
            if not test_name:
                messages.error(request, "Test name is required")
                return redirect('laboratory:laboratorytestslist')
            
            # Get or create Charge Category
            category_name = request.POST.get('category_name', '').strip()
            charge_category_name = request.POST.get('charge_category', '').strip()
            
            # Create the laboratory test
            test = LaboratoryTest.objects.create(
                test_name=test_name,
                test_category=category_name or charge_category_name,  # Use whichever is filled
                specimen_type=request.POST.get('test_type', ''),
                notes=request.POST.get('method', ''),
                ordered_by=request.user,
                status='pending'  # Default status
            )
            
            # Optional: Save to Charge model as well (for billing)
            if charge_category_name:
                # Try to find or create charge category
                charge_cat, _ = ChargeCategory.objects.get_or_create(
                    name=charge_category_name,
                    defaults={'is_active': True}
                )
                
                # Create the charge
                standard_charge = request.POST.get('standard_charge', 0)
                tax_percent = request.POST.get('tax', 0)
                charge_name = request.POST.get('charge_name', test_name)
                
                if standard_charge:
                    Charge.objects.create(
                        category=charge_cat,
                        name=charge_name,
                        standard_price=standard_charge,
                        tax_percent=tax_percent or 0,
                        is_active=True
                    )
            
            messages.success(request, f"Test '{test.test_name}' added successfully!")
            return redirect('laboratory:laboratorytestslist')
            
        except Exception as e:
            messages.error(request, f"Error adding test: {str(e)}")
            return redirect('laboratory:laboratorytestslist')
    
    # ── GET request - show the test list ──
    tests = LaboratoryTest.objects.all().order_by('-ordered_at')
    
    context = {
        'tests': tests,
    }
    return render(request, 'laboratory/laboratorytestslist.html', context)


@login_required
def tests_list(request):
    """Laboratory test catalogue — lists LaboratoryTest records"""

    if request.method == 'POST':
        try:
            def safe_decimal(val, default=0):
                try:
                    return Decimal(str(val)) if val else Decimal(default)
                except Exception:
                    return Decimal(default)

            test = LaboratoryTest.objects.create(
                test_name=request.POST.get('test_name', '').strip(),
                test_category=request.POST.get('category_name', '').strip(),
                specimen_type=request.POST.get('test_type', '').strip(),
                notes=request.POST.get('method', '').strip(),
                cost=safe_decimal(request.POST.get('standard_charge')),
                tax_percent=safe_decimal(request.POST.get('tax')),
                ordered_by=request.user,
                status='pending',
            )

            # Also create a Charge in billing catalogue if charge category given
            charge_category_name = request.POST.get('charge_category', '').strip()
            charge_name = request.POST.get('charge_name', test.test_name).strip()
            if charge_category_name and test.cost:
                charge_cat, _ = ChargeCategory.objects.get_or_create(
                    name=charge_category_name,
                    defaults={'is_active': True}
                )
                Charge.objects.get_or_create(
                    category=charge_cat,
                    name=charge_name,
                    defaults={
                        'standard_price': test.cost,
                        'tax_percent': test.tax_percent,
                        'is_active': True,
                    }
                )

            messages.success(request, f"Test '{test.test_name}' added successfully!")
        except Exception as e:
            messages.error(request, f"Error saving test: {str(e)}")

        return redirect('laboratory:laboratorytestslist')

    # GET
    search_query = request.GET.get('search', '').strip()
    tests_qs = LaboratoryTest.objects.all().order_by('test_name')

    if search_query:
        tests_qs = tests_qs.filter(
            Q(test_name__icontains=search_query) |
            Q(test_category__icontains=search_query) |
            Q(specimen_type__icontains=search_query)
        )

    per_page  = int(request.GET.get('per_page', 20))
    paginator = Paginator(tests_qs, per_page)
    tests     = paginator.get_page(request.GET.get('page', 1))

    context = {
        'tests':         tests,
        'total_records': paginator.count,
        'search_query':  search_query,
    }
    return render(request, 'laboratory/laboratorytestslist.html', context)

    

@login_required
def invoice_print(request, invoice_id):
    """Print/View invoice"""
    invoice = get_object_or_404(LaboratoryInvoice, id=invoice_id)
    items = invoice.items.all()
    
    context = {
        'invoice': invoice,
        'items': items,
    }
    return render(request, 'laboratory/invoice_print.html', context)