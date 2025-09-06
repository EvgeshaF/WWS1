from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_http_methods
from loguru import logger
import datetime
import json

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


def render_with_messages(request, template_name, context, success_redirect=None):
    """Универсальная функция для рендеринга с поддержкой HTMX"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    if is_htmx:
        response = render_toast_response(request)
        if success_redirect:
            response['HX-Redirect'] = success_redirect
        return response
    else:
        if success_redirect:
            return redirect(success_redirect)
        return render(request, template_name, context)


def validate_admin_creation_step(request, required_step):
    """Проверяет корректность шага создания администратора с дополнительными проверками"""
    admin_creation = request.session.get('admin_creation')

    if not admin_creation:
        logger.warning("Данные создания администратора не найдены в сессии")
        return False, 'create_admin_step1'

    current_step = admin_creation.get('step', 0)
    if current_step < required_step - 1:
        logger.warning(f"Текущий шаг ({current_step}) меньше требуемого ({required_step})")
        return False, f'create_admin_step{current_step + 1}'

    # Дополнительные проверки данных
    if required_step >= 2 and not admin_creation.get('username'):
        logger.warning("Шаг 2: отсутствует username")
        return False, 'create_admin_step1'

    if required_step >= 3:
        if not admin_creation.get('first_name') or not admin_creation.get('last_name'):
            logger.warning("Шаг 3: отсутствуют имя/фамилия")
            return False, 'create_admin_step2'

    return True, None


@ratelimit(key='ip', rate='3/m', method='POST')
@require_http_methods(["GET", "POST"])
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
                context = {'form': form, 'text': language.text_create_admin_step1, 'step': 1}
                return render_with_messages(request, 'users/create_admin_step1.html', context)
            else:
                # Сохраняем данные в сессии для следующих шагов
                request.session['admin_creation'] = {
                    'username': username,
                    'password': password,
                    'step': 1
                }
                request.session.modified = True

                logger.success(f"Данные сохранены в сессии: {username}")
                messages.success(request, f"Benutzerdaten für '{username}' erfolgreich validiert")

                return render_with_messages(
                    request,
                    'users/create_admin_step1.html',
                    {'form': form, 'text': language.text_create_admin_step1, 'step': 1},
                    reverse('create_admin_step2')
                )
        else:
            logger.error(f"Форма невалидна: {form.errors}")
            messages.error(request, "Formular ist ungültig. Bitte überprüfen Sie die Eingaben.")

        # Рендерим форму с ошибками
        context = {'form': form, 'text': language.text_create_admin_step1, 'step': 1}
        return render_with_messages(request, 'users/create_admin_step1.html', context)

    # GET-запрос
    form = CreateAdminUserForm()
    context = {'form': form, 'text': language.text_create_admin_step1, 'step': 1}
    return render(request, 'users/create_admin_step1.html', context)


def validate_contact_data(contacts_data_raw):
    """Валидация данных контактов"""
    try:
        contacts_data = json.loads(contacts_data_raw)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON контактов: {e}")
        return None, "Fehler beim Verarbeiten der Kontaktdaten"

    if not contacts_data:
        return None, "Bitte fügen Sie mindestens einen Kontakt hinzu"

    # Проверяем наличие email
    has_email = any(contact.get('type') == 'email' for contact in contacts_data)
    if not has_email:
        return None, "Bitte fügen Sie mindestens eine E-Mail-Adresse hinzu"

    # Дополнительная валидация контактов
    for i, contact in enumerate(contacts_data):
        contact_type = contact.get('type', '')
        contact_value = contact.get('value', '').strip()

        if not contact_type or not contact_value:
            return None, f"Kontakt {i + 1}: Typ und Wert sind erforderlich"

        # Валидация формата email
        if contact_type == 'email':
            import re
            email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_pattern, contact_value):
                return None, f"Ungültiges E-Mail-Format: {contact_value}"

        # Валидация формата телефона
        elif contact_type in ['phone', 'mobile', 'fax']:
            phone_pattern = r'^[\+]?[0-9\s\-\(\)]{7,20}$'
            if not re.match(phone_pattern, contact_value):
                return None, f"Ungültiges Telefonformat: {contact_value}"

    return contacts_data, None


@ratelimit(key='ip', rate='3/m', method='POST')
@require_http_methods(["GET", "POST"])
def create_admin_step2(request):
    """Шаг 2: Профиль администратора с контактами"""
    # Проверка предыдущего шага
    is_valid, redirect_to = validate_admin_creation_step(request, 2)
    if not is_valid:
        messages.error(request, "Bitte vollenden Sie zuerst die vorherigen Schritte")
        return redirect(redirect_to)

    admin_creation = request.session.get('admin_creation')

    if request.method == 'POST':
        logger.info("Обработка POST запроса для шага 2")

        form = AdminProfileForm(request.POST)

        # Получаем и валидируем данные контактов
        contacts_data_raw = request.POST.get('contacts_data', '[]')
        contacts_data, validation_error = validate_contact_data(contacts_data_raw)

        if validation_error:
            messages.error(request, validation_error)
            context = {
                'form': form, 'text': language.text_create_admin_step2,
                'step': 2, 'username': admin_creation['username'],
                'existing_contacts': contacts_data_raw
            }
            return render_with_messages(request, 'users/create_admin_step2.html', context)

        if form.is_valid():
            # Обновляем данные в сессии
            admin_creation.update({
                'salutation': form.cleaned_data['salutation'],
                'title': form.cleaned_data['title'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone'],
                'contacts': contacts_data,
                'step': 2
            })

            # Извлекаем основной email из контактов для удобства
            primary_email = None
            for contact in contacts_data:
                if contact.get('type') == 'email':
                    if contact.get('primary', False):
                        primary_email = contact.get('value')
                        break
                    elif not primary_email:
                        primary_email = contact.get('value')

            if primary_email:
                admin_creation['primary_email'] = primary_email

            request.session['admin_creation'] = admin_creation
            request.session.modified = True

            logger.success(f"Данные профиля и {len(contacts_data)} контактов сохранены в сессии")
            messages.success(request, f"Profildaten und {len(contacts_data)} Kontakte erfolgreich erfasst")

            return render_with_messages(
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

        # Рендерим форму с ошибками
        context = {
            'form': form, 'text': language.text_create_admin_step2,
            'step': 2, 'username': admin_creation['username'],
            'existing_contacts': contacts_data_raw
        }
        return render_with_messages(request, 'users/create_admin_step2.html', context)

    # GET-запрос
    form = AdminProfileForm()
    existing_contacts = admin_creation.get('contacts', [])

    context = {
        'form': form,
        'text': language.text_create_admin_step2,
        'step': 2,
        'username': admin_creation['username'],
        'existing_contacts': json.dumps(existing_contacts) if existing_contacts else '[]'
    }
    return render(request, 'users/create_admin_step2.html', context)


@ratelimit(key='ip', rate='2/m', method='POST')
@require_http_methods(["GET", "POST"])
def create_admin_step3(request):
    """Шаг 3: Разрешения и создание администратора"""
    # Проверка предыдущих шагов
    is_valid, redirect_to = validate_admin_creation_step(request, 3)
    if not is_valid:
        messages.error(request, "Bitte vollenden Sie die vorherigen Schritte")
        return redirect(redirect_to)

    admin_creation = request.session.get('admin_creation')

    if request.method == 'POST':
        logger.info(f"НАЧАЛИ создания администратора: {admin_creation['username']}")

        form = AdminPermissionsForm(request.POST)
        if form.is_valid():
            try:
                # Создание пользователя
                user_manager = UserManager()

                # Подготовка данных пользователя
                now = datetime.datetime.now()
                contacts = admin_creation.get('contacts', [])

                # Находим основной email
                primary_email = admin_creation.get('primary_email', '')
                if not primary_email and contacts:
                    for contact in contacts:
                        if contact.get('type') == 'email':
                            if contact.get('primary', False):
                                primary_email = contact.get('value', '')
                                break
                    if not primary_email:
                        for contact in contacts:
                            if contact.get('type') == 'email':
                                primary_email = contact.get('value', '')
                                break

                # Находим основной телефон
                primary_phone = ''
                for contact in contacts:
                    if contact.get('type') in ['phone', 'mobile'] and contact.get('primary', False):
                        primary_phone = contact.get('value', '')
                        break
                if not primary_phone:
                    for contact in contacts:
                        if contact.get('type') in ['phone', 'mobile']:
                            primary_phone = contact.get('value', '')
                            break

                user_data = {
                    'username': admin_creation['username'],
                    'password': make_password(admin_creation['password']),
                    'profile': {
                        'salutation': admin_creation.get('salutation', ''),
                        'title': admin_creation.get('title', ''),
                        'first_name': admin_creation.get('first_name', ''),
                        'last_name': admin_creation.get('last_name', ''),
                        'email': primary_email,
                        'phone': primary_phone,
                        'contacts': contacts,
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

                logger.info(f"Создаем пользователя с {len(contacts)} контактами")
                logger.info(f"Основной email: {primary_email}")
                logger.info(f"Основной телефон: {primary_phone}")

                # Используем UserManager.create_user
                if user_manager.create_user(user_data):
                    # Очищаем сессию
                    if 'admin_creation' in request.session:
                        del request.session['admin_creation']
                        request.session.modified = True

                    # Подготавливаем сводку по контактам для логирования
                    contact_summary = {}
                    for contact in contacts:
                        contact_type = contact.get('type', 'unknown')
                        if contact_type in contact_summary:
                            contact_summary[contact_type] += 1
                        else:
                            contact_summary[contact_type] = 1

                    contact_info = ', '.join([f"{count} {type_name}" for type_name, count in contact_summary.items()])

                    success_msg = f"Administrator '{user_data['username']}' wurde erfolgreich erstellt! Kontakte: {contact_info}"
                    logger.success(success_msg)
                    messages.success(request, success_msg)

                    return render_with_messages(
                        request,
                        'users/create_admin_step3.html',
                        {
                            'form': form, 'text': language.text_create_admin_step3,
                            'step': 3, 'username': admin_creation.get('username', ''),
                            'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}",
                            'contact_count': len(contacts),
                            'primary_email': primary_email
                        },
                        reverse('home')
                    )
                else:
                    messages.error(request, "Fehler beim Erstellen des Administrators")

            except Exception as e:
                logger.exception(f"КРИТИЧЕСКАЯ ОШИБКА при создании администратора: {e}")
                messages.error(request, f"Kritischer Fehler: {str(e)}")

        else:
            logger.error(f"Форма невалидна: {form.errors}")
            messages.error(request, "Bitte korrigieren Sie die Formularfehler")

        # Рендерим форму с ошибками
        context = {
            'form': form, 'text': language.text_create_admin_step3,
            'step': 3, 'username': admin_creation.get('username', ''),
            'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}",
            'contact_count': len(admin_creation.get('contacts', [])),
            'primary_email': admin_creation.get('primary_email', '')
        }
        return render_with_messages(request, 'users/create_admin_step3.html', context)

    # GET запрос
    form = AdminPermissionsForm()
    contacts = admin_creation.get('contacts', [])
    context = {
        'form': form,
        'text': language.text_create_admin_step3,
        'step': 3,
        'username': admin_creation.get('username', ''),
        'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}",
        'contact_count': len(contacts),
        'primary_email': admin_creation.get('primary_email', '')
    }
    return render(request, 'users/create_admin_step3.html', context)