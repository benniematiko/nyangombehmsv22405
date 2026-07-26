# reports/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Add this view function
@login_required
def finance(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Finance',
    }
    return render(request, 'reports/finance.html', context)


def appointments(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Appointment',
    }
    return render(request, 'reports/appointments.html', context)

def opd(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'OPD',
    }
    return render(request, 'reports/opd.html', context)

def ipd(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'IPD',
    }
    return render(request, 'reports/ipd.html', context)


def pharmacy(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Pharmacy',
    }
    return render(request, 'reports/pharmacy.html', context)


def laboratory(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Laboratory',
    }
    return render(request, 'reports/laboratory.html', context)

def radiology(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Radiology',
    }
    return render(request, 'reports/radiology.html', context)


def bloodbank(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Blood Bank',
    }
    return render(request, 'reports/bloodbank.html', context)


def ambulance(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Ambulance',
    }
    return render(request, 'reports/ambulance.html', context)


def birthdeath(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'birthdeath',
    }
    return render(request, 'reports/birthdeath.html', context)


def humanresource(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Human Resource',
    }
    return render(request, 'reports/humanresource.html', context)


def insurance(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Insurance',
    }
    return render(request, 'reports/insurance.html', context)


def inventory(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Inventory',
    }
    return render(request, 'reports/inventory.html', context)

def live_consultation(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Live Consultation',
    }
    return render(request, 'reports/liveconsultation.html', context)


def log(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Log',
    }
    return render(request, 'reports/log.html', context)


def ot(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'OT',
    }
    return render(request, 'reports/ot.html', context)

def patient(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Patient',
    }
    return render(request, 'reports/patient.html', context)




def daily_transaction(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Finance',
    }
    return render(request, 'reports/daily_transaction.html', context)



def all_transaction(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Finance',
    }
    return render(request, 'reports/all_transaction.html', context)

def income_report(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Finance',
    }
    return render(request, 'reports/income_report.html', context)

def income_group(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Finance',
    }
    return render(request, 'reports/income_group.html', context)

def expense_report(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Finance',
    }
    return render(request, 'reports/expense_report.html', context)

def expense_group(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Finance',
    }
    return render(request, 'reports/expense_group.html', context)

def patient_bill(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Finance',
    }
    return render(request, 'reports/patient_bill.html', context)

def referral_report(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Finance',
    }
    return render(request, 'reports/referral_report.html', context)

def processing_transaction(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Finance',
    }
    return render(request, 'reports/processing_transaction.html', context)


def generate_financial_statement(request):
    """Main reports dashboard/home page"""
    context = {
        'title': 'Finance',
    }
    return render(request, 'reports/generate_financial_statement', context)