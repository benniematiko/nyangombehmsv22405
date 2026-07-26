from django.shortcuts import render

def messaging_home(request):
    return render(request, 'messaging/index.html')