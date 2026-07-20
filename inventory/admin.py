from django.contrib import admin
from .models import (
    Supplier,
    ItemCategory,
    InventoryItem,
    StockTransaction,
    StockCount,
    StockCountItem,
    PurchaseOrder,
    PurchaseOrderItem,
)


# ====================== SIMPLE REGISTRATIONS ======================

admin.site.register(Supplier)
admin.site.register(ItemCategory)
admin.site.register(StockCount)
admin.site.register(StockCountItem)


# ====================== CUSTOM ADMIN CLASSES ======================

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'supplier', 'current_quantity', 
                   'reorder_level', 'is_low_stock', 'is_active']
    list_filter = ['category', 'supplier', 'status', 'is_active']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['available_quantity']

    def is_low_stock(self, obj):
        return obj.current_quantity <= obj.reorder_level
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_number', 'transaction_type', 'item', 'quantity', 
                   'transaction_date', 'performed_by', 'status']
    list_filter = ['transaction_type', 'status']
    search_fields = ['transaction_number', 'item__name']
    readonly_fields = ['transaction_number', 'total_cost']
    date_hierarchy = 'transaction_date'


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'order_date', 'status', 'total_amount']
    list_filter = ['status', 'payment_mode']
    search_fields = ['po_number', 'supplier__name']
    readonly_fields = ['po_number', 'total_amount']
    date_hierarchy = 'order_date'


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'item', 'quantity', 'unit_price', 'line_total']
    list_filter = ['purchase_order__status']
    search_fields = ['item__name']


# ====================== INLINE EDITING (Optional but useful) ======================

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


# Improve PurchaseOrder with inline items
PurchaseOrderAdmin.inlines = [PurchaseOrderItemInline]