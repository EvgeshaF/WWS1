# auth/decorators.py - Декораторы для проверки авторизации и прав доступа

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from loguru import logger
import time
from collections import defaultdict
from datetime import datetime, timedelta

# Хранилище для rate limiting
_rate_limit_storage = defaultdict(list)


def login_required(redirect_url: str = 'users:login_page'):
    """
    Декоратор для проверки авторизации пользователя

    Args:
        redirect_url: URL для перенаправления неавторизованных пользователей

    Usage:
        @login_required()
        def my_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Проверяем авторизацию
            from .authentication import is_user_authenticated
            is_auth, user_data = is_user_authenticated(request)

            if not is_auth:
                logger.warning(f"🚫 Неавторизованный доступ к {view_func.__name__}")

                # Для AJAX запросов возвращаем JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Authentifizierung erforderlich',
                        'redirect_url': redirect_url
                    }, status=401)

                # Для обычных запросов - редирект
                messages.warning(request, "Bitte melden Sie sich an, um auf diese Seite zuzugreifen")
                return redirect(redirect_url)

            # Обновляем время последней активности
            from .session import refresh_session_activity
            refresh_session_activity(request)

            # Добавляем данные пользователя в request для удобства
            request.user_data = user_data

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def admin_required(redirect_url: str = 'home'):
    """
    Декоратор для проверки прав администратора

    Args:
        redirect_url: URL для перенаправления пользователей без прав

    Usage:
        @admin_required()
        def admin_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Сначала проверяем авторизацию
            from .authentication import is_user_authenticated
            is_auth, user_data = is_user_authenticated(request)

            if not is_auth:
                logger.warning(f"🚫 Неавторизованный доступ к админ-функции {view_func.__name__}")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Administratorrechte erforderlich'
                    }, status=403)

                messages.error(request, "Zugriff verweigert: Administratorrechte erforderlich")
                return redirect('users:login_page')

            # Проверяем права администратора
            if not user_data.get('is_admin', False):
                logger.warning(f"🚫 Попытка доступа к админ-функции без прав: {user_data.get('username')}")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Administratorrechte erforderlich'
                    }, status=403)

                messages.error(request, "Zugriff verweigert: Diese Funktion ist nur für Administratoren verfügbar")
                return redirect(redirect_url)

            # Обновляем активность
            from .session import refresh_session_activity
            refresh_session_activity(request)

            request.user_data = user_data

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def anonymous_required(redirect_url: str = 'home'):
    """
    Декоратор для страниц, доступных только неавторизованным пользователям
    (например, страница регистрации или входа)

    Args:
        redirect_url: URL для перенаправления авторизованных пользователей

    Usage:
        @anonymous_required()
        def register_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            from .authentication import is_user_authenticated
            is_auth, _ = is_user_authenticated(request)

            if is_auth:
                logger.debug(f"ℹ️ Авторизованный пользователь перенаправлен с {view_func.__name__}")
                messages.info(request, "Sie sind bereits angemeldet")
                return redirect(redirect_url)

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def permission_required(permission: str, redirect_url: str = 'home'):
    """
    Декоратор для проверки конкретного разрешения

    Args:
        permission: Требуемое разрешение (например, 'can_manage_users')
        redirect_url: URL для перенаправления при отсутствии прав

    Usage:
        @permission_required('can_manage_users')
        def manage_users_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            from .authentication import is_user_authenticated, verify_user_permissions
            is_auth, user_data = is_user_authenticated(request)

            if not is_auth:
                logger.warning(f"🚫 Неавторизованный доступ к {view_func.__name__}")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Authentifizierung erforderlich'
                    }, status=401)

                messages.warning(request, "Bitte melden Sie sich an")
                return redirect('users:login_page')

            # Проверяем разрешение
            if not verify_user_permissions(user_data, permission):
                logger.warning(f"🚫 Недостаточно прав для {view_func.__name__}: {user_data.get('username')}")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Berechtigung "{permission}" erforderlich'
                    }, status=403)

                messages.error(request, "Zugriff verweigert: Unzureichende Berechtigungen")
                return redirect(redirect_url)

            from .session import refresh_session_activity
            refresh_session_activity(request)

            request.user_data = user_data

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def rate_limit_user(max_requests: int = 5, time_window: int = 60):
    """
    Декоратор для ограничения частоты запросов от пользователя

    Args:
        max_requests: Максимальное количество запросов
        time_window: Временное окно в секундах

    Usage:
        @rate_limit_user(max_requests=5, time_window=60)
        def api_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Получаем идентификатор пользователя
            user_id = request.session.get('user_id') or request.META.get('REMOTE_ADDR', 'unknown')
            key = f"{view_func.__name__}:{user_id}"

            now = datetime.now()
            cutoff = now - timedelta(seconds=time_window)

            # Очищаем старые записи
            _rate_limit_storage[key] = [
                timestamp for timestamp in _rate_limit_storage[key]
                if timestamp > cutoff
            ]

            # Проверяем лимит
            if len(_rate_limit_storage[key]) >= max_requests:
                logger.warning(f"⚠️ Rate limit превышен для {user_id} в {view_func.__name__}")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Zu viele Anfragen. Bitte versuchen Sie es später erneut.'
                    }, status=429)

                messages.warning(request, "Zu viele Anfragen. Bitte warten Sie einen Moment.")
                return HttpResponseForbidden("Rate limit exceeded")

            # Добавляем текущий запрос
            _rate_limit_storage[key].append(now)

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def session_activity_required(max_inactive_seconds: int = 3600):
    """
    Декоратор для проверки активности сессии

    Args:
        max_inactive_seconds: Максимальное время неактивности в секундах

    Usage:
        @session_activity_required(max_inactive_seconds=1800)
        def sensitive_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            from .session import is_session_expired, clear_user_session

            if is_session_expired(request, max_inactive_seconds):
                logger.warning(f"⏰ Сессия истекла для {request.session.get('username')}")

                clear_user_session(request)

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Sitzung abgelaufen. Bitte melden Sie sich erneut an.',
                        'redirect_url': 'users:login_page'
                    }, status=401)

                messages.warning(request, "Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.")
                return redirect('users:login_page')

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator