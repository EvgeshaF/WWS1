from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('register/', views.register_company, name='register_company'),
    path('info/', views.company_info, name='company_info'),
    path('edit/', views.edit_company, name='edit_company'),
    path('delete/', views.delete_company, name='delete_company'),

    # Алиасы для совместимости
    path('list/', views.company_info, name='company_list'),  # Перенаправляем на info
]