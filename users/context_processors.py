# users/context_processors.py - Context processor для аутентификации - ИСПРАВЛЕНО

from loguru import logger
from .user_utils import UserManager
from mongodb.mongodb_config import MongoConfig


def auth_context(request):
    """Context processor для передачи информации об аутентификации"""
    try:
        # ИСПРАВЛЕНО: импортируем функцию из views
        from .views import is_user_authenticated, should_show_login_modal

        # Проверяем, аутентифицирован ли пользователь
        is_auth, user_data = is_user_authenticated(request)

        # Определяем, нужно ли показывать модальное окно входа
        show_login = False
        if not is_auth:
            show_login = should_show_login_modal()

        # Получаем информацию о системе
        system_info = get_system_info()

        context = {
            # Информация о пользователе
            'is_authenticated': is_auth,
            'current_user': user_data,
            'user_display_name': get_user_display_name(user_data) if user_data else None,

            # Информация об аутентификации
            'show_login_modal': show_login,
            'requires_auth': not is_auth and should_show_login_modal(),

            # Системная информация
            'system_info': system_info,
            'system_version': '1.0.0',

            # Статистика пользователей (для администраторов)
            'user_stats': get_user_stats() if is_auth and user_data and user_data.get('is_admin') else None
        }

        logger.debug(f"Auth context: is_auth={is_auth}, show_login={show_login}")
        return context

    except Exception as e:
        logger.error(f"Ошибка в auth_context: {e}")
        return {
            'is_authenticated': False,
            'current_user': None,
            'show_login_modal': False,
            'requires_auth': False,
            'system_info': {'status': 'error'},
            'system_version': '1.0.0'
        }


def get_user_display_name(user_data):
    """Формирует отображаемое имя пользователя"""
    if not user_data:
        return None

    try:
        profile = user_data.get('profile', {})
        first_name = profile.get('first_name', '')
        last_name = profile.get('last_name', '')

        if first_name and last_name:
            return f"{first_name} {last_name}"
        elif first_name:
            return first_name
        else:
            return user_data.get('username', 'User')

    except Exception as e:
        logger.error(f"Ошибка получения display name: {e}")
        return user_data.get('username', 'User')


def get_system_info():
    """Получает информацию о состоянии системы"""
    try:
        # Проверяем MongoDB
        config = MongoConfig.read_config()
        mongodb_status = 'connected' if config.get('setup_completed') else 'disconnected'

        # Проверяем пользователей
        try:
            user_manager = UserManager()
            admin_count = user_manager.get_admin_count()
            user_status = 'ready' if admin_count > 0 else 'no_admins'
        except Exception:
            user_status = 'error'
            admin_count = 0

        # Проверяем компанию
        try:
            from company.company_manager import CompanyManager
            company_manager = CompanyManager()
            company_status = 'registered' if company_manager.has_company() else 'not_registered'
        except Exception:
            company_status = 'error'

        return {
            'status': 'ready' if all([
                mongodb_status == 'connected',
                user_status == 'ready',
                company_status == 'registered'
            ]) else 'incomplete',
            'mongodb': mongodb_status,
            'users': user_status,
            'company': company_status,
            'admin_count': admin_count
        }

    except Exception as e:
        logger.error(f"Ошибка получения системной информации: {e}")
        return {
            'status': 'error',
            'mongodb': 'error',
            'users': 'error',
            'company': 'error',
            'admin_count': 0
        }


def get_user_stats():
    """Получает статистику пользователей для администраторов"""
    try:
        user_manager = UserManager()
        stats = user_manager.get_collection_stats()

        return {
            'total_users': stats.get('total_users', 0),
            'active_users': stats.get('active_users', 0),
            'admin_users': stats.get('admin_users', 0),
            'locked_users': stats.get('locked_users', 0)
        }

    except Exception as e:
        logger.error(f"Ошибка получения статистики пользователей: {e}")
        return {
            'total_users': 0,
            'active_users': 0,
            'admin_users': 0,
            'locked_users': 0
        }