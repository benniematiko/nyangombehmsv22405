from django.contrib import admin
from .models import Stock, Prescription, PrescriptionItem, Supplier



class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'quantity_in_stock', 'selling_price', 'expiry_date', 'needs_restock')
    list_filter = ('expiry_date',)
    search_fields = ('item_name', 'generic_name')

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



@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone_number', 'is_active')
    search_fields = ('name', 'contact_person')