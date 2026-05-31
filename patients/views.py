from django.shortcuts import render

def patients_home(request):   
    return render(request, 'patients/patients.html')
