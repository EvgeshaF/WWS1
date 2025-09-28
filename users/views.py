# users/views.py - ПОЛНОЕ ИСПРАВЛЕНИЕ с функциями создания администратора

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from loguru import logger
import datetime
import json

from .forms import (
    LoginForm, CreateAdminUserForm, AdminProfileForm,
    AdminPermissionsForm, get_communication_types_from_mongodb,
    get_communication_config_from_mongodb
)
from .user_utils import UserManager
from . import language
from django_ratelimit.decorators import ratelimit


def is_user_authenticated(request):
    """Проверяет, авторизован ли пользователь"""
    try:
        user_authenticated = request.session.get('user_authenticated', False)
        if user_authenticated:
            username = request.session.get('username')
            if username:
                user_manager = UserManager()
                user_data = user_manager.find_user_by_username(username)
                if user_data and user_data.get('is_active', False):
                    return True, user_data
                else:
                    clear_user_session(request)
                    return False, None
        return False, None
    except Exception as e:
        logger.error(f"Ошибка проверки авторизации: {e}")
        return False, None


def clear_user_session(request):
    """Очищает данные пользователя из сессии"""
    session_keys = ['user_authenticated', 'user_id', 'username', 'is_admin', 'user_data']
    for key in session_keys:
        if key in request.session:
            del request.session[key]
    request.session.modified = True


def should_show_login_modal():
    """Определяет, нужно ли показывать модальное окно входа"""
    try:
        user_manager = UserManager()
        admin_count = user_manager.get_admin_count()
        return admin_count > 0
    except Exception as e:
        logger.error(f"Ошибка проверки необходимости показа модального окна: {e}")
        return False


@ratelimit(key='ip', rate='5/m', method='POST')
@require_http_methods(["GET"])
def login_page_view(request):
    """Отдельная страница входа (альтернатива модальному окну)"""
    try:
        # Если пользователь уже авторизован, перенаправляем на главную
        is_auth, _ = is_user_authenticated(request)
        if is_auth:
            return redirect('home')

        form = LoginForm()

        # Получаем дополнительную информацию для отображения
        try:
            user_manager = UserManager()
            admin_count = user_manager.get_admin_count()
        except Exception:
            admin_count = 0

        context = {
            'form': form,
            'admin_count': admin_count,
            'system_version': '1.0.0'
        }

        return render(request, 'users/login_page.html', context)

    except Exception as e:
        logger.error(f"Ошибка в login_page_view: {e}")
        messages.error(request, "Ein Fehler ist aufgetreten")
        return redirect('home')


@require_http_methods(["GET", "POST"])
@never_cache
def login_view(request):
    """Форма авторизации с поддержкой AJAX и обычных запросов"""
    try:
        if request.method == "POST":
            logger.info("🔐 Обработка POST запроса для входа")

            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

            username = request.POST.get("username", "").strip()
            password = request.POST.get("password", "")
            remember_me = request.POST.get("remember_me") == "on"

            logger.info(f"Попытка входа: {username}, AJAX: {is_ajax}")

            # Валидация
            if not username:
                error_message = "Benutzername ist erforderlich"
                if is_ajax:
                    return JsonResponse({'success': False, 'message': error_message})
                else:
                    messages.error(request, error_message)
                    form = LoginForm(request.POST)
                    return render(request, 'users/login_page.html', {'form': form})

            if not password:
                error_message = "Passwort ist erforderlich"
                if is_ajax:
                    return JsonResponse({'success': False, 'message': error_message})
                else:
                    messages.error(request, error_message)
                    form = LoginForm(request.POST)
                    return render(request, 'users/login_page.html', {'form': form})

            # Аутентификация
            user_manager = UserManager()
            user = user_manager.authenticate_user(username, password)

            if user:
                logger.success(f"✅ Пользователь '{username}' успешно авторизован")

                # Сохраняем в сессии
                request.session["user_authenticated"] = True
                request.session["user_id"] = str(user["_id"])
                request.session["username"] = user["username"]
                request.session["is_admin"] = user.get("is_admin", False)
                request.session["user_data"] = {
                    'username': user['username'],
                    'is_admin': user.get('is_admin', False),
                    'is_active': user.get('is_active', True),
                    'profile': user.get('profile', {})
                }

                if remember_me:
                    request.session.set_expiry(1209600)  # 2 недели
                else:
                    request.session.set_expiry(0)  # До закрытия браузера

                request.session.modified = True

                # Формируем приветственное сообщение
                profile = user.get('profile', {})
                display_name = profile.get('first_name', username)
                if profile.get('last_name'):
                    display_name += f" {profile['last_name']}"

                success_message = f"Willkommen, {display_name}!"

                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': success_message,
                        'redirect_url': reverse('home')
                    })
                else:
                    messages.success(request, success_message)
                    return redirect('home')

            else:
                error_message = "Ungültiger Benutzername oder Passwort"
                logger.warning(f"❌ Неудачная попытка входа для '{username}'")

                if is_ajax:
                    return JsonResponse({'success': False, 'message': error_message})
                else:
                    messages.error(request, error_message)
                    form = LoginForm(request.POST)
                    return render(request, 'users/login_page.html', {'form': form})

        # GET запрос - показываем страницу входа
        form = LoginForm()

        # Получаем дополнительную информацию для отображения
        try:
            user_manager = UserManager()
            admin_count = user_manager.get_admin_count()
        except Exception:
            admin_count = 0

        context = {
            'form': form,
            'admin_count': admin_count,
            'system_version': '1.0.0'
        }

        return render(request, 'users/login_page.html', context)

    except Exception as e:
        logger.exception(f"💥 КРИТИЧЕСКАЯ ОШИБКА в login_view: {e}")
        error_message = "Ein unerwarteter Fehler ist aufgetreten"

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_message})
        else:
            messages.error(request, error_message)
            form = LoginForm()
            return render(request, 'users/login_page.html', {'form': form})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Выход из системы с улучшенной обработкой"""
    try:
        username = request.session.get('username', 'Unknown')
        logger.info(f"🚪 Выход пользователя: {username}")

        # Получаем информацию о пользователе перед очисткой сессии
        user_display_name = None
        if 'user_data' in request.session:
            user_data = request.session['user_data']
            profile = user_data.get('profile', {})
            first_name = profile.get('first_name', '')
            if first_name:
                user_display_name = first_name
            else:
                user_display_name = username

        # Очищаем сессию
        request.session.flush()

        # Формируем сообщение
        if user_display_name:
            message = f"Auf Wiedersehen, {user_display_name}! Sie wurden erfolgreich abgemeldet."
        else:
            message = "Sie wurden erfolgreich abgemeldet."

        messages.success(request, message)
        logger.success(f"✅ Пользователь '{username}' успешно вышел из системы")

        return redirect('home')

    except Exception as e:
        logger.error(f"❌ Ошибка при выходе: {e}")
        # В любом случае очищаем сессию
        request.session.flush()
        messages.info(request, "Sie wurden abgemeldet.")
        return redirect('home')


# ==================== СОЗДАНИЕ АДМИНИСТРАТОРА ====================

def render_with_messages(request, template_name, context, success_redirect=None):
    """Универсальная функция для рендеринга с поддержкой HTMX"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    if is_htmx:
        # Создаем JSON ответ с сообщениями
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

        if success_redirect:
            response['HX-Redirect'] = success_redirect
        return response
    else:
        if success_redirect:
            return redirect(success_redirect)
        return render(request, template_name, context)


@ratelimit(key='ip', rate='10/m', method='POST')
def create_admin_step1(request):
    """Шаг 1: Создание базовых учетных данных администратора"""
    logger.info("🚀 === ВХОД В create_admin_step1 ===")

    if request.method == 'POST':
        logger.info("📥 POST запрос для создания учетных данных")

        form = CreateAdminUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            logger.info(f"✅ Форма валидна для пользователя: {username}")

            # Проверяем, что пользователь не существует
            user_manager = UserManager()
            existing_user = user_manager.find_user_by_username(username)

            if existing_user:
                error_msg = language.error_messages['user_exists']
                logger.error(f"❌ {error_msg}: {username}")
                messages.error(request, error_msg)

                context = {'form': form, 'text': language.text_create_admin_step1, 'step': 1}
                return render_with_messages(request, 'create_admin_step1.html', context)

            # Сохраняем данные в сессию
            request.session['admin_creation'] = {
                'username': username,
                'password': make_password(password),  # Хешируем пароль
                'step': 1,
                'created_at': datetime.datetime.now().isoformat()
            }
            request.session.modified = True

            success_msg = language.success_messages['step1_completed'].format(username=username)
            logger.success(f"✅ {success_msg}")
            messages.success(request, success_msg)

            return render_with_messages(
                request,
                'create_admin_step1.html',
                {'form': form, 'text': language.text_create_admin_step1, 'step': 1},
                reverse('users:create_admin_step2')
            )
        else:
            logger.error(f"❌ Форма невалидна: {form.errors}")
            messages.error(request, language.validation_messages['form_invalid'])

    # GET запрос
    form = CreateAdminUserForm()
    context = {'form': form, 'text': language.text_create_admin_step1, 'step': 1}
    return render(request, 'create_admin_step1.html', context)


@ratelimit(key='ip', rate='10/m', method='POST')
def create_admin_step2(request):
    """Шаг 2: Профильные данные и контакты администратора"""
    logger.info("🚀 === ВХОД В create_admin_step2 ===")

    # Проверяем наличие данных шага 1
    admin_creation = request.session.get('admin_creation')
    if not admin_creation or admin_creation.get('step') != 1:
        logger.error("❌ Данные шага 1 отсутствуют")
        messages.error(request, language.error_messages['step_incomplete'])
        return redirect('users:create_admin_step1')

    username = admin_creation['username']
    logger.info(f"📝 Шаг 2 для пользователя: {username}")

    if request.method == 'POST':
        logger.info("📥 POST запрос для профильных данных")

        form = AdminProfileForm(request.POST)
        if form.is_valid():
            logger.info("✅ Основная форма валидна")

            # Получаем данные основной формы
            profile_data = {
                'salutation': form.cleaned_data['salutation'],
                'title': form.cleaned_data.get('title', ''),
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone']
            }

            # Обрабатываем дополнительные контакты
            additional_contacts_data = request.POST.get('additional_contacts_data', '[]')
            try:
                additional_contacts = json.loads(additional_contacts_data)
                logger.info(f"📞 Получено дополнительных контактов: {len(additional_contacts)}")
            except json.JSONDecodeError:
                logger.error("❌ Ошибка парсинга JSON дополнительных контактов")
                additional_contacts = []

            # Формируем полные контактные данные
            contacts = {
                'system_email': profile_data['email'],
                'system_phone': profile_data['phone'],
                'additional_contacts': additional_contacts
            }

            # Обновляем данные в сессии
            admin_creation.update({
                'profile': profile_data,
                'contacts': contacts,
                'step': 2,
                'updated_at': datetime.datetime.now().isoformat()
            })
            request.session['admin_creation'] = admin_creation
            request.session.modified = True

            contact_info = f"System-E-Mail, System-Telefon"
            if additional_contacts:
                contact_info += f" + {len(additional_contacts)} zusätzliche"

            success_msg = language.success_messages['step2_completed'].format(contact_info=contact_info)
            logger.success(f"✅ {success_msg}")
            messages.success(request, success_msg)

            return render_with_messages(
                request,
                'create_admin_step2.html',
                {'form': form, 'text': language.text_create_admin_step2, 'step': 2, 'username': username},
                reverse('users:create_admin_step3')
            )
        else:
            logger.error(f"❌ Форма профиля невалидна: {form.errors}")
            messages.error(request, language.validation_messages['form_invalid'])

    # GET запрос
    form = AdminProfileForm()

    # Получаем типы контактов для передачи в шаблон
    contact_type_choices = get_communication_types_from_mongodb()
    communication_config = get_communication_config_from_mongodb()

    context = {
        'form': form,
        'text': language.text_create_admin_step2,
        'step': 2,
        'username': username,
        'contact_type_choices': contact_type_choices,
        'contact_type_choices_json': json.dumps([{'value': choice[0], 'text': choice[1]} for choice in contact_type_choices]),
        'communication_config': communication_config,
        'existing_additional_contacts': []  # Пустой список для новых пользователей
    }

    return render(request, 'create_admin_step2.html', context)


@ratelimit(key='ip', rate='5/m', method='POST')
def create_admin_step3(request):
    """Шаг 3: Права доступа и создание администратора"""
    logger.info("🚀 === ВХОД В create_admin_step3 ===")

    # Проверяем наличие данных предыдущих шагов
    admin_creation = request.session.get('admin_creation')
    if not admin_creation or admin_creation.get('step') != 2:
        logger.error("❌ Данные предыдущих шагов отсутствуют")
        messages.error(request, language.error_messages['step_incomplete'])
        return redirect('users:create_admin_step1')

    username = admin_creation['username']
    profile = admin_creation.get('profile', {})
    full_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()

    logger.info(f"🔐 Шаг 3 для пользователя: {username} ({full_name})")

    if request.method == 'POST':
        logger.info("📥 POST запрос для создания администратора")

        form = AdminPermissionsForm(request.POST)
        if form.is_valid():
            logger.info("✅ Форма прав доступа валидна")

            # Собираем все данные для создания пользователя
            user_data = {
                # Основные данные
                'username': admin_creation['username'],
                'password': admin_creation['password'],  # Уже хешированный

                # Профильные данные
                'profile': admin_creation['profile'],

                # Контактные данные
                'contacts': admin_creation['contacts'],

                # Права доступа
                'is_admin': True,
                'is_active': True,
                'is_super_admin': form.cleaned_data.get('is_super_admin', True),
                'permissions': {
                    'can_manage_users': form.cleaned_data.get('can_manage_users', True),
                    'can_manage_database': form.cleaned_data.get('can_manage_database', True),
                    'can_view_logs': form.cleaned_data.get('can_view_logs', True),
                    'can_manage_settings': form.cleaned_data.get('can_manage_settings', True),
                },

                # Настройки безопасности
                'security': {
                    'password_expires': form.cleaned_data.get('password_expires', True),
                    'two_factor_required': form.cleaned_data.get('two_factor_required', True),
                },

                # Системные поля
                'created_at': datetime.datetime.now(),
                'modified_at': datetime.datetime.now(),
                'deleted': False,
                'last_login': None,
                'failed_login_attempts': 0,
                'locked_until': None,
                'password_changed_at': datetime.datetime.now()
            }

            # Создаем пользователя
            user_manager = UserManager()
            success = user_manager.create_user(user_data)

            if success:
                # Очищаем данные из сессии
                if 'admin_creation' in request.session:
                    del request.session['admin_creation']
                    request.session.modified = True

                # Подсчитываем контакты для сообщения
                contacts_count = 2  # system email + phone
                additional_contacts = admin_creation.get('contacts', {}).get('additional_contacts', [])
                if additional_contacts:
                    contacts_count += len(additional_contacts)

                contact_info = f"{contacts_count} Kontakte insgesamt"
                success_msg = language.success_messages['admin_created'].format(
                    username=username,
                    contact_info=contact_info
                )

                logger.success(f"🎉 {success_msg}")
                messages.success(request, success_msg)

                return render_with_messages(
                    request,
                    'create_admin_step3.html',
                    {'form': form, 'text': language.text_create_admin_step3, 'step': 3, 'username': username, 'full_name': full_name},
                    reverse('home')
                )
            else:
                error_msg = language.error_messages['user_creation_error']
                logger.error(f"❌ {error_msg}")
                messages.error(request, error_msg)
        else:
            logger.error(f"❌ Форма прав доступа невалидна: {form.errors}")
            messages.error(request, language.validation_messages['form_invalid'])

    # GET запрос
    form = AdminPermissionsForm()
    context = {
        'form': form,
        'text': language.text_create_admin_step3,
        'step': 3,
        'username': username,
        'full_name': full_name
    }

    return render(request, 'create_admin_step3.html', context)