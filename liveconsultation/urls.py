from django.urls import path
from . import views

app_name = 'liveconsultation'

urlpatterns = [
    path('', views.liveconsultation_home, name='liveconsultation_home'),
    path('meetings/', views.livemeeting_home, name='livemeeting_home'),
]