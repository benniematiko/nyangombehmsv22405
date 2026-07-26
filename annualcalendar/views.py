# annualcalendar/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Add this view function
@login_required
def annualcalendar_home(request):
    """Main annualcalendar dashboard/home page"""
    context = {
        'title': 'Annual Calendar',
    }
    return render(request, 'annualcalendar/annualcalendar_home.html', context)