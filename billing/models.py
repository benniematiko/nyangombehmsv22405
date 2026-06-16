from django.db import models
from django.utils import timezone
import uuid


# ==============================================================================
# INSURANCE PROVIDERS — Master List
# ==============================================================================

class InsuranceProvider(models.Model):
    """
    Master list of Insurance Providers / Schemes
    Examples: NHIF, SHA, Jubilee, etc.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Full name of the insurance provider"
    )
    code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text="Short code (e.g. NHIF, SHA, JUBILEE)"
    )
    contact_person = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    is_empaneled = models.BooleanField(
        default=True,
        help_text="Hospital has active agreement with this provider"
    )
    
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Insurance Provider"
        verbose_name_plural = "Insurance Providers"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name


# ==============================================================================
# CHARGE CATALOGUE — Categories and individual charge items
# ==============================================================================

class ChargeCategory(models.Model):
    """
    Top-level grouping for charge items.
    Examples: Consultation, Laboratory, Radiology, Pharmacy, Procedures
    """
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name        = 'Charge Category'
        verbose_name_plural = 'Charge Categories'
        ordering            = ['name']


class Charge(models.Model):
    """
    Individual charge line item linked to a category.
    Examples: General Consultation (KES 500), Full Blood Count (KES 800)
    """
    category       = models.ForeignKey(
                         ChargeCategory,
                         on_delete=models.CASCADE,
                         related_name='charges'
                     )
    name           = models.CharField(max_length=200)
    standard_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_percent    = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                         help_text="VAT percentage e.g. 16.00 for 16%")
    description    = models.TextField(blank=True, null=True)
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} — KES {self.standard_price}"

    class Meta:
        ordering = ['category__name', 'name']


# ==============================================================================
# BILLING INVOICE — Central financial ledger wrapper
# ==============================================================================

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

    visit          = models.ForeignKey(
                         'opd.PatientVisit',
                         on_delete=models.PROTECT,
                         related_name='invoices'
                     )
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, db_index=True)

    # Insurance Fields
    insurance_provider = models.ForeignKey(
        InsuranceProvider,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='invoices'
    )
    insurance_claim_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Claim reference number from insurance"
    )
    insurance_approved_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00,
        help_text="Amount approved by insurance"
    )

    # Financial Aggregations (KES)
    total_amount   = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_amount= models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_amount     = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_amount     = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    amount_paid    = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    payment_mode   = models.CharField(max_length=20, choices=PAYMENT_MODES, default='Cash')
    status         = models.CharField(max_length=20, choices=BILLING_STATUS, default='Unpaid')
    payment_note   = models.CharField(max_length=255, blank=True, null=True,
                         help_text="M-Pesa codes, bank references, etc.")

    created_at     = models.DateTimeField(default=timezone.now)
    updated_at     = models.DateTimeField(auto_now=True)

    def update_totals(self):
        items = self.items.all()
        self.total_amount = sum(item.quantity * item.unit_price for item in items)
        self.tax_amount   = sum(
            (item.quantity * item.unit_price) * (item.tax_percent / 100)
            for item in items
        )
        self.net_amount = (self.total_amount + self.tax_amount) - self.discount_amount

        if self.amount_paid <= 0:
            self.status = 'Unpaid'
        elif self.amount_paid >= self.net_amount:
            self.status = 'Fully Paid'
        else:
            self.status = 'Partially Paid'

        self.save()

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} — Case: {self.visit.case_id}"

    @property
    def balance_due(self):
        return self.net_amount - self.amount_paid


# ==============================================================================
# BILLING ITEM — Line-item per service rendered
# ==============================================================================

class BillingItem(models.Model):
    """
    Line-item tracking model for individual charges within an invoice.
    """
    MODULE_CHOICES = [
        ('Appointment', 'Appointment Fees'),
        ('OPD', 'OPD / Triage Consultation'),
        ('Laboratory', 'Laboratory Investigations'),
        ('Radiology', 'Radiology Scans'),
        ('Blood Bank', 'Blood Issues / Components'),
        ('Pharmacy', 'Pharmacy Dispensing'),
    ]

    invoice            = models.ForeignKey(BillingInvoice, on_delete=models.CASCADE, related_name='items')
    originating_module = models.CharField(max_length=30, choices=MODULE_CHOICES)
    item_name          = models.CharField(max_length=200)
    quantity           = models.PositiveIntegerField(default=1)
    unit_price         = models.DecimalField(max_digits=10, decimal_places=2)
    tax_percent        = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    row_total          = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        base_cost      = self.quantity * self.unit_price
        tax_cost       = base_cost * (self.tax_percent / 100)
        self.row_total = base_cost + tax_cost
        super().save(*args, **kwargs)
        self.invoice.update_totals()

    def delete(self, *args, **kwargs):
        invoice_ref = self.invoice
        super().delete(*args, **kwargs)
        invoice_ref.update_totals()

    def __str__(self):
        return f"{self.item_name} ({self.originating_module})"


# ==============================================================================
# Helper function to seed initial insurance providers
# ==============================================================================

def create_initial_insurance_providers():
    """Create default insurance providers"""
    providers = [
        {"name": "NHIF", "code": "NHIF", "is_empaneled": True},
        {"name": "SHA", "code": "SHA", "is_empaneled": True},
        {"name": "Jubilee Medical Insurance", "code": "JUBILEE", "is_empaneled": True},
        {"name": "CIC Health Care", "code": "CIC", "is_empaneled": True},
        {"name": "APA Insurance", "code": "APA", "is_empaneled": True},
    ]
    
    for data in providers:
        InsuranceProvider.objects.get_or_create(
            name=data["name"],
            defaults=data
        )