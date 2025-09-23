from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from loguru import logger
import datetime
import json
import re

from .forms import CreateAdminUserForm, AdminProfileForm, AdminPermissionsForm, get_contact_type_choices
from mongodb.mongodb_config import MongoConfig
from .user_utils import UserManager
from . import language
from django_ratelimit.decorators import ratelimit


@never_cache
def render_toast_response(request):
    """JSON response with messages for HTMX - ИСПРАВЛЕНА"""
    try:
        storage = messages.get_messages(request)
        messages_list = []

        for message in storage:
            messages_list.append({
                'tags': message.tags,
                'text': str(message),
                'delay': 5000
            })

        logger.info(f"Отправляем JSON ответ с {len(messages_list)} сообщениями")
        for msg in messages_list:
            logger.info(f"Сообщение: {msg['tags']} - {msg['text']}")

        # Формируем JSON ответ
        response_data = {
            'messages': messages_list,
            'status': 'success' if any(msg['tags'] == 'success' for msg in messages_list) else 'error'
        }

        response = JsonResponse(response_data, safe=False)

        # Устанавливаем правильные заголовки
        response['Content-Type'] = 'application/json; charset=utf-8'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        logger.debug(f"JSON response created successfully: {response_data}")
        return response

    except Exception as e:
        logger.error(f"Ошибка создания JSON ответа: {e}")
        # Возвращаем минимальный JSON ответ при ошибке
        return JsonResponse({
            'messages': [{'tags': 'error', 'text': 'Ein unerwarteter Fehler ist aufgetreten', 'delay': 5000}],
            'status': 'error'
        })


@never_cache
def render_with_messages(request, template_name, context, success_redirect=None):
    """Universal function for rendering with HTMX support"""
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
    """Validates admin creation step with additional checks"""
    admin_creation = request.session.get('admin_creation')

    if not admin_creation:
        logger.warning("Admin creation data not found in session")
        return False, 'users:create_admin_step1'

    current_step = admin_creation.get('step', 0)
    if current_step < required_step - 1:
        logger.warning(f"Current step ({current_step}) less than required ({required_step})")
        return False, f'users:create_admin_step{current_step + 1}'

    # Additional data checks
    if required_step >= 2 and not admin_creation.get('username'):
        logger.warning("Step 2: missing username")
        return False, 'users:create_admin_step1'

    if required_step >= 3:
        if not admin_creation.get('first_name') or not admin_creation.get('last_name'):
            logger.warning("Step 3: missing first_name/last_name")
            return False, 'users:create_admin_step2'

    return True, None


def validate_additional_contacts_data(additional_contacts_data_raw):
    """Validate additional contact data - НОВАЯ ФУНКЦИЯ"""
    try:
        additional_contacts_data = json.loads(additional_contacts_data_raw) if additional_contacts_data_raw else []
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error for additional contacts: {e}")
        return None, "Fehler beim Verarbeiten der zusätzlichen Kontaktdaten"

    # Дополнительные контакты ОПЦИОНАЛЬНЫ, поэтому пустой список разрешен
    if not additional_contacts_data:
        logger.info("Нет дополнительных контактов - это нормально")
        return [], None

    # Валидируем каждый дополнительный контакт
    for i, contact in enumerate(additional_contacts_data):
        contact_type = contact.get('type', '')
        contact_value = contact.get('value', '').strip()

        if not contact_type or not contact_value:
            return None, f"Zusätzlicher Kontakt {i + 1}: Typ und Wert sind erforderlich"

        # Validate email format
        if contact_type == 'email':
            email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_pattern, contact_value):
                return None, f"Ungültiges E-Mail-Format: {contact_value}"

        # Validate phone format
        elif contact_type in ['mobile', 'fax']:
            phone_pattern = r'^[\+]?[0-9\s\-\(\)]{7,20}$'
            if not re.match(phone_pattern, contact_value):
                return None, f"Ungültiges Telefonformat: {contact_value}"

    logger.info(f"Валидация дополнительных контактов прошла успешно: {len(additional_contacts_data)} контактов")
    return additional_contacts_data, None


@ratelimit(key='ip', rate='3/m', method='POST')
@require_http_methods(["GET", "POST"])
@never_cache
def create_admin_step1(request):
    """Step 1: Create admin account credentials"""
    try:
        # Check if MongoDB is configured
        config = MongoConfig.read_config()
        if not config.get('setup_completed'):
            messages.error(request, "MongoDB muss zuerst konfiguriert werden")
            return redirect('home')

        if request.method == 'POST':
            logger.info("Processing POST request for step 1")

            form = CreateAdminUserForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']

                logger.info(f"Form validation passed for: {username}")

                # Use UserManager for checking
                user_manager = UserManager()
                existing_user = user_manager.find_user_by_username(username)

                if existing_user:
                    logger.warning(f"User {username} already exists")
                    messages.error(request, f"Benutzer '{username}' existiert bereits")
                    context = {'form': form, 'text': language.text_create_admin_step1, 'step': 1}
                    return render_with_messages(request, 'create_admin_step1.html', context)
                else:
                    # Save data in session for next steps
                    request.session['admin_creation'] = {
                        'username': username,
                        'password': password,
                        'step': 1
                    }
                    request.session.modified = True

                    logger.success(f"Data saved in session: {username}")
                    messages.success(request, f"Benutzerdaten für '{username}' erfolgreich validiert")

                    return render_with_messages(
                        request,
                        'users/create_admin_step1.html',
                        {'form': form, 'text': language.text_create_admin_step1, 'step': 1},
                        reverse('users:create_admin_step2')
                    )
            else:
                logger.error(f"Form invalid: {form.errors}")
                messages.error(request, "Formular ist ungültig. Bitte überprüfen Sie die Eingaben.")

            # Render form with errors
            context = {'form': form, 'text': language.text_create_admin_step1, 'step': 1}
            return render_with_messages(request, 'create_admin_step1.html', context)

        # GET request
        form = CreateAdminUserForm()
        context = {'form': form, 'text': language.text_create_admin_step1, 'step': 1}
        return render(request, 'create_admin_step1.html', context)

    except Exception as e:
        logger.error(f"Error in create_admin_step1: {e}")
        messages.error(request, "Ein unerwarteter Fehler ist aufgetreten")
        return redirect('home')


@ratelimit(key='ip', rate='3/m', method='POST')
@require_http_methods(["GET", "POST"])
@never_cache
def create_admin_step2(request):
    """Step 2: Admin profile with main contacts + optional additional contacts - ОБНОВЛЕН"""
    try:
        # Check previous step
        is_valid, redirect_to = validate_admin_creation_step(request, 2)
        if not is_valid:
            messages.error(request, "Bitte vollenden Sie zuerst die vorherigen Schritte")
            return redirect(redirect_to)

        admin_creation = request.session.get('admin_creation')

        # Получаем типы контактов для передачи в шаблон
        contact_type_choices = get_contact_type_choices()
        contact_type_choices_json = json.dumps([{'value': value, 'text': text} for value, text in contact_type_choices])

        if request.method == 'POST':
            logger.info("Processing POST request for step 2")

            form = AdminProfileForm(request.POST)

            # НОВОЕ: Получаем и валидируем ДОПОЛНИТЕЛЬНЫЕ контакты (опциональные)
            additional_contacts_data_raw = request.POST.get('additional_contacts_data', '[]')
            logger.info(f"Получены дополнительные контакты: {additional_contacts_data_raw}")

            additional_contacts_data, validation_error = validate_additional_contacts_data(additional_contacts_data_raw)

            if validation_error:
                logger.error(f"Ошибка валидации дополнительных контактов: {validation_error}")
                messages.error(request, validation_error)
                context = {
                    'form': form, 'text': language.text_create_admin_step2,
                    'step': 2, 'username': admin_creation['username'],
                    'existing_additional_contacts': additional_contacts_data_raw,
                    'contact_type_choices': contact_type_choices,
                    'contact_type_choices_json': contact_type_choices_json
                }
                return render_with_messages(request, 'create_admin_step2.html', context)

            if form.is_valid():
                logger.info(f"Форма валидна, данные: {form.cleaned_data}")

                # НОВОЕ: Теперь email и phone берутся из формы (обязательные поля)
                primary_email = form.cleaned_data['email']
                primary_phone = form.cleaned_data['phone']

                logger.info(f"Основные контакты - email: {primary_email}, phone: {primary_phone}")

                # Создаем список всех контактов (основные + дополнительные)
                all_contacts = [
                    {
                        'type': 'email',
                        'value': primary_email,
                        'label': 'Haupt-E-Mail',
                        'primary': True
                    },
                    {
                        'type': 'phone',
                        'value': primary_phone,
                        'label': 'Haupttelefon',
                        'primary': True
                    }
                ]

                # Добавляем дополнительные контакты
                if additional_contacts_data:
                    all_contacts.extend(additional_contacts_data)

                # Update session data
                admin_creation.update({
                    'salutation': form.cleaned_data['salutation'],
                    'title': form.cleaned_data['title'],
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'email': primary_email,  # Основной email из формы
                    'phone': primary_phone,  # Основной телефон из формы
                    'all_contacts': all_contacts,  # Все контакты (основные + дополнительные)
                    'additional_contacts': additional_contacts_data,  # Только дополнительные
                    'step': 2
                })

                request.session['admin_creation'] = admin_creation
                request.session.modified = True

                contact_summary = f"Haupt-E-Mail, Haupttelefon"
                if additional_contacts_data:
                    contact_summary += f" + {len(additional_contacts_data)} zusätzliche"

                logger.success(f"Profile data and contacts saved in session: {contact_summary}")
                messages.success(request, f"Profildaten und Kontakte erfolgreich erfasst ({contact_summary})")

                return render_with_messages(
                    request,
                    'users/create_admin_step2.html',
                    {
                        'form': form, 'text': language.text_create_admin_step2,
                        'step': 2, 'username': admin_creation['username'],
                        'contact_type_choices': contact_type_choices,
                        'contact_type_choices_json': contact_type_choices_json
                    },
                    reverse('users:create_admin_step3')
                )
            else:
                logger.error(f"Step 2 form invalid: {form.errors}")
                messages.error(request, "Formular ist ungültig. Bitte überprüfen Sie die Eingaben.")

            # Render form with errors
            context = {
                'form': form, 'text': language.text_create_admin_step2,
                'step': 2, 'username': admin_creation['username'],
                'existing_additional_contacts': additional_contacts_data_raw,
                'contact_type_choices': contact_type_choices,
                'contact_type_choices_json': contact_type_choices_json
            }
            return render_with_messages(request, 'create_admin_step2.html', context)

        # GET request
        form = AdminProfileForm()
        existing_additional_contacts = admin_creation.get('additional_contacts', [])

        context = {
            'form': form,
            'text': language.text_create_admin_step2,
            'step': 2,
            'username': admin_creation['username'],
            'existing_additional_contacts': json.dumps(existing_additional_contacts) if existing_additional_contacts else '[]',
            'contact_type_choices': contact_type_choices,
            'contact_type_choices_json': contact_type_choices_json
        }
        return render(request, 'create_admin_step2.html', context)

    except Exception as e:
        logger.exception(f"КРИТИЧЕСКАЯ ОШИБКА в create_admin_step2: {e}")
        messages.error(request, "Ein unerwarteter Fehler ist aufgetreten")
        return redirect('users:create_admin_step1')


@ratelimit(key='ip', rate='2/m', method='POST')
@require_http_methods(["GET", "POST"])
@never_cache
def create_admin_step3(request):
    """Step 3: Permissions and create admin - UPDATED FOR NEW CONTACT STRUCTURE"""
    try:
        # Check previous steps
        is_valid, redirect_to = validate_admin_creation_step(request, 3)
        if not is_valid:
            messages.error(request, "Bitte vollenden Sie die vorherigen Schritte")
            return redirect(redirect_to)

        admin_creation = request.session.get('admin_creation')

        if request.method == 'POST':
            logger.info(f"Starting admin creation: {admin_creation['username']}")

            form = AdminPermissionsForm(request.POST)
            if form.is_valid():
                try:
                    # Create user
                    user_manager = UserManager()

                    # Prepare user data
                    now = datetime.datetime.now()
                    all_contacts = admin_creation.get('all_contacts', [])

                    # ИСПРАВЛЕНО: Используем email и phone из сессии (уже валидированы в step2)
                    primary_email = admin_creation.get('email', '')
                    primary_phone = admin_creation.get('phone', '')

                    if not primary_email:
                        logger.error("Primary email not found in session")
                        messages.error(request, "Haupt-E-Mail nicht gefunden. Bitte beginnen Sie erneut.")
                        return redirect('users:create_admin_step2')

                    # CORRECT STRUCTURE - matching JSON schema
                    user_data = {
                        'username': admin_creation['username'],
                        'password': make_password(admin_creation['password']),

                        # Profile object (nested structure like in JSON)
                        'profile': {
                            'salutation': admin_creation.get('salutation', ''),
                            'title': admin_creation.get('title', ''),
                            'first_name': admin_creation.get('first_name', ''),
                            'last_name': admin_creation.get('last_name', ''),
                            'email': primary_email,
                            'phone': primary_phone,
                            'contacts': all_contacts,  # Все контакты (основные + дополнительные)
                        },

                        # Permissions object (nested structure like in JSON)
                        'permissions': {
                            'is_super_admin': form.cleaned_data.get('is_super_admin', False),
                            'can_manage_users': form.cleaned_data.get('can_manage_users', False),
                            'can_manage_database': form.cleaned_data.get('can_manage_database', False),
                            'can_view_logs': form.cleaned_data.get('can_view_logs', False),
                            'can_manage_settings': form.cleaned_data.get('can_manage_settings', False),
                            'password_expires': form.cleaned_data.get('password_expires', True),
                            'two_factor_required': form.cleaned_data.get('two_factor_required', False),
                        },

                        # Top-level admin flags
                        'is_admin': True,  # This user is admin
                        'is_active': True,

                        # Timestamps
                        'created_at': now,
                        'modified_at': now,
                        'deleted': False,
                        'last_login': None,
                        'failed_login_attempts': 0,
                        'locked_until': None,
                        'password_changed_at': now
                    }

                    logger.info(f"Creating user with structure matching JSON schema")
                    logger.info(f"Username: {user_data['username']}")
                    logger.info(f"Profile email: {user_data['profile']['email']}")
                    logger.info(f"Profile first_name: {user_data['profile']['first_name']}")
                    logger.info(f"Profile last_name: {user_data['profile']['last_name']}")
                    logger.info(f"Is admin: {user_data['is_admin']}")
                    logger.info(f"Is active: {user_data['is_active']}")
                    logger.info(f"Total contacts count: {len(user_data['profile']['contacts'])}")

                    # Use UserManager.create_user
                    if user_manager.create_user(user_data):
                        # Clear session
                        if 'admin_creation' in request.session:
                            del request.session['admin_creation']
                            request.session.modified = True

                        # Prepare contact summary for logging
                        main_contacts = 2  # email + phone (основные)
                        additional_contacts = len(admin_creation.get('additional_contacts', []))
                        total_contacts = main_contacts + additional_contacts

                        if additional_contacts > 0:
                            contact_info = f"{main_contacts} Hauptkontakte + {additional_contacts} zusätzliche = {total_contacts} insgesamt"
                        else:
                            contact_info = f"{main_contacts} Hauptkontakte"

                        success_msg = f"Administrator '{user_data['username']}' wurde erfolgreich erstellt!"
                        logger.success(success_msg)
                        messages.success(request, success_msg)

                        # НОВОЕ СООБЩЕНИЕ: информируем о следующем шаге
                        messages.info(request, "Nächster Schritt: Registrieren Sie Ihre Firma, um die Systemkonfiguration abzuschließen.")

                        # ИЗМЕНЕНО: перенаправляем на регистрацию компании с параметром
                        company_registration_url = reverse('company:register_company') + '?from_admin=true'

                        return render_with_messages(
                            request,
                            'users/create_admin_step3.html',
                            {
                                'form': form, 'text': language.text_create_admin_step3,
                                'step': 3, 'username': admin_creation.get('username', ''),
                                'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}",
                                'contact_count': total_contacts,
                                'primary_email': primary_email
                            },
                            company_registration_url  # ИЗМЕНЕНО: теперь на регистрацию компании
                        )

                except Exception as e:
                    logger.exception(f"CRITICAL ERROR creating admin: {e}")
                    messages.error(request, f"Kritischer Fehler: {str(e)}")

            else:
                logger.error(f"Form invalid: {form.errors}")
                messages.error(request, "Bitte korrigieren Sie die Formularfehler")

            # Render form with errors
            total_contacts = len(admin_creation.get('all_contacts', []))
            context = {
                'form': form, 'text': language.text_create_admin_step3,
                'step': 3, 'username': admin_creation.get('username', ''),
                'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}",
                'contact_count': total_contacts,
                'primary_email': admin_creation.get('email', '')
            }
            return render_with_messages(request, 'create_admin_step3.html', context)

        # GET request
        form = AdminPermissionsForm()
        total_contacts = len(admin_creation.get('all_contacts', []))
        context = {
            'form': form,
            'text': language.text_create_admin_step3,
            'step': 3,
            'username': admin_creation.get('username', ''),
            'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}",
            'contact_count': total_contacts,
            'primary_email': admin_creation.get('email', '')
        }
        return render(request, 'create_admin_step3.html', context)

    except Exception as e:
        logger.error(f"Error in create_admin_step3: {e}")
        messages.error(request, "Ein unerwarteter Fehler ist aufgetreten")
        return redirect('users:create_admin_step2')