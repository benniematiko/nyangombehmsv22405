from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class FinanceTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    description = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    transaction_date = models.DateTimeField(default=timezone.now)
    payment_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='finance_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.description}"
    
    class Meta:
        ordering = ['-transaction_date']


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Medical Supplies', 'Medical Supplies'),
        ('Laboratory Supplies', 'Laboratory Supplies'),
        ('Pharmacy', 'Pharmacy'),
        ('Equipment', 'Equipment'),
        ('Maintenance', 'Maintenance'),
        ('Utilities', 'Utilities'),
        ('Salaries', 'Salaries'),
        ('Administrative', 'Administrative'),
        ('Training', 'Training'),
        ('Transport', 'Transport'),
        ('Other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    voucher_number = models.CharField(max_length=50, unique=True)
    payee_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    expense_date = models.DateField(default=timezone.now)
    net_amount = models.DecimalField(max_digits=15, decimal_places=2)
    gross_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    reference_code = models.CharField(max_length=100, blank=True, null=True)
    attachment = models.FileField(upload_to='expenses/%Y/%m/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='expenses_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disbursed_at = models.DateTimeField(blank=True, null=True)
    disbursed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses_disbursed')
    
    def __str__(self):
        return f"{self.voucher_number} - {self.payee_name}"
    
    class Meta:
        ordering = ['-expense_date', '-created_at']


class ExpenseItem(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='items')
    classification = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=200)
    gl_code = models.CharField(max_length=50, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    quantity = models.IntegerField(default=1)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    row_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.name} - {self.expense.voucher_number}"