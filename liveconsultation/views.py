from django.shortcuts import render

def liveconsultation_home(request):
    return render(request, 'liveconsultation/consultation.html')

def livemeeting_home(request):
    return render(request, 'liveconsultation/meeting.html')