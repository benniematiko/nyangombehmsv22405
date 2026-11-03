from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, Q, F
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta

from .models import (
    Supplier, ItemCategory, InventoryItem, StockTransaction,
    StockCount, StockCountItem, PurchaseOrder, PurchaseOrderItem
)


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def inventory_home(request):
    """
    Inventory dashboard showing summary statistics.
    """
    # Counts
    total_items = InventoryItem.objects.filter(is_active=True).count()
    low_stock_items = InventoryItem.objects.filter(
        current_quantity__lte=F('reorder_level'),
        is_active=True
    ).count()
    out_of_stock_items = InventoryItem.objects.filter(
        current_quantity=0,
        is_active=True
    ).count()
    total_categories = ItemCategory.objects.filter(is_active=True).count()
    total_suppliers = Supplier.objects.filter(is_active=True).count()
    
    # Recent transactions
    recent_transactions = StockTransaction.objects.select_related(
        'item', 'performed_by'
    ).order_by('-transaction_date')[:10]
    
    # Pending purchase orders
    pending_pos = PurchaseOrder.objects.filter(
        status__in=['Draft', 'Submitted', 'Approved']
    ).count()
    
    context = {
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'out_of_stock_items': out_of_stock_items,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'pending_pos': pending_pos,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'inventory/inventory_home.html', context)




@login_required
def item_stock_list(request):
    """
    Item Stock List page.
    """
    items = (
        InventoryItem.objects
        .select_related('category', 'supplier')
        .filter(is_active=True)
        .order_by('name')
    )
    context = {
        'items': items,
        'categories': ItemCategory.objects.filter(is_active=True),
        'suppliers': Supplier.objects.filter(is_active=True),
    }
    return render(request, 'inventory/item_stock_list.html', context)

    