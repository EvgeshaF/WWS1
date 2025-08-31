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
        logger.info("Обработка POST запроса для шага 1")

        form = CreateAdminUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            logger.info(f"Валидация формы прошла для: {username}")

            # Используем UserManager для проверки
            user_manager = UserManager()

            # Проверяем, что пользователь с таким именем не существует
            existing_user = user_manager.find_user_by_username(username)
            if existing_user:
                logger.warning(f"Пользователь {username} уже существует")
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

                logger.success(f"Данные сохранены в сессии: {username}")
                messages.success(request, f"Benutzerdaten für '{username}' erfolgreich validiert")

                if is_htmx:
                    return render_toast_response(request)
                else:
                    # Прямой redirect для не-HTMX запросов
                    logger.info("Перенаправляем на шаг 2 (не HTMX)")
                    return redirect('create_admin_step2')
        else:
            logger.error(f"Форма невалидна: {form.errors}")
            messages.error(request, "Formular ist ungültig. Bitte überprüfen Sie die Eingaben.")
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
        logger.info("Обработка POST запроса для шага 2")

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

            logger.success("Данные профиля сохранены в сессии")
            messages.success(request, "Profildaten erfolgreich erfasst")

            if is_htmx:
                return render_toast_response(request)
            else:
                return redirect('create_admin_step3')
        else:
            logger.error(f"Форма шага 2 невалидна: {form.errors}")
            messages.error(request, "Formular ist ungültig. Bitte überprüfen Sie die Eingaben.")
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

    # Проверяем сессию
    admin_creation = request.session.get('admin_creation')
    if not admin_creation or admin_creation.get('step') != 2:
        messages.error(request, "Bitte vollenden Sie die vorherigen Schritte")
        return redirect('create_admin_step1')

    if request.method == 'POST':
        logger.info(f"Создание администратора: {admin_creation['username']}")

        form = AdminPermissionsForm(request.POST)
        if form.is_valid():
            try:
                # Подготавливаем данные пользователя
                user_data = {
                    'username': admin_creation['username'],
                    'password': make_password(admin_creation['password']),
                    'profile': {
                        'salutation': admin_creation.get('salutation', ''),
                        'title': admin_creation.get('title', ''),
                        'first_name': admin_creation.get('first_name', ''),
                        'last_name': admin_creation.get('last_name', ''),
                        'email': admin_creation.get('email', ''),
                        'phone': admin_creation.get('phone', ''),
                    },
                    'permissions': {
                        'is_super_admin': form.cleaned_data.get('is_super_admin', False),
                        'can_manage_users': form.cleaned_data.get('can_manage_users', False),
                        'can_manage_database': form.cleaned_data.get('can_manage_database', False),
                        'can_view_logs': form.cleaned_data.get('can_view_logs', False),
                        'can_manage_settings': form.cleaned_data.get('can_manage_settings', False),
                        'password_expires': form.cleaned_data.get('password_expires', True),
                        'two_factor_required': form.cleaned_data.get('two_factor_required', False),
                    },
                    'is_admin': True,
                    'is_active': True
                }

                logger.info("Данные пользователя подготовлены")

                # Создаем пользователя
                user_manager = UserManager()
                creation_result = user_manager.create_user(user_data)

                if creation_result:
                    # Двойная проверка создания
                    verification = user_manager.find_user_by_username(user_data['username'])
                    if verification:
                        # Очищаем сессию
                        if 'admin_creation' in request.session:
                            del request.session['admin_creation']

                        success_msg = f"Administrator '{admin_creation['username']}' wurde erfolgreich erstellt!"
                        logger.success(success_msg)
                        messages.success(request, success_msg)

                        return redirect('home')
                    else:
                        logger.error("Пользователь не найден после создания")
                        messages.error(request, "Administrator wurde nicht korrekt gespeichert")
                else:
                    logger.error("Создание пользователя не удалось")
                    messages.error(request, "Fehler beim Erstellen des Administrators")

            except Exception as e:
                logger.exception(f"Ошибка при создании администратора: {e}")
                messages.error(request, f"Fehler: {str(e)}")

        else:
            logger.error(f"Форма невалидна: {form.errors}")
            messages.error(request, "Bitte korrigieren Sie die Formularfehler")

    else:  # GET
        form = AdminPermissionsForm()

    return render(request, 'users/create_admin_step3.html', {
        'form': form,
        'text': language.text_create_admin_step3,
        'step': 3,
        'username': admin_creation.get('username', ''),
        'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}"
    })