from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Donor(models.Model):
    BLOOD_TYPES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
    last_donation_date = models.DateField(null=True, blank=True)
    total_donations = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.blood_type}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def can_donate(self):
        if not self.is_available:
            return False
        if self.last_donation_date:
            from datetime import date, timedelta
            days_since_last = (date.today() - self.last_donation_date).days
            return days_since_last >= 56  # 8 weeks minimum between donations
        return True

class BloodStock(models.Model):
    BLOOD_TYPES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES, unique=True)
    quantity_ml = models.IntegerField(default=0)  # Quantity in milliliters
    min_threshold_ml = models.IntegerField(default=5000)  # Minimum threshold in ml
    max_capacity_ml = models.IntegerField(default=50000)  # Maximum capacity in ml
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.blood_type} - {self.quantity_ml}ml"
    
    def is_low(self):
        return self.quantity_ml < self.min_threshold_ml
    
    def is_critical(self):
        return self.quantity_ml < (self.min_threshold_ml / 2)
    
    def get_percentage(self):
        if self.max_capacity_ml == 0:
            return 0
        return (self.quantity_ml / self.max_capacity_ml) * 100

class Donation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('deferred', 'Deferred'),
    ]
    
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    donation_date = models.DateTimeField(default=timezone.now)
    quantity_ml = models.IntegerField()  # Quantity in ml
    blood_type = models.CharField(max_length=3, choices=Donor.BLOOD_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)

    PAYMENT_MODES = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('cheque', 'Cheque'),
        ('card', 'Card'),
    ]

    bag = models.CharField(max_length=50, blank=True, default='')
    unit_type = models.CharField(max_length=20, blank=True, default='')
    lot = models.CharField(max_length=50, blank=True, default='')
    institution = models.CharField(max_length=150, blank=True, default='')
    charge_category = models.CharField(max_length=100, blank=True, default='')
    charge_name = models.CharField(max_length=100, blank=True, default='')
    standard_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODES, default='cash')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)



    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.donor.get_full_name()} - {self.donation_date.date()} - {self.quantity_ml}ml"
    
    def save(self, *args, **kwargs):
        # Set blood type from donor if not specified
        if not self.blood_type and self.donor:
            self.blood_type = self.donor.blood_type
        
        # If donation is completed, update donor record and blood stock
        if self.status == 'completed' and not self.pk:
            # Update donor
            self.donor.last_donation_date = self.donation_date.date()
            self.donor.total_donations += 1
            self.donor.save()
            
            # Update blood stock
            stock, created = BloodStock.objects.get_or_create(blood_type=self.blood_type)
            stock.quantity_ml += self.quantity_ml
            stock.save()
        
        super().save(*args, **kwargs)

class BloodRequest(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]
    
    patient_name = models.CharField(max_length=200)
    patient_age = models.IntegerField()
    patient_gender = models.CharField(max_length=1, choices=Donor.GENDER_CHOICES)
    blood_type = models.CharField(max_length=3, choices=Donor.BLOOD_TYPES)
    quantity_ml = models.IntegerField()
    hospital_name = models.CharField(max_length=200)
    hospital_address = models.TextField()
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField()
    request_date = models.DateTimeField(auto_now_add=True)
    required_by = models.DateTimeField()
    fulfilled_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.patient_name} - {self.blood_type} - {self.quantity_ml}ml"


class Component(models.Model):
    COMPONENT_TYPES = [
        ('cryo', 'Cryo'),
        ('rbc', 'Red Cells'),
        ('wbc', 'White Cells & Granulocytes'),
        ('plasma', 'Plasma'),
        ('platelets', 'Platelets'),
    ]
    UNIT_CHOICES = [('ml', 'ml'), ('units', 'Units')]

    blood_type = models.CharField(max_length=3, choices=Donor.BLOOD_TYPES)
    bag_type = models.CharField(max_length=20, blank=True, default='')
    component = models.CharField(max_length=20, choices=COMPONENT_TYPES)
    bags = models.PositiveIntegerField(default=1)
    volume = models.PositiveIntegerField(null=True, blank=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, blank=True, default='ml')
    lot = models.CharField(max_length=50)
    institution = models.CharField(max_length=150, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blood_type} - {self.get_component_display()} - Lot {self.lot}"