# companies/urls.py
from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('register/', views.register_company, name='register_company'),
    path('registration-success/', views.registration_success, name='registration_success'),
    path('list/', views.company_list, name='company_list'),
]