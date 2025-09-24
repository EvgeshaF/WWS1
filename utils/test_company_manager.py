# test_company_manager.py - Скрипт для диагностики CompanyManager
# Выполните этот скрипт в Django shell: python manage.py shell < test_company_manager.py

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WWS1.settings')
django.setup()

from loguru import logger
from company.company_manager import CompanyManager
from mongodb.mongodb_config import MongoConfig
from mongodb.mongodb_utils import MongoConnection


def test_company_manager():
    """Тестирует все аспекты CompanyManager"""

    logger.info("=" * 60)
    logger.info("🧪 НАЧИНАЕМ ТЕСТИРОВАНИЕ COMPANY MANAGER")
    logger.info("=" * 60)

    # Тест 1: Проверка MongoDB подключения
    logger.info("1️⃣ Тестируем подключение к MongoDB...")
    try:
        db = MongoConnection.get_database()
        if db:
            logger.success(f"✅ MongoDB подключение: OK, база данных: {db.name}")
        else:
            logger.error("❌ MongoDB подключение: FAILED")
            return
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к MongoDB: {e}")
        return

    # Тест 2: Создание CompanyManager
    logger.info("2️⃣ Создаем CompanyManager...")
    try:
        company_manager = CompanyManager()
        logger.success("✅ CompanyManager создан успешно")
        logger.info(f"🔍 Database: {company_manager.db}")
        logger.info(f"🔍 Collection name: {company_manager.company_collection_name}")
    except Exception as e:
        logger.error(f"❌ Ошибка создания CompanyManager: {e}")
        return

    # Тест 3: Получение коллекции
    logger.info("3️⃣ Получаем коллекцию...")
    try:
        collection = company_manager.get_collection()
        if collection:
            logger.success(f"✅ Коллекция получена: {collection.name}")

            # Проверяем существующие коллекции
            existing_collections = db.list_collection_names()
            logger.info(f"🔍 Существующие коллекции: {existing_collections}")

            if company_manager.company_collection_name in existing_collections:
                logger.success(f"✅ Коллекция {company_manager.company_collection_name} существует")
            else:
                logger.warning(f"⚠️ Коллекция {company_manager.company_collection_name} не существует, будет создана")
        else:
            logger.error("❌ Не удалось получить коллекцию")
            return
    except Exception as e:
        logger.error(f"❌ Ошибка получения коллекции: {e}")
        return

    # Тест 4: Проверка содержимого коллекции
    logger.info("4️⃣ Проверяем содержимое коллекции...")
    try:
        # Получаем все документы
        documents = list(collection.find({}))
        logger.info(f"🔍 Всего документов в коллекции: {len(documents)}")

        # Ищем документы компании
        company_docs = list(collection.find({'type': 'company_info'}))
        logger.info(f"🔍 Документов компании (type: company_info): {len(company_docs)}")

        if company_docs:
            for i, doc in enumerate(company_docs):
                logger.info(f"🔍 Документ компании {i + 1}:")
                logger.info(f"   - _id: {doc.get('_id')}")
                logger.info(f"   - company_name: {doc.get('company_name')}")
                logger.info(f"   - legal_form: {doc.get('legal_form')}")
                logger.info(f"   - created_at: {doc.get('created_at')}")
                logger.info(f"   - modified_at: {doc.get('modified_at')}")
        else:
            logger.warning("⚠️ Документы компании не найдены")

    except Exception as e:
        logger.error(f"❌ Ошибка проверки содержимого коллекции: {e}")

    # Тест 5: Тестируем has_company()
    logger.info("5️⃣ Тестируем has_company()...")
    try:
        has_company_result = company_manager.has_company()
        logger.info(f"🔍 has_company() возвращает: {has_company_result}")

        if has_company_result:
            logger.success("✅ has_company(): Компания найдена")
        else:
            logger.warning("⚠️ has_company(): Компания не найдена")

    except Exception as e:
        logger.error(f"❌ Ошибка has_company(): {e}")
        has_company_result = False

    # Тест 6: Тестируем get_company()
    logger.info("6️⃣ Тестируем get_company()...")
    try:
        company_data = company_manager.get_company()
        logger.info(f"🔍 get_company() возвращает: {type(company_data)}")

        if company_data:
            logger.success("✅ get_company(): Данные компании получены")
            logger.info(f"🔍 Название компании: {company_data.get('company_name')}")
            logger.info(f"🔍 Правовая форма: {company_data.get('legal_form')}")
            logger.info(f"🔍 Email: {company_data.get('email')}")
            logger.info(f"🔍 Телефон: {company_data.get('phone')}")
        else:
            logger.warning("⚠️ get_company(): Данные компании не найдены")

    except Exception as e:
        logger.error(f"❌ Ошибка get_company(): {e}")
        company_data = None

    # Тест 7: Анализ несоответствия
    logger.info("7️⃣ Анализируем несоответствия...")
    if company_data and not has_company_result:
        logger.error("🚨 ПРОБЛЕМА НАЙДЕНА!")
        logger.error("   get_company() возвращает данные, но has_company() = False")
        logger.error("   Это указывает на проблему в логике has_company()")

        # Проверяем логику has_company() вручную
        logger.info("🔍 Проверяем логику has_company() вручную...")
        manual_check = collection.find_one({'type': 'company_info'})
        logger.info(f"🔍 Ручная проверка find_one({{'type': 'company_info'}}): {manual_check is not None}")

        if manual_check:
            logger.error("🚨 Ручная проверка показывает, что данные ЕСТЬ!")
            logger.error("🚨 Проблема в методе has_company() в CompanyManager")

    elif not company_data and has_company_result:
        logger.error("🚨 ОБРАТНАЯ ПРОБЛЕМА!")
        logger.error("   has_company() = True, но get_company() не возвращает данные")

    elif company_data and has_company_result:
        logger.success("✅ Логика работает правильно: данные есть и has_company() = True")

    elif not company_data and not has_company_result:
        logger.info("ℹ️ Компания действительно не зарегистрирована")

    # Тест 8: Создаем тестовую компанию если её нет
    if not company_data:
        logger.info("8️⃣ Создаем тестовую компанию...")
        test_company_data = {
            'company_name': 'Test Company GmbH',
            'legal_form': 'gmbh',
            'email': 'test@company.de',
            'phone': '+49 123 456789',
            'street': 'Teststraße 1',
            'postal_code': '12345',
            'city': 'Teststadt',
            'country': 'deutschland'
        }

        try:
            success = company_manager.create_or_update_company(test_company_data)
            if success:
                logger.success("✅ Тестовая компания создана")

                # Повторяем проверки
                logger.info("🔄 Повторяем проверки после создания...")
                has_company_after = company_manager.has_company()
                company_data_after = company_manager.get_company()

                logger.info(f"🔍 После создания has_company(): {has_company_after}")
                logger.info(f"🔍 После создания get_company(): {company_data_after is not None}")

                if has_company_after and company_data_after:
                    logger.success("✅ После создания все работает правильно")
                else:
                    logger.error("❌ После создания проблемы остались")
            else:
                logger.error("❌ Не удалось создать тестовую компанию")

        except Exception as e:
            logger.error(f"❌ Ошибка создания тестовой компании: {e}")

    logger.info("=" * 60)
    logger.info("🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    logger.info("=" * 60)


if __name__ == "__main__":
    test_company_manager()