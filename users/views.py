# users/views.py - ОБНОВЛЕН для использования WWS1.auth

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

# ✅ ИМПОРТИРУЕМ ИЗ ЦЕНТРАЛИЗОВАННОГО МОДУЛЯ WWS1.auth
from auth import (
    authenticate_user,
    is_user_authenticated,
    clear_user_session,
    get_user_display_name,
    create_user_session,
    anonymous_required,
    login_required,
    admin_required,
)

from .forms import (
    LoginForm, CreateAdminUserForm, AdminProfileForm,
    AdminPermissionsForm, get_communication_types_from_mongodb,
    get_communication_config_from_mongodb
)
from .user_utils import UserManager
from . import language
from django_ratelimit.decorators import ratelimit


# ==================== АУТЕНТИФИКАЦИЯ ====================

@ratelimit(key='ip', rate='5/m', method='POST')
@require_http_methods(["GET"])
@anonymous_required(redirect_url='/')
def login_page_view(request):
    """Отдельная страница входа"""
    try:
        form = LoginForm()

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
        logger.error(f"❌ Ошибка в login_page_view: {e}")
        messages.error(request, "Ein Fehler ist aufgetreten")
        return redirect('home')


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

            if not username:
                error_message = "Benutzername ist erforderlich"
                if is_ajax:
                    return JsonResponse({'success': False, 'message': error_message})
                messages.error(request, error_message)
                form = LoginForm(request.POST)
                return render(request, 'users/login_page.html', {'form': form})

            if not password:
                error_message = "Passwort ist erforderlich"
                if is_ajax:
                    return JsonResponse({'success': False, 'message': error_message})
                messages.error(request, error_message)
                form = LoginForm(request.POST)
                return render(request, 'users/login_page.html', {'form': form})

            # ✅ ИСПОЛЬЗУЕМ WWS1.auth
            user = authenticate_user(username, password)

            if user:
                logger.success(f"✅ Пользователь '{username}' успешно авторизован")

                # ✅ СОЗДАЕМ СЕССИЮ через WWS1.auth
                create_user_session(request, user, remember_me)

                # Формируем приветственное сообщение
                display_name = get_user_display_name(user)
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

        # GET запрос
        form = LoginForm()

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
    """Выход из системы"""
    try:
        username = request.session.get('username', 'Unknown')
        logger.info(f"🚪 Выход пользователя: {username}")

        # Получаем информацию о пользователе перед очисткой
        user_display_name = None
        if 'user_data' in request.session:
            user_data = request.session['user_data']
            user_display_name = get_user_display_name(user_data)

        # ✅ ИСПОЛЬЗУЕМ WWS1.auth для очистки
        clear_user_session(request)

        # Полная очистка сессии
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
        request.session.flush()
        messages.info(request, "Sie wurden abgemeldet.")
        return redirect('home')


# ==================== ПРИМЕРЫ ЗАЩИЩЕННЫХ VIEWS ====================

@login_required
def user_profile(request):
    """
    Профиль пользователя - требует авторизации
    request.current_user добавлен декоратором @login_required
    """
    user_data = request.current_user

    context = {
        'user_data': user_data,
        'display_name': get_user_display_name(user_data)
    }

    return render(request, 'users/profile.html', context)


@admin_required
def admin_panel(request):
    """
    Панель администратора - требует прав админа
    request.current_user добавлен декоратором
    """
    user_data = request.current_user

    context = {
        'user_data': user_data,
        'is_super_admin': user_data.get('is_super_admin', False)
    }

    return render(request, 'users/admin_panel.html', context)

# ==================== СОЗДАНИЕ АДМИНИСТРАТОРА ====================
# (Код создания администратора остается без изменений)