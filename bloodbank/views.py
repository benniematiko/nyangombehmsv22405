from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, F
from django.core.paginator import Paginator
from .models import Donor, BloodStock, Donation, BloodRequest
from .forms import DonorForm, BloodRequestForm, DonationForm
from datetime import datetime, timedelta

def is_admin_or_staff(user):
    return user.is_staff or user.is_superuser

@login_required
def bloodbank_home(request):
    """Blood bank home/dashboard view"""
    context = {
        'total_donors': Donor.objects.count(),
        'available_donors': Donor.objects.filter(is_available=True).count(),
        'total_donations': Donation.objects.filter(status='completed').count(),
        'pending_requests': BloodRequest.objects.filter(status='pending').count(),
        'blood_stocks': BloodStock.objects.all(),
        'low_stock': BloodStock.objects.filter(quantity_ml__lt=F('min_threshold_ml')),
        'critical_stock': BloodStock.objects.filter(quantity_ml__lt=(F('min_threshold_ml') / 2)),
        'recent_donations': Donation.objects.filter(status='completed').order_by('-donation_date')[:5],
        'urgent_requests': BloodRequest.objects.filter(priority='urgent', status='pending'),
        'total_blood_quantity': BloodStock.objects.aggregate(total=Sum('quantity_ml'))['total'] or 0,
    }
    return render(request, 'bloodbank/bloodbank_home.html', context)

@login_required
def donor_list(request):
    """List all donors with search and filter"""
    donors = Donor.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        donors = donors.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Filter by blood type
    blood_type = request.GET.get('blood_type', '')
    if blood_type:
        donors = donors.filter(blood_type=blood_type)
    
    # Filter by availability
    availability = request.GET.get('availability', '')
    if availability == 'available':
        donors = donors.filter(is_available=True)
    elif availability == 'unavailable':
        donors = donors.filter(is_available=False)
    
    paginator = Paginator(donors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'blood_types': Donor.BLOOD_TYPES,
        'search_query': search_query,
        'selected_blood_type': blood_type,
        'selected_availability': availability,
    }
    return render(request, 'bloodbank/donor_list.html', context)

@login_required
def donor_detail(request, donor_id):
    """View donor details"""
    donor = get_object_or_404(Donor, id=donor_id)
    donations = donor.donations.all().order_by('-donation_date')
    
    context = {
        'donor': donor,
        'donations': donations,
        'can_donate': donor.can_donate(),
    }
    return render(request, 'bloodbank/donor_detail.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def donor_create(request):
    """Create a new donor"""
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            donor = form.save()
            messages.success(request, f'Donor {donor.get_full_name()} created successfully!')
            return redirect('bloodbank:donor_list')
    else:
        form = DonorForm()
    
    return render(request, 'bloodbank/donor_form.html', {'form': form, 'title': 'Add Donor'})

@login_required
@user_passes_test(is_admin_or_staff)
def donor_edit(request, donor_id):
    """Edit donor details"""
    donor = get_object_or_404(Donor, id=donor_id)
    
    if request.method == 'POST':
        form = DonorForm(request.POST, instance=donor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Donor {donor.get_full_name()} updated successfully!')
            return redirect('bloodbank:donor_detail', donor_id=donor.id)
    else:
        form = DonorForm(instance=donor)
    
    return render(request, 'bloodbank/donor_form.html', {'form': form, 'title': 'Edit Donor', 'donor': donor})

@login_required
@user_passes_test(is_admin_or_staff)
def donor_delete(request, donor_id):
    """Delete a donor"""
    donor = get_object_or_404(Donor, id=donor_id)
    if request.method == 'POST':
        donor_name = donor.get_full_name()
        donor.delete()
        messages.success(request, f'Donor {donor_name} deleted successfully!')
        return redirect('bloodbank:donor_list')
    
    return render(request, 'bloodbank/donor_confirm_delete.html', {'donor': donor})

@login_required
def blood_stock(request):
    """View blood stock levels"""
    stocks = BloodStock.objects.all().order_by('blood_type')
    
    # Calculate statistics
    total_quantity = stocks.aggregate(total=Sum('quantity_ml'))['total'] or 0
    low_stock_count = stocks.filter(quantity_ml__lt=F('min_threshold_ml')).count()
    critical_stock_count = stocks.filter(quantity_ml__lt=(F('min_threshold_ml') / 2)).count()
    
    context = {
        'stocks': stocks,
        'total_quantity': total_quantity,
        'low_stock_count': low_stock_count,
        'critical_stock_count': critical_stock_count,
        'blood_types': Donor.BLOOD_TYPES,
    }
    return render(request, 'bloodbank/blood_stock.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def donation_create(request):
    """Record a new donation"""
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            # Set blood type from donor if not specified
            if not donation.blood_type and donation.donor:
                donation.blood_type = donation.donor.blood_type
            donation.save()
            messages.success(request, f'Donation recorded successfully!')
            return redirect('bloodbank:donation_list')
    else:
        form = DonationForm()
    
    # Pass donor choices for the form
    context = {
        'form': form,
        'title': 'Record Donation',
    }
    return render(request, 'bloodbank/donation_form.html', context)

@login_required
def donation_list(request):
    """List all donations"""
    donations = Donation.objects.all().order_by('-donation_date')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        donations = donations.filter(status=status)
    
    # Filter by date
    date_filter = request.GET.get('date_filter', '')
    if date_filter == 'today':
        today = timezone.now().date()
        donations = donations.filter(donation_date__date=today)
    elif date_filter == 'week':
        week_ago = timezone.now() - timedelta(days=7)
        donations = donations.filter(donation_date__gte=week_ago)
    elif date_filter == 'month':
        month_ago = timezone.now() - timedelta(days=30)
        donations = donations.filter(donation_date__gte=month_ago)
    
    # Calculate total quantity
    total_quantity = donations.aggregate(total=Sum('quantity_ml'))['total'] or 0
    
    paginator = Paginator(donations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_quantity': total_quantity,
        'status_choices': Donation.STATUS_CHOICES,
        'selected_status': status,
        'selected_date_filter': date_filter,
    }
    return render(request, 'bloodbank/donation_list.html', context)

@login_required
def blood_request_list(request):
    """List all blood requests"""
    requests = BloodRequest.objects.all().order_by('-request_date')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        requests = requests.filter(status=status)
    
    # Filter by priority
    priority = request.GET.get('priority', '')
    if priority:
        requests = requests.filter(priority=priority)
    
    paginator = Paginator(requests, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': BloodRequest.STATUS_CHOICES,
        'priority_choices': BloodRequest.PRIORITY_CHOICES,
        'selected_status': status,
        'selected_priority': priority,
    }
    return render(request, 'bloodbank/request_list.html', context)

@login_required
def blood_request_create(request):
    """Create a new blood request"""
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save()
            messages.success(request, f'Blood request for {blood_request.patient_name} created successfully!')
            return redirect('bloodbank:request_list')
    else:
        form = BloodRequestForm()
    
    context = {
        'form': form,
        'title': 'Create Blood Request',
    }
    return render(request, 'bloodbank/request_form.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def blood_request_update(request, request_id):
    """Update blood request status"""
    blood_request = get_object_or_404(BloodRequest, id=request_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if status in dict(BloodRequest.STATUS_CHOICES):
            blood_request.status = status
            if status == 'fulfilled':
                blood_request.fulfilled_date = timezone.now()
                
                # Deduct from blood stock
                stock = BloodStock.objects.filter(blood_type=blood_request.blood_type).first()
                if stock and stock.quantity_ml >= blood_request.quantity_ml:
                    stock.quantity_ml -= blood_request.quantity_ml
                    stock.save()
                    messages.success(request, f'Request fulfilled! Blood stock updated.')
                else:
                    messages.error(request, 'Insufficient blood stock to fulfill this request!')
                    return redirect('bloodbank:request_list')
            
            if notes:
                blood_request.notes = notes
            
            blood_request.save()
            messages.success(request, f'Request status updated to {status}!')
        
        return redirect('bloodbank:request_list')
    
    context = {
        'blood_request': blood_request,
        'status_choices': BloodRequest.STATUS_CHOICES,
    }
    return render(request, 'bloodbank/request_update.html', context)