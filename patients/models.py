from django.db import models
from django.utils import timezone
from billing.models import InsuranceProvider


class Patient(models.Model):
    # ==================== CHOICES ====================
    GENDER_CHOICES = [
        ('', 'Select Gender'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('', 'Select Blood Group'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('', 'Select Marital Status'),
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
    ]

    # ==================== CORE FIELDS ====================
    patient_number = models.CharField(max_length=50, unique=True, db_index=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name="Gender"
    )
    
    # Additional Personal Information
    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        blank=True,
        null=True,
        verbose_name="Blood Group"
    )
    
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        blank=True,
        null=True,
        verbose_name="Marital Status"
    )
    
    # Contact & Identification
    phone_number = models.CharField(max_length=15, db_index=True)
    email = models.EmailField(blank=True, null=True)
    national_id_or_passport = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Medical Information
    allergies = models.TextField(blank=True, null=True, help_text="Any known allergies (medication, food, environmental)")
    remarks = models.TextField(blank=True, null=True, help_text="General observations or notes about the patient")
    
    # ==================== INSURANCE ====================
    insurance_provider = models.ForeignKey(
        InsuranceProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients'
    )
    insurance_id = models.CharField(max_length=50, blank=True, null=True, 
                                   help_text="Insurance policy/membership number")
    insurance_validity = models.DateField(blank=True, null=True, 
                                         help_text="Insurance policy expiry date")
    
    # Next of Kin Details
    next_of_kin_name = models.CharField(max_length=100, blank=True, null=True)
    next_of_kin_phone = models.CharField(max_length=15, blank=True, null=True)
    next_of_kin_relationship = models.CharField(max_length=50, blank=True, null=True)
    
    # Patient Photo
    patient_photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True)
    
    # System Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        today = timezone.now().date()
        age = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return age

    def __str__(self):
        return f"{self.patient_number} - {self.full_name}"