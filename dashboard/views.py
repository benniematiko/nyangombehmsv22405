from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required  # Protects the dashboard so logged-out users can't sneak in
def home(request):
    # This renders dashboard/templates/dashboard/dashboard.html
    return render(request, 'dashboard/dashboard.html')