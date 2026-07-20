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


# ============================================================
# ITEM MANAGEMENT
# ============================================================

@login_required
def item_list(request):
    """
    List all inventory items with search and filtering.
    """
    items = InventoryItem.objects.select_related('category', 'supplier').filter(is_active=True)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        items = items.filter(category_id=category_id)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        items = items.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(items, 20)
    page = request.GET.get('page', 1)
    items = paginator.get_page(page)
    
    categories = ItemCategory.objects.filter(is_active=True)
    
    context = {
        'items': items,
        'categories': categories,
        'search_query': search_query,
        'category_id': category_id,
        'status_filter': status_filter,
    }
    return render(request, 'inventory/item_list.html', context)


@login_required
def item_detail(request, item_id):
    """
    View item details and transaction history.
    """
    item = get_object_or_404(InventoryItem.objects.select_related('category', 'supplier'), id=item_id)
    transactions = StockTransaction.objects.filter(item=item).order_by('-transaction_date')[:20]
    
    context = {
        'item': item,
        'transactions': transactions,
    }
    return render(request, 'inventory/item_detail.html', context)


@login_required
def item_add(request):
    """
    Add a new inventory item.
    """
    categories = ItemCategory.objects.filter(is_active=True)
    suppliers = Supplier.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            category_id = request.POST.get('category')
            supplier_id = request.POST.get('supplier')
            unit = request.POST.get('unit', 'Each')
            reorder_level = request.POST.get('reorder_level', 10)
            reorder_quantity = request.POST.get('reorder_quantity', 50)
            cost_price = request.POST.get('cost_price', 0)
            selling_price = request.POST.get('selling_price', 0)
            tax_rate = request.POST.get('tax_rate', 0)
            description = request.POST.get('description', '')
            
            # Validation
            if not name:
                messages.error(request, "Item name is required.")
                return redirect('inventory:item_add')
            
            if not category_id:
                messages.error(request, "Please select a category.")
                return redirect('inventory:item_add')
            
            category = get_object_or_404(ItemCategory, id=category_id)
            supplier = None
            if supplier_id:
                supplier = get_object_or_404(Supplier, id=supplier_id)
            
            # Create item
            item = InventoryItem.objects.create(
                name=name,
                category=category,
                supplier=supplier,
                unit=unit,
                reorder_level=reorder_level,
                reorder_quantity=reorder_quantity,
                cost_price=cost_price,
                selling_price=selling_price,
                tax_rate=tax_rate,
                description=description,
                current_quantity=0,
                is_active=True,
            )
            
            messages.success(request, f"Item '{name}' added successfully!")
            return redirect('inventory:item_detail', item_id=item.id)
            
        except Exception as e:
            messages.error(request, f"Error adding item: {str(e)}")
    
    context = {
        'categories': categories,
        'suppliers': suppliers,
    }
    return render(request, 'inventory/item_add.html', context)


@login_required
def item_edit(request, item_id):
    """
    Edit an existing inventory item.
    """
    item = get_object_or_404(InventoryItem, id=item_id)
    categories = ItemCategory.objects.filter(is_active=True)
    suppliers = Supplier.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            item.name = request.POST.get('name')
            item.category_id = request.POST.get('category')
            item.supplier_id = request.POST.get('supplier') or None
            item.unit = request.POST.get('unit', 'Each')
            item.reorder_level = request.POST.get('reorder_level', 10)
            item.reorder_quantity = request.POST.get('reorder_quantity', 50)
            item.cost_price = request.POST.get('cost_price', 0)
            item.selling_price = request.POST.get('selling_price', 0)
            item.tax_rate = request.POST.get('tax_rate', 0)
            item.description = request.POST.get('description', '')
            item.is_active = request.POST.get('is_active') == 'on'
            item.save()
            
            messages.success(request, f"Item '{item.name}' updated successfully!")
            return redirect('inventory:item_detail', item_id=item.id)
            
        except Exception as e:
            messages.error(request, f"Error updating item: {str(e)}")
    
    context = {
        'item': item,
        'categories': categories,
        'suppliers': suppliers,
    }
    return render(request, 'inventory/item_edit.html', context)


@login_required
def item_delete(request, item_id):
    """
    Delete an inventory item.
    """
    if request.method == 'POST':
        item = get_object_or_404(InventoryItem, id=item_id)
        item.delete()
        messages.success(request, "Item deleted successfully!")
    return redirect('inventory:item_list')


# ============================================================
# CATEGORY MANAGEMENT
# ============================================================

@login_required
def category_list(request):
    """
    List and manage item categories.
    """
    categories = ItemCategory.objects.all().order_by('name')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name:
            ItemCategory.objects.create(name=name, description=description)
            messages.success(request, f"Category '{name}' added successfully!")
            return redirect('inventory:category_list')
    
    context = {'categories': categories}
    return render(request, 'inventory/category_list.html', context)


@login_required
def category_add(request):
    """
    Add a new category.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name:
            ItemCategory.objects.create(name=name, description=description)
            messages.success(request, f"Category '{name}' added successfully!")
            return redirect('inventory:category_list')
    
    return render(request, 'inventory/category_add.html')


# ============================================================
# SUPPLIER MANAGEMENT
# ============================================================

@login_required
def supplier_list(request):
    """
    List all suppliers.
    """
    suppliers = Supplier.objects.filter(is_active=True).order_by('name')
    
    if request.method == 'POST':
        try:
            supplier = Supplier.objects.create(
                name=request.POST.get('name'),
                supplier_type=request.POST.get('supplier_type', 'General'),
                contact_person=request.POST.get('contact_person'),
                phone=request.POST.get('phone'),
                email=request.POST.get('email'),
                address=request.POST.get('address'),
                tax_id=request.POST.get('tax_id'),
                website=request.POST.get('website'),
                notes=request.POST.get('notes', ''),
                is_active=True,
            )
            messages.success(request, f"Supplier '{supplier.name}' added successfully!")
            return redirect('inventory:supplier_list')
            
        except Exception as e:
            messages.error(request, f"Error adding supplier: {str(e)}")
    
    context = {'suppliers': suppliers}
    return render(request, 'inventory/supplier_list.html', context)


@login_required
def supplier_add(request):
    """
    Add a new supplier.
    """
    if request.method == 'POST':
        try:
            supplier = Supplier.objects.create(
                name=request.POST.get('name'),
                supplier_type=request.POST.get('supplier_type', 'General'),
                contact_person=request.POST.get('contact_person'),
                phone=request.POST.get('phone'),
                email=request.POST.get('email'),
                address=request.POST.get('address'),
                tax_id=request.POST.get('tax_id'),
                website=request.POST.get('website'),
                notes=request.POST.get('notes', ''),
                is_active=True,
            )
            messages.success(request, f"Supplier '{supplier.name}' added successfully!")
            return redirect('inventory:supplier_list')
            
        except Exception as e:
            messages.error(request, f"Error adding supplier: {str(e)}")
    
    return render(request, 'inventory/supplier_add.html')


# ============================================================
# STOCK MOVEMENTS
# ============================================================

@login_required
def stock_transactions(request):
    """
    View all stock transactions.
    """
    transactions = StockTransaction.objects.select_related('item', 'performed_by').all().order_by('-transaction_date')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        transactions = transactions.filter(
            Q(transaction_number__icontains=search_query) |
            Q(item__name__icontains=search_query) |
            Q(reference_number__icontains=search_query)
        )
    
    # Filter by type
    trans_type = request.GET.get('type', '')
    if trans_type:
        transactions = transactions.filter(transaction_type=trans_type)
    
    # Pagination
    paginator = Paginator(transactions, 20)
    page = request.GET.get('page', 1)
    transactions = paginator.get_page(page)
    
    context = {
        'transactions': transactions,
        'search_query': search_query,
        'trans_type': trans_type,
    }
    return render(request, 'inventory/stock_transactions.html', context)


@login_required
def stock_add(request):
    """
    Add stock (purchase/receipt).
    """
    items = InventoryItem.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                item_id = request.POST.get('item')
                quantity = int(request.POST.get('quantity', 0))
                unit_cost = Decimal(request.POST.get('unit_cost', 0))
                batch_number = request.POST.get('batch_number', '')
                expiry_date = request.POST.get('expiry_date')
                reference_number = request.POST.get('reference_number', '')
                notes = request.POST.get('notes', '')
                
                if not item_id or quantity <= 0:
                    messages.error(request, "Please select an item and enter a valid quantity.")
                    return redirect('inventory:stock_add')
                
                item = get_object_or_404(InventoryItem, id=item_id)
                
                # Create transaction
                StockTransaction.objects.create(
                    transaction_type='Purchase',
                    item=item,
                    quantity=quantity,
                    unit_cost=unit_cost,
                    batch_number=batch_number,
                    expiry_date=expiry_date if expiry_date else None,
                    reference_number=reference_number,
                    reference_notes=notes,
                    performed_by=request.user,
                    status='Completed',
                    transaction_date=timezone.now(),
                )
                
                # Update item quantity
                item.current_quantity += quantity
                item.save()
                
                messages.success(request, f"{quantity} units of '{item.name}' added to stock!")
                return redirect('inventory:stock_transactions')
                
        except Exception as e:
            messages.error(request, f"Error adding stock: {str(e)}")
    
    context = {'items': items}
    return render(request, 'inventory/stock_add.html', context)


@login_required
def stock_issue(request):
    """
    Issue stock (sale/usage).
    """
    items = InventoryItem.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                item_id = request.POST.get('item')
                quantity = int(request.POST.get('quantity', 0))
                reference_number = request.POST.get('reference_number', '')
                notes = request.POST.get('notes', '')
                
                if not item_id or quantity <= 0:
                    messages.error(request, "Please select an item and enter a valid quantity.")
                    return redirect('inventory:stock_issue')
                
                item = get_object_or_404(InventoryItem, id=item_id)
                
                # Check stock availability
                if item.current_quantity < quantity:
                    messages.error(request, f"Insufficient stock! Available: {item.current_quantity}")
                    return redirect('inventory:stock_issue')
                
                # Create transaction
                StockTransaction.objects.create(
                    transaction_type='Issue',
                    item=item,
                    quantity=quantity,
                    unit_cost=item.cost_price,
                    reference_number=reference_number,
                    reference_notes=notes,
                    performed_by=request.user,
                    status='Completed',
                    transaction_date=timezone.now(),
                )
                
                # Update item quantity
                item.current_quantity -= quantity
                item.save()
                
                messages.success(request, f"{quantity} units of '{item.name}' issued!")
                return redirect('inventory:stock_transactions')
                
        except Exception as e:
            messages.error(request, f"Error issuing stock: {str(e)}")
    
    context = {'items': items}
    return render(request, 'inventory/stock_issue.html', context)


@login_required
def stock_adjust(request):
    """
    Adjust stock (manual adjustment).
    """
    items = InventoryItem.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                item_id = request.POST.get('item')
                adjustment_type = request.POST.get('adjustment_type')  # 'increase' or 'decrease'
                quantity = int(request.POST.get('quantity', 0))
                notes = request.POST.get('notes', '')
                
                if not item_id or quantity <= 0:
                    messages.error(request, "Please select an item and enter a valid quantity.")
                    return redirect('inventory:stock_adjust')
                
                item = get_object_or_404(InventoryItem, id=item_id)
                
                if adjustment_type == 'decrease' and item.current_quantity < quantity:
                    messages.error(request, f"Insufficient stock! Available: {item.current_quantity}")
                    return redirect('inventory:stock_adjust')
                
                # Create transaction
                StockTransaction.objects.create(
                    transaction_type='Adjustment',
                    item=item,
                    quantity=quantity,
                    unit_cost=item.cost_price,
                    reference_notes=f"Adjustment: {adjustment_type} - {notes}",
                    performed_by=request.user,
                    status='Completed',
                    transaction_date=timezone.now(),
                )
                
                # Update item quantity
                if adjustment_type == 'increase':
                    item.current_quantity += quantity
                else:
                    item.current_quantity -= quantity
                item.save()
                
                messages.success(request, f"Stock adjusted for '{item.name}'!")
                return redirect('inventory:stock_transactions')
                
        except Exception as e:
            messages.error(request, f"Error adjusting stock: {str(e)}")
    
    context = {'items': items}
    return render(request, 'inventory/stock_adjust.html', context)


# ============================================================
# PURCHASE ORDERS
# ============================================================

@login_required
def purchase_order_list(request):
    """
    List all purchase orders.
    """
    pos = PurchaseOrder.objects.select_related('supplier', 'created_by').all().order_by('-order_date')
    
    search_query = request.GET.get('search', '')
    if search_query:
        pos = pos.filter(
            Q(po_number__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        pos = pos.filter(status=status_filter)
    
    paginator = Paginator(pos, 20)
    page = request.GET.get('page', 1)
    pos = paginator.get_page(page)
    
    context = {
        'pos': pos,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'inventory/purchase_order_list.html', context)


@login_required
def purchase_order_add(request):
    """
    Add a new purchase order.
    """
    suppliers = Supplier.objects.filter(is_active=True)
    items = InventoryItem.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                supplier_id = request.POST.get('supplier')
                expected_delivery = request.POST.get('expected_delivery')
                payment_mode = request.POST.get('payment_mode', 'Cash')
                payment_terms = request.POST.get('payment_terms', '')
                notes = request.POST.get('notes', '')
                
                if not supplier_id:
                    messages.error(request, "Please select a supplier.")
                    return redirect('inventory:purchase_order_add')
                
                supplier = get_object_or_404(Supplier, id=supplier_id)
                
                po = PurchaseOrder.objects.create(
                    supplier=supplier,
                    expected_delivery=expected_delivery if expected_delivery else None,
                    payment_mode=payment_mode,
                    payment_terms=payment_terms,
                    notes=notes,
                    created_by=request.user,
                    status='Draft',
                )
                
                # Get item data from POST
                item_ids = request.POST.getlist('item_id[]')
                quantities = request.POST.getlist('quantity[]')
                unit_prices = request.POST.getlist('unit_price[]')
                tax_rates = request.POST.getlist('tax_rate[]')
                
                for i, item_id in enumerate(item_ids):
                    if item_id and int(quantities[i]) > 0:
                        item = get_object_or_404(InventoryItem, id=item_id)
                        PurchaseOrderItem.objects.create(
                            purchase_order=po,
                            item=item,
                            quantity=int(quantities[i]),
                            unit_price=Decimal(unit_prices[i] or 0),
                            tax_rate=Decimal(tax_rates[i] or 0),
                        )
                
                messages.success(request, f"Purchase Order {po.po_number} created successfully!")
                return redirect('inventory:purchase_order_detail', po_id=po.id)
                
        except Exception as e:
            messages.error(request, f"Error creating purchase order: {str(e)}")
    
    context = {
        'suppliers': suppliers,
        'items': items,
    }
    return render(request, 'inventory/purchase_order_add.html', context)


@login_required
def purchase_order_detail(request, po_id):
    """
    View purchase order details.
    """
    po = get_object_or_404(PurchaseOrder.objects.select_related('supplier', 'created_by'), id=po_id)
    items = PurchaseOrderItem.objects.filter(purchase_order=po).select_related('item')
    
    context = {
        'po': po,
        'items': items,
    }
    return render(request, 'inventory/purchase_order_detail.html', context)


# ============================================================
# STOCK COUNTS
# ============================================================

@login_required
def stock_count_list(request):
    """
    List all stock counts.
    """
    stock_counts = StockCount.objects.select_related('counted_by').all().order_by('-count_date')
    
    paginator = Paginator(stock_counts, 20)
    page = request.GET.get('page', 1)
    stock_counts = paginator.get_page(page)
    
    context = {
        'stock_counts': stock_counts,
    }
    return render(request, 'inventory/stock_count_list.html', context)


@login_required
def stock_count_add(request):
    """
    Add a new stock count.
    """
    if request.method == 'POST':
        try:
            count = StockCount.objects.create(
                counted_by=request.user,
                notes=request.POST.get('notes', ''),
                status='In Progress',
            )
            
            # Add all items to the count
            items = InventoryItem.objects.filter(is_active=True)
            for item in items:
                StockCountItem.objects.create(
                    stock_count=count,
                    item=item,
                    system_quantity=item.current_quantity,
                    physical_quantity=item.current_quantity,  # Default to system quantity
                )
            
            messages.success(request, f"Stock count {count.count_number} created successfully!")
            return redirect('inventory:stock_count_list')
            
        except Exception as e:
            messages.error(request, f"Error creating stock count: {str(e)}")
    
    return render(request, 'inventory/stock_count_add.html')


# ============================================================
# REPORTS
# ============================================================

@login_required
def low_stock_report(request):
    """
    Report of items with low stock.
    """
    items = InventoryItem.objects.filter(
        current_quantity__lte=F('reorder_level'),
        is_active=True
    ).order_by('current_quantity')
    
    context = {'items': items}
    return render(request, 'inventory/low_stock_report.html', context)


@login_required
def expiring_items_report(request):
    """
    Report of items with expiring stock.
    """
    # Get items with expiry dates from transactions
    # This is a simplified version - you'd need to track expiry in stock
    expired_items = StockTransaction.objects.filter(
        expiry_date__lte=timezone.now().date() + timedelta(days=30),
        transaction_type='Purchase',
        status='Completed'
    ).select_related('item').distinct('item')
    
    context = {'expired_items': expired_items}
    return render(request, 'inventory/expiring_items_report.html', context)


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
    
    # Low stock items list (for the dashboard widget)
    low_stock_items_list = InventoryItem.objects.filter(
        current_quantity__lte=F('reorder_level'),
        is_active=True
    ).order_by('current_quantity')[:10]
    
    context = {
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'out_of_stock_items': out_of_stock_items,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'pending_pos': pending_pos,
        'recent_transactions': recent_transactions,
        'low_stock_items_list': low_stock_items_list,  # ← Add this
    }
    return render(request, 'inventory/inventory_home.html', context)