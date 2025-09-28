# users/urls.py - ОБНОВЛЕННЫЕ URL с поддержкой аутентификации

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # ==================== АУТЕНТИФИКАЦИЯ ====================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ==================== СОЗДАНИЕ АДМИНИСТРАТОРА ====================
    path('create-admin/step1/', views.create_admin_step1, name='create_admin_step1'),
    path('create-admin/step2/', views.create_admin_step2, name='create_admin_step2'),
    path('create-admin/step3/', views.create_admin_step3, name='create_admin_step3'),

    # ==================== УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ (будущие функции) ====================
    # path('profile/', views.user_profile, name='user_profile'),
    # path('change-password/', views.change_password, name='change_password'),
    # path('users/', views.user_list, name='user_list'),
    # path('users/<str:username>/', views.user_detail, name='user_detail'),
    # path('users/<str:username>/edit/', views.user_edit, name='user_edit'),
    # path('users/<str:username>/delete/', views.user_delete, name='user_delete'),
]