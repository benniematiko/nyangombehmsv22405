from django.urls import path
from . import views

app_name = 'laboratory'

urlpatterns = [
    path('', views.laboratory_home, name='laboratory_home'),
    path('generate-bill/', views.laboratory_generate_bill_view, name='generate_bill'),
    path('add-test/', views.add_test, name='add_test'),
    path('test/<int:test_id>/', views.test_detail, name='test_detail'),
    path('test/<int:test_id>/update-result/', views.update_test_result, name='update_test_result'),
    path('test/<int:test_id>/create-invoice/', views.create_invoice, name='create_invoice'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:invoice_id>/record-payment/', views.record_payment, name='record_payment'),
    path('test/<int:test_id>/delete/', views.delete_test, name='delete_test'),
]