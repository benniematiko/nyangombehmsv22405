from django.urls import path
from . import views

# This matches the 'dashboard' namespace from your settings redirect rules
app_name = 'dashboard' 

urlpatterns = [
    # For now, this points to an index or home view inside the dashboard app
    # path('', views.dashboard_home, name='home'), 
]