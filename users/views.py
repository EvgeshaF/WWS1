# users/views.py - ПОЛНОЕ ИСПРАВЛЕНИЕ

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

from .forms import LoginForm
from .user_utils import UserManager
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
@require_http_methods(["GET", "POST"])
@never_cache
def login_view(request):
    """Форма авторизации с поддержкой AJAX"""
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
                    return render(request, 'users/login_page.html', {'form': LoginForm()})

            if not password:
                error_message = "Passwort ist erforderlich"
                if is_ajax:
                    return JsonResponse({'success': False, 'message': error_message})
                else:
                    messages.error(request, error_message)
                    return render(request, 'users/login_page.html', {'form': LoginForm()})

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

                success_message = f"Willkommen, {user.get('profile', {}).get('first_name', username)}!"

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
                    return render(request, 'users/login_page.html', {'form': LoginForm()})

        # GET запрос
        form = LoginForm()
        return render(request, 'users/login_page.html', {'form': form})

    except Exception as e:
        logger.exception(f"💥 КРИТИЧЕСКАЯ ОШИБКА в login_view: {e}")
        error_message = "Ein unerwarteter Fehler ist aufgetreten"

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_message})
        else:
            messages.error(request, error_message)
            return render(request, 'users/login_page.html', {'form': LoginForm()})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Выход из системы"""
    try:
        username = request.session.get('username', 'Unknown')
        logger.info(f"🚪 Выход пользователя: {username}")
        request.session.flush()
        messages.info(request, "Sie wurden erfolgreich abgemeldet")
        return redirect('home')
    except Exception as e:
        logger.error(f"Ошибка при выходе: {e}")
        request.session.flush()
        return redirect('home')