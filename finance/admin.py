from django.contrib import admin
from .models import FinanceTransaction, Expense, ExpenseItem


@admin.register(FinanceTransaction)
class FinanceTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_type', 'amount', 'category', 'transaction_date', 'status', 'created_by']
    list_filter = ['transaction_type', 'status', 'transaction_date']
    search_fields = ['description', 'reference', 'category']
    date_hierarchy = 'transaction_date'


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['voucher_number', 'payee_name', 'category', 'net_amount', 'expense_date', 'status']
    list_filter = ['status', 'category', 'expense_date']
    search_fields = ['voucher_number', 'payee_name', 'description']
    date_hierarchy = 'expense_date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ExpenseItem)
class ExpenseItemAdmin(admin.ModelAdmin):
    list_display = ['expense', 'name', 'unit_price', 'quantity', 'row_total']
    list_filter = ['expense__category']
    search_fields = ['name', 'gl_code']