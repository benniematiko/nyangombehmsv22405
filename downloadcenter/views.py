from django.shortcuts import render

def downloadcenter_home(request):
    return render(request, 'downloadcenter/index.html')