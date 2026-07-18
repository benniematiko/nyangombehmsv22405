from django.shortcuts import render

def ipd_home(request):   
    return render(request, 'ipd/ipd.html')
