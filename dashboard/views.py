from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from finance.models import FinanceTransaction
from pharmacy.models import Purchase
from billing.models import BillingItem
from opd.models import PatientVisit
from patients.models import Patient
from laboratory.models import LaboratoryInvoice

# Safe imports for modules not yet fully built
try:
    from appointments.models import Appointment
except Exception:
    Appointment = None

try:
    from ipd.models import IPDPatient
except Exception:
    IPDPatient = None


@login_required
def home(request):

    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    # ── OPD Revenue (from PatientVisit.paid_amount) ──
    opd_revenue = PatientVisit.objects.aggregate(
        total=Sum('paid_amount')
    )['total'] or Decimal('0.00')

    # ── Pharmacy Revenue (from Purchase.payment_amount) ──
    pharmacy_revenue = Purchase.objects.aggregate(
        total=Sum('payment_amount')
    )['total'] or Decimal('0.00')

    # ── Laboratory Revenue (from LaboratoryInvoice.amount_paid) ──
    laboratory_revenue = LaboratoryInvoice.objects.aggregate(
        total=Sum('amount_paid')
    )['total'] or Decimal('0.00')

    # ── Other department revenue from BillingItem ──
    billing_totals = BillingItem.objects.aggregate(
        radiology=Sum('row_total', filter=Q(originating_module='Radiology')),
        blood_bank=Sum('row_total', filter=Q(originating_module='Blood Bank')),
        ipd=Sum('row_total', filter=Q(originating_module='IPD')),
        ambulance=Sum('row_total', filter=Q(originating_module='Ambulance')),
    )

    # ── Finance Summary (from FinanceTransaction) ──
    total_income = FinanceTransaction.objects.filter(
        transaction_type='Income',
        status='Completed'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    total_expenses = FinanceTransaction.objects.filter(
        transaction_type='Expense',
        status='Completed'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    monthly_income = FinanceTransaction.objects.filter(
        transaction_type='Income',
        status='Completed',
        payment_date__gte=start_of_month
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    monthly_expenses = FinanceTransaction.objects.filter(
        transaction_type='Expense',
        status='Completed',
        payment_date__gte=start_of_month
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    today_income = FinanceTransaction.objects.filter(
        transaction_type='Income',
        status='Completed',
        payment_date=today
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    today_expenses = FinanceTransaction.objects.filter(
        transaction_type='Expense',
        status='Completed',
        payment_date=today
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    net_profit = total_income - total_expenses
    monthly_profit = monthly_income - monthly_expenses

    # ── Patient Statistics ──
    total_patients = Patient.objects.count()
    new_patients_today = Patient.objects.filter(created_at__date=today).count()
    total_visits = PatientVisit.objects.count()
    visits_today = PatientVisit.objects.filter(created_at__date=today).count()

    # ── Appointments (safe — table may not exist yet) ──
    today_appointments = 0
    pending_appointments = 0
    if Appointment:
        try:
            today_appointments = Appointment.objects.filter(
                appointment_date__date=today
            ).count()
            pending_appointments = Appointment.objects.filter(
                status='scheduled'
            ).count()
        except Exception:
            pass

    # ── Pharmacy counts ──
    total_prescriptions = Purchase.objects.count()
    prescriptions_today = Purchase.objects.filter(created_at__date=today).count()

    # ── IPD (safe) ──
    ipd_patients = 0
    if IPDPatient:
        try:
            ipd_patients = IPDPatient.objects.filter(status='admitted').count()
        except Exception:
            pass

    # ── Recent Transactions ──
    recent_transactions = FinanceTransaction.objects.select_related(
        'category'
    ).order_by('-created_at')[:10]

    context = {
        # Department revenue tiles
        'opd_revenue':          opd_revenue,
        'pharmacy_collected_revenue': pharmacy_revenue,
        'laboratory_revenue':   laboratory_revenue,
        'radiology_revenue':    billing_totals['radiology'] or Decimal('0.00'),
        'blood_bank_revenue':   billing_totals['blood_bank'] or Decimal('0.00'),
        'ipd_revenue':          billing_totals['ipd'] or Decimal('0.00'),
        'ambulance_revenue':    billing_totals['ambulance'] or Decimal('0.00'),

        # Finance summary tiles
        'general_revenue':      total_income,
        'expenses_outflow':     total_expenses,
        'total_income':         total_income,
        'total_expenses':       total_expenses,
        'net_profit':           net_profit,
        'monthly_income':       monthly_income,
        'monthly_expenses':     monthly_expenses,
        'monthly_profit':       monthly_profit,
        'today_income':         today_income,
        'today_expenses':       today_expenses,

        # Patient & activity stats
        'total_patients':       total_patients,
        'new_patients_today':   new_patients_today,
        'total_visits':         total_visits,
        'visits_today':         visits_today,
        'today_appointments':   today_appointments,
        'pending_appointments': pending_appointments,
        'total_prescriptions':  total_prescriptions,
        'prescriptions_today':  prescriptions_today,
        'ipd_patients':         ipd_patients,

        # Recent activity
        'recent_transactions':  recent_transactions,

        # Date
        'today':                today,
    }

    return render(request, 'dashboard/dashboard.html', context)