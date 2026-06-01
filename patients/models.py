from django.db import models
from django.utils import timezone

class Patient(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    # Unique identifier (e.g., EMH-PT-2026-0001)
    patient_number = models.CharField(max_length=50, unique=True, db_index=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    # Contact & Identification
    phone_number = models.CharField(max_length=15, db_index=True)  # Supports M-Pesa tracking later
    email = models.EmailField(blank=True, null=True)
    national_id_or_passport = models.CharField(max_length=30, blank=True, null=True)
    
    # Next of Kin Details
    next_of_kin_name = models.CharField(max_length=100, blank=True, null=True)
    next_of_kin_phone = models.CharField(max_length=15, blank=True, null=True)
    next_of_kin_relationship = models.CharField(max_length=50, blank=True, null=True)
    
    # System Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.patient_number} - {self.full_name}"
