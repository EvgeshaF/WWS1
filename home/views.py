from django.shortcuts import render, redirect

from mongodb.mongodb_config import MongoConfig


def home(request):
    """Проверяет первый ли старт программы, наличие файла mongo_config.env"""
    config_status = MongoConfig.check_config_completeness()

    if config_status == 'connection_required' or config_status == 'ping_failed':
        return redirect('mongo_connection')
    elif config_status == 'login_required' or config_status == 'login_failed':
        return redirect('mongo_login')
    elif config_status == 'db_required':
        return redirect('create_database')
    # else:
        #messages.success(request, language.mess_server_connect_success)
        #return redirect('user_login')
    return render(request, 'home/home.html', locals())