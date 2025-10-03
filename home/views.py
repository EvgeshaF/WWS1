# home/views.py - ИСПРАВЛЕНО: одинаковый интерфейс до и после авторизации

from django.shortcuts import render, redirect
from django.contrib import messages
from loguru import logger

from mongodb.mongodb_config import MongoConfig
from users.user_utils import UserManager
from user_auth import is_user_authenticated

def home(request):
    """
    Главная страница с проверкой состояния системы и авторизации
    Показывает одинаковый интерфейс до и после авторизации
    """
    try:
        logger.info("🏠 Загрузка главной страницы")

        # Проверяем авторизацию пользователя
        try:
            from users.views import is_user_authenticated
            is_auth, user_data = is_user_authenticated(request)
            logger.info(f"👤 Пользователь авторизован: {is_auth}")

            if user_data:
                username = user_data.get('username', 'Unknown')
                is_admin = user_data.get('is_admin', False)
                logger.info(f"👤 Данные пользователя: {username} (admin: {is_admin})")
        except Exception as e:
            logger.error(f"Ошибка проверки авторизации: {e}")
            is_auth, user_data = False, None

        # Шаг 1: Проверяем MongoDB конфигурацию
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

        elif config_status == 'complete':
            logger.success("✅ MongoDB: конфигурация завершена")
        else:
            logger.error(f"❌ MongoDB: неизвестный статус конфигурации: {config_status}")
            messages.error(request, "Unbekannter MongoDB-Konfigurationsstatus")
            return render(request, 'home.html', {
                'setup_complete': False,
                'error': 'Unbekannte MongoDB-Konfiguration',
                'is_authenticated': is_auth,
                'current_user': user_data
            })

        # Шаг 2: Проверяем наличие администраторов в системе
        logger.info("2️⃣ Проверяем наличие администраторов...")
        try:
            user_manager = UserManager()
            admin_count = user_manager.get_admin_count()
            logger.info(f"👥 Найдено администраторов: {admin_count}")
        except Exception as e:
            logger.error(f"❌ Ошибка проверки администраторов: {e}")
            messages.error(request, "Fehler beim Überprüfen der Administratoren")
            admin_count = 0

        # Шаг 3: Проверяем наличие зарегистрированной компании
        logger.info("3️⃣ Проверяем наличие зарегистрированной компании...")
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

        # КРИТИЧНО: Не показываем предупреждения, чтобы интерфейс был одинаковым
        # Предупреждения будут отображаться в самом шаблоне

        logger.success("✅ Главная страница загружена")

        # Подготавливаем контекст для шаблона
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

            # ВАЖНО: Всегда показываем одинаковые флаги независимо от авторизации
            'show_no_admin_warning': admin_count == 0,
            'show_no_company_warning': not has_company,

            # Рекомендации для следующих шагов (одинаковые для всех)
            'next_steps': get_next_steps(is_auth, admin_count, has_company),

            # НОВОЕ: Флаг для показа кнопок авторизации
            'requires_auth': not is_auth,
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
            'current_user': None
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
    ВАЖНО: Возвращает одинаковые шаги независимо от авторизации
    """
    steps = []

    # Если нет администраторов - самый приоритетный шаг
    if admin_count == 0:
        steps.append({
            'title': 'Administrator erstellen',
            'description': 'Erstellen Sie den ersten Administrator',
            'icon': 'bi-person-plus',
            'priority': 'critical',
            'action': 'create_admin'
        })

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
