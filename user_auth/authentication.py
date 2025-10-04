# WWS1/auth/authentication.py - Основная логика аутентификации

from typing import Optional, Dict, Any, Tuple
from loguru import logger
from django.contrib.auth.hashers import check_password
import datetime

from users.user_utils import UserManager


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:

    try:
        logger.info(f"🔑 Попытка аутентификации: {username}")

        user_manager = UserManager()
        user = user_manager.find_user_by_username(username)

        if not user:
            logger.warning(f"❌ Пользователь '{username}' не найден")
            return None

        if not user.get('is_active', False):
            logger.warning(f"❌ Пользователь '{username}' неактивен")
            return None

        # Проверяем временную блокировку
        locked_until = user.get('locked_until')
        if locked_until and locked_until > datetime.datetime.now():
            logger.warning(f"❌ Пользователь '{username}' заблокирован до {locked_until}")
            return None

        # Проверяем пароль
        stored_password = user.get('password')
        if not stored_password:
            logger.error(f"❌ У пользователя '{username}' отсутствует пароль")
            return None

        if check_password(password, stored_password):
            _update_login_success(username)
            logger.success(f"✅ Пользователь '{username}' успешно авторизован")
            return user
        else:
            _update_login_failure(username)
            logger.warning(f"❌ Неверный пароль для '{username}'")
            return None

    except Exception as e:
        logger.error(f"❌ Ошибка аутентификации '{username}': {e}")
        return None


def is_user_authenticated(request) -> Tuple[bool, Optional[Dict[str, Any]]]:

    try:
        user_authenticated = request.session.get('user_authenticated', False)

        if not user_authenticated:
            return False, None

        username = request.session.get('username')
        if not username:
            clear_user_session(request)
            return False, None

        user_manager = UserManager()
        user_data = user_manager.find_user_by_username(username)

        if user_data and user_data.get('is_active', False):
            return True, user_data
        else:
            clear_user_session(request)
            return False, None

    except Exception as e:
        logger.error(f"❌ Ошибка проверки авторизации: {e}")
        return False, None


def clear_user_session(request) -> None:

    try:
        session_keys = [
            'user_authenticated',
            'user_id',
            'username',
            'is_admin',
            'user_data',
            'login_timestamp',
            'last_activity'
        ]

        for key in session_keys:
            if key in request.session:
                del request.session[key]

        request.session.modified = True
        logger.debug("🧹 Сессия пользователя очищена")

    except Exception as e:
        logger.error(f"❌ Ошибка очистки сессии: {e}")


def should_show_login_modal() -> bool:

    try:
        user_manager = UserManager()
        admin_count = user_manager.get_admin_count()
        return admin_count > 0

    except Exception as e:
        logger.error(f"❌ Ошибка проверки необходимости показа модального окна: {e}")
        return False


def get_user_display_name(user_data: Optional[Dict[str, Any]]) -> Optional[str]:

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
        logger.error(f"❌ Ошибка получения display name: {e}")
        return user_data.get('username', 'User')


def verify_user_permissions(user_data: Dict[str, Any],
                            required_permission: str) -> bool:

    try:
        # Суперадминистратор имеет все права
        if user_data.get('is_super_admin', False):
            return True

        # Проверяем конкретное разрешение
        permissions = user_data.get('permissions', {})
        return permissions.get(required_permission, False)

    except Exception as e:
        logger.error(f"❌ Ошибка проверки разрешений: {e}")
        return False


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:

    try:
        user_manager = UserManager()
        return user_manager.find_user_by_email(email)

    except Exception as e:
        logger.error(f"❌ Ошибка поиска пользователя по email: {e}")
        return None


# ==================== ПРИВАТНЫЕ ФУНКЦИИ ====================

def _update_login_success(username: str) -> None:
    """Обновляет данные успешного входа"""
    try:
        user_manager = UserManager()
        collection = user_manager.get_collection()

        if collection is not None:
            collection.update_one(
                {'username': username},
                {
                    '$set': {
                        'last_login': datetime.datetime.now(),
                        'failed_login_attempts': 0,
                        'locked_until': None
                    }
                }
            )
            logger.debug(f"✅ Обновлены данные успешного входа для '{username}'")

    except Exception as e:
        logger.error(f"❌ Ошибка обновления данных входа для '{username}': {e}")


def _update_login_failure(username: str) -> None:
    """Обновляет данные неудачного входа и блокирует при необходимости"""
    try:
        user_manager = UserManager()
        collection = user_manager.get_collection()

        if collection is not None:
            result = collection.update_one(
                {'username': username},
                {'$inc': {'failed_login_attempts': 1}}
            )

            if result.modified_count > 0:
                user = collection.find_one({'username': username})
                if user and user.get('failed_login_attempts', 0) >= 5:
                    locked_until = datetime.datetime.now() + datetime.timedelta(minutes=15)
                    collection.update_one(
                        {'username': username},
                        {'$set': {'locked_until': locked_until}}
                    )
                    logger.warning(f"⚠️ Пользователь '{username}' заблокирован до {locked_until}")

    except Exception as e:
        logger.error(f"❌ Ошибка обновления данных неудачного входа для '{username}': {e}")