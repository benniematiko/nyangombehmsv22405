from django.shortcuts import render

def laboratory_home(request):   
    return render(request, 'laboratory/laboratory.html')
