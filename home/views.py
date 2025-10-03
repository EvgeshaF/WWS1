# home/views.py - ИСПРАВЛЕНО: правильная логика перенаправлений

from django.shortcuts import render, redirect
from django.contrib import messages
from loguru import logger

from mongodb.mongodb_config import MongoConfig
from users.user_utils import UserManager
from user_auth import is_user_authenticated

def home(request):

    try:
        logger.info("🏠 Загрузка главной страницы")

        # ==================== ШАГ 1: ПРОВЕРКА MONGODB ====================
        logger.info("1️⃣ Проверяем конфигурацию MongoDB...")
        config_status = MongoConfig.check_config_completeness()

        if config_status == 'connection_required' or config_status == 'ping_failed':
            logger.warning(f"❌ MongoDB: требуется настройка подключения ({config_status})")
            messages.warning(request, "MongoDB-Verbindung muss konfiguriert werden")
            return redirect('create_database_step1')

        elif config_status == 'login_required' or config_status == 'login_failed':
            logger.warning(f"❌ MongoDB: требуется авторизация ({config_status})")
            messages.warning(request, "MongoDB-Administratoranmeldung erforderlich")
            return redirect('create_database_step2')

        elif config_status == 'db_required':
            logger.warning("❌ MongoDB: требуется создание базы данных")
            messages.warning(request, "MongoDB-Datenbank muss erstellt werden")
            return redirect('create_database_step3')

        elif config_status != 'complete':
            logger.error(f"❌ MongoDB: неизвестный статус конфигурации: {config_status}")
            messages.error(request, "Unbekannter MongoDB-Konfigurationsstatus")
            return render(request, 'home.html', {
                'setup_complete': False,
                'error': 'Unbekannte MongoDB-Konfiguration',
                'is_authenticated': False,
                'current_user': None
            })

        logger.success("✅ MongoDB: конфигурация завершена")

        # ==================== ШАГ 2: ПРОВЕРКА АДМИНИСТРАТОРОВ ====================
        logger.info("2️⃣ Проверяем наличие администраторов...")
        try:
            user_manager = UserManager()
            admin_count = user_manager.get_admin_count()
            logger.info(f"👥 Найдено администраторов: {admin_count}")
        except Exception as e:
            logger.error(f"❌ Ошибка проверки администраторов: {e}")
            messages.error(request, "Fehler beim Überprüfen der Administratoren")
            admin_count = 0

        # ✅ ИСПРАВЛЕНИЕ: Если админов нет, перенаправляем на создание
        if admin_count == 0:
            logger.warning("❌ Администраторы не найдены, перенаправляем на создание")
            messages.warning(request, "Administrator muss erstellt werden")
            return redirect('users:create_admin_step1')

        logger.success(f"✅ Найдено администраторов: {admin_count}")

        # ==================== ШАГ 3: ПРОВЕРКА АВТОРИЗАЦИИ ====================
        logger.info("3️⃣ Проверяем авторизацию пользователя...")
        try:
            is_auth, user_data = is_user_authenticated(request)
            logger.info(f"👤 Пользователь авторизован: {is_auth}")

            if user_data:
                username = user_data.get('username', 'Unknown')
                is_admin = user_data.get('is_admin', False)
                logger.info(f"👤 Данные пользователя: {username} (admin: {is_admin})")
        except Exception as e:
            logger.error(f"Ошибка проверки авторизации: {e}")
            is_auth, user_data = False, None

        # ==================== ШАГ 4: ПРОВЕРКА КОМПАНИИ ====================
        logger.info("4️⃣ Проверяем наличие зарегистрированной компании...")
        try:
            from company.company_manager import CompanyManager
            company_manager = CompanyManager()

            has_company = company_manager.has_company()
            company_data = company_manager.get_company()

            # Дополнительная проверка через прямой запрос
            if not has_company and company_data is None:
                collection = company_manager.get_collection()
                if collection is not None:
                    direct_count = collection.count_documents({'type': 'company_info'})
                    if direct_count > 0:
                        direct_company = collection.find_one({'type': 'company_info'})
                        if direct_company is not None:
                            logger.warning("⚠️ Найдена компания прямым запросом")
                            has_company = True
                            company_data = direct_company

            if not has_company:
                logger.warning("❌ Компания не зарегистрирована")
                company_name = 'Keine Firma registriert'
            else:
                company_name = company_data.get('company_name', 'Неизвестно') if company_data else 'Не настроено'
                logger.success(f"✅ Компания найдена: {company_name}")

        except Exception as e:
            logger.error(f"❌ Ошибка проверки компании: {e}")
            has_company = False
            company_name = 'Fehler beim Laden'
            company_data = None

        # ==================== ФОРМИРОВАНИЕ КОНТЕКСТА ====================
        logger.success("✅ Главная страница загружена")

        context = {
            'setup_complete': True,
            'admin_count': admin_count,
            'has_company': has_company,
            'company_name': company_name,
            'company_data': company_data,

            # Информация об авторизации
            'is_authenticated': is_auth,
            'current_user': {
                'username': user_data.get('username'),
                'is_admin': user_data.get('is_admin', False),
                'is_active': user_data.get('is_active', True),
                'profile': {
                    'first_name': user_data.get('profile', {}).get('first_name', ''),
                    'last_name': user_data.get('profile', {}).get('last_name', ''),
                    'salutation': user_data.get('profile', {}).get('salutation', ''),
                }
            } if user_data else None,

            'user_display_name': get_user_display_name(user_data) if user_data else None,

            # Дополнительная информация для шаблона
            'mongodb_status': 'Aktiv',
            'database_status': 'Bereit',
            'system_status': 'Online',

            # Статистика
            'total_users': admin_count,
            'system_version': '1.0.0',

            # ✅ ИСПРАВЛЕНИЕ: Правильная логика показа модального окна
            # Модальное окно показывается только если:
            # - Есть администраторы (admin_count > 0)
            # - Пользователь НЕ авторизован
            # - Не находимся на странице создания админа
            'show_login_modal': admin_count > 0 and not is_auth,
            'requires_auth': admin_count > 0 and not is_auth,

            # Рекомендации для следующих шагов
            'next_steps': get_next_steps(is_auth, admin_count, has_company),
        }

        return render(request, 'home.html', context)

    except Exception as e:
        logger.exception(f"💥 КРИТИЧЕСКАЯ ОШИБКА в home view: {e}")
        messages.error(request, "Ein kritischer Systemfehler ist aufgetreten")

        error_context = {
            'setup_complete': False,
            'error': 'Kritischer Systemfehler',
            'error_details': str(e),
            'admin_count': 0,
            'has_company': False,
            'company_name': 'Fehler',
            'is_authenticated': False,
            'current_user': None,
            'show_login_modal': False,
            'requires_auth': False,
        }

        return render(request, 'home.html', error_context)


def get_user_display_name(user_data):
    """Получает отображаемое имя пользователя"""
    if not user_data:
        return None

    profile = user_data.get('profile', {})
    first_name = profile.get('first_name', '')
    last_name = profile.get('last_name', '')

    if first_name and last_name:
        return f"{first_name} {last_name}"
    elif first_name:
        return first_name
    else:
        return user_data.get('username', 'Unknown')


def get_next_steps(is_authenticated, admin_count, has_company):
    """
    Определяет следующие шаги для пользователя
    """
    steps = []

    # Если не авторизован, но есть админы
    if not is_authenticated and admin_count > 0:
        steps.append({
            'title': 'Anmelden',
            'description': 'Melden Sie sich an, um das System zu verwalten',
            'icon': 'bi-box-arrow-in-right',
            'priority': 'high',
            'action': 'login'
        })

    # Если нет компании
    if not has_company:
        steps.append({
            'title': 'Firma registrieren',
            'description': 'Registrieren Sie Ihre Firma im System',
            'icon': 'bi-building-add',
            'priority': 'high',
            'action': 'register_company'
        })

    # Если все настроено
    if is_authenticated and admin_count > 0 and has_company:
        steps.append({
            'title': 'System bereit',
            'description': 'Das System ist vollständig konfiguriert und einsatzbereit',
            'icon': 'bi-check-circle-fill',
            'priority': 'success',
            'action': 'ready'
        })

    return steps