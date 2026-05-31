

from django.shortcuts import render


def billing_home(request):
   
    return render(request, 'billing/billing.html')

