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
    return render(request, 'ambulance/ambulance.html', context)


@login_required
def ambulancegeneratebill(request):
    """Main ambulance dashboard/home page"""
    context = {
        'title': 'Ambulance Service',
    }
    return render(request, 'ambulance/ambulancegeneratebill.html', context)
@login_required
def ambulance_list(request):
    """Main ambulance dashboard/home page"""
    context = {
        'title': 'Ambulance Service',
    }
    return render(request, 'ambulance/ambulancelist.html', context)