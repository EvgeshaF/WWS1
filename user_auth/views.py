# auth/views.py - View-функции для авторизации

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from loguru import logger

from .authentication import authenticate_user, is_user_authenticated
from .session import create_user_session, clear_user_session
from .decorators import anonymous_required
from .forms import LoginForm


@require_http_methods(["GET", "POST"])
@never_cache
def login_view(request):

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
            user = authenticate_user(username, password)

            if user:
                logger.success(f"✅ Пользователь '{username}' успешно авторизован")

                # Создаем сессию
                create_user_session(request, user, remember_me)

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
            from users.user_utils import UserManager
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
        clear_user_session(request)
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
        clear_user_session(request)
        request.session.flush()
        messages.info(request, "Sie wurden abgemeldet.")
        return redirect('home')


@require_http_methods(["GET"])
@anonymous_required()
def login_page_view(request):

    try:
        form = LoginForm()

        # Получаем дополнительную информацию для отображения
        try:
            from users.user_utils import UserManager
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


@require_http_methods(["POST"])
@never_cache
def refresh_session_view(request):

    try:
        is_auth, user_data = is_user_authenticated(request)

        if not is_auth:
            return JsonResponse({
                'success': False,
                'message': 'Sitzung abgelaufen'
            }, status=401)

        from .session import refresh_session_activity
        refresh_session_activity(request)

        return JsonResponse({
            'success': True,
            'message': 'Sitzung aktualisiert'
        })

    except Exception as e:
        logger.error(f"❌ Ошибка обновления сессии: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Fehler beim Aktualisieren der Sitzung'
        }, status=500)