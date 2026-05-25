from django.urls import path
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    # Django handles the backend validation automatically; we just give it a template
    path('login/', auth_views.LoginView.as_callable(template_name='accounts/login.html') if hasattr(auth_views.LoginView, 'as_callable') else auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_callable() if hasattr(auth_views.LogoutView, 'as_callable') else auth_views.LogoutView.as_view(), name='logout'),
]