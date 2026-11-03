from django.db import models
from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor

class IPDPatient(models.Model):
    ADMISSION_STATUS = [
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged'),
        ('transferred', 'Transferred'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='ipd_admissions')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='ipd_patients')
    admission_date = models.DateTimeField(auto_now_add=True)
    discharge_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ADMISSION_STATUS, default='admitted')  # ✅ This field exists
    ward = models.CharField(max_length=100, blank=True, null=True)
    bed_number = models.CharField(max_length=20, blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    admission_reason = models.TextField(blank=True, null=True)

    symptoms_type = models.CharField(max_length=100, blank=True, null=True)
    symptoms_title = models.CharField(max_length=200, blank=True, null=True)
    symptoms_description = models.TextField(blank=True, null=True)
    case_id = models.CharField(max_length=50, blank=True, null=True)
    casualty = models.BooleanField(default=False)
    old_patient = models.BooleanField(default=False)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=1000)
    reference = models.CharField(max_length=100, blank=True, null=True)
    live_consultation = models.BooleanField(default=False)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ipd_admissions_created')
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.status} - {self.admission_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-admission_date']



class BedGroup(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Bed(models.Model):
    group = models.ForeignKey(BedGroup, on_delete=models.CASCADE, related_name='beds')
    name = models.CharField(max_length=20)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.group.name} - {self.name}"