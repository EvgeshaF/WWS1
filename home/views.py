from django.shortcuts import render, redirect

from mongodb.mongodb_config import MongoConfig
from users.user_utils import UserManager
from companies.views import CompanyManager


def home(request):
    """Проверяет первый ли старт программы, наличие файла mongo_config.env"""
    config_status = MongoConfig.check_config_completeness()

    # Шаг 1: Проверяем MongoDB конфигурацию
    if config_status == 'connection_required' or config_status == 'ping_failed':
        return redirect('create_database_step1')
    elif config_status == 'login_required' or config_status == 'login_failed':
        return redirect('create_database_step2')
    elif config_status == 'db_required':
        return redirect('create_database_step3')
    elif config_status == 'complete':
        # Шаг 2: Проверяем, есть ли администраторы в системе
        user_manager = UserManager()
        admin_count = user_manager.get_admin_count()

        if admin_count == 0:
            # Нет администраторов - перенаправляем на создание первого администратора
            return redirect('users:create_admin_step1')

        # Шаг 3: Проверяем, есть ли зарегистрированная компания
        company_manager = CompanyManager()
        if not company_manager.has_active_company():
            # Нет компании - перенаправляем на регистрацию компании
            return redirect('companies:register_company')

        # Все настроено - показываем главную страницу
        primary_company = company_manager.get_primary_company()
        company_name = primary_company.get('company_name', 'Неизвестно') if primary_company else 'Не настроено'

        return render(request, 'home/home.html', {
            'admin_count': admin_count,
            'setup_complete': True,
            'company_name': company_name,
            'has_company': True
        })

    # Если что-то пошло не так, показываем главную страницу с ошибкой
    return render(request, 'home/home.html', {
        'setup_complete': False,
        'error': 'Неизвестная ошибка конфигурации'
    })