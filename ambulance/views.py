# ambulance/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Add this view function
@login_required
def ambulance_home(request):
    """Main ambulance dashboard/home page"""
    context = {
        'title': 'Ambulance Service',
    }
    return render(request, 'ambulance/ambulance_home.html', context)