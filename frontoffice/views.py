# ambulance/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Add this view function
@login_required
def frontoffice_home(request):
    """Main frontoffice dashboard/home page"""
    context = {
        'title': 'Front Office',
    }
    return render(request, 'ambulance/office_home.html', context)