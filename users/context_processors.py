from loguru import logger
from mongodb.mongodb_config import MongoConfig

from user_auth import (
    is_user_authenticated,
    get_user_display_name,
    should_show_login_modal,
)
from .user_utils import UserManager


def auth_context(request):
    """Context processor для передачи информации об аутентификации"""
    try:
        # ИСПОЛЬЗУЕМ НОВЫЙ МОДУЛЬ AUTH
        is_auth, user_data = is_user_authenticated(request)

        # Проверяем, не находимся ли мы на странице создания админа
        current_path = request.path
        is_admin_creation_page = (
                '/users/create-admin/' in current_path or
                current_path.startswith('/users/create-admin/') or
                'create-admin' in current_path
        )

        logger.debug(f"🔍 Current path: {current_path}")
        logger.debug(f"🔍 is_admin_creation_page: {is_admin_creation_page}")

        # Определяем, нужно ли показывать модальное окно входа
        show_login = False
        if not is_auth and not is_admin_creation_page:
            # ИСПОЛЬЗУЕМ НОВЫЙ МОДУЛЬ AUTH
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
            'is_admin_creation_page': is_admin_creation_page,

            # Системная информация
            'system_info': system_info,
            'system_version': '1.0.0',

            # Статистика пользователей (для администраторов)
            'user_stats': get_user_stats() if is_auth and user_data and user_data.get('is_admin') else None
        }

        logger.debug(f"Auth context: is_auth={is_auth}, show_login={show_login}, admin_creation={is_admin_creation_page}")
        return context

    except Exception as e:
        logger.error(f"Ошибка в auth_context: {e}")
        return {
            'is_authenticated': False,
            'current_user': None,
            'show_login_modal': False,
            'requires_auth': False,
            'is_admin_creation_page': False,
            'system_info': {'status': 'error'},
            'system_version': '1.0.0'
        }


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