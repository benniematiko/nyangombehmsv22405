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