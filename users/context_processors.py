# users/context_processors.py - ИСПРАВЛЕНИЕ: не показываем login modal на страницах создания админа

from loguru import logger
from .user_utils import UserManager
from mongodb.mongodb_config import MongoConfig


def auth_context(request):
    """Context processor для передачи информации об аутентификации"""
    try:
        # Проверяем, аутентифицирован ли пользователь
        is_auth, user_data = is_user_authenticated(request)

        # КРИТИЧНО: Не показываем login modal на страницах создания администратора
        current_path = request.path
        is_admin_creation_page = (
                '/users/create-admin/' in current_path or
                current_path.startswith('/users/create-admin/') or
                'create-admin' in current_path
        )

        # DEBUG
        logger.debug(f"🔍 Current path: {current_path}")
        logger.debug(f"🔍 is_admin_creation_page: {is_admin_creation_page}")

        # Определяем, нужно ли показывать модальное окно входа
        show_login = False
        if not is_auth and not is_admin_creation_page:
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
            'is_admin_creation_page': is_admin_creation_page,  # НОВОЕ

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


def is_user_authenticated(request):
    """Проверяет, авторизован ли пользователь"""
    try:
        user_authenticated = request.session.get('user_authenticated', False)
        if user_authenticated:
            username = request.session.get('username')
            if username:
                from .user_utils import UserManager
                user_manager = UserManager()
                user_data = user_manager.find_user_by_username(username)
                if user_data and user_data.get('is_active', False):
                    return True, user_data
                else:
                    # Очищаем недействительную сессию
                    session_keys = ['user_authenticated', 'user_id', 'username', 'is_admin', 'user_data']
                    for key in session_keys:
                        if key in request.session:
                            del request.session[key]
                    request.session.modified = True
                    return False, None
        return False, None
    except Exception as e:
        logger.error(f"Ошибка проверки авторизации: {e}")
        return False, None


def should_show_login_modal():
    """Определяет, нужно ли показывать модальное окно входа"""
    try:
        user_manager = UserManager()
        admin_count = user_manager.get_admin_count()
        return admin_count > 0
    except Exception as e:
        logger.error(f"Ошибка проверки необходимости показа модального окна: {e}")
        return False


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