from django.shortcuts import render

def laboratory_home(request):
    # Change from 'pharmacy.html' to 'pharmacy/pharmacy.html'
    return render(request, 'laboratory/laboratory.html')
