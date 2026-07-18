from django.urls import path
from . import views  # Imports your local views.py containing login_view and logout_view

app_name = 'accounts'

urlpatterns = [
    # 1. Custom validation Login handler view
    path('login/', views.login_view, name='login'),
    
    # 2. Custom "Are you sure?" confirmation template page view
    path('logout/', views.logout_view, name='logout_confirm'),
    
    # 3. Secure execution path triggered by the confirmation form countdown timer
    path('logout/execute/', views.logout_execute_view, name='logout'),
]