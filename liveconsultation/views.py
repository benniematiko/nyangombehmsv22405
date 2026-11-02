from django.shortcuts import render

def liveconsultation_home(request):
    return render(request, 'liveconsultation/liveconsultation.html')

def livemeeting_home(request):
    return render(request, 'liveconsultation/livemeeting.html')