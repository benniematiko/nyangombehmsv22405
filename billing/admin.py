from django.contrib import admin
from .models import BillingInvoice, BillingItem

class BillingItemInline(admin.TabularInline):
    model = BillingItem
    extra = 1

@admin.register(BillingInvoice)
class BillingInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'get_case_id', 'net_amount', 'amount_paid', 'status', 'created_at')
    list_filter = ('status', 'payment_mode')
    search_fields = ('invoice_number', 'visit__case_id')
    inlines = [BillingItemInline]

    def get_case_id(self, obj):
        return obj.visit.case_id
    get_case_id.short_description = 'Case ID'