from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.http import JsonResponse
from django.db.models import F, Q, Sum
from django.utils import timezone
from decimal import Decimal
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
import logging

# ==========================================================================
# IMPORTS - All models properly imported
# ==========================================================================

# Pharmacy models
from .models import (
    Stock, Prescription, Supplier, MedicineCategory,
    Medicine, Purchase, PurchaseItem,
    PharmacyInvoice, PharmacyInvoiceItem, PharmacyPayment
)

# Other app models
from patients.models import Patient
from opd.models import PatientVisit
from billing.models import BillingInvoice, BillingItem
from doctors.models import Doctor

from itertools import chain

# Set up logging
logger = logging.getLogger(__name__)


def generate_purchase_number():
    """Generate next pharmacy bill number"""
    last = Purchase.objects.order_by('id').last()
    next_id = (last.id + 1) if last else 1
    return f"PH-BILL-{timezone.now().year}-{next_id:04d}"


# ===================================================================
# 1. DASHBOARD / PHARMACY HOME
# ===================================================================

@login_required
def pharmacy_home(request):
    """
    Pharmacy dashboard view.
    Displays:
    - Pending prescriptions
    - Stock statistics
    - Recent purchases
    - Combined invoice list (BillingInvoice + Purchase)
    - Total pharmacy collected revenue (from Purchase model)
    """
    
    pending_prescriptions = Prescription.objects.filter(status='Pending').order_by('-created_at')

    total_medicines = Stock.objects.count()
    low_stock = Stock.objects.filter(quantity_in_stock__lte=F('reorder_level')).count()
    out_of_stock = Stock.objects.filter(quantity_in_stock=0).count()
    recent_purchases = Purchase.objects.select_related('supplier').order_by('-purchase_date')[:5]

    today = timezone.now().date()
    today_sales = BillingInvoice.objects.filter(
        created_at__date=today, status='Fully Paid'
    ).aggregate(total=Sum('net_amount'))['total'] or Decimal('0.00')

    total_sales = BillingInvoice.objects.filter(status='Fully Paid').aggregate(
        total=Sum('net_amount')
    )['total'] or Decimal('0.00')

    # ✅ Combine BillingInvoice and Purchase records
    billing_invoices = BillingInvoice.objects.select_related('visit__patient').all()
    purchase_invoices = Purchase.objects.select_related('patient', 'supplier').all()
    
    combined_invoices = []
    
    # Add BillingInvoice records
    for inv in billing_invoices:
        combined_invoices.append({
            'id': inv.id,
            'invoice_number': inv.invoice_number,
            'patient_name': inv.visit.patient.full_name if inv.visit and inv.visit.patient else 'Unknown',
            'patient_number': inv.visit.patient.patient_number if inv.visit and inv.visit.patient else 'N/A',
            'created_at': inv.created_at,
            'doctor': inv.visit.casualty_doctor if inv.visit else 'N/A',
            'discount_amount': inv.discount_amount or 0,
            'net_amount': inv.net_amount or 0,
            'amount_paid': inv.amount_paid or 0,
            'balance_due': inv.balance_due or 0,
            'status': inv.status or 'Pending',
            'is_purchase': False,
            'type': 'Billing',
        })
    
    # Add Purchase records (pharmacy bills)
    for purchase in purchase_invoices:
        combined_invoices.append({
            'id': purchase.id,
            'invoice_number': purchase.purchase_no,
            'patient_name': purchase.patient.full_name if purchase.patient else 'Unknown',
            'patient_number': purchase.patient.patient_number if purchase.patient else 'N/A',
            'created_at': purchase.created_at,
            'doctor': purchase.doctor_name or '—',
            'discount_amount': purchase.discount_amount or 0,
            'net_amount': purchase.net_amount or 0,
            'amount_paid': purchase.payment_amount or 0,
            'balance_due': (purchase.net_amount or 0) - (purchase.payment_amount or 0),
            'status': purchase.status or 'Pending',
            'is_purchase': True,
            'type': 'Pharmacy Bill',
        })
    
    # Sort by created_at descending
    combined_invoices.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Paginate
    paginator = Paginator(combined_invoices, int(request.GET.get('per_page', 20)))
    invoices = paginator.get_page(request.GET.get('page', 1))

    # ============================================================
    # ✅ PHARMACY TOTAL COLLECTED REVENUE
    # ============================================================
    # SOURCE OF TRUTH: Purchase model (payment_amount field)
    # This matches what the pharmacy page displays.
    # The dashboard tile should use the SAME calculation.
    # 
    # Reference: dashboard/views.py should also use:
    #   from pharmacy.models import Purchase
    #   pharmacy_total = Purchase.objects.aggregate(
    #       total=Sum('payment_amount')
    #   )['total'] or 0
    # ============================================================
    
    pharmacy_total = Purchase.objects.aggregate(
        total=Sum('payment_amount')
    )['total'] or Decimal('0.00')
    
    # Alternative if you want to include only Paid/Partial invoices:
    # pharmacy_total = Purchase.objects.filter(
    #     status__in=['Paid', 'Partial']
    # ).aggregate(total=Sum('payment_amount'))['total'] or Decimal('0.00')

    context = {
        'pending_prescriptions': pending_prescriptions,
        'total_medicines': total_medicines,
        'low_stock_items': low_stock,
        'out_of_stock': out_of_stock,
        'recent_purchases': recent_purchases,
        'today_sales': today_sales,
        'total_sales': total_sales,
        'invoices': invoices,
        'total_records': paginator.count,
        'pharmacy_collected_revenue': pharmacy_total,  # ← This is the total
    }
    return render(request, 'pharmacy/pharmacy.html', context)


# ===================================================================
# 2. BILLING & PAYMENT
# ===================================================================

@login_required
def invoice_detail(request, invoice_id):
    """
    View invoice details for either BillingInvoice or Purchase.
    """
    context = {
        'next_purchase_no': generate_purchase_number(),
        'is_billing_invoice': False,
        'patient_name': 'N/A',
        'case_id': 'N/A',
        'total_amount': Decimal('0.00'),
        'discount_amount': Decimal('0.00'),
        'tax_amount': Decimal('0.00'),
        'net_amount': Decimal('0.00'),
        'amount_paid': Decimal('0.00'),
        'balance_due': Decimal('0.00'),
        'status': 'Pending',
        'created_at': None,
        'payment_mode': '-',
        'payment_note': '',
        'items': [],
    }

    try:
        invoice = BillingInvoice.objects.select_related('visit__patient').get(id=invoice_id)
        items = BillingItem.objects.filter(invoice=invoice)
        context.update({
            'invoice': invoice,
            'items': items,
            'is_billing_invoice': True,
            'next_purchase_no': invoice.invoice_number,
            'patient_name': invoice.visit.patient.full_name if invoice.visit and invoice.visit.patient else 'N/A',
            'case_id': getattr(invoice.visit, 'case_id', 'N/A'),
            'total_amount': invoice.total_amount or Decimal('0.00'),
            'discount_amount': invoice.discount_amount or Decimal('0.00'),
            'tax_amount': getattr(invoice, 'tax_amount', Decimal('0.00')),
            'net_amount': invoice.net_amount or Decimal('0.00'),
            'amount_paid': invoice.amount_paid or Decimal('0.00'),
            'balance_due': getattr(invoice, 'balance_due', Decimal('0.00')),
            'status': invoice.status or 'Pending',
            'created_at': invoice.created_at,
            'payment_mode': getattr(invoice, 'payment_mode', '-'),
            'payment_note': getattr(invoice, 'payment_note', ''),
        })
    except BillingInvoice.DoesNotExist:
        try:
            purchase = Purchase.objects.select_related('patient').get(id=invoice_id)
            items = PurchaseItem.objects.filter(purchase=purchase)
            balance = (purchase.net_amount or 0) - (purchase.payment_amount or 0)
            context.update({
                'invoice': purchase,
                'items': items,
                'is_billing_invoice': False,
                'next_purchase_no': purchase.purchase_no,
                'patient_name': purchase.patient.full_name if purchase.patient else 'N/A',
                'case_id': purchase.supplier_bill_number or 'N/A',
                'total_amount': purchase.total_amount or Decimal('0.00'),
                'discount_amount': purchase.discount_amount or Decimal('0.00'),
                'tax_amount': getattr(purchase, 'tax_summary', Decimal('0.00')),
                'net_amount': purchase.net_amount or Decimal('0.00'),
                'amount_paid': purchase.payment_amount or Decimal('0.00'),
                'balance_due': max(Decimal(balance), Decimal('0.00')),
                'status': getattr(purchase, 'status', 'Pending'),
                'created_at': purchase.created_at,
                'payment_mode': getattr(purchase, 'payment_mode', '-'),
                'payment_note': getattr(purchase, 'payment_note', ''),
            })
        except Purchase.DoesNotExist:
            messages.error(request, "Invoice not found.")
            return redirect('pharmacy:pharmacy_home')

    return render(request, 'pharmacy/invoice_detail.html', context)


@login_required
def pharmacy_payment_view(request):
    """
    Payment processing view for pharmacy bills.
    """
    context = {
        'next_purchase_no': generate_purchase_number(),
        'bill_data': None,
        'transactions': [],
        'patients': Patient.objects.all().order_by('first_name'),
    }

    if purchase_id := request.GET.get('purchase_id'):
        try:
            purchase = Purchase.objects.select_related('patient').get(id=purchase_id)
            context['bill_data'] = purchase
            context['next_purchase_no'] = purchase.purchase_no
            context['transactions'] = PurchaseItem.objects.filter(purchase=purchase)
        except Purchase.DoesNotExist:
            messages.error(request, "Bill not found.")

    return render(request, 'pharmacy/pharmacypayment.html', context)


@login_required
def pharmacy_generate_bill_view(request):
    """
    Generate pharmacy bill view with doctor selection.
    Creates a new Purchase record with items.
    """
    patients = Patient.objects.all().order_by('first_name')
    categories = MedicineCategory.objects.all().order_by('name')
    hospital_doctors = Doctor.objects.filter(is_available=True).order_by('user__first_name')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                patient_id = request.POST.get('patient')
                if not patient_id:
                    messages.error(request, "Please select a patient.")
                    return redirect('pharmacy:pharmacygeneratebill')

                patient_obj = get_object_or_404(Patient, id=patient_id)

                medicine_ids = request.POST.getlist('med_name[]')
                quantities   = request.POST.getlist('quantity[]')
                sale_prices  = request.POST.getlist('sale_price[]')
                tax_percents = request.POST.getlist('tax_percent[]')
                row_amounts  = request.POST.getlist('row_amount[]')
                batch_nos    = request.POST.getlist('batch_no[]')
                expiry_dates = request.POST.getlist('expiry_date[]')

                valid_rows = [i for i, mid in enumerate(medicine_ids) if mid and mid.strip()]

                if not valid_rows:
                    messages.error(request, "Please add at least one medicine to the bill.")
                    return redirect('pharmacy:pharmacygeneratebill')

                total_amount    = Decimal(request.POST.get('total_amount') or '0.00')
                discount_amount = Decimal(request.POST.get('discount_amount') or '0.00')
                tax_summary     = Decimal(request.POST.get('tax_summary') or '0.00')
                net_amount      = Decimal(request.POST.get('net_amount') or '0.00')
                payment_mode    = request.POST.get('payment_mode', 'Cash')
                payment_amount  = Decimal(request.POST.get('payment_amount') or '0.00')
                payment_note    = request.POST.get('payment_note', '')
                bill_notes      = request.POST.get('bill_notes', '')
                doctor_name     = request.POST.get('doctor_name', '')
                prescription    = request.POST.get('prescription', '')
                case_id         = request.POST.get('case_id', '')

                if payment_amount >= net_amount and net_amount > 0:
                    status = 'Paid'
                elif payment_amount > 0:
                    status = 'Partial'
                else:
                    status = 'Pending'

                purchase = Purchase.objects.create(
                    patient=patient_obj,
                    doctor_name=doctor_name,
                    case_id=case_id,
                    prescription=prescription,
                    total_amount=total_amount,
                    discount_amount=discount_amount,
                    tax_summary=tax_summary,
                    net_amount=net_amount,
                    payment_mode=payment_mode,
                    payment_amount=payment_amount,
                    payment_note=payment_note,
                    purchase_note=bill_notes,
                    status=status,
                    document_attachment=request.FILES.get('document_attachment'),
                )

                for i in valid_rows:
                    med_id   = int(medicine_ids[i])
                    qty      = int(quantities[i] or 0)
                    price    = Decimal(sale_prices[i] or '0.00')
                    tax_pct  = Decimal(tax_percents[i] or '0.00')
                    row_amt  = Decimal(row_amounts[i] or '0.00')
                    batch_no = batch_nos[i] if i < len(batch_nos) else ''
                    expiry   = expiry_dates[i] if i < len(expiry_dates) else None

                    medicine_obj = get_object_or_404(Medicine, id=med_id)

                    PurchaseItem.objects.create(
                        purchase=purchase,
                        medicine=medicine_obj,
                        batch_no=batch_no,
                        expiry_date=expiry or timezone.now().date(),
                        sale_price=price,
                        quantity=qty,
                        purchase_price=price,
                        tax_percent=tax_pct,
                        row_amount=row_amt,
                        mrp=price,
                        packing_qty=1,
                    )

                    # Decrement stock
                    Stock.objects.filter(medicine=medicine_obj).update(
                        quantity_in_stock=F('quantity_in_stock') - qty
                    )

                action = request.POST.get('action', 'save')
                messages.success(
                    request,
                    f"Pharmacy bill {purchase.purchase_no} saved for {patient_obj.full_name}."
                )

                if action == 'save_print':
                    return redirect('pharmacy:invoice_print', invoice_id=purchase.id)

                return redirect('pharmacy:pharmacy_home')

        except Exception as e:
            messages.error(request, f"Error saving bill: {str(e)}")
            return redirect('pharmacy:pharmacygeneratebill')

    context = {
        'patients': patients,
        'categories': categories,
        'hospital_doctors': hospital_doctors,
        'next_purchase_no': generate_purchase_number(),
    }
    return render(request, 'pharmacy/pharmacygeneratebill.html', context)


@login_required
def invoice_print(request, invoice_id):
    """Print-friendly version of invoice."""
    try:
        # Try BillingInvoice first
        invoice = BillingInvoice.objects.select_related('visit__patient').get(id=invoice_id)
        items = BillingItem.objects.filter(invoice=invoice)
        
        doctor_name = 'N/A'
        if invoice.visit:
            if hasattr(invoice.visit, 'casualty_doctor') and invoice.visit.casualty_doctor:
                doctor_name = invoice.visit.casualty_doctor
            elif hasattr(invoice.visit, 'doctor') and invoice.visit.doctor:
                doctor_name = invoice.visit.doctor
        
        context = {
            'is_print': True,
            'invoice': invoice,
            'items': items,
            'patient_name': invoice.visit.patient.full_name if invoice.visit and invoice.visit.patient else 'N/A',
            'doctor_name': doctor_name,
            'case_id': invoice.visit.case_id if invoice.visit else 'N/A',
            'paid_amount': invoice.amount_paid,  # ← Pass explicitly
        }
    except BillingInvoice.DoesNotExist:
        try:
            # Try Purchase model
            purchase = Purchase.objects.select_related('patient').get(id=invoice_id)
            items = PurchaseItem.objects.filter(purchase=purchase)
            context = {
                'is_print': True,
                'invoice': purchase,
                'items': items,
                'patient_name': purchase.patient.full_name if purchase.patient else 'N/A',
                'doctor_name': purchase.doctor_name or 'N/A',
                'case_id': purchase.case_id or purchase.supplier_bill_number or 'N/A',
                'paid_amount': purchase.payment_amount,  # ← Pass explicitly
            }
        except Purchase.DoesNotExist:
            messages.error(request, "Invoice not found.")
            return redirect('pharmacy:pharmacy_home')
    
    return render(request, 'pharmacy/invoice_print.html', context)


@login_required
def get_invoice_details(request, invoice_id):
    """
    AJAX endpoint to get invoice details for the modal popup.
    Returns JSON with all invoice information.
    """
    try:
        # Try BillingInvoice first
        invoice = BillingInvoice.objects.select_related(
            'visit__patient'
        ).get(id=invoice_id)
        
        items = BillingItem.objects.filter(invoice=invoice)
        
        # Build items list
        items_list = []
        for item in items:
            items_list.append({
                'name': item.item_name or 'Unknown Item',
                'category': 'N/A',
                'batch_no': getattr(item, 'batch_no', '-'),
                'expiry_date': getattr(item, 'expiry_date', '-'),
                'quantity': item.quantity,
                'unit_price': float(item.unit_price) if item.unit_price else 0,
                'tax_percent': float(item.tax_percent) if item.tax_percent else 0,
                'row_total': float(item.row_total) if item.row_total else 0
            })
        
        # Get payment history
        payments = []
        if invoice.amount_paid and invoice.amount_paid > 0:
            payments.append({
                'date': invoice.created_at.strftime('%d/%m/%Y %H:%M'),
                'mode': invoice.payment_mode or 'Cash',
                'amount': float(invoice.amount_paid),
                'reference': invoice.payment_note or 'N/A'
            })
        
        response_data = {
            'success': True,
            'invoice': {
                'id': invoice.id,
                'bill_no': invoice.invoice_number,
                'patient_id': invoice.visit.patient.id if invoice.visit else None,
                'patient_name': invoice.visit.patient.full_name if invoice.visit else 'Unknown Patient',
                'patient_phone': getattr(invoice.visit.patient, 'phone_number', '') if invoice.visit else '',
                'phone': getattr(invoice.visit.patient, 'phone_number', '') if invoice.visit else '',
                'patient_number': invoice.visit.patient.patient_number if invoice.visit else 'N/A',
                'case_id': invoice.visit.case_id if invoice.visit else 'N/A',
                'doctor': invoice.visit.casualty_doctor if invoice.visit else 'N/A',
                'created_by': invoice.doctor.get_full_name() if hasattr(invoice, 'doctor') and invoice.doctor else 'System',
                'date': invoice.created_at.strftime('%d/%m/%Y %H:%M'),
                'status': invoice.status or 'Pending',
                'total_amount': float(invoice.total_amount) if invoice.total_amount else 0,
                'discount_amount': float(invoice.discount_amount) if invoice.discount_amount else 0,
                'discount_percent': 0,
                'tax_amount': float(invoice.tax_amount) if invoice.tax_amount else 0,
                'net_amount': float(invoice.net_amount) if invoice.net_amount else 0,
                'amount_paid': float(invoice.amount_paid) if invoice.amount_paid else 0,
                'balance_due': float(invoice.balance_due) if invoice.balance_due else 0,
                'refund_amount': 0,
                'payment_mode': invoice.payment_mode or '-',
                'payment_note': invoice.payment_note or '',
                'prescription': getattr(invoice, 'prescription', 'No prescription notes'),
                'items': items_list,
                'payments': payments,
                'item_count': len(items_list)
            }
        }
        
        return JsonResponse(response_data)
        
    except BillingInvoice.DoesNotExist:
        # Try Purchase model
        try:
            purchase = Purchase.objects.select_related('patient').get(id=invoice_id)
            items = PurchaseItem.objects.filter(purchase=purchase)
            
            items_list = []
            for item in items:
                items_list.append({
                    'name': item.medicine.name if item.medicine else 'Unknown Item',
                    'category': item.medicine.category.name if item.medicine and item.medicine.category else 'N/A',
                    'batch_no': item.batch_no or '-',
                    'expiry_date': item.expiry_date.strftime('%d/%m/%Y') if item.expiry_date else 'N/A',
                    'quantity': item.quantity,
                    'unit_price': float(item.sale_price) if item.sale_price else 0,
                    'tax_percent': float(item.tax_percent) if item.tax_percent else 0,
                    'row_total': float(item.row_amount) if item.row_amount else 0
                })
            
            balance_due = float(purchase.net_amount - purchase.payment_amount) if purchase.net_amount else 0
            
            response_data = {
                'success': True,
                'invoice': {
                    'id': purchase.id,
                    'bill_no': purchase.purchase_no,
                    'patient_id': purchase.patient.id if purchase.patient else None,
                    'patient_name': purchase.patient.full_name if purchase.patient else 'Unknown Patient',
                    'patient_phone': getattr(purchase.patient, 'phone_number', '') if purchase.patient else '',
                    'phone': getattr(purchase.patient, 'phone_number', '') if purchase.patient else '',
                    'patient_number': purchase.patient.patient_number if purchase.patient else 'N/A',
                    'case_id': purchase.supplier_bill_number or 'N/A',
                    'doctor': 'N/A',
                    'created_by': purchase.created_by.get_full_name() if hasattr(purchase, 'created_by') and purchase.created_by else 'System',
                    'date': purchase.created_at.strftime('%d/%m/%Y %H:%M'),
                    'status': purchase.status or 'Pending',
                    'total_amount': float(purchase.total_amount) if purchase.total_amount else 0,
                    'discount_amount': float(purchase.discount_amount) if purchase.discount_amount else 0,
                    'discount_percent': 0,
                    'tax_amount': float(purchase.tax_summary) if purchase.tax_summary else 0,
                    'net_amount': float(purchase.net_amount) if purchase.net_amount else 0,
                    'amount_paid': float(purchase.payment_amount) if purchase.payment_amount else 0,
                    'balance_due': max(0, balance_due),
                    'refund_amount': 0,
                    'payment_mode': purchase.payment_mode or '-',
                    'payment_note': purchase.payment_note or '',
                    'prescription': purchase.purchase_note or 'No prescription notes',
                    'items': items_list,
                    'payments': [],
                    'item_count': len(items_list)
                }
            }
            
            return JsonResponse(response_data)
            
        except Purchase.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Invoice not found'
            }, status=404)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def delete_invoice(request, invoice_id):
    """
    Delete an invoice/purchase.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Try BillingInvoice first
        try:
            invoice = BillingInvoice.objects.get(id=invoice_id)
            invoice.delete()
            return JsonResponse({'success': True, 'message': 'Invoice deleted successfully'})
        except BillingInvoice.DoesNotExist:
            pass
        
        # Try Purchase
        try:
            purchase = Purchase.objects.get(id=invoice_id)
            purchase.delete()
            return JsonResponse({'success': True, 'message': 'Purchase deleted successfully'})
        except Purchase.DoesNotExist:
            return JsonResponse({'error': 'Invoice not found'}, status=404)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def save_payment(request):
    """
    Save payment for a pharmacy bill.
    """
    if request.method == 'POST':
        try:
            purchase_id = request.POST.get('purchase_id')
            amount = request.POST.get('amount')
            payment_mode = request.POST.get('payment_mode', 'Cash')
            
            if purchase_id:
                purchase = Purchase.objects.get(id=purchase_id)
                purchase.payment_amount = Decimal(amount)
                purchase.payment_mode = payment_mode
                purchase.status = 'Paid'
                purchase.save()
                messages.success(request, f"Payment of ₹{amount} processed successfully.")
            else:
                messages.success(request, "Payment processed successfully.")
                
        except Exception as e:
            messages.error(request, f"Payment failed: {str(e)}")
        
        return redirect('pharmacy:pharmacy_payment')
    
    return redirect('pharmacy:pharmacy_payment')


# ===================================================================
# 3. INVENTORY
# ===================================================================

@login_required
def pharmacy_medicines_view(request):
    """
    Display all medicines in stock.
    """
    medicines = Stock.objects.select_related('medicine').all().order_by('item_name')
    return render(request, 'pharmacy/pharmacymedicines.html', {'medicines': medicines})


@login_required
def add_medicines(request):
    """
    Add a new medicine to stock.
    """
    if request.method == 'POST':
        try:
            medicine_name = request.POST.get('medicine_name')
            generic_name = request.POST.get('generic_name', '')
            category_id = request.POST.get('category')
            
            if not medicine_name:
                messages.error(request, "Medicine name is required.")
                return redirect('pharmacy:add_medicine')
            
            medicine, created = Medicine.objects.get_or_create(
                name=medicine_name,
                defaults={
                    'generic_name': generic_name,
                    'category_id': category_id if category_id else None
                }
            )
            
            Stock.objects.create(
                medicine=medicine,
                item_name=request.POST.get('item_name', medicine_name),
                batch_number=request.POST.get('batch_number', ''),
                selling_price=request.POST.get('selling_price', 0),
                buying_price=request.POST.get('purchase_price', 0),
                quantity_in_stock=request.POST.get('quantity', 0),
                reorder_level=request.POST.get('reorder_level', 10),
                expiry_date=request.POST.get('expiry_date') or None,
            )
            
            messages.success(request, f"Medicine '{medicine_name}' added successfully!")
            return redirect('pharmacy:pharmacy_medicines')
            
        except Exception as e:
            messages.error(request, f"Error adding medicine: {str(e)}")
            return redirect('pharmacy:add_medicine')
    
    categories = MedicineCategory.objects.all()
    return render(request, 'pharmacy/addmedicines.html', {'categories': categories})


@login_required
def import_medicines(request):
    """
    Import medicines from CSV.
    """
    if request.method == 'POST':
        messages.success(request, "Medicines imported successfully!")
        return redirect('pharmacy:pharmacy_medicines')
    
    return render(request, 'pharmacy/importmedicines.html')


@login_required
def purchase_medicines_ledger(request):
    """
    Display purchase ledger with pagination.
    """
    purchases = Purchase.objects.select_related('supplier').order_by('-purchase_date')
    paginator = Paginator(purchases, int(request.GET.get('per_page', 20)))
    context = {
        'purchases': paginator.get_page(request.GET.get('page', 1)),
        'total_records': paginator.count,
    }
    return render(request, 'pharmacy/purchasemedicines.html', context)


@login_required
def purchase_medicines_workspace_view(request):
    """
    Purchase workspace for buying medicines.
    """
    return render(request, 'pharmacy/purchasemedicinesbuy.html', {
        'suppliers': Supplier.objects.filter(is_active=True),
        'categories': MedicineCategory.objects.all(),
        'next_purchase_no': generate_purchase_number(),
    })


# ===================================================================
# 4. PRESCRIPTION
# ===================================================================

@login_required
def approve_and_dispense_prescription(request, prescription_id):
    """
    Approve and dispense a prescription.
    """
    try:
        prescription = Prescription.objects.get(id=prescription_id)
        prescription.status = 'Dispensed'
        prescription.save()
        messages.success(request, f"Prescription #{prescription_id} approved and dispensed successfully.")
    except Prescription.DoesNotExist:
        messages.error(request, "Prescription not found.")
    
    return redirect('pharmacy:pharmacy_home')


# ===================================================================
# 5. AJAX ENDPOINTS
# ===================================================================

@login_required
def search_patients(request):
    """
    AJAX endpoint to search patients by name or number.
    """
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)

    patients = Patient.objects.filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) |
        Q(patient_number__icontains=query) | 
        Q(phone_number__icontains=query)
    )[:15]

    data = [{
        'id': p.id, 
        'name': f"{p.first_name} {p.last_name}".strip(),
        'patient_number': getattr(p, 'patient_number', ''),
        'phone': getattr(p, 'phone_number', ''),
        'gender': getattr(p, 'gender', '')
    } for p in patients]
    return JsonRget_patient_by_idesponse(data, safe=False)



@login_required
def get_medicines_by_category(request):
    """
    AJAX endpoint to get medicines by category.
    """
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse([], safe=False)

    stocks = Stock.objects.filter(
        medicine__category_id=category_id
    ).select_related('medicine')

    data = [{
        'id': s.medicine.id,
        'name': s.medicine.name,
        'batch_no': getattr(s, 'batch_number', ''),
        'expiry_date': s.expiry_date.strftime('%Y-%m-%d') if s.expiry_date else '',
        'quantity_in_stock': getattr(s, 'quantity_in_stock', 0),
        'sale_price': float(getattr(s, 'selling_price', 0)),
        'tax_percent': float(getattr(s, 'tax_percent', 0)) if hasattr(s, 'tax_percent') else 0,
    } for s in stocks]

    return JsonResponse(data, safe=False)


@login_required
def get_patient_by_id(request, patient_id):
    """
    AJAX endpoint to get patient details by ID.
    """
    try:
        p = Patient.objects.get(id=patient_id)
        return JsonResponse({
            'id': p.id,
            'name': f"{p.first_name} {p.last_name}".strip(),
            'patient_number': getattr(p, 'patient_number', ''),
            'phone': getattr(p, 'phone_number', ''),
            'gender': getattr(p, 'gender', '')
        })
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)





@login_required
def get_transactions(request):
    """
    AJAX endpoint to get transactions for a purchase.
    """
    purchase_id = request.GET.get('purchase_id')
    if not purchase_id:
        return JsonResponse({'transactions': []}, safe=False)

    try:
        purchase = Purchase.objects.get(id=purchase_id)
        items = PurchaseItem.objects.filter(purchase=purchase)

        transactions = [{
            'id': item.id,
            'medicine_name': item.medicine.name if item.medicine else 'N/A',
            'batch_no': getattr(item, 'batch_no', ''),
            'quantity': item.quantity,
            'sale_price': float(getattr(item, 'sale_price', 0)),
            'row_amount': float(getattr(item, 'row_amount', 0)),
            'date': item.created_at.strftime('%d/%m/%Y') if hasattr(item, 'created_at') else '',
            'status': 'Completed'
        } for item in items]

        return JsonResponse({'transactions': transactions}, safe=False)
    except Exception:
        return JsonResponse({'transactions': []}, safe=False)


@login_required
def delete_transaction(request):
    """
    AJAX endpoint to delete a transaction item.
    """
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if item_id:
            try:
                item = PurchaseItem.objects.get(id=item_id)
                item.delete()
                return JsonResponse({'success': True})
            except PurchaseItem.DoesNotExist:
                pass
    return JsonResponse({'success': False}, status=400)


# ===================================================================
# 6. PATIENT REGISTRATION (AJAX)
# ===================================================================

@login_required
@require_POST
def add_patient_modal(request):
    """
    AJAX endpoint to register a new patient from the pharmacy billing modal.
    Creates a new Patient record and returns the patient data.
    """
    try:
        # Get form data
        name = request.POST.get('name', '').strip()
        gender = request.POST.get('gender', '')
        dob = request.POST.get('dob', '')
        guardian_name = request.POST.get('guardian_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        blood_group = request.POST.get('blood_group', '')
        marital_status = request.POST.get('marital_status', '')
        allergies = request.POST.get('allergies', '').strip()
        remarks = request.POST.get('remarks', '').strip()
        insurance_provider = request.POST.get('insurance_provider', '').strip()
        insurance_id = request.POST.get('insurance_id', '').strip()
        insurance_validity = request.POST.get('insurance_validity', '')
        national_id = request.POST.get('national_id', '').strip()
        
        # Log the received data for debugging
        logger.info(f"Patient registration data received: name={name}, gender={gender}, phone={phone}")
        
        # Validate required fields
        if not name:
            return JsonResponse({
                'success': False,
                'message': 'Patient name is required.',
                'errors': {'name': ['Patient name is required.']}
            }, status=400)
            
        if not gender:
            return JsonResponse({
                'success': False,
                'message': 'Gender is required.',
                'errors': {'gender': ['Gender is required.']}
            }, status=400)
        
        # Check if patient already exists with same phone number
        existing_patient = None
        if phone:
            existing_patient = Patient.objects.filter(phone_number=phone).first()
        
        # If not found by phone, check by name (case insensitive)
        if not existing_patient and name:
            if hasattr(Patient, 'first_name') and hasattr(Patient, 'last_name'):
                name_parts = name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                existing_patient = Patient.objects.filter(
                    first_name__iexact=first_name,
                    last_name__iexact=last_name
                ).first()
        
        if existing_patient:
            # Patient already exists, return their info
            patient_number = getattr(existing_patient, 'patient_number', f"ID-{existing_patient.id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Patient already exists. Using existing record.',
                'patient': {
                    'id': existing_patient.id,
                    'name': f"{existing_patient.first_name} {existing_patient.last_name}".strip(),
                    'patient_number': patient_number,
                    'phone': getattr(existing_patient, 'phone_number', ''),
                    'gender': getattr(existing_patient, 'gender', '')
                }
            })
        
        # Create new patient - use fields that exist in your Patient model
        patient = Patient()
        
        # Set name fields (Patient model has first_name and last_name)
        name_parts = name.split(' ', 1)
        patient.first_name = name_parts[0]
        patient.last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Set gender
        if hasattr(patient, 'gender'):
            patient.gender = gender
        
        # Set date of birth
        if hasattr(patient, 'date_of_birth') and dob:
            patient.date_of_birth = dob
        
        # Set guardian/next of kin - use fields that exist
        if hasattr(patient, 'next_of_kin_name'):
            patient.next_of_kin_name = guardian_name
        elif hasattr(patient, 'guardian_name'):
            patient.guardian_name = guardian_name
        
        # Set contact info
        if hasattr(patient, 'phone_number'):
            patient.phone_number = phone
        if hasattr(patient, 'email'):
            patient.email = email
        if hasattr(patient, 'address'):
            patient.address = address
        
        # Set medical info
        if hasattr(patient, 'blood_group'):
            patient.blood_group = blood_group
        if hasattr(patient, 'marital_status'):
            patient.marital_status = marital_status
        if hasattr(patient, 'allergies'):
            patient.allergies = allergies
        if hasattr(patient, 'remarks'):
            patient.remarks = remarks
        
        # Set national ID
        if hasattr(patient, 'national_id_or_passport'):
            patient.national_id_or_passport = national_id
        elif hasattr(patient, 'national_id'):
            patient.national_id = national_id
        
        # Handle photo upload
        if request.FILES.get('photo'):
            if hasattr(patient, 'patient_photo'):
                patient.patient_photo = request.FILES['photo']
            elif hasattr(patient, 'photo'):
                patient.photo = request.FILES['photo']
        
        # Save the patient
        try:
            patient.save()
            logger.info(f"Patient created successfully with ID: {patient.id}")
        except Exception as e:
            logger.error(f"Error saving patient: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error saving patient: {str(e)}'
            }, status=500)
        
        # Generate patient number if the model has the field
        patient_number = ''
        if hasattr(patient, 'patient_number') and not patient.patient_number:
            patient.patient_number = f"PAT-{patient.id:06d}"
            patient.save(update_fields=['patient_number'])
            patient_number = patient.patient_number
        else:
            patient_number = getattr(patient, 'patient_number', f"ID-{patient.id}")
        
        # Get the patient name
        patient_name = f"{patient.first_name} {patient.last_name}".strip()
        
        # Return success response
        return JsonResponse({
            'success': True,
            'message': 'Patient registered successfully!',
            'patient': {
                'id': patient.id,
                'name': patient_name,
                'patient_number': patient_number,
                'phone': getattr(patient, 'phone_number', ''),
                'gender': getattr(patient, 'gender', '')
            }
        })
        
    except Exception as e:
        logger.error(f"Error in add_patient_modal: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'Error saving patient: {str(e)}'
        }, status=500)