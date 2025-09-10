# companies/urls.py - РАСШИРЕННАЯ ВЕРСИЯ
from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    # Регистрация компании
    path('register/', views.register_company, name='register_company'),

    # Просмотр списка компаний (в нашем случае - единственной компании)
    path('list/', views.company_list, name='company_list'),

    # Детали компании
    path('details/', views.company_details, name='company_details'),

    # Редактирование компании
    path('edit/', views.company_edit, name='company_edit'),

    # Удаление компании (с подтверждением)
    path('delete/', views.company_delete, name='company_delete'),

    # AJAX/API endpoints
    path('api/status/', views.company_status_api, name='company_status_api'),
    path('api/validate/', views.validate_company_data, name='validate_company_data'),
]