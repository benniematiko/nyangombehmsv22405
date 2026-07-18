from django.db import models
from django.utils import timezone
import random

class PatientVisit(models.Model):
    STATUS_CHOICES = [
        ('Triage', 'In Triage'),
        ('Consultation', 'With Doctor'),
        ('Laboratory', 'Sent to Lab'),
        ('Radiology', 'Sent to X-Ray'),
        ('Pharmacy', 'Sent to Pharmacy'),
        ('Discharged', 'Discharged'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('Cash', 'Cash'),
        ('M-Pesa', 'M-Pesa'),
        ('Bank/Card', 'Bank Transfer / Card'),
        ('Insurance Claim', 'Insurance Claim'),
    ]

    # Link back to your core Patient model
    patient = models.ForeignKey(
        'patients.Patient', 
        on_delete=models.PROTECT, 
        related_name='visits'
    )
    
    # This is the Case ID used in your billing search bar
    case_id = models.CharField(max_length=50, unique=True, db_index=True, blank=True)
    
    # Base Triage Data (Collected at OPD entry)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, help_text="°C", blank=True, null=True)
    bp_systolic = models.PositiveIntegerField(help_text="mmHg", blank=True, null=True)
    bp_diastolic = models.PositiveIntegerField(help_text="mmHg", blank=True, null=True)
    pulse_rate = models.PositiveIntegerField(help_text="bpm", blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="kg", blank=True, null=True)
    
    # NEW FIELDS FOR OPD CONSULTATION
    # Symptoms Information
    symptoms_type = models.CharField(max_length=255, blank=True, null=True)
    symptoms_title = models.CharField(max_length=255, blank=True, null=True)
    symptoms_description = models.TextField(blank=True, null=True)
    
    # Medical Notes
    notes = models.TextField(blank=True, null=True, help_text="Prescription / Dispensing Notes")
    known_allergies = models.TextField(blank=True, null=True)
    
    # Consultation Details
    appointment_date = models.DateTimeField(default=timezone.now)
    casualty = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')
    old_patient = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')
    reference = models.CharField(max_length=255, blank=True, null=True)
    casualty_doctor = models.CharField(max_length=255, blank=True, null=True)
    
    # Insurance and Charges
    apply_insurance = models.BooleanField(default=False)
    charge_category = models.CharField(max_length=255, blank=True, null=True)
    charge_selection = models.CharField(max_length=255, blank=True, null=True)
    standard_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    applied_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subtotal_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Payment Information
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODE_CHOICES, default='Cash')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Consultation Status
    live_consultation = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], default='No')
    
    # Staff who created the visit
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_visits'
    )
    
    # Tracking Status across the facility
    current_stage = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Triage')
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Auto-generates a clean, unique Case ID on creation.
        Example format: EMH-26-OPD8942
        """
        if not self.case_id:
            year_suffix = timezone.now().strftime('%y') # '26'
            random_digits = random.randint(1000, 9999)
            generated_id = f"EMH-{year_suffix}-OPD{random_digits}"
            
            # Prevent token collisions
            while PatientVisit.objects.filter(case_id=generated_id).exists():
                random_digits = random.randint(1000, 9999)
                generated_id = f"EMH-{year_suffix}-OPD{random_digits}"
                
            self.case_id = generated_id
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Case {self.case_id} — {self.patient.full_name}"