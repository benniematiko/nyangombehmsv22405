from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.expense_list, name='expenses'),
    path('addexpense/', views.add_expense, name='addexpense'),
    path('addincome/', views.add_income, name='add_income'),      # ← fixed name
    path('voucher/<int:expense_id>/details/', views.expense_details, name='expense_details'),
    path('voucher/<int:expense_id>/edit/', views.edit_expense, name='edit_expense'),
    path('voucher/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    path('voucher/<int:expense_id>/print/', views.print_expense, name='print_expense'),
    path('voucher/<int:expense_id>/disburse/', views.disburse_expense, name='disburse_expense'),
]