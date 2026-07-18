from django.db import models
from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor

class RadiologyTest(models.Model):
    TEST_STATUS = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='radiology_tests')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    test_name = models.CharField(max_length=200)
    test_category = models.CharField(max_length=100, blank=True, null=True)
    body_part = models.CharField(max_length=100, blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    finding = models.TextField(blank=True, null=True)
    impression = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=TEST_STATUS, default='pending')
    notes = models.TextField(blank=True, null=True)
    ordered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='radiology_tests_ordered')
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='radiology_tests_performed')
    ordered_at = models.DateTimeField(auto_now_add=True)
    performed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.test_name} - {self.patient.full_name}"
    
    class Meta:
        ordering = ['-ordered_at']