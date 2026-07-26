# referrals/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Add this view function
@login_required
def referrals_home(request):
    """Main referrals dashboard/home page"""
    context = {
        'title': 'Referrals',
    }
    return render(request, 'referrals/referrals_home.html', context)