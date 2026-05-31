from django.shortcuts import render

def radiology_home(request):   
    return render(request, 'radiology/radiology.html')
