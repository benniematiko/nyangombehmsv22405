from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

def radiology_home(request):
    # Dummy context to prevent template variable crashes for the table
    context = {
        'invoices': [], # Add mock data here if you want to test the table loop
        'total_records': 0
    }
    return render(request, 'radiology/radiology.html', context)

def generate_bill_view(request):
    # Temporary placeholder
    return render(request, 'radiology/radiology.html') 

def investigations_view(request):
    # Temporary placeholder
    return render(request, 'radiology/radiology.html')

def invoice_details(request, invoice_id):
    # This feeds your modal's JavaScript AJAX fetch request
    return JsonResponse({'success': True, 'invoice': {}})

def invoice_delete(request, invoice_id):
    if request.method == 'POST':
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid method'})