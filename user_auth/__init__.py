# WWS1/auth/__init__.py - Централизованная система аутентификации


from .authentication import (
    authenticate_user,
    is_user_authenticated,
    clear_user_session,
    should_show_login_modal,
    get_user_display_name,
    verify_user_permissions,
)

from .decorators import (
    login_required,
    admin_required,
    anonymous_required,
    permission_required,
    rate_limit_user,
)

from .session import (
    create_user_session,
    update_user_session,
    get_session_data,
    extend_session,
    is_session_expired,
    refresh_session_activity,
    get_session_info,
)

__version__ = '1.0.0'
__author__ = 'WWS1 Development Team'

__all__ = [
    # Authentication
    'authenticate_user',
    'is_user_authenticated',
    'clear_user_session',
    'should_show_login_modal',
    'get_user_display_name',
    'verify_user_permissions',

    # Decorators
    'login_required',
    'admin_required',
    'anonymous_required',
    'permission_required',
    'rate_limit_user',

    # Session Management
    'create_user_session',
    'update_user_session',
    'get_session_data',
    'extend_session',
    'is_session_expired',
    'refresh_session_activity',
    'get_session_info',
]

# Экспортируем также для удобного доступа
from . import authentication
from . import decorators
from . import session