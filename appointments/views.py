from django.shortcuts import render

def appointments_home(request):
    return render(request, 'appointments/appointments.html')
