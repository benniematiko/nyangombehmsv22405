from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal

# Models
from .models import Expense, ExpenseItem, FinanceTransaction


@login_required
def expense_list(request):
    """Display list of all expenses"""
    expenses = Expense.objects.all().order_by('-expense_date', '-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        expenses = expenses.filter(
            Q(payee_name__icontains=search_query) |
            Q(voucher_number__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(expenses, int(request.GET.get('per_page', 20)))
    page_obj = paginator.get_page(request.GET.get('page', 1))
    
    context = {
        'expenses': page_obj,
        'total_records': paginator.count,
        'search_query': search_query,
    }
    return render(request, 'finance/expense.html', context)


@login_required
def add_expense(request):
    """Add a new expense"""
    if request.method == 'POST':
        try:
            # Auto-generate voucher number if not provided
            voucher_number = request.POST.get('voucher_number', '').strip()
            if not voucher_number:
                from django.utils import timezone
                year = timezone.now().year
                last = Expense.objects.order_by('-id').first()
                next_num = (last.id + 1) if last else 1
                voucher_number = f"EXP-{year}-{next_num:04d}"

            expense = Expense.objects.create(
                payee_name=request.POST.get('payee_name'),
                voucher_number=voucher_number,
                category=request.POST.get('category'),
                expense_date=request.POST.get('expense_date') or timezone.now().date(),
                net_amount=request.POST.get('net_amount'),
                payment_method=request.POST.get('payment_method', 'Cash'),
                description=request.POST.get('description'),
                notes=request.POST.get('description'),
                reference_code=request.POST.get('reference_code', ''),
                created_by=request.user,
                status='Pending'
            )

            if request.FILES.get('attachment'):
                expense.attachment = request.FILES['attachment']
                expense.save()

            # Mirror to FinanceTransaction for dashboard totals
            FinanceTransaction.objects.create(
                transaction_type='Expense',
                category=expense.category,
                amount=expense.net_amount,
                total_amount=expense.net_amount,
                description=f"{expense.voucher_number} — {expense.payee_name}",
                reference=expense.voucher_number,
                payment_date=expense.expense_date,
                status='Completed',
                created_by=request.user
            )

            messages.success(request, f"Expense {expense.voucher_number} recorded successfully!")
            return redirect('finance:expenses')

        except Exception as e:
            messages.error(request, f"Error recording expense: {str(e)}")
            return redirect('finance:expenses')

    return redirect('finance:expenses')


@login_required
def add_income(request):
    """Add income record"""
    if request.method == 'POST':
        try:
            # Create income transaction
            transaction = FinanceTransaction.objects.create(
                transaction_type='Income',
                category=request.POST.get('category', 'other'),
                amount=request.POST.get('amount'),
                total_amount=request.POST.get('amount'),
                description=request.POST.get('description'),
                reference=request.POST.get('reference', ''),
                payment_date=request.POST.get('transaction_date') or timezone.now().date(),
                status='Completed',
                created_by=request.user
            )
            
            messages.success(request, f"Income of {transaction.amount} recorded successfully!")
            return redirect(request.META.get('HTTP_REFERER', 'finance:expense_list'))
            
        except Exception as e:
            messages.error(request, f"Error recording income: {str(e)}")
            return redirect('finance:expense_list')
    
    # GET request - render income form
    context = {
        'categories': FinanceTransaction.CATEGORY_CHOICES if hasattr(FinanceTransaction, 'CATEGORY_CHOICES') else [],
    }
    return render(request, 'finance/add_income.html', context)


@login_required
def expense_details(request, expense_id):
    """Get expense details for AJAX modal"""
    try:
        expense = get_object_or_404(Expense, id=expense_id)
        
        # Get expense items if they exist
        items = ExpenseItem.objects.filter(expense=expense)
        
        items_list = []
        for item in items:
            items_list.append({
                'id': item.id,
                'classification': item.classification or 'General',
                'name': item.name or 'Item',
                'gl_code': item.gl_code or '—',
                'unit_price': float(item.unit_price) if item.unit_price else 0,
                'quantity': item.quantity or 1,
                'tax_percent': float(item.tax_percent) if item.tax_percent else 0,
                'row_total': float(item.row_total) if item.row_total else 0,
            })
        
        # If no items, create a default one
        if not items_list:
            items_list.append({
                'id': None,
                'classification': expense.category or 'General',
                'name': expense.description or 'Expense Item',
                'gl_code': '—',
                'unit_price': float(expense.net_amount) if expense.net_amount else 0,
                'quantity': 1,
                'tax_percent': 0,
                'row_total': float(expense.net_amount) if expense.net_amount else 0,
            })
        
        response_data = {
            'success': True,
            'expense': {
                'id': expense.id,
                'voucher_number': expense.voucher_number,
                'payee_name': expense.payee_name,
                'category': expense.category,
                'date': expense.expense_date.strftime('%d/%m/%Y %H:%M') if expense.expense_date else '',
                'net_amount': float(expense.net_amount) if expense.net_amount else 0,
                'gross_amount': float(expense.gross_amount) if expense.gross_amount else float(expense.net_amount) if expense.net_amount else 0,
                'tax_amount': float(expense.tax_amount) if expense.tax_amount else 0,
                'payment_method': expense.payment_method or 'Bank Transfer',
                'reference_code': expense.reference_code or '—',
                'notes': expense.notes or expense.description or 'No notes',
                'description': expense.description or expense.notes or 'No description',
                'justification': expense.description or 'No justification',
                'status': expense.status or 'Pending',
                'created_by': expense.created_by.get_full_name() if expense.created_by else 'System',
                'items': items_list,
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def edit_expense(request, expense_id):
    """Edit an existing expense"""
    expense = get_object_or_404(Expense, id=expense_id)
    
    if request.method == 'POST':
        try:
            expense.payee_name = request.POST.get('payee_name', expense.payee_name)
            expense.voucher_number = request.POST.get('voucher_number', expense.voucher_number)
            expense.category = request.POST.get('category', expense.category)
            expense.expense_date = request.POST.get('expense_date') or expense.expense_date
            expense.net_amount = request.POST.get('net_amount', expense.net_amount)
            expense.payment_method = request.POST.get('payment_method', expense.payment_method)
            expense.description = request.POST.get('description', expense.description)
            expense.notes = request.POST.get('description', expense.notes)
            expense.reference_code = request.POST.get('reference_code', expense.reference_code)
            expense.save()
            
            messages.success(request, f"Expense '{expense.voucher_number}' updated successfully!")
            return redirect('finance:expense_list')
            
        except Exception as e:
            messages.error(request, f"Error updating expense: {str(e)}")
            return redirect('finance:expense_list')
    
    context = {'expense': expense}
    return render(request, 'finance/edit_expense.html', context)


@login_required
def delete_expense(request, expense_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        expense = get_object_or_404(Expense, id=expense_id)
        voucher_number = expense.voucher_number

        # Delete the mirrored FinanceTransaction so dashboard total updates
        FinanceTransaction.objects.filter(
            transaction_type='Expense',
            reference=voucher_number
        ).delete()

        expense.delete()

        return JsonResponse({'success': True, 'message': f'Expense {voucher_number} deleted successfully'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def print_expense(request, expense_id):
    """Print expense voucher"""
    expense = get_object_or_404(Expense, id=expense_id)
    items = ExpenseItem.objects.filter(expense=expense)
    
    context = {
        'expense': expense,
        'items': items,
        'is_print': True,
    }
    return render(request, 'finance/print_expense.html', context)


@login_required
def disburse_expense(request, expense_id):
    """Disburse funds for an expense"""
    expense = get_object_or_404(Expense, id=expense_id)
    
    if request.method == 'POST':
        try:
            expense.status = 'Approved'
            expense.disbursed_at = timezone.now()
            expense.disbursed_by = request.user
            expense.save()
            
            messages.success(request, f"Funds disbursed for '{expense.voucher_number}' successfully!")
            return redirect('finance:expense_list')
            
        except Exception as e:
            messages.error(request, f"Error disbursing funds: {str(e)}")
            return redirect('finance:expense_list')
    
    context = {'expense': expense}
    return render(request, 'finance/disburse_expense.html', context)