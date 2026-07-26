# birthdeath/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Add this view function
@login_required
def birthdeath_home(request):
    """Main birthdeath dashboard/home page"""
    context = {
        'title': 'Birthdeath',
    }
    return render(request, 'birthdeath/birthdeath.html', context)