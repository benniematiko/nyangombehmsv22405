from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal

from .models import LaboratoryTest, LaboratoryInvoice, LaboratoryInvoiceItem, LaboratoryPayment
from patients.models import Patient
from doctors.models import Doctor


@login_required
def laboratory_home(request):
    """Laboratory dashboard"""
    tests = LaboratoryTest.objects.all().order_by('-ordered_at')
    
    # Statistics
    total_tests = tests.count()
    pending_tests = tests.filter(status='pending').count()
    completed_tests = tests.filter(status='completed').count()
    in_progress_tests = tests.filter(status='in_progress').count()
    
    # Recent tests
    recent_tests = tests[:10]
    
    # Invoices
    invoices = LaboratoryInvoice.objects.all().order_by('-issue_date')[:10]
    
    context = {
        'tests': recent_tests,
        'total_tests': total_tests,
        'pending_tests': pending_tests,
        'completed_tests': completed_tests,
        'in_progress_tests': in_progress_tests,
        'invoices': invoices,
    }
    return render(request, 'laboratory/laboratory.html', context)


@login_required
def laboratory_generate_bill_view(request):
    """Generate bill for laboratory services"""
    patients = Patient.objects.all().order_by('first_name')

    last_invoice = LaboratoryInvoice.objects.order_by('-id').first()
    next_id = (last_invoice.id + 1) if last_invoice else 1
    next_invoice_no = f"LAB-{timezone.now().year}-{next_id:04d}"

    if request.method == 'POST':
        try:
            patient_id = request.POST.get('patient')
            patient = get_object_or_404(Patient, id=patient_id)

            # ── Capture case_id and doctor_name from the form ──
            case_id = request.POST.get('case_id', '').strip()
            doctor_name = request.POST.get('doctor_name', '').strip()

            subtotal = Decimal(request.POST.get('total_amount', 0) or 0)
            discount = Decimal(request.POST.get('discount_amount', 0) or 0)
            tax = Decimal(request.POST.get('tax_summary', 0) or 0)
            total = Decimal(request.POST.get('net_amount', 0) or 0)

            invoice = LaboratoryInvoice.objects.create(
                invoice_number=request.POST.get('bill_number') or next_invoice_no,
                patient=patient,
                case_id=case_id,                # ← saved
                doctor_name=doctor_name,        # ← saved
                subtotal=subtotal,
                discount_amount=discount,
                tax_amount=tax,
                total_amount=total,
                amount_paid=Decimal(request.POST.get('payment_amount', 0) or 0),
                balance_due=total - Decimal(request.POST.get('payment_amount', 0) or 0),
                status='issued',
                notes=request.POST.get('bill_notes', ''),
                created_by=request.user
            )

            # Create invoice items from form
            test_ids = request.POST.getlist('test_name[]')
            row_amounts = request.POST.getlist('row_amount[]')
            tax_percents = request.POST.getlist('tax_percent[]')

            for i in range(len(test_ids)):
                if test_ids[i] and row_amounts[i]:
                    amount = Decimal(row_amounts[i] or 0)
                    tax_pct = Decimal(tax_percents[i] or 0)

                    test_obj = LaboratoryTest.objects.filter(id=test_ids[i]).first()
                    description = test_obj.test_name if test_obj else f"Test #{test_ids[i]}"

                    LaboratoryInvoiceItem.objects.create(
                        invoice=invoice,
                        test=test_obj,
                        description=description,
                        quantity=1,
                        unit_price=amount,
                        tax_percent=tax_pct,
                        total=amount + (amount * tax_pct / 100)
                    )

            messages.success(request, f"Invoice {invoice.invoice_number} created successfully!")

            action = request.POST.get('action', 'save')
            if action == 'save_print':
                return redirect('laboratory:invoice_detail', invoice_id=invoice.id)
            return redirect('laboratory:invoice_detail', invoice_id=invoice.id)

        except Exception as e:
            messages.error(request, f"Error generating bill: {str(e)}")
            return redirect('laboratory:laboratory_home')

    context = {
        'patients': patients,
        'next_bill_no': next_invoice_no,   # matches template variable name
    }
    return render(request, 'laboratory/laboratorygeneratebill.html', context)

@login_required
def add_test(request):
    """Add a new laboratory test"""
    if request.method == 'POST':
        try:
            test = LaboratoryTest.objects.create(
                patient_id=request.POST.get('patient'),
                doctor_id=request.POST.get('doctor') or None,
                test_name=request.POST.get('test_name'),
                test_category=request.POST.get('test_category'),
                specimen_type=request.POST.get('specimen_type'),
                notes=request.POST.get('notes'),
                ordered_by=request.user
            )
            messages.success(request, f"Test '{test.test_name}' added successfully!")
            return redirect('laboratory:laboratory_home')
        except Exception as e:
            messages.error(request, f"Error adding test: {str(e)}")
            return redirect('laboratory:laboratory_home')
    
    patients = Patient.objects.all()
    doctors = Doctor.objects.filter(is_available=True)
    context = {
        'patients': patients,
        'doctors': doctors,
    }
    return render(request, 'laboratory/add_test.html', context)


@login_required
def test_detail(request, test_id):
    """View test details"""
    test = get_object_or_404(LaboratoryTest, id=test_id)
    context = {'test': test}
    return render(request, 'laboratory/test_detail.html', context)


@login_required
def update_test_result(request, test_id):
    """Update test results"""
    test = get_object_or_404(LaboratoryTest, id=test_id)
    
    if request.method == 'POST':
        try:
            test.result = request.POST.get('result')
            test.normal_range = request.POST.get('normal_range')
            test.status = 'completed'
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
    """Create an invoice for laboratory tests"""
    test = get_object_or_404(LaboratoryTest, id=test_id)
    
    if request.method == 'POST':
        try:
            # Generate invoice number
            last_invoice = LaboratoryInvoice.objects.order_by('-id').first()
            next_id = (last_invoice.id + 1) if last_invoice else 1
            invoice_number = f"LAB-{timezone.now().year}-{next_id:04d}"
            
            # Get amounts from form
            subtotal = Decimal(request.POST.get('subtotal', 0))
            discount = Decimal(request.POST.get('discount', 0))
            tax = Decimal(request.POST.get('tax', 0))
            total = subtotal - discount + tax
            
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
            
            # Create invoice item
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
    """View invoice details"""
    invoice = get_object_or_404(LaboratoryInvoice, id=invoice_id)
    items = invoice.items.all()
    payments = invoice.payments.all()
    
    context = {
        'invoice': invoice,
        'items': items,
        'payments': payments,
    }
    return render(request, 'laboratory/invoice_detail.html', context)


@login_required
def record_payment(request, invoice_id):
    """Record a payment for an invoice"""
    invoice = get_object_or_404(LaboratoryInvoice, id=invoice_id)
    
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', 0))
            if amount <= 0:
                messages.error(request, "Amount must be greater than 0")
                return redirect('laboratory:invoice_detail', invoice_id=invoice.id)
            
            payment = LaboratoryPayment.objects.create(
                invoice=invoice,
                amount=amount,
                payment_method=request.POST.get('payment_method', 'cash'),
                reference=request.POST.get('reference', ''),
                notes=request.POST.get('notes', ''),
                received_by=request.user
            )
            
            # Update invoice
            invoice.amount_paid += amount
            invoice.balance_due = invoice.total_amount - invoice.amount_paid
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
    """Delete a test"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        test = get_object_or_404(LaboratoryTest, id=test_id)
        test_name = test.test_name
        test.delete()
        return JsonResponse({'success': True, 'message': f'Test {test_name} deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def delete_invoice(request, invoice_id):
    """Delete an invoice"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        invoice = get_object_or_404(LaboratoryInvoice, id=invoice_id)
        invoice_number = invoice.invoice_number
        invoice.delete()
        return JsonResponse({'success': True, 'message': f'Invoice {invoice_number} deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)