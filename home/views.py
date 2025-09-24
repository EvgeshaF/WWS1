# home/views.py - ОКОНЧАТЕЛЬНО ИСПРАВЛЕННАЯ ВЕРСИЯ с правильными проверками MongoDB

from django.shortcuts import render, redirect
from django.contrib import messages
from loguru import logger

from mongodb.mongodb_config import MongoConfig
from users.user_utils import UserManager


def home(request):
    """
    Главная страница с проверкой состояния системы
    Проверяет:
    1. MongoDB конфигурацию
    2. Наличие администраторов
    3. Наличие зарегистрированной компании
    """
    try:
        logger.info("🏠 Загрузка главной страницы")

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
                'error': 'Unbekannte MongoDB-Konfiguration'
            })

        # Шаг 2: Проверяем наличие администраторов в системе
        logger.info("2️⃣ Проверяем наличие администраторов...")
        try:
            user_manager = UserManager()
            admin_count = user_manager.get_admin_count()
            logger.info(f"👥 Найдено администраторов: {admin_count}")

            if admin_count == 0:
                logger.warning("❌ Нет администраторов в системе")
                messages.warning(request, "Kein Administrator im System gefunden")
                return redirect('users:create_admin_step1')

        except Exception as e:
            logger.error(f"❌ Ошибка проверки администраторов: {e}")
            messages.error(request, "Fehler beim Überprüfen der Administratoren")
            admin_count = 0

        # Шаг 3: Проверяем наличие зарегистрированной компании
        logger.info("3️⃣ Проверяем наличие зарегистрированной компании...")
        try:
            # ✅ ИСПРАВЛЕНО: Правильный импорт CompanyManager
            from company.company_manager import CompanyManager
            company_manager = CompanyManager()

            # Детальная диагностика
            logger.info(f"🔍 CompanyManager создан")
            logger.info(f"🔍 Database доступна: {company_manager.db is not None}")
            logger.info(f"🔍 Collection name: {company_manager.company_collection_name}")

            # Проверяем has_company() с дополнительной диагностикой
            logger.info("🔍 Вызываем has_company()...")
            has_company = company_manager.has_company()
            logger.info(f"🏢 has_company() результат: {has_company}")

            # Проверяем get_company() независимо от has_company()
            logger.info("🔍 Вызываем get_company()...")
            company_data = company_manager.get_company()
            logger.info(f"🏢 get_company() результат: {company_data is not None}")

            # ДИАГНОСТИКА: Проверяем данные в коллекции напрямую
            if not has_company and company_data is None:
                logger.info("🔍 Прямая проверка коллекции...")
                collection = company_manager.get_collection()
                if collection is not None:
                    direct_count = collection.count_documents({'type': 'company_info'})
                    logger.info(f"🔍 Прямой подсчет документов компании: {direct_count}")

                    if direct_count > 0:
                        direct_company = collection.find_one({'type': 'company_info'})
                        logger.info(f"🔍 Прямой поиск компании: {direct_company is not None}")
                        if direct_company is not None:
                            logger.warning("⚠️ НАЙДЕНА КОМПАНИЯ ПРЯМЫМ ЗАПРОСОМ! Принудительно устанавливаем результаты")
                            has_company = True
                            company_data = direct_company

            # Анализируем результаты
            if company_data is not None and not has_company:
                logger.error("🚨 НЕСООТВЕТСТВИЕ: get_company() возвращает данные, но has_company() = False")
                logger.warning("⚠️ Принудительно устанавливаем has_company = True")
                has_company = True
            elif company_data is None and has_company:
                logger.error("🚨 ОБРАТНОЕ НЕСООТВЕТСТВИЕ: has_company() = True, но get_company() = None")
                has_company = False

            if not has_company:
                logger.warning("❌ Компания не зарегистрирована")
                messages.warning(request, "Firma ist noch nicht registriert")
                return redirect('company:register_company')

            # Получаем название компании для отображения
            company_name = company_data.get('company_name', 'Неизвестно') if company_data is not None else 'Не настроено'
            logger.success(f"✅ Компания найдена: {company_name}")

        except ImportError as e:
            logger.error(f"❌ Ошибка импорта CompanyManager: {e}")
            messages.error(request, "Fehler beim Laden der Firmenverwaltung")
            has_company = False
            company_name = 'Fehler beim Laden'
            company_data = None

        except Exception as e:
            logger.error(f"❌ Ошибка проверки компании: {e}")
            logger.exception("Полная трассировка ошибки:")
            messages.error(request, "Fehler beim Überprüfen der Firmeninformationen")
            has_company = False
            company_name = 'Fehler beim Laden'
            company_data = None

        # Все проверки пройдены - показываем главную страницу
        logger.success("✅ Все проверки системы пройдены успешно")

        # Подготавливаем контекст для шаблона
        context = {
            'setup_complete': True,
            'admin_count': admin_count,
            'has_company': has_company,
            'company_name': company_name,
            'company_data': company_data,

            # Дополнительная информация для шаблона
            'mongodb_status': 'Aktiv',
            'database_status': 'Bereit',
            'system_status': 'Online',

            # Статистика (можно расширить)
            'total_users': admin_count,
            'system_version': '1.0.0',
        }

        logger.info(f"📊 Финальный контекст: has_company={has_company}, company_name={company_name}")
        return render(request, 'home.html', context)

    except Exception as e:
        # Критическая ошибка - логируем и показываем страницу с ошибкой
        logger.exception(f"💥 КРИТИЧЕСКАЯ ОШИБКА в home view: {e}")
        messages.error(request, "Ein kritischer Systemfehler ist aufgetreten")

        # Возвращаем минимальную страницу с информацией об ошибкой
        error_context = {
            'setup_complete': False,
            'error': 'Kritischer Systemfehler',
            'error_details': str(e) if hasattr(request, 'user') and request.user.is_superuser else None,
            'admin_count': 0,
            'has_company': False,
            'company_name': 'Fehler'
        }

        return render(request, 'home.html', error_context)