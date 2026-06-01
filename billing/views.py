from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from opd.models import PatientVisit
from .models import BillingInvoice



def billing_home(request):
    """
    Renders the central billing modules dashboard. 
    If a valid case_id is passed in the URL parameters, it loads that case's financial sheet.
    """
    case_id = request.GET.get('case_id', '').strip()
    context = {}

    if case_id:
        try:
            # 1. Attempt to locate the active patient encounter by its Case ID
            visit = PatientVisit.objects.get(case_id=case_id)
            
            # 2. Fetch the invoice linked to this visit, or automatically create one if it's their first time at billing
            invoice, created = BillingInvoice.objects.get_or_create(visit=visit)
            
            # 3. Pack everything cleanly into the context to render on the frontend page
            context['visit'] = visit
            context['invoice'] = invoice
            context['invoice_items'] = invoice.items.all()
            
            if created:
                messages.success(request, f"Initialized new billing ledger for Case: {case_id}")
            else:
                messages.success(request, f"Loaded active ledger details for Case: {case_id}")

        except PatientVisit.DoesNotExist:
            messages.error(request, f"No medical encounter record found matching Case ID: '{case_id}'")
            return redirect('billing:dashboard')

    return render(request, 'billing/billing.html', context)    

