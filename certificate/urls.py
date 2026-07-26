from django.urls import path
from . import views

app_name = 'certificate'

urlpatterns = [
    path('', views.certificate_home, name='certificate_home'),
]