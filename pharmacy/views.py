from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.db.models import F
from django.utils import timezone
from decimal import Decimal

# Central Application Model Registries
from .models import (
    Stock, 
    Prescription,     
    Supplier, 
    MedicineCategory, 
    Medicine, 
    Purchase, 
    PurchaseItem
)
from billing.models import BillingInvoice, BillingItem

# =========================================================================
# 1. CORE PHARMACY DASHBOARDS & MANAGEMENT VIEWS
# =========================================================================

@login_required
def pharmacy_home(request):
    """ Central dashboard showing pending prescriptions queue & handling filters """
    pending_prescriptions = Prescription.objects.filter(status='Pending').order_by('-created_at')
    
    # Hydrates the structural category selection layout in pharmacy.html
    medicine_categories = MedicineCategory.objects.all().order_by('name')
    
    context = {
        'pending_prescriptions': pending_prescriptions,
        'medicine_categories': medicine_categories,
        'total_records': pending_prescriptions.count()
    }
    return render(request, 'pharmacy/pharmacy.html', context)


@login_required
def pharmacy_generate_bill_view(request):
    """ Displays details of an individual prescription handling dispatch mapping """
    case_id = request.GET.get('case_id', '').strip()
    context = {}
    
    if case_id:
        context['prescriptions'] = Prescription.objects.filter(visit__case_id=case_id)
        context['case_id'] = case_id
        
    return render(request, 'pharmacy/pharmacygeneratebill.html', context)


@login_required
def pharmacy_medicines_view(request):
    """ Inventory monitoring window listing items in stock room """
    medicines = Stock.objects.all().order_by('item_name')
    return render(request, 'pharmacy/pharmacymedicines.html', {'medicines': medicines})


@login_required
def import_medicines(request):
    """ Landing panel matching background CSV/Excel batch imports """
    return render(request, 'pharmacy/importmedicines.html')


@login_required
def add_medicines(request):
    """ For adding physical stock entries manually into database registry """
    return render(request, 'pharmacy/addmedicines.html')


@login_required
def purchase_medicines_ledger(request):
    """ Displays wholesale tracking ledger records histories """
    purchases = Purchase.objects.select_related('supplier').all().order_by('-purchase_date', '-id')
    context = {'purchases': purchases}
    return render(request, 'pharmacy/purchasemedicines.html', context)


# =========================================================================
# 2. TRANSACTIONAL DISPENSING ACTIONS HANDLER
# =========================================================================

@login_required
def approve_and_dispense_prescription(request, prescription_id):
    """
    POST action processor: Validates stock level requirements, 
    decrements inventory numbers, and forwards items straight to billing.
    """
    if request.method == 'POST':
        prescription = get_object_or_404(Prescription, id=prescription_id, status='Pending')
        visit = prescription.visit
        
        try:
            with transaction.atomic():
                # Initialize or track central patient financial record wrapper
                invoice, created = BillingInvoice.objects.get_or_create(visit=visit)
                
                for item in prescription.items.all():
                    stock_item = item.medicine  
                    qty_needed = item.quantity_prescribed
                    
                    if stock_item.quantity_in_stock < qty_needed:
                        messages.error(
                            request, 
                            f"Insufficient Stock: '{stock_item.item_name}' can't fill order. "
                            f"Needed: {qty_needed}, Available: {stock_item.quantity_in_stock}."
                        )
                        return redirect('pharmacy:pharmacy_home')
                    
                    # Decrement active pharmacy stock levels safely
                    stock_item.quantity_in_stock -= qty_needed
                    stock_item.save()
                    
                    item.quantity_dispensed = qty_needed
                    item.save()

                    # Create line-item entry inside central patient ledger
                    BillingItem.objects.create(
                        invoice=invoice,
                        originating_module='Pharmacy',
                        item_name=stock_item.item_name,
                        quantity=qty_needed,
                        unit_price=stock_item.selling_price,
                        row_total=stock_item.selling_price * qty_needed,
                        tax_percent=Decimal('0.00')
                    )
                
                # Turn status index away from pending pool
                prescription.status = 'Dispensed'
                prescription.save()
                
                messages.success(request, f"Prescription items for Case {visit.case_id} pushed successfully to Billing Desk.")
                
        except Exception as e:
            messages.error(request, f"Database transaction processing exception context: {str(e)}")
            
    return redirect('pharmacy:pharmacy_home')


# =========================================================================
# 3. UNIFIED INTERACTIVE PROCUREMENT WORKSPACE (FBV)
# =========================================================================

@login_required
def purchase_medicines_workspace_view(request):
    """
    Handles rendering the dynamic multi-row purchasing form workspace (GET)
    and committing vendor invoice matrix arrays straight to stock shelf records (POST).
    """
    if request.method == 'POST':
        medicine_ids = request.POST.getlist('med_name[]')
        batch_numbers = request.POST.getlist('batch_no[]')
        expiry_dates = request.POST.getlist('expiry_date[]')
        mrps = request.POST.getlist('mrp[]')
        batch_amounts = request.POST.getlist('batch_amount[]')
        sale_prices = request.POST.getlist('sale_price[]')
        packing_qtys = request.POST.getlist('packing_qty[]')
        quantities = request.POST.getlist('quantity[]')
        purchase_prices = request.POST.getlist('purchase_price[]')
        tax_percents = request.POST.getlist('tax_percent[]')
        row_amounts = request.POST.getlist('row_amount[]')

        if not medicine_ids or medicine_ids == [''] or medicine_ids == [None]:
            messages.error(request, "Cannot submit an empty purchase ledger row entry.")
            return redirect('pharmacy:purchasemedicinesbuy')

        try:
            with transaction.atomic():
                supplier_id = request.POST.get('supplier')
                if not supplier_id:
                    messages.error(request, "Please select a valid supplier.")
                    return redirect('pharmacy:purchasemedicinesbuy')
                    
                supplier_obj = get_object_or_404(Supplier, id=supplier_id)
                
                # Initialize parent procurement matrix transaction receipt header
                purchase = Purchase.objects.create(
                    supplier=supplier_obj,
                    purchase_date=timezone.now(),
                    supplier_bill_number=request.POST.get('supplier_bill_number', '').strip(), 
                    total_amount=Decimal(request.POST.get('total_amount') or '0.00'),
                    discount_amount=Decimal(request.POST.get('discount_amount') or '0.00'),
                    tax_summary=Decimal(request.POST.get('tax_summary') or '0.00'),
                    net_amount=Decimal(request.POST.get('net_amount') or '0.00'),
                    payment_mode=request.POST.get('payment_mode', 'Cash'),
                    payment_amount=Decimal(request.POST.get('payment_amount') or '0.00'),
                    payment_note=request.POST.get('payment_note', ''),
                    purchase_note=request.POST.get('purchase_note', ''),
                    document_attachment=request.FILES.get('document_attachment')
                )

                # Process transactional structural array sets line by line
                for i in range(len(medicine_ids)):
                    if not medicine_ids[i]: 
                        continue
                        
                    med_id = int(medicine_ids[i])
                    qty_added = int(quantities[i] or 0)
                    batch_num = batch_numbers[i].strip()
                    
                    medicine_obj = Medicine.objects.get(id=med_id)
                    b_amt = batch_amounts[i] if (i < len(batch_amounts) and batch_amounts[i] != '') else None
                    
                    PurchaseItem.objects.create(
                        purchase=purchase,
                        medicine=medicine_obj,
                        batch_no=batch_num,
                        expiry_date=expiry_dates[i],
                        mrp=Decimal(mrps[i] or '0.00'),
                        batch_amount=Decimal(b_amt) if b_amt else None,
                        sale_price=Decimal(sale_prices[i] or '0.00'),
                        packing_qty=int(packing_qtys[i] or 1),
                        quantity=qty_added,
                        purchase_price=Decimal(purchase_prices[i] or '0.00'),
                        tax_percent=Decimal(tax_percents[i] or '0.00'),
                        row_amount=Decimal(row_amounts[i] or '0.00')
                    )

                    # Hydrate active pharmacy core stock records
                    stock_record, created = Stock.objects.get_or_create(
                        item_name=medicine_obj.name,
                        defaults={
                            'generic_name': medicine_obj.category.name if medicine_obj.category else "General",
                            'batch_number': batch_num,
                            'quantity_in_stock': qty_added,
                            'buying_price': Decimal(purchase_prices[i] or '0.00'),
                            'selling_price': Decimal(sale_prices[i] or '0.00'),
                            'expiry_date': expiry_dates[i]
                        }
                    )

                    if not created:
                        stock_record.batch_number = batch_num
                        stock_record.buying_price = Decimal(purchase_prices[i] or '0.00')
                        stock_record.selling_price = Decimal(sale_prices[i] or '0.00')
                        stock_record.expiry_date = expiry_dates[i]
                        stock_record.quantity_in_stock = F('quantity_in_stock') + qty_added
                        stock_record.save()
                        # Syncs object instance values straight out of db data pools immediately
                        stock_record.refresh_from_db()

                messages.success(request, "Purchase Voucher recorded successfully!")
                return redirect('pharmacy:purchasemedicines')

        except Exception as e:
            messages.error(request, f"Procurement Processing Error: {str(e)}")
            return redirect('pharmacy:purchasemedicinesbuy')

    # --- GET Request Workflow ---
    suppliers = Supplier.objects.filter(is_active=True).order_by('name')
    categories = MedicineCategory.objects.all().order_by('name')
    
    last_purchase = Purchase.objects.all().order_by('id').last()
    next_id = (last_purchase.id + 1) if last_purchase else 1
    predicted_bill_no = f"EMP-PURC-{timezone.now().year}-{next_id:04d}"
    
    context = {
        'suppliers': suppliers,
        'categories': categories,
        'next_purchase_no': predicted_bill_no,
    }
    return render(request, 'pharmacy/purchasemedicinesbuy.html', context)

# =========================================================================
# 4. JSON CASCADING DISPATCH ENDPOINTS (API LAYER)
# =========================================================================

def get_medicines_by_category(request):
    """ Asynchronously loads medicines filtered by target primary Category id """
    category_id = request.GET.get('category_id')
    medicines = Medicine.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(medicines), safe=False)