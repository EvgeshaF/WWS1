from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
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
    return response


def render_form_with_messages(request, template_name, context, redirect_url=None):
    """Унифицированная обработка форм для HTMX и обычных запросов"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    if is_htmx:
        response = render_toast_response(request)
        if redirect_url:
            response['HX-Redirect'] = redirect_url
        return response
    else:
        if redirect_url:
            return redirect(redirect_url.split('/')[-2])  # Извлекаем имя URL
        return render(request, template_name, context)


def validate_admin_creation_step(request, required_step):
    """Проверяет корректность шага создания администратора"""
    admin_creation = request.session.get('admin_creation')

    if not admin_creation:
        return False, 'create_admin_step1'

    current_step = admin_creation.get('step', 0)
    if current_step < required_step - 1:
        return False, f'create_admin_step{current_step + 1}'

    return True, None


@ratelimit(key='ip', rate='3/m', method='POST')
def create_admin_step1(request):
    """Шаг 1: Создание учетных данных администратора"""
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
            existing_user = user_manager.find_user_by_username(username)

            if existing_user:
                logger.warning(f"Пользователь {username} уже существует")
                messages.error(request, f"Benutzer '{username}' existiert bereits")
                return render_form_with_messages(request, 'users/create_admin_step1.html', {
                    'form': form, 'text': language.text_create_admin_step1, 'step': 1
                })
            else:
                # Сохраняем данные в сессии для следующих шагов
                request.session['admin_creation'] = {
                    'username': username,
                    'password': password,
                    'step': 1
                }

                logger.success(f"Данные сохранены в сессии: {username}")
                messages.success(request, f"Benutzerdaten für '{username}' erfolgreich validiert")

                # ✅ ИСПРАВЛЕНО: правильный редирект для HTMX
                return render_form_with_messages(
                    request,
                    'users/create_admin_step1.html',
                    {'form': form, 'text': language.text_create_admin_step1, 'step': 1},
                    reverse('create_admin_step2')
                )
        else:
            logger.error(f"Форма невалидна: {form.errors}")
            messages.error(request, "Formular ist ungültig. Bitte überprüfen Sie die Eingaben.")
            return render_form_with_messages(request, 'users/create_admin_step1.html', {
                'form': form, 'text': language.text_create_admin_step1, 'step': 1
            })

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
    # ✅ ИСПРАВЛЕНО: проверка предыдущего шага
    is_valid, redirect_to = validate_admin_creation_step(request, 2)
    if not is_valid:
        messages.error(request, "Bitte vollenden Sie zuerst die vorherigen Schritte")
        return redirect(redirect_to)

    admin_creation = request.session.get('admin_creation')

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

            # ✅ ИСПРАВЛЕНО: правильный редирект для HTMX
            return render_form_with_messages(
                request,
                'users/create_admin_step2.html',
                {
                    'form': form, 'text': language.text_create_admin_step2,
                    'step': 2, 'username': admin_creation['username']
                },
                reverse('create_admin_step3')
            )
        else:
            logger.error(f"Форма шага 2 невалидна: {form.errors}")
            messages.error(request, "Formular ist ungültig. Bitte überprüfen Sie die Eingaben.")
            return render_form_with_messages(request, 'users/create_admin_step2.html', {
                'form': form, 'text': language.text_create_admin_step2,
                'step': 2, 'username': admin_creation['username']
            })

    else:  # GET-запрос
        form = AdminProfileForm()

    return render(request, 'users/create_admin_step2.html', {
        'form': form,
        'text': language.text_create_admin_step2,
        'step': 2,
        'username': admin_creation['username']
    })


@ratelimit(key='ip', rate='2/m', method='POST')
def create_admin_step3(request):
    """Шаг 3: Разрешения и создание администратора"""
    # ✅ ИСПРАВЛЕНО: проверка предыдущих шагов
    is_valid, redirect_to = validate_admin_creation_step(request, 3)
    if not is_valid:
        messages.error(request, "Bitte vollenden Sie die vorherigen Schritte")
        return redirect(redirect_to)

    admin_creation = request.session.get('admin_creation')

    if request.method == 'POST':
        logger.info(f"НАЧАЛО создания администратора: {admin_creation['username']}")

        form = AdminPermissionsForm(request.POST)
        if form.is_valid():
            try:
                # Создание пользователя (существующий код...)
                user_manager = UserManager()

                # Подготовка данных пользователя
                now = datetime.datetime.now()
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
                    'is_active': True,
                    'created_at': now,
                    'modified_at': now,
                    'deleted': False,
                    'last_login': None,
                    'failed_login_attempts': 0,
                    'locked_until': None,
                    'password_changed_at': now
                }

                # ✅ ИСПРАВЛЕНО: используем UserManager.create_user
                if user_manager.create_user(user_data):
                    # Очищаем сессию
                    if 'admin_creation' in request.session:
                        del request.session['admin_creation']

                    success_msg = f"Administrator '{user_data['username']}' wurde erfolgreich erstellt!"
                    logger.success(success_msg)
                    messages.success(request, success_msg)

                    # ✅ ИСПРАВЛЕНО: правильный редирект для HTMX
                    return render_form_with_messages(
                        request,
                        'users/create_admin_step3.html',
                        {
                            'form': form, 'text': language.text_create_admin_step3,
                            'step': 3, 'username': admin_creation.get('username', ''),
                            'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}"
                        },
                        reverse('home')
                    )
                else:
                    messages.error(request, "Fehler beim Erstellen des Administrators")

            except Exception as e:
                logger.exception(f"КРИТИЧЕСКАЯ ОШИБКА при создании администратора: {e}")
                messages.error(request, f"Kritischer Fehler: {str(e)}")

            return render_form_with_messages(request, 'users/create_admin_step3.html', {
                'form': form, 'text': language.text_create_admin_step3,
                'step': 3, 'username': admin_creation.get('username', ''),
                'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}"
            })

        else:
            logger.error(f"Форма невалидна: {form.errors}")
            messages.error(request, "Bitte korrigieren Sie die Formularfehler")
            return render_form_with_messages(request, 'users/create_admin_step3.html', {
                'form': form, 'text': language.text_create_admin_step3,
                'step': 3, 'username': admin_creation.get('username', ''),
                'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}"
            })

    else:  # GET
        form = AdminPermissionsForm()

    return render(request, 'users/create_admin_step3.html', {
        'form': form,
        'text': language.text_create_admin_step3,
        'step': 3,
        'username': admin_creation.get('username', ''),
        'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}"
    })