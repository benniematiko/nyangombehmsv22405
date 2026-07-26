from django.shortcuts import render

def frontcms_home(request):
    return render(request, 'frontcms/index.html')