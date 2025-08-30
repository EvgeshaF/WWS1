from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from loguru import logger
import datetime

from .forms import CreateAdminUserForm, AdminProfileForm, AdminPermissionsForm
from mongodb.mongodb_config import MongoConfig
from mongodb.mongodb_utils import MongoConnection
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

            # Проверяем, что пользователь с таким именем не существует
            if _user_exists(username):
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
                'is_active': True,
                'created_at': datetime.datetime.now(),
                'modified_at': datetime.datetime.now(),
                'deleted': False
            }

            # Создаем пользователя в MongoDB
            if _create_admin_user(user_data):
                # Очищаем сессию
                if 'admin_creation' in request.session:
                    del request.session['admin_creation']

                success_msg = f"Administrator '{admin_creation['username']}' erfolgreich erstellt"
                logger.success(success_msg)
                messages.success(request, success_msg)

                if is_htmx:
                    return render_toast_response(request)
                return redirect('home')
            else:
                messages.error(request, f"Fehler beim Erstellen des Administrators")
                if is_htmx:
                    return render_toast_response(request)
        else:
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


def _user_exists(username):
    """Проверяет существование пользователя"""
    try:
        db = MongoConnection.get_database()
        if not db:
            return False

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        users_collection = f"{db_name}_users" if db_name else 'users'

        user = db[users_collection].find_one({
            'username': username,
            'deleted': False
        })
        return user is not None
    except Exception as e:
        logger.error(f"Ошибка проверки существования пользователя: {e}")
        return True  # В случае ошибки считаем, что пользователь существует


def _create_admin_user(user_data):
    """Создает администратора в MongoDB"""
    try:
        db = MongoConnection.get_database()
        if not db:
            return False

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        users_collection = f"{db_name}_users" if db_name else 'users'

        # Создаем пользователя
        result = db[users_collection].insert_one(user_data)

        if result.inserted_id:
            logger.success(f"Администратор '{user_data['username']}' создан с ID: {result.inserted_id}")
            return True
        return False

    except Exception as e:
        logger.error(f"Ошибка создания администратора: {e}")
        return False