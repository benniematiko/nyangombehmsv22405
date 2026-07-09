from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

# ==========================================================================
# 1. CORE REGISTRIES & AUXILIARY REFERENCE TABLES
# ==========================================================================

class Supplier(models.Model):
    """
    Registry of pharmaceutical distributors and medical supply vendors.
    Sits at the top of the file to guarantee safe foreign key resolution.
    """
    name = models.CharField(max_length=150, unique=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return self.name


class MedicineCategory(models.Model):
    """System definition category tags for drugs."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Medicine Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Medicine(models.Model):
    """Base generic medicine descriptor table profiles."""
    category = models.ForeignKey(MedicineCategory, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=255, unique=True)
    generic_name = models.CharField(max_length=255, blank=True, null=True)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Medicines"

    def __str__(self):
        return self.name


# ==========================================================================
# 2. PHARMACY INVENTORY STOCK MANAGEMENT
# ==========================================================================

class Stock(models.Model):
    """
    Tracks medicine inventory, shelf quantities, and baseline retail pricing 
    at the Eagles Mission Hospital pharmacy.
    """
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name='stock_items', null=True, blank=True)
    item_name = models.CharField(max_length=200, db_index=True)
    generic_name = models.CharField(max_length=200, blank=True, null=True)
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    
    quantity_in_stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10, help_text="Alert threshold to restock item")
    
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost price per unit", default=0.00)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Retail billing charge per unit", default=0.00)
    
    expiry_date = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['item_name']
        verbose_name_plural = "Stock Inventory"

    @property
    def is_expired(self):
        return self.expiry_date <= timezone.now().date()

    @property
    def needs_restock(self):
        return self.quantity_in_stock <= self.reorder_level

    @property
    def is_out_of_stock(self):
        return self.quantity_in_stock <= 0

    # DYNAMIC LAYOUT FALLBACK TRANSLATORS
    @property
    def company_name(self):
        name_lower = self.item_name.lower()
        if "beta" in name_lower or "paracetamol" in name_lower:
            return "Beta Healthcare"
        elif "cosmos" in name_lower or "amoxicillin" in name_lower:
            return "Cosmos Limited"
        elif "gsk" in name_lower or "cetirizine" in name_lower or "glaxo" in name_lower:
            return "GlaxoSmithKline"
        return "Eagles Pharmacy Wholesaler"

    @property
    def category(self):
        name_lower = self.item_name.lower()
        if "amox" in name_lower or "cap" in name_lower:
            return "Antibiotics"
        elif "para" in name_lower or "hedex" in name_lower:
            return "Analgesics"
        elif "cetirizine" in name_lower:
            return "Antihistamines"
        return "General Stock"

    @property
    def group(self):
        if self.category == "Antibiotics":
            return "Prescription Only"
        return "General OTC"

    @property
    def unit_type(self):
        name_lower = self.item_name.lower()
        if "syr" in name_lower or "susp" in name_lower or "liquid" in name_lower:
            return "Bottle"
        elif "cap" in name_lower:
            return "Capsule"
        elif "drops" in name_lower:
            return "Vial"
        return "Tablet"

    def __str__(self):
        return f"{self.item_name} ({self.quantity_in_stock} Units remaining)"


# ==========================================================================
# 3. CLINICAL PRESCRIPTIONS FLOW
# ==========================================================================

class Prescription(models.Model):
    """
    Master clinical container for a drug order. Generated by a clinician 
    and dispatched to the pharmacy using the Case ID.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending Dispensing'),
        ('Dispensed', 'Sent to Billing / Handed Over'),
        ('Cancelled', 'Cancelled / Adjusted'),
    ]

    visit = models.ForeignKey(
        'opd.PatientVisit', 
        on_delete=models.PROTECT, 
        related_name='prescriptions'
    )
    prescribed_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='issued_prescriptions'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    clinical_note = models.TextField(blank=True, null=True, help_text="Diagnosis context or special instructions")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Rx for Case {self.visit.case_id} — {self.status}"


class PrescriptionItem(models.Model):
    """
    Line item matching individual drugs, dosages, and quantities ordered 
    within a master prescription request card.
    """
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Stock, on_delete=models.PROTECT, related_name='prescription_lines')
    
    dosage_instruction = models.CharField(max_length=255, help_text="e.g., 1x3 for 5 days")
    quantity_prescribed = models.PositiveIntegerField(default=1)
    quantity_dispensed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.medicine.item_name} x {self.quantity_prescribed}"


# ==========================================================================
# 4. EXTERNAL WHOLESALE SUPPLY PURCHASING
# ==========================================================================

class Purchase(models.Model):
    """
    Tracks ledger headers regarding external warehouse acquisitions 
    from verified suppliers.
    """
    PAYMENT_MODE_CHOICES = [
        ('Cash', 'Cash'),
        ('M-Pesa', 'M-Pesa'),
        ('Bank', 'Bank Transfer'),
        ('Insurance', 'Insurance'),
        ('Credit', 'Credit'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Partial', 'Partial'),
    ]  

    purchase_no = models.CharField(max_length=100, unique=True, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchases', null=True, blank=True)
    
    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='pharmacy_bills', null=True, blank=True)
    doctor_name = models.CharField(max_length=200, blank=True, null=True)
    case_id = models.CharField(max_length=100, blank=True, null=True)
    prescription = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    supplier_bill_number = models.CharField(max_length=100, blank=True, null=True)
    purchase_date = models.DateTimeField(default=timezone.now)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_summary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODE_CHOICES, default='Cash')
    payment_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_note = models.CharField(max_length=255, blank=True, null=True)
    purchase_note = models.TextField(blank=True, null=True)
    document_attachment = models.FileField(upload_to='pharmacy/purchases/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-purchase_date']
        verbose_name_plural = "Purchases"

    def save(self, *args, **kwargs):
        if not self.purchase_no:
            last_purchase = Purchase.objects.all().order_by('id').last()
            next_id = (last_purchase.id + 1) if last_purchase else 1
            self.purchase_no = f"PH-BILL-{timezone.now().year}-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        if self.patient:
            return f"{self.purchase_no} — {self.patient.full_name}"
        return f"{self.purchase_no} — {self.supplier.name if self.supplier else 'N/A'}"


class PurchaseItem(models.Model):
    """
    Itemized drug rows incoming from an external vendor delivery invoice sheet.
    """
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name='purchase_items')
    batch_no = models.CharField(max_length=100)
    expiry_date = models.DateField()
    
    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Maximum Retail Price")
    batch_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    packing_qty = models.IntegerField(default=1)
    quantity = models.IntegerField(default=0)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    row_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Purchase Items"

    def save(self, *args, **kwargs):
        if self.row_amount == 0 and self.quantity and self.purchase_price:
            base_amount = self.quantity * self.purchase_price
            tax_amount = base_amount * (self.tax_percent / 100)
            self.row_amount = base_amount + tax_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.medicine.name} — Batch: {self.batch_no} ({self.purchase.purchase_no})"


# ==========================================================================
# 5. PHARMACY BILLING / INVOICE TRANSACTIONS
# ==========================================================================

class PharmacyInvoice(models.Model):
    """
    Master invoice record for pharmacy billing transactions.
    Used for tracking patient pharmacy bills and payments.
    """
    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Partial', 'Partial'),
        ('Pending', 'Pending'),
        ('Refunded', 'Refunded'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('Cash', 'Cash'),
        ('M-Pesa', 'M-Pesa'),
        ('Bank', 'Bank Transfer'),
        ('Insurance', 'Insurance'),
        ('Credit', 'Credit'),
    ]

    invoice_number = models.CharField(max_length=100, unique=True, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, related_name='pharmacy_invoices', null=True, blank=True)
    patient_name = models.CharField(max_length=200, blank=True, null=True)
    patient_number = models.CharField(max_length=50, blank=True, null=True)
    doctor = models.CharField(max_length=200, blank=True, null=True)
    case_id = models.CharField(max_length=100, blank=True, null=True)
    prescription = models.TextField(blank=True, null=True)
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODE_CHOICES, default='Cash')
    payment_note = models.TextField(blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pharmacy_invoices', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Pharmacy Invoices"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = PharmacyInvoice.objects.all().order_by('id').last()
            next_id = (last_invoice.id + 1) if last_invoice else 1
            self.invoice_number = f"PH-INV-{timezone.now().year}-{next_id:04d}"
        
        # Calculate balance due
        self.balance_due = self.net_amount - self.amount_paid
        
        # Auto-update payment status
        if self.balance_due <= 0:
            self.payment_status = 'Paid'
        elif self.amount_paid > 0 and self.balance_due > 0:
            self.payment_status = 'Partial'
        else:
            self.payment_status = 'Pending'
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} — {self.patient_name or 'Unknown Patient'}"


class PharmacyInvoiceItem(models.Model):
    """
    Line items for pharmacy invoices.
    Tracks individual medicines, quantities, and amounts billed.
    """
    invoice = models.ForeignKey(PharmacyInvoice, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Stock, on_delete=models.PROTECT, related_name='invoice_items')
    medicine_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True, null=True)
    batch_no = models.CharField(max_length=100, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity = models.PositiveIntegerField(default=1)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    row_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['id']
        verbose_name_plural = "Pharmacy Invoice Items"

    def save(self, *args, **kwargs):
        # Auto-calculate row total
        if self.quantity and self.unit_price:
            base_amount = self.quantity * self.unit_price
            tax_amount = base_amount * (self.tax_percent / 100)
            self.row_total = base_amount + tax_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.medicine_name} x {self.quantity} ({self.invoice.invoice_number})"


class PharmacyPayment(models.Model):
    """
    Tracks individual payments made against pharmacy invoices.
    """
    PAYMENT_MODE_CHOICES = [
        ('Cash', 'Cash'),
        ('M-Pesa', 'M-Pesa'),
        ('Bank', 'Bank Transfer'),
        ('Insurance', 'Insurance'),
        ('Credit', 'Credit'),
    ]

    invoice = models.ForeignKey(PharmacyInvoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODE_CHOICES, default='Cash')
    reference = models.CharField(max_length=100, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    received_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pharmacy_payments')
    payment_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']
        verbose_name_plural = "Pharmacy Payments"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update invoice amount_paid and balance_due
        total_paid = self.invoice.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        self.invoice.amount_paid = total_paid
        self.invoice.balance_due = self.invoice.net_amount - total_paid
        if self.invoice.balance_due <= 0:
            self.invoice.payment_status = 'Paid'
        elif total_paid > 0 and self.invoice.balance_due > 0:
            self.invoice.payment_status = 'Partial'
        else:
            self.invoice.payment_status = 'Pending'
        self.invoice.save(update_fields=['amount_paid', 'balance_due', 'payment_status'])

    def __str__(self):
        return f"Payment {self.id} — {self.invoice.invoice_number} (Kshs {self.amount})"