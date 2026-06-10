from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from pharmacy.models import Prescription
# ❌ Removed global billing model import to fix tracking error
from django.db.models import Sum, F, Q, ExpressionWrapper, DecimalField

@login_required
def home(request):
    # Inline imports to break circular dependencies
    from billing.models import BillingItem
    
    # Run a unified database aggregation pass for all hospital modules
    department_totals = BillingItem.objects.aggregate(
        opd=Sum('row_total', filter=Q(originating_module='OPD')),
        laboratory=Sum('row_total', filter=Q(originating_module='Laboratory')),
        radiology=Sum('row_total', filter=Q(originating_module='Radiology')),
        blood_bank=Sum('row_total', filter=Q(originating_module='Blood Bank')),
        pharmacy=Sum('row_total', filter=Q(originating_module='Pharmacy')),
        # If appointment has separate items in BillingItem:
        appointment=Sum('row_total', filter=Q(originating_module='Appointment')),
    )

    # Pack values cleanly into context with a fallback default of 0.00
    context = {
        'opd_revenue': department_totals['opd'] or 0.00,
        'laboratory_revenue': department_totals['laboratory'] or 0.00,
        'radiology_revenue': department_totals['radiology'] or 0.00,
        'blood_bank_revenue': department_totals['blood_bank'] or 0.00,
        'pharmacy_collected_revenue': department_totals['pharmacy'] or 0.00,
        'appointment_revenue': department_totals['appointment'] or 0.00,
        
        # Placeholders for fields that cross-reference external tables (like expenses or IPD)
        'ipd_revenue': 0.00, 
        'ambulance_revenue': 0.00,
        'general_revenue': 0.00,
        'expenses_outflow': 0.00,
    }
    
    return render(request, 'dashboard/dashboard.html', context)












