# radiology/urls.py
from django.urls import path
from . import views

app_name = 'radiology'

urlpatterns = [
    path('', views.radiology_home, name='radiology_home'),
    
    # 1. Fixed previously:
    path('generate-bill/', views.generate_bill_view, name='radiologygenerate_bill'), 
    
    # 2. FIX THIS LINE: Added the underscore to match line 452 in your template
    path('investigations/', views.investigations_view, name='radiology_investigations'),
    
    path('invoice/<int:invoice_id>/details/', views.invoice_details, name='invoice_detail'),
    path('invoice/<int:invoice_id>/delete/', views.invoice_delete, name='invoice_delete'),
]