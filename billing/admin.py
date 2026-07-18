from django.contrib import admin
from .models import (
    InsuranceProvider,
    ChargeCategory,
    Charge,
    BillingInvoice,
    BillingItem
)


# ==============================================================================
# INSURANCE PROVIDER ADMIN
# ==============================================================================

@admin.register(InsuranceProvider)
class InsuranceProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'is_empaneled', 'phone', 'email']
    list_filter = ['is_active', 'is_empaneled']
    search_fields = ['name', 'code', 'contact_person', 'email']
    ordering = ['name']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'code', 'contact_person', 'phone', 'email']
        }),
        ('Address & Contact', {
            'fields': ['address', 'website']
        }),
        ('Status', {
            'fields': ['is_active', 'is_empaneled']
        }),
        ('Notes', {
            'fields': ['notes']
        }),
    ]


# ==============================================================================
# CHARGE CATALOGUE ADMIN (Your existing configuration preserved)
# ==============================================================================

@admin.register(ChargeCategory)
class ChargeCategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'is_active', 'created_at')
    list_filter   = ('is_active',)
    search_fields = ('name',)


@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'standard_price', 'tax_percent', 'is_active')
    list_filter   = ('category', 'is_active')
    search_fields = ('name',)


# ==============================================================================
# BILLING INVOICE & ITEMS ADMIN
# ==============================================================================

class BillingItemInline(admin.TabularInline):
    model = BillingItem
    extra = 0
    readonly_fields = ['row_total']
    fields = ['originating_module', 'item_name', 'quantity', 'unit_price', 
              'tax_percent', 'row_total']


@admin.register(BillingInvoice)
class BillingInvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 
        'visit', 
        'insurance_provider',
        'net_amount', 
        'amount_paid', 
        'balance_due',
        'status',
        'payment_mode',
        'created_at'
    ]
    list_filter = ['status', 'payment_mode', 'insurance_provider', 'created_at']
    search_fields = ['invoice_number', 'visit__case_id', 'insurance_claim_number']
    ordering = ['-created_at']
    readonly_fields = ['invoice_number', 'total_amount', 'tax_amount', 
                      'net_amount', 'balance_due']
    
    fieldsets = [
        ('Invoice Information', {
            'fields': ['invoice_number', 'visit', 'created_at']
        }),
        ('Insurance Details', {
            'fields': ['insurance_provider', 'insurance_claim_number', 'insurance_approved_amount']
        }),
        ('Financial Summary', {
            'fields': [
                'total_amount', 'tax_amount', 'discount_amount', 
                'net_amount', 'amount_paid', 'balance_due'
            ]
        }),
        ('Payment', {
            'fields': ['payment_mode', 'status', 'payment_note']
        }),
    ]
    
    inlines = [BillingItemInline]


@admin.register(BillingItem)
class BillingItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'originating_module', 'item_name', 'quantity', 
                   'unit_price', 'row_total']
    list_filter = ['originating_module', 'invoice__status']
    search_fields = ['item_name', 'invoice__invoice_number']
    readonly_fields = ['row_total']
    ordering = ['-invoice__created_at']