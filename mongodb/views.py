from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from loguru import logger

from .forms import MongoConnectionForm, MongoLoginForm, CreateDatabaseForm
from .mongodb_config import MongoConfig
from .mongodb_utils import MongoConnection
from . import language

from django_ratelimit.decorators import ratelimit


def render_toast_response(request):
    """JSON ответ с сообщениями для HTMX"""
    storage = messages.get_messages(request)
    messages_list = []
    for message in storage:
        messages_list.append({
            'tags': message.tags,
            'text': str(message),
            'delay': 5000
        })

    response = JsonResponse({'messages': messages_list})
    response['Content-Type'] = 'application/json'
    return response


def render_form_with_messages(request, template_name, context):
    """Рендерит форму с сообщениями для HTMX"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    if is_htmx:
        return render_toast_response(request)
    else:
        return render(request, template_name, context)


def validate_previous_steps(step):
    """Проверяет завершенность предыдущих шагов"""
    config = MongoConfig.read_config()

    if step >= 2:
        if not config.get('host') or not config.get('port'):
            return False, 'create_database_step1'

    if step >= 3:
        if not all([config.get('admin_user'), config.get('admin_password')]):
            return False, 'create_database_step2'

    return True, None


@ratelimit(key='ip', rate='5/m', method='POST')
def create_database_step1(request):
    """Форма конфигурации сервера MongoDB (хост, порт)"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    if request.method == 'POST':
        form = MongoConnectionForm(request.POST)
        if form.is_valid():
            host = form.cleaned_data['host']
            try:
                port = int(form.cleaned_data['port'])
            except (ValueError, TypeError):
                messages.error(request, language.mess_form_invalid)
                return render_form_with_messages(request, 'mongodb/create_dbconfig_step1.html', {
                    'form': form, 'text': language.text_server_conf, 'step': 1
                })

            # Проверяем соединение с сервером
            if MongoConnection.test_connection(host, port):
                # Сохраняем конфигурацию
                MongoConfig.update_config({'host': host, 'port': port})

                mess = f"{host}:{port} — {language.mess_server_ping_success}"
                logger.success(mess)
                messages.success(request, mess)

                # ИСПРАВЛЕНО: правильный редирект для HTMX
                if is_htmx:
                    response = render_toast_response(request)
                    response['HX-Redirect'] = reverse('create_database_step2')
                    return response
                return redirect('create_database_step2')
            else:
                # Детальная диагностика для лучшего сообщения об ошибке
                if host == 'ef-soft.local':
                    error_msg = f"{language.mess_server_ping_error}. Überprüfen Sie, ob ef-soft.local erreichbar ist oder verwenden Sie 'localhost'."
                else:
                    error_msg = f"{language.mess_server_ping_error}. Überprüfen Sie, ob MongoDB auf {host}:{port} läuft."

                messages.error(request, error_msg)
                return render_form_with_messages(request, 'mongodb/create_dbconfig_step1.html', {
                    'form': form, 'text': language.text_server_conf, 'step': 1
                })
        else:
            messages.error(request, language.mess_form_invalid)
            return render_form_with_messages(request, 'mongodb/create_dbconfig_step1.html', {
                'form': form, 'text': language.text_server_conf, 'step': 1
            })

    else:  # GET-запрос
        config = MongoConfig.read_config() or {}

        if config:
            # Если конфиг есть — используем его
            form = MongoConnectionForm(initial={
                'host': config.get('host', 'localhost'),
                'port': config.get('port', 27017),
            })
        else:
            # Если конфиг отсутствует — используем дефолты формы
            form = MongoConnectionForm()

            # Показываем предупреждение только для GET-запросов без конфига
            logger.warning(language.mess_server_configuration_warning)
            messages.warning(request, language.mess_server_configuration_warning)
            messages.info(request, "Standardwerte: localhost:27017. Stellen Sie sicher, dass MongoDB läuft.")

    return render(request, 'mongodb/create_dbconfig_step1.html', {
        'form': form,
        'text': language.text_server_conf,
        'step': 1
    })


@ratelimit(key='ip', rate='5/m', method='POST')
def create_database_step2(request):
    """Форма авторизации администратора MongoDB"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    # ИСПРАВЛЕНО: Проверяем предыдущие шаги
    is_valid, redirect_to = validate_previous_steps(2)
    if not is_valid:
        messages.error(request, "Bitte vollenden Sie zuerst die vorherigen Schritte")
        return redirect(redirect_to)

    config = MongoConfig.read_config()

    if request.method == 'POST':
        form = MongoLoginForm(request.POST)
        if form.is_valid():
            admin_user = form.cleaned_data['admin_user']
            admin_password = form.cleaned_data['admin_password']
            db_name = form.cleaned_data['db_name']

            # Проверяем авторизацию администратора
            if MongoConnection.authenticate_admin(admin_user, admin_password):
                # Сохраняем данные авторизации в конфигурацию
                MongoConfig.update_config({
                    'admin_user': admin_user,
                    'admin_password': admin_password,
                    'db_name': db_name,
                    'auth_source': 'admin'
                })

                success_msg = f"{language.mess_login_success1}{admin_user}{language.mess_login_success2}"
                logger.success(success_msg)
                messages.success(request, success_msg)

                # ИСПРАВЛЕНО: правильный редирект для HTMX
                if is_htmx:
                    response = render_toast_response(request)
                    response['HX-Redirect'] = reverse('create_database_step3')
                    return response
                return redirect('create_database_step3')
            else:
                messages.error(request, language.mess_login_admin_error)
                return render_form_with_messages(request, 'mongodb/create_dbconfig_step2.html', {
                    'form': form, 'text': language.text_login_form, 'step': 2
                })
        else:
            messages.error(request, language.mess_form_invalid)
            return render_form_with_messages(request, 'mongodb/create_dbconfig_step2.html', {
                'form': form, 'text': language.text_login_form, 'step': 2
            })

    else:  # GET-запрос
        # Предварительно заполняем форму из конфигурации, если данные есть
        initial_data = {}
        if config.get('admin_user'):
            initial_data['admin_user'] = config['admin_user']
        if config.get('db_name'):
            initial_data['db_name'] = config['db_name']

        form = MongoLoginForm(initial=initial_data)

    return render(request, 'mongodb/create_dbconfig_step2.html', {
        'form': form,
        'text': language.text_login_form,
        'step': 2
    })


@ratelimit(key='ip', rate='3/m', method='POST')
def create_database_step3(request):
    """Форма создания новой базы данных"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    # ИСПРАВЛЕНО: Проверяем предыдущие шаги
    is_valid, redirect_to = validate_previous_steps(3)
    if not is_valid:
        messages.error(request, "Bitte vollenden Sie zuerst die vorherigen Schritte")
        return redirect(redirect_to)

    if request.method == 'POST':
        form = CreateDatabaseForm(request.POST)
        if form.is_valid():
            db_name = form.cleaned_data['db_name']

            # Проверяем, что база данных не существует
            if MongoConnection.database_exists(db_name):
                messages.error(request, f"Datenbank '{db_name}' existiert bereits")
                return render_form_with_messages(request, 'mongodb/create_dbconfig_step3.html', {
                    'form': form, 'text': language.text_create_db_form, 'step': 3
                })
            else:
                # Создаем базу данных
                if MongoConnection.create_database_step3(db_name):
                    # Обновляем конфигурацию с новой БД
                    MongoConfig.update_config({
                        'db_name': db_name,
                        'setup_completed': True
                    })

                    success_msg = f"Datenbank '{db_name}' mit allen Kollektionen erfolgreich erstellt"
                    logger.success(success_msg)
                    messages.success(request, success_msg)

                    # ИСПРАВЛЕНО: правильный редирект для HTMX
                    if is_htmx:
                        response = render_toast_response(request)
                        response['HX-Redirect'] = reverse('home')
                        return response
                    return redirect('home')
                else:
                    messages.error(request, f"Fehler beim Erstellen der Datenbank '{db_name}'")
                    return render_form_with_messages(request, 'mongodb/create_dbconfig_step3.html', {
                        'form': form, 'text': language.text_create_db_form, 'step': 3
                    })
        else:
            messages.error(request, language.mess_form_invalid)
            return render_form_with_messages(request, 'mongodb/create_dbconfig_step3.html', {
                'form': form, 'text': language.text_create_db_form, 'step': 3
            })

    else:  # GET-запрос
        form = CreateDatabaseForm()

    return render(request, 'mongodb/create_dbconfig_step3.html', {
        'form': form,
        'text': language.text_create_db_form,
        'step': 3
    })