from django.db import models
from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor


class LaboratoryTest(models.Model):
    TEST_STATUS = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE, 
        related_name='lab_tests',
        null=True,      # Made nullable to avoid migration issues
        blank=True
    )
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    test_name = models.CharField(max_length=200)
    test_category = models.CharField(max_length=100, blank=True, null=True)
    specimen_type = models.CharField(max_length=100, blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    normal_range = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=TEST_STATUS, default='pending')
    notes = models.TextField(blank=True, null=True)
    ordered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lab_tests_ordered')
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_tests_performed')
    ordered_at = models.DateTimeField(auto_now_add=True)
    performed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.test_name} - {self.patient.full_name if self.patient else 'No Patient'}"
    
    class Meta:
        ordering = ['-ordered_at']


class LaboratoryInvoice(models.Model):
    INVOICE_STATUS = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_invoices')
    visit = models.ForeignKey('opd.PatientVisit', on_delete=models.SET_NULL, null=True, blank=True)
    case_id = models.CharField(max_length=50, blank=True, null=True)        # ← NEW
    doctor_name = models.CharField(max_length=200, blank=True, null=True)   # ← NEW
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    balance_due = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lab_invoices_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.invoice_number} - {self.patient.full_name if self.patient else 'No Patient'}"
    
    class Meta:
        ordering = ['-issue_date']

class LaboratoryInvoiceItem(models.Model):
    invoice = models.ForeignKey(LaboratoryInvoice, on_delete=models.CASCADE, related_name='items')
    test = models.ForeignKey(LaboratoryTest, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_number}"


class LaboratoryPayment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('insurance', 'Insurance'),
        ('other', 'Other'),
    ]
    
    invoice = models.ForeignKey(LaboratoryInvoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lab_payments_received')
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.amount}"
    
    class Meta:
        ordering = ['-payment_date']