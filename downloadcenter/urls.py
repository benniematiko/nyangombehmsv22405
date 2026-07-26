from django.urls import path
from . import views

app_name = 'downloadcenter'

urlpatterns = [
    path('', views.downloadcenter_home, name='downloadcenter_home'),
]