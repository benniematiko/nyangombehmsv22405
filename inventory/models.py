from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


# ============================================================
# 1. SUPPLIER MANAGEMENT
# ============================================================

class Supplier(models.Model):
    """
    Suppliers/Vendors who supply items to the hospital.
    """
    SUPPLIER_TYPE_CHOICES = [
        ('Pharmaceutical', 'Pharmaceutical'),
        ('Medical Equipment', 'Medical Equipment'),
        ('Surgical', 'Surgical'),
        ('Lab Supplies', 'Lab Supplies'),
        ('General', 'General'),
        ('Other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    supplier_type = models.CharField(max_length=50, choices=SUPPLIER_TYPE_CHOICES, default='General')
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return self.name


# ============================================================
# 2. CATEGORY MANAGEMENT
# ============================================================

class ItemCategory(models.Model):
    """
    Categories for inventory items.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Item Categories"

    def __str__(self):
        return self.name


# ============================================================
# 3. ITEM / PRODUCT MANAGEMENT
# ============================================================

class InventoryItem(models.Model):
    """
    Master list of all inventory items.
    """
    UNIT_CHOICES = [
        ('Each', 'Each'),
        ('Box', 'Box'),
        ('Carton', 'Carton'),
        ('Bottle', 'Bottle'),
        ('Vial', 'Vial'),
        ('Packet', 'Packet'),
        ('Strip', 'Strip'),
        ('Tablet', 'Tablet'),
        ('Capsule', 'Capsule'),
        ('Sachet', 'Sachet'),
        ('Tube', 'Tube'),
        ('Can', 'Can'),
        ('Jar', 'Jar'),
        ('Kg', 'Kilogram'),
        ('Gm', 'Gram'),
        ('Ltr', 'Liter'),
        ('Ml', 'Milliliter'),
        ('Pair', 'Pair'),
        ('Set', 'Set'),
        ('Other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Discontinued', 'Discontinued'),
        ('Out of Stock', 'Out of Stock'),
    ]
    
    # Basic Information
    code = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(ItemCategory, on_delete=models.PROTECT, related_name='items')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    
    # Units & Quantities
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='Each')
    reorder_level = models.PositiveIntegerField(default=10, help_text="Minimum stock before reorder")
    reorder_quantity = models.PositiveIntegerField(default=50, help_text="Quantity to reorder when stock is low")
    max_stock_level = models.PositiveIntegerField(default=500, help_text="Maximum stock to hold")
    
    # Pricing
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Tracking
    batch_tracking = models.BooleanField(default=False, help_text="Track items by batch number")
    expiry_tracking = models.BooleanField(default=False, help_text="Track expiry dates")
    serial_tracking = models.BooleanField(default=False, help_text="Track by serial number")
    
    # Current Stock
    current_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0, help_text="Reserved for orders/patients")
    available_quantity = models.PositiveIntegerField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    is_active = models.BooleanField(default=True)
    
    # Additional
    notes = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='inventory/items/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Inventory Items"

    def save(self, *args, **kwargs):
        # Auto-generate code if not provided
        if not self.code:
            last_item = InventoryItem.objects.all().order_by('id').last()
            next_id = (last_item.id + 1) if last_item else 1
            self.code = f"INV-{timezone.now().year}-{next_id:04d}"
        
        # Calculate available quantity
        self.available_quantity = self.current_quantity - self.reserved_quantity
        
        # Update status based on stock
        if self.available_quantity <= 0:
            self.status = 'Out of Stock'
        else:
            self.status = 'Active'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"

    def is_low_stock(self):
        return self.current_quantity <= self.reorder_level


# ============================================================
# 4. STOCK MOVEMENT / TRANSACTIONS
# ============================================================

class StockTransaction(models.Model):
    """
    Record all stock movements (in/out/adjustments).
    """
    TRANSACTION_TYPE_CHOICES = [
        ('Purchase', 'Purchase'),
        ('Sale', 'Sale'),
        ('Return', 'Return'),
        ('Adjustment', 'Adjustment'),
        ('Transfer', 'Transfer'),
        ('Issue', 'Issue'),
        ('Receipt', 'Receipt'),
        ('Disposal', 'Disposal'),
        ('Damage', 'Damage'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    transaction_number = models.CharField(max_length=50, unique=True, editable=False)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name='transactions')
    
    # Quantities
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Batch/Serial tracking
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Reference
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    reference_notes = models.TextField(blank=True, null=True)
    
    # Relationships
    performed_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='stock_transactions')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_approved')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Timestamps
    transaction_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transaction_date']
        verbose_name_plural = "Stock Transactions"

    def save(self, *args, **kwargs):
        if not self.transaction_number:
            last_trans = StockTransaction.objects.all().order_by('id').last()
            next_id = (last_trans.id + 1) if last_trans else 1
            prefix = 'STK'  # Stock transaction prefix
            self.transaction_number = f"{prefix}-{timezone.now().year}-{next_id:04d}"
        
        # Calculate total cost
        self.total_cost = self.quantity * self.unit_cost
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_number} - {self.item.name}"


# ============================================================
# 5. STOCK ADJUSTMENT / COUNT
# ============================================================

class StockCount(models.Model):
    """
    Periodic stock counts/physical inventory.
    """
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    count_number = models.CharField(max_length=50, unique=True, editable=False)
    count_date = models.DateTimeField(default=timezone.now)
    counted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='stock_counts')
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-count_date']
        verbose_name_plural = "Stock Counts"

    def save(self, *args, **kwargs):
        if not self.count_number:
            last_count = StockCount.objects.all().order_by('id').last()
            next_id = (last_count.id + 1) if last_count else 1
            self.count_number = f"CT-{timezone.now().year}-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.count_number} - {self.count_date.strftime('%d/%m/%Y')}"


class StockCountItem(models.Model):
    """
    Individual items in a stock count.
    """
    stock_count = models.ForeignKey(StockCount, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name='stock_counts')
    system_quantity = models.PositiveIntegerField(default=0)
    physical_quantity = models.PositiveIntegerField(default=0)
    variance = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Stock Count Items"
        unique_together = ['stock_count', 'item']

    def save(self, *args, **kwargs):
        # Calculate variance
        self.variance = self.physical_quantity - self.system_quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - System: {self.system_quantity}, Physical: {self.physical_quantity}"


# ============================================================
# 6. PURCHASE ORDERS
# ============================================================

class PurchaseOrder(models.Model):
    """
    Purchase orders for stock replenishment.
    """
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Approved', 'Approved'),
        ('Ordered', 'Ordered'),
        ('Received', 'Received'),
        ('Cancelled', 'Cancelled'),
    ]
    
    PAYMENT_MODE_CHOICES = [
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Credit', 'Credit'),
        ('Cheque', 'Cheque'),
    ]
    
    po_number = models.CharField(max_length=50, unique=True, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    order_date = models.DateTimeField(default=timezone.now)
    expected_delivery = models.DateField(blank=True, null=True)
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODE_CHOICES, default='Cash')
    payment_terms = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='purchase_orders')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_approved')
    
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date']
        verbose_name_plural = "Purchase Orders"

    def save(self, *args, **kwargs):
        if not self.po_number:
            last_po = PurchaseOrder.objects.all().order_by('id').last()
            next_id = (last_po.id + 1) if last_po else 1
            self.po_number = f"PO-{timezone.now().year}-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.po_number} - {self.supplier.name}"


class PurchaseOrderItem(models.Model):
    """
    Items in a purchase order.
    """
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name='po_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    quantity_received = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Purchase Order Items"

    def save(self, *args, **kwargs):
        # Calculate line total
        tax_amount = self.quantity * self.unit_price * (self.tax_rate / 100)
        self.line_total = (self.quantity * self.unit_price) + tax_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity} x {self.unit_price}"