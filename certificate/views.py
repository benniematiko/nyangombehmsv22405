from django.shortcuts import render

def certificate_home(request):
    return render(request, 'certificate/index.html')