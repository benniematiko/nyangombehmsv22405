from django.db import models
from django.utils import timezone
import uuid

class BillingInvoice(models.Model):
    """
    Central financial ledger wrapper tracking the overall accumulated costs
    for a specific patient visit instance across Eagles Mission Hospital.
    """
    PAYMENT_MODES = [
        ('Cash', 'Cash'),
        ('M-Pesa', 'M-Pesa'),
        ('Bank', 'Bank'),
        ('Insurance', 'Insurance'),
    ]
    
    BILLING_STATUS = [
        ('Unpaid', 'Unpaid'),
        ('Partially Paid', 'Partially Paid'),
        ('Fully Paid', 'Fully Paid'),
    ]

    # Explicit link to the active encounter in the OPD app
    visit = models.ForeignKey(
        'opd.PatientVisit', 
        on_delete=models.PROTECT, 
        related_name='invoices'
    )
    
    # Auto-generated clean invoice track token (e.g., INV-89F3A1)
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, db_index=True)
    
    # Financial Aggregations (shs)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Transactional Metadata
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default='Cash')
    status = models.CharField(max_length=20, choices=BILLING_STATUS, default='Unpaid')
    payment_note = models.CharField(max_length=255, blank=True, null=True, help_text="M-Pesa transaction codes, bank reference numbers, etc.")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def update_totals(self):
        """
        Recalculates invoice summary totals based on attached item lines.
        Call this method whenever an invoice item is created, altered, or deleted.
        """
        items = self.items.all()
        # Sum base amounts and tax fractions from individual child items
        self.total_amount = sum(item.quantity * item.unit_price for item in items)
        self.tax_amount = sum((item.quantity * item.unit_price) * (item.tax_percent / 100) for item in items)
        
        # Calculate terminal totals
        self.net_amount = (self.total_amount + self.tax_amount) - self.discount_amount
        
        # Auto-evaluate operational billing status
        if self.amount_paid <= 0:
            self.status = 'Unpaid'
        elif self.amount_paid >= self.net_amount:
            self.status = 'Fully Paid'
        else:
            self.status = 'Partially Paid'
            
        self.save()

    def save(self, *args, **kwargs):
        """Auto-generates unique lookup keys before creating records."""
        if not self.invoice_number:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} — Case: {self.visit.case_id}"

    @property
    def balance_due(self):
        return self.net_amount - self.amount_paid


class BillingItem(models.Model):
    """
    Line-item tracking model indicating exactly which module generated a specific charge 
    (matches the individual service modules displayed on your Single Module Billing panel).
    """
    MODULE_CHOICES = [
        ('Appointment', 'Appointment Fees'),
        ('OPD', 'OPD / Triage Consultation'),
        ('Laboratory', 'Laboratory Investigations'),
        ('Radiology', 'Radiology Scans'),
        ('Blood Bank', 'Blood Issues / Components'),
        ('Pharmacy', 'Pharmacy Dispensing'),
    ]

    invoice = models.ForeignKey(BillingInvoice, on_delete=models.CASCADE, related_name='items')
    originating_module = models.CharField(max_length=30, choices=MODULE_CHOICES)
    
    item_name = models.CharField(max_length=200, help_text="e.g., Full Blood Count, Paracetamol 500mg, Consultation")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Tax percentage rate (e.g., 16.00 for 16% VAT)")
    row_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        """Evaluates row totals and pushes calculations up to the invoice wrapper parent."""
        base_cost = self.quantity * self.unit_price
        tax_cost = base_cost * (self.tax_percent / 100)
        self.row_total = base_cost + tax_cost
        
        super().save(*args, **kwargs)
        # Inform the master invoice card wrapper to sync values
        self.invoice.update_totals()

    def delete(self, *args, **kwargs):
        """Forces an invoice update balance pass if an item row is removed."""
        invoice_ref = self.invoice
        super().delete(*args, **kwargs)
        invoice_ref.update_totals()

    def __str__(self):
        return f"{self.item_name} ({self.originating_module})"