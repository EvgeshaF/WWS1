from django.shortcuts import render, redirect

from mongodb.mongodb_config import MongoConfig
from users.user_utils import UserManager


def home(request):
    """Проверяет первый ли старт программы, наличие файла mongo_config.env"""
    config_status = MongoConfig.check_config_completeness()

    if config_status == 'connection_required' or config_status == 'ping_failed':
        return redirect('mongo_connection')
    elif config_status == 'login_required' or config_status == 'login_failed':
        return redirect('mongo_login')
    elif config_status == 'db_required':
        return redirect('create_database')
    elif config_status == 'complete':
        # Проверяем, есть ли администраторы в системе
        user_manager = UserManager()
        admin_count = user_manager.get_admin_count()

        if admin_count == 0:
            # Нет администраторов - перенаправляем на создание первого администратора
            return redirect('create_admin_step1')

        # Система полностью настроена
        return render(request, 'home/home.html', {
            'admin_count': admin_count,
            'setup_complete': True
        })

    # Если что-то пошло не так, показываем главную страницу
    return render(request, 'home/home.html', locals())