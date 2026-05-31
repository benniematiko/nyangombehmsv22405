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


def import_medicines(request):
    return render(request, 'pharmacy/importmedicines.html')

def add_medicines(request):
    return render(request, 'pharmacy/addmedicines.html')

def purchase_medicines(request):
    return render(request, 'pharmacy/purchasemedicines.html')



def purchase_medicines_buy(request):
    return render(request, 'pharmacy/purchasemedicinesbuy.html')