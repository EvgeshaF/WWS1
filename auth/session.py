# auth/session.py - Управление сессиями пользователей

from typing import Dict, Any, Optional
from loguru import logger
import datetime


def create_user_session(request, user_data: Dict[str, Any], remember_me: bool = False) -> None:
    """
    Создает сессию для пользователя после успешной авторизации

    Args:
        request: Django request object
        user_data: Данные пользователя из MongoDB
        remember_me: Запомнить пользователя (длительная сессия)
    """
    try:
        # Сохраняем основные данные в сессии
        request.session["user_authenticated"] = True
        request.session["user_id"] = str(user_data.get("_id"))
        request.session["username"] = user_data.get("username")
        request.session["is_admin"] = user_data.get("is_admin", False)

        # Сохраняем профильные данные
        request.session["user_data"] = {
            'username': user_data.get('username'),
            'is_admin': user_data.get('is_admin', False),
            'is_active': user_data.get('is_active', True),
            'profile': user_data.get('profile', {}),
            'permissions': user_data.get('permissions', {})
        }

        # Устанавливаем время создания сессии
        request.session["login_timestamp"] = datetime.datetime.now().isoformat()
        request.session["last_activity"] = datetime.datetime.now().isoformat()

        # Настраиваем срок жизни сессии
        if remember_me:
            request.session.set_expiry(1209600)  # 2 недели
        else:
            request.session.set_expiry(0)  # До закрытия браузера

        request.session.modified = True

        logger.success(f"✅ Сессия создана для пользователя: {user_data.get('username')}")

    except Exception as e:
        logger.error(f"❌ Ошибка создания сессии: {e}")
        raise


def update_user_session(request, update_data: Dict[str, Any]) -> None:
    """
    Обновляет данные в существующей сессии

    Args:
        request: Django request object
        update_data: Данные для обновления
    """
    try:
        if 'user_data' in request.session:
            request.session['user_data'].update(update_data)
        else:
            request.session['user_data'] = update_data

        request.session["last_activity"] = datetime.datetime.now().isoformat()
        request.session.modified = True

        logger.debug(f"🔄 Сессия обновлена для: {request.session.get('username')}")

    except Exception as e:
        logger.error(f"❌ Ошибка обновления сессии: {e}")


def get_session_data(request, key: str = None) -> Optional[Any]:
    """
    Получает данные из сессии

    Args:
        request: Django request object
        key: Ключ данных (если None, возвращает все user_data)

    Returns:
        Данные из сессии или None
    """
    try:
        if key:
            return request.session.get(key)
        else:
            return request.session.get('user_data')

    except Exception as e:
        logger.error(f"❌ Ошибка получения данных из сессии: {e}")
        return None


def clear_user_session(request) -> None:
    """
    Очищает данные пользователя из сессии (logout)

    Args:
        request: Django request object
    """
    try:
        # Список ключей для очистки
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


def extend_session(request, seconds: int = 1800) -> None:
    """
    Продлевает срок жизни сессии

    Args:
        request: Django request object
        seconds: Количество секунд для продления
    """
    try:
        request.session.set_expiry(seconds)
        request.session.modified = True
        logger.debug(f"⏰ Сессия продлена на {seconds} секунд")

    except Exception as e:
        logger.error(f"❌ Ошибка продления сессии: {e}")


def is_session_expired(request, max_inactive_seconds: int = 3600) -> bool:
    """
    Проверяет, истекла ли сессия по неактивности

    Args:
        request: Django request object
        max_inactive_seconds: Максимальное время неактивности в секундах

    Returns:
        True если сессия истекла
    """
    try:
        last_activity_str = request.session.get('last_activity')
        if not last_activity_str:
            return True

        last_activity = datetime.datetime.fromisoformat(last_activity_str)
        now = datetime.datetime.now()

        inactive_seconds = (now - last_activity).total_seconds()

        return inactive_seconds > max_inactive_seconds

    except Exception as e:
        logger.error(f"❌ Ошибка проверки истечения сессии: {e}")
        return True


def refresh_session_activity(request) -> None:
    """
    Обновляет время последней активности в сессии

    Args:
        request: Django request object
    """
    try:
        request.session["last_activity"] = datetime.datetime.now().isoformat()
        request.session.modified = True

    except Exception as e:
        logger.error(f"❌ Ошибка обновления активности сессии: {e}")


def get_session_info(request) -> Dict[str, Any]:
    """
    Получает информацию о текущей сессии

    Args:
        request: Django request object

    Returns:
        Словарь с информацией о сессии
    """
    try:
        login_timestamp_str = request.session.get('login_timestamp')
        last_activity_str = request.session.get('last_activity')

        login_time = None
        last_activity = None
        session_duration = None
        inactive_duration = None

        if login_timestamp_str:
            login_time = datetime.datetime.fromisoformat(login_timestamp_str)
            session_duration = (datetime.datetime.now() - login_time).total_seconds()

        if last_activity_str:
            last_activity = datetime.datetime.fromisoformat(last_activity_str)
            inactive_duration = (datetime.datetime.now() - last_activity).total_seconds()

        return {
            'is_authenticated': request.session.get('user_authenticated', False),
            'username': request.session.get('username'),
            'is_admin': request.session.get('is_admin', False),
            'login_time': login_time,
            'last_activity': last_activity,
            'session_duration_seconds': session_duration,
            'inactive_duration_seconds': inactive_duration,
            'session_key': request.session.session_key
        }

    except Exception as e:
        logger.error(f"❌ Ошибка получения информации о сессии: {e}")
        return {}