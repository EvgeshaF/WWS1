from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    # Основные URL для управления компанией
    path('register/', views.register_company, name='register_company'),
    path('info/', views.company_info, name='company_info'),
    path('edit/', views.edit_company, name='edit_company'),
    path('delete/', views.delete_company, name='delete_company'),

    # API endpoints для работы с данными компании
    path('stats/', views.company_stats_json, name='company_stats_json'),
    path('status/', views.company_status, name='company_status'),
    path('export/', views.export_company_data, name='export_company_data'),
    path('import/', views.import_company_data, name='import_company_data'),
    path('validate/', views.company_validation_check, name='company_validation_check'),
    path('set-primary/', views.set_primary_company, name='set_primary_company'),

    # Debug endpoint (только в DEBUG режиме)
    path('debug/', views.debug_company_data, name='debug_company_data'),

    # Алиасы для совместимости со старыми URL
    path('list/', views.company_info, name='company_list'),  # Перенаправляем на info
]