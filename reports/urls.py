# reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'  # This creates the 'reports' namespace

urlpatterns = [
    path('', views.finance, name='finance'),  # This creates 'reports:reports_home'
    path('appointments/', views.appointments, name='appointments'), 
    path('opd/', views.opd, name='opd'), 
    path('ipd/', views.ipd, name='ipd'), 
    path('pharmacy/', views.pharmacy, name='pharmacy'), 
    path('laboratory/', views.laboratory, name='laboratory'), 
    path('radiology/', views.radiology, name='radiology'), 
    path('bloodbank/', views.bloodbank, name='bloodbank'), 
    path('ambulance/', views.ambulance, name='ambulance'), 
    path('birthdeath/', views.birthdeath, name='birthdeath'), 
    path('humanresource/', views.humanresource, name='humanresource'), 
    path('insurance/', views.insurance, name='insurance'), 
    path('inventory/', views.inventory, name='inventory'), 
    path('liveconsultation/', views.live_consultation, name='live_consultation'), 
    path('log/', views.log, name='log'), 
    path('ot/', views.ot, name='ot'), 
    path('patient/', views.patient, name='patient'), 




    path('dailytransaction/', views.daily_transaction, name='daily_transaction'),  
    path('alltransaction/', views.all_transaction, name='all_transaction'), 

    path('incomereport/', views.income_report, name='income_report'),  
    path('incomegroup/', views.income_group, name='income_group'),  
    path('expensereport/', views.expense_report, name='expense_report'),  
    path('expensegroup/', views.expense_group, name='expense_group'),  
    path('referralreport/', views.referral_report, name='referral_report'), 

    path('processingtransaction/', views.processing_transaction, name='processing_transaction'),  

    path('patientbill/', views.patient_bill, name='patient_bill'),  


    path('generatefinancialstatement/', views.generate_financial_statement, name='generate_financial_statement'),  


    
]