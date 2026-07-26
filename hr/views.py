# hr/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Add this view function
@login_required
def hr_home(request):
    """Main hr dashboard/home page"""
    context = {
        'title': 'hr',
    }
    return render(request, 'hr/hr.html', context)