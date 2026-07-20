from django.contrib import admin
from .models import (
    Stock, Prescription, PrescriptionItem, Supplier,
    MedicineCategory, MedicineGroup, MedicineComposition, Medicine,
    Purchase, PurchaseItem,
    PharmacyInvoice, PharmacyInvoiceItem, PharmacyPayment
)


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1


class PharmacyInvoiceItemInline(admin.TabularInline):
    model = PharmacyInvoiceItem
    extra = 1


# ============================================================
# 1. MEDICINE CATEGORY
# ============================================================
@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('name',)


# ============================================================
# 2. MEDICINE GROUP
# ============================================================
@admin.register(MedicineGroup)
class MedicineGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('name',)


# ============================================================
# 3. MEDICINE COMPOSITION
# ============================================================
@admin.register(MedicineComposition)
class MedicineCompositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)
    ordering = ('name',)


# ============================================================
# 4. MEDICINE
# ============================================================
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'group', 'composition', 'manufacturer', 'is_active')
    list_filter = ('category', 'group', 'is_active')
    search_fields = ('name', 'generic_name', 'manufacturer')
    list_editable = ('is_active',)
    autocomplete_fields = ('category', 'group', 'composition')
    ordering = ('name',)


# ============================================================
# 5. STOCK
# ============================================================
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'medicine', 'quantity_in_stock', 'reorder_level', 'selling_price', 'expiry_date', 'needs_restock', 'is_out_of_stock')  # ← Added reorder_level here
    list_filter = ('expiry_date', 'medicine__category', 'medicine__group')
    search_fields = ('item_name', 'generic_name', 'medicine__name')
    list_editable = ('quantity_in_stock', 'selling_price', 'reorder_level')  # ← Now reorder_level is in list_display
    ordering = ('item_name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('medicine', 'item_name', 'generic_name')
        }),
        ('Stock Details', {
            'fields': ('quantity_in_stock', 'reorder_level', 'expiry_date')
        }),
        ('Pricing', {
            'fields': ('buying_price', 'selling_price')
        }),
        ('Batch Information', {
            'fields': ('batch_number',)
        }),
    )


# ============================================================
# 6. PRESCRIPTION
# ============================================================
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('get_case_id', 'get_patient_name', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('visit__case_id', 'visit__patient__first_name')
    inlines = [PrescriptionItemInline]

    def get_case_id(self, obj):
        return obj.visit.case_id
    get_case_id.short_description = 'Case ID'

    def get_patient_name(self, obj):
        return obj.visit.patient.full_name
    get_patient_name.short_description = 'Patient Name'


# ============================================================
# 7. PRESCRIPTION ITEM
# ============================================================
@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ('prescription', 'medicine', 'quantity_prescribed', 'quantity_dispensed')
    search_fields = ('prescription__visit__case_id', 'medicine__item_name')


# ============================================================
# 8. SUPPLIER
# ============================================================
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone_number', 'is_active')
    search_fields = ('name', 'contact_person')
    list_filter = ('is_active',)
    list_editable = ('is_active',)


# ============================================================
# 9. PURCHASE
# ============================================================
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('purchase_no', 'patient', 'supplier', 'total_amount', 'payment_amount', 'status', 'purchase_date')
    list_filter = ('status', 'payment_mode', 'purchase_date')
    search_fields = ('purchase_no', 'patient__first_name', 'patient__last_name', 'supplier__name')
    inlines = [PurchaseItemInline]
    readonly_fields = ('purchase_no', 'created_at', 'updated_at')
    ordering = ('-purchase_date',)


# ============================================================
# 10. PURCHASE ITEM
# ============================================================
@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'medicine', 'quantity', 'sale_price', 'row_amount', 'batch_no')
    search_fields = ('purchase__purchase_no', 'medicine__name')
    list_filter = ('purchase__status',)


# ============================================================
# 11. PHARMACY INVOICE
# ============================================================
@admin.register(PharmacyInvoice)
class PharmacyInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'patient_name', 'net_amount', 'amount_paid', 'balance_due', 'payment_status', 'created_at')
    list_filter = ('payment_status', 'payment_mode', 'created_at')
    search_fields = ('invoice_number', 'patient_name', 'patient_number')
    inlines = [PharmacyInvoiceItemInline]
    readonly_fields = ('invoice_number', 'balance_due', 'created_at', 'updated_at')
    ordering = ('-created_at',)


# ============================================================
# 12. PHARMACY INVOICE ITEM
# ============================================================
@admin.register(PharmacyInvoiceItem)
class PharmacyInvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'medicine_name', 'quantity', 'unit_price', 'row_total')
    search_fields = ('invoice__invoice_number', 'medicine_name')
    list_filter = ('invoice__payment_status',)


# ============================================================
# 13. PHARMACY PAYMENT
# ============================================================
@admin.register(PharmacyPayment)
class PharmacyPaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'payment_mode', 'reference', 'payment_date')
    list_filter = ('payment_mode', 'payment_date')
    search_fields = ('invoice__invoice_number', 'reference')
    ordering = ('-payment_date',)