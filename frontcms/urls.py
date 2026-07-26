from django.urls import path
from . import views

app_name = 'frontcms'

urlpatterns = [
    path('', views.frontcms_home, name='frontcms_home'),
]