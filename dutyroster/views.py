# dutyroster/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Add this view function
@login_required
def dutyroster_home(request):
    """Main dutyroster dashboard/home page"""
    context = {
        'title': 'Dutyroster',
    }
    return render(request, 'dutyroster/dutyroster.html', context)