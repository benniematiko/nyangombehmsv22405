from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ChargeCategory, Charge


# ==============================================================================
# BILLING HOME — Main billing dashboard
# ==============================================================================
@login_required
def billing_home(request):
    """Main billing dashboard view"""
    return render(request, 'billing/billing.html')


# ==============================================================================
# CHARGE CATALOGUE API — Powers cascading dropdowns on addpatient.html
# ==============================================================================

@login_required
def get_charge_categories(request):
    """
    Returns all active charge categories as JSON.
    GET /billing/api/charge-categories/
    Response: [{"id": 1, "name": "Consultation"}, ...]
    """
    categories = ChargeCategory.objects.filter(is_active=True).values('id', 'name')
    return JsonResponse(list(categories), safe=False)


@login_required
def get_charges_by_category(request):
    """
    Returns all active charges for a given category as JSON.
    GET /billing/api/charges/?category_id=3
    Response: [{"id": 7, "name": "General Consultation", "standard_price": "500.00", "tax_percent": "0.00"}, ...]
    """
    category_id = request.GET.get('category_id')

    if not category_id:
        return JsonResponse({'error': 'category_id parameter is required'}, status=400)

    try:
        category_id = int(category_id)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid category_id'}, status=400)

    charges = Charge.objects.filter(
        category_id=category_id,
        is_active=True
    ).values('id', 'name', 'standard_price', 'tax_percent')

    return JsonResponse(list(charges), safe=False)