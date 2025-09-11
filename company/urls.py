# company/urls.py - Упрощенные URLs для одной компании

from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    # Регистрация компании (только если еще не создана)
    path('register/', views.register_company, name='register_company'),

    # Просмотр данных компании
    path('details/', views.company_details, name='company_details'),

    # Редактирование данных компании
    path('edit/', views.edit_company, name='edit_company'),
]