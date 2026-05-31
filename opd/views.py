from django.shortcuts import render


def opd_home(request):
   
    return render(request, 'opd/opd.html')

