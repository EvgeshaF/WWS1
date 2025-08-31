from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from loguru import logger
import datetime

from .forms import CreateAdminUserForm, AdminProfileForm, AdminPermissionsForm
from mongodb.mongodb_config import MongoConfig
from mongodb.mongodb_utils import MongoConnection
from .user_utils import UserManager
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

    # Логируем ответ для отладки
    logger.debug(f"Отправляем toast ответ: {messages_list}")

    return response


@ratelimit(key='ip', rate='3/m', method='POST')
def create_admin_step1(request):
    """Шаг 1: Создание учетных данных администратора"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    # Проверяем, что MongoDB настроена
    config = MongoConfig.read_config()
    if not config.get('setup_completed'):
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    if request.method == 'POST':
        form = CreateAdminUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Используем UserManager для проверки
            user_manager = UserManager()

            # Отладочная информация
            user_manager.debug_collection_info()

            # Проверяем, что пользователь с таким именем не существует
            existing_user = user_manager.find_user_by_username(username)
            if existing_user:
                messages.error(request, f"Benutzer '{username}' existiert bereits")
                if is_htmx:
                    return render_toast_response(request)
            else:
                # Сохраняем данные в сессии для следующих шагов
                request.session['admin_creation'] = {
                    'username': username,
                    'password': password,
                    'step': 1
                }

                messages.success(request, f"Benutzerdaten für '{username}' erfolgreich validiert")
                if is_htmx:
                    return render_toast_response(request)
                return redirect('create_admin_step2')
        else:
            messages.error(request, language.mess_form_invalid)
            if is_htmx:
                return render_toast_response(request)

    else:  # GET-запрос
        form = CreateAdminUserForm()

    return render(request, 'users/create_admin_step1.html', {
        'form': form,
        'text': language.text_create_admin_step1,
        'step': 1
    })


@ratelimit(key='ip', rate='3/m', method='POST')
def create_admin_step2(request):
    """Шаг 2: Профиль администратора"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    # Проверяем, что первый шаг завершен
    admin_creation = request.session.get('admin_creation')
    if not admin_creation or admin_creation.get('step') != 1:
        messages.error(request, "Bitte vollenden Sie zuerst Schritt 1")
        return redirect('create_admin_step1')

    if request.method == 'POST':
        form = AdminProfileForm(request.POST)
        if form.is_valid():
            # Обновляем данные в сессии
            admin_creation.update({
                'salutation': form.cleaned_data['salutation'],
                'title': form.cleaned_data['title'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone'],
                'step': 2
            })
            request.session['admin_creation'] = admin_creation

            messages.success(request, "Profildaten erfolgreich erfasst")
            if is_htmx:
                return render_toast_response(request)
            return redirect('create_admin_step3')
        else:
            messages.error(request, language.mess_form_invalid)
            if is_htmx:
                return render_toast_response(request)

    else:  # GET-запрос
        form = AdminProfileForm()

    return render(request, 'users/create_admin_step2.html', {
        'form': form,
        'text': language.text_create_admin_step2,
        'step': 2,
        'username': admin_creation['username']
    })


@ratelimit(key='ip', rate='3/m', method='POST')
def create_admin_step3(request):
    """Шаг 3: Разрешения и создание администратора"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    # Проверяем, что предыдущие шаги завершены
    admin_creation = request.session.get('admin_creation')
    if not admin_creation or admin_creation.get('step') != 2:
        messages.error(request, "Bitte vollenden Sie die vorherigen Schritte")
        return redirect('create_admin_step1')

    if request.method == 'POST':
        logger.info(f"Создание администратора: {admin_creation['username']}")

        form = AdminPermissionsForm(request.POST)
        if form.is_valid():
            # Собираем все данные для создания пользователя
            user_data = {
                'username': admin_creation['username'],
                'password': make_password(admin_creation['password']),
                'profile': {
                    'salutation': admin_creation['salutation'],
                    'title': admin_creation['title'],
                    'first_name': admin_creation['first_name'],
                    'last_name': admin_creation['last_name'],
                    'email': admin_creation['email'],
                    'phone': admin_creation['phone'],
                },
                'permissions': {
                    'is_super_admin': form.cleaned_data['is_super_admin'],
                    'can_manage_users': form.cleaned_data['can_manage_users'],
                    'can_manage_database': form.cleaned_data['can_manage_database'],
                    'can_view_logs': form.cleaned_data['can_view_logs'],
                    'can_manage_settings': form.cleaned_data['can_manage_settings'],
                    'password_expires': form.cleaned_data['password_expires'],
                    'two_factor_required': form.cleaned_data['two_factor_required'],
                },
                'is_admin': True,
                'is_active': True
            }

            # Логируем данные (без пароля)
            log_data = {k: v for k, v in user_data.items() if k != 'password'}
            logger.info(f"Данные для создания пользователя: {log_data}")

            # Используем UserManager для создания пользователя
            user_manager = UserManager()

            # Создаем пользователя
            creation_result = user_manager.create_user(user_data)
            logger.info(f"Результат создания пользователя: {creation_result}")

            if creation_result:
                # Очищаем сессию
                if 'admin_creation' in request.session:
                    del request.session['admin_creation']
                    logger.info("Сессия очищена")

                success_msg = f"Administrator '{admin_creation['username']}' erfolgreich erstellt"
                logger.success(success_msg)
                messages.success(request, success_msg)

                if is_htmx:
                    logger.info("Отправляем HTMX ответ с сообщением об успехе")
                    return render_toast_response(request)
                else:
                    logger.info("Перенаправляем на главную страницу (не HTMX)")
                    return redirect('home')
            else:
                error_msg = f"Fehler beim Erstellen des Administrators '{admin_creation['username']}'"
                logger.error(error_msg)
                messages.error(request, error_msg)
                if is_htmx:
                    return render_toast_response(request)
        else:
            logger.error(f"Форма невалидна: {form.errors}")
            messages.error(request, language.mess_form_invalid)
            if is_htmx:
                return render_toast_response(request)

    else:  # GET-запрос
        form = AdminPermissionsForm()

    return render(request, 'users/create_admin_step3.html', {
        'form': form,
        'text': language.text_create_admin_step3,
        'step': 3,
        'username': admin_creation['username'],
        'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}"
    })


# Удаляем старые функции, так как теперь используем UserManager
def _user_exists(username):
    """Проверяет существование пользователя (deprecated - использовать UserManager)"""
    user_manager = UserManager()
    return user_manager.find_user_by_username(username) is not None


def _create_admin_user(user_data):
    """Создает администратора в MongoDB (deprecated - использовать UserManager)"""
    user_manager = UserManager()
    return user_manager.create_user(user_data)