from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from .models import Stock, Prescription
from billing.models import BillingInvoice, BillingItem

# ==========================================
# 1. EXISTENT RENDERING DASHBOARD VIEWS
# ==========================================

def pharmacy_home(request):
    """ Central dashboard showing pending prescriptions queue """
    # Fetch active prescription orders waiting for verification   
    pending_prescriptions = Prescription.objects.filter(status='Pending').order_by('-created_at')
    context = {'pending_prescriptions': pending_prescriptions}
    return render(request, 'pharmacy/pharmacy.html', context)


def pharmacy_generate_bill_view(request):
    """ Displays details of an individual prescription handling dispatch mapping """
    case_id = request.GET.get('case_id', '').strip()
    context = {}
    
    if case_id:
        # Pull prescriptions matching a typed Case ID session
        context['prescriptions'] = Prescription.objects.filter(visit__case_id=case_id)
        context['case_id'] = case_id
        
    return render(request, 'pharmacy/pharmacygeneratebill.html', context)


def pharmacy_medicines_view(request):
    """ Inventory monitoring window listing items in stock room """
    # Query your real Stock model table rows
    medicines = Stock.objects.all().order_by('item_name')
    return render(request, 'pharmacy/pharmacymedicines.html', {'medicines': medicines})


def import_medicines(request):
    return render(request, 'pharmacy/importmedicines.html')


def add_medicines(request):
    """ For adding physical stock entries into database via UI forms """
    return render(request, 'pharmacy/addmedicines.html')



def purchase_medicines(request):
    """ Points to templates/pharmacy/purchasemedicines.html """
    # Fetch all wholesale order histories ordered by newest arrivals first
    purchases = MedicinePurchase.objects.all().order_by('-purchase_date', '-created_at')
    
    context = {
        'purchases': purchases
    }
    return render(request, 'pharmacy/purchasemedicines.html', context)


def purchase_medicines_buy(request):
    return render(request, 'pharmacy/purchasemedicinesbuy.html')


# ==========================================
# 2. FUNCTIONAL TRANSACTION TRANSACTION HANDSHAKE VIEW
# ==========================================

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
                # Grab or open up a master invoice file inside billing app matching this visit Case ID
                invoice, created = BillingInvoice.objects.get_or_create(visit=visit)
                
                # Check allocations item by item
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
                    
                    # Deduct stock ledger values
                    stock_item.quantity_in_stock -= qty_needed
                    stock_item.save()
                    
                    # Log fulfillment amounts
                    item.quantity_dispensed = qty_needed
                    item.save()
                    
                    # Forward entry directly into the Billing module invoices itemized sheet
                    BillingItem.objects.create(
                        invoice=invoice,
                        originating_module='Pharmacy',
                        item_name=stock_item.item_name,
                        quantity=qty_needed,
                        unit_price=stock_item.selling_price
                    )
                
                # Close the prescription log record session
                prescription.status = 'Dispensed'
                prescription.save()
                
                messages.success(request, f"Prescription items for Case {visit.case_id} pushed successfully to Billing Desk.")
                
        except Exception as e:
            messages.error(request, f"Database transaction processing exception context: {str(e)}")
            
    return redirect('pharmacy:pharmacy_home')