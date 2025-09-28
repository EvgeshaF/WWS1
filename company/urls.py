# company/urls.py - ОБНОВЛЕНО для новой структуры views
from django.urls import path
from . import views  # Импортируем основной views.py, который реэкспортирует все

# Альтернативно можно импортировать напрямую из подкаталога:
# from .views import registration, crud, extra

app_name = 'company'

urlpatterns = [
    # Многошаговая регистрация компании (теперь 5 шагов вместо 6)
    path('register/', views.register_company, name='register_company'),
    path('register/step1/', views.register_company_step1, name='register_company_step1'),
    path('register/step2/', views.register_company_step2, name='register_company_step2'),
    path('register/step3/', views.register_company_step3, name='register_company_step3'),
    path('register/step4/', views.register_company_step4, name='register_company_step4'),
    path('register/step5/', views.register_company_step5, name='register_company_step5'),

    # Управление компанией
    path('info/', views.company_info, name='company_info'),
    path('edit/', views.edit_company, name='edit_company'),

    # Редактирование отдельных шагов
    path('edit/step1/', views.edit_company_step1, name='edit_company_step1'),
    path('edit/step2/', views.edit_company_step2, name='edit_company_step2'),
    path('edit/step3/', views.edit_company_step3, name='edit_company_step3'),
    path('edit/step4/', views.edit_company_step4, name='edit_company_step4'),
    path('edit/step5/', views.edit_company_step5, name='edit_company_step5'),

    path('delete/', views.delete_company, name='delete_company'),

    # API endpoints
    path('stats/', views.company_stats_json, name='company_stats_json'),
    path('status/', views.company_status, name='company_status'),
    path('export/', views.export_company_data, name='export_company_data'),
    path('import/', views.import_company_data, name='import_company_data'),
    path('validate/', views.company_validation_check, name='company_validation_check'),
    path('set-primary/', views.set_primary_company, name='set_primary_company'),

    # Debug endpoint
    path('debug/', views.debug_company_data, name='debug_company_data'),
]