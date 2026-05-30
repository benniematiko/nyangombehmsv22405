from django.shortcuts import render

def pharmacy_home(request):
    # Change from 'pharmacy.html' to 'pharmacy/pharmacy.html'
    return render(request, 'pharmacy/pharmacy.html')


def pharmacy_generate_bill_view(request):
    # Points to templates/pharmacy/pharmacygeneratebill.html
    return render(request, 'pharmacy/pharmacygeneratebill.html')

def pharmacy_medicines_view(request):
    # Points to templates/pharmacy/pharmacymedicines.html
    return render(request, 'pharmacy/pharmacymedicines.html')