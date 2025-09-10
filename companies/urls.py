# companies/urls.py
from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('register/', views.register_company, name='register_company'),
    path('list/', views.company_list, name='company_list'),
]