# company/company_manager.py - ИСПРАВЛЕНО: все проверки MongoDB объектов

import datetime
import json

from loguru import logger

from mongodb.mongodb_config import MongoConfig
from mongodb.mongodb_utils import MongoConnection


class CompanyManager:
    """Упрощенный менеджер для работы с единственной компанией"""

    def __init__(self):
        self.db = MongoConnection.get_database()
        # ✅ ИСПРАВЛЕНО: Правильная проверка объекта базы данных
        if self.db is None:
            logger.error("База данных недоступна")
            self.company_collection_name = None
            return

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не найдено в конфигурации")
            self.company_collection_name = None
        else:
            self.company_collection_name = f"{db_name}_company_info"

    def get_collection(self):
        """Получает коллекцию информации о компании"""
        # ✅ ИСПРАВЛЕНО: Правильная проверка
        if self.db is None or not self.company_collection_name:
            logger.warning("База данных или имя коллекции недоступны")
            return None

        try:
            # Проверяем существование коллекции
            existing_collections = self.db.list_collection_names()
            if self.company_collection_name not in existing_collections:
                # Создаем коллекцию
                collection = self.db.create_collection(self.company_collection_name)
                logger.info(f"Коллекция '{self.company_collection_name}' создана")

            return self.db[self.company_collection_name]
        except Exception as e:
            logger.error(f"Ошибка получения коллекции: {e}")
            return None

    def has_company(self):
        """Проверяет, зарегистрирована ли компания"""
        try:
            collection = self.get_collection()
            # ✅ ИСПРАВЛЕНО: Правильная проверка
            if collection is None:
                logger.warning("Коллекция недоступна в has_company()")
                return False

            # ✅ КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Добавляем дополнительную проверку на валидные данные
            logger.info("🔍 Выполняем find_one({'type': 'company_info'}) в has_company()")
            company = collection.find_one({'type': 'company_info'})

            # ✅ ИСПРАВЛЕНО: Проверяем не только существование документа, но и наличие обязательных полей
            if company is None:
                logger.info("🔍 has_company() результат: False (документ не найден)")
                return False

            # ✅ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: Убеждаемся что у компании есть основные данные
            has_required_fields = (
                    company.get('company_name') and
                    str(company.get('company_name')).strip() != '' and
                    company.get('legal_form') and
                    str(company.get('legal_form')).strip() != ''
            )

            if not has_required_fields:
                logger.warning("🔍 has_company() результат: False (найден документ, но нет обязательных полей)")
                logger.warning(f"🔍 company_name: '{company.get('company_name')}'")
                logger.warning(f"🔍 legal_form: '{company.get('legal_form')}'")
                return False

            logger.info(f"🔍 has_company() результат: True (найдена компания: {company.get('company_name', 'Без названия')})")
            return True

        except Exception as e:
            logger.error(f"Ошибка проверки наличия компании: {e}")
            return False

    def get_company(self):
        """Получает данные компании"""
        try:
            collection = self.get_collection()
            # ✅ ИСПРАВЛЕНО: Правильная проверка
            if collection is None:
                logger.warning("Коллекция недоступна в get_company()")
                return None

            logger.info("🔍 Выполняем find_one({'type': 'company_info'}) в get_company()")
            company = collection.find_one({'type': 'company_info'})

            if company is None:  # ✅ ИСПРАВЛЕНО: Правильная проверка
                logger.info("🔍 get_company() компания не найдена")
                return None
            else:
                logger.info(f"🔍 get_company() найдена компания: {company.get('company_name', 'Без названия')}")
                logger.info(f"🔍 Основные поля: email={company.get('email')}, phone={company.get('phone')}")
                return company

        except Exception as e:
            logger.error(f"Ошибка получения данных компании: {e}")
            return None

    def get_primary_company(self):
        """Alias для совместимости - возвращает единственную компанию"""
        return self.get_company()

    def create_or_update_company(self, company_data):
        """Создает или обновляет информацию о компании"""
        try:
            collection = self.get_collection()
            # ✅ ИСПРАВЛЕНО: Правильная проверка
            if collection is None:
                logger.error("Коллекция недоступна")
                return False

            # ✅ ДОПОЛНИТЕЛЬНАЯ ВАЛИДАЦИЯ: Проверяем обязательные поля
            required_fields = ['company_name', 'legal_form']
            for field in required_fields:
                if not company_data.get(field) or str(company_data.get(field)).strip() == '':
                    logger.error(f"Обязательное поле '{field}' отсутствует или пустое")
                    return False

            # Добавляем служебные поля
            now = datetime.datetime.now()
            company_data.update({
                'type': 'company_info',  # Тип записи для идентификации
                'modified_at': now
            })

            # Проверяем, существует ли уже запись
            existing = collection.find_one({'type': 'company_info'})

            if existing is not None:  # ✅ ИСПРАВЛЕНО: Правильная проверка
                # Обновляем существующую запись
                logger.info("🔄 Обновляем существующую компанию")
                result = collection.update_one(
                    {'type': 'company_info'},
                    {'$set': company_data}
                )
                if result.modified_count > 0:
                    logger.success(f"Информация о компании '{company_data['company_name']}' обновлена")
                    return True
                else:
                    logger.warning("Данные компании не изменились")
                    return True
            else:
                # Создаем новую запись
                logger.info("➕ Создаем новую компанию")
                company_data['created_at'] = now
                result = collection.insert_one(company_data)
                if result.inserted_id is not None:  # ✅ ИСПРАВЛЕНО: Правильная проверка
                    logger.success(f"Компания '{company_data['company_name']}' зарегистрирована с ID: {result.inserted_id}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Ошибка создания/обновления компании: {e}")
            return False

    def delete_company(self):
        """Удаляет информацию о компании (полное удаление)"""
        try:
            collection = self.get_collection()
            # ✅ ИСПРАВЛЕНО: Правильная проверка
            if collection is None:
                return False

            result = collection.delete_one({'type': 'company_info'})
            if result.deleted_count > 0:
                logger.success("Информация о компании удалена")
                return True
            else:
                logger.warning("Компания для удаления не найдена")
                return False

        except Exception as e:
            logger.error(f"Ошибка удаления компании: {e}")
            return False

    def get_company_stats(self):
        """Возвращает статистику по компании"""
        try:
            collection = self.get_collection()
            # ✅ ИСПРАВЛЕНО: Правильная проверка
            if collection is None:
                return None

            company = collection.find_one({'type': 'company_info'})
            # ✅ ИСПРАВЛЕНО: Правильная проверка
            if company is None:
                return None

            # Подсчитываем заполненные поля
            filled_fields = 0
            total_fields = 0
            required_fields = ['company_name', 'legal_form', 'street', 'postal_code', 'city', 'country', 'email', 'phone']
            optional_fields = ['commercial_register', 'tax_number', 'vat_id', 'tax_id', 'fax', 'website', 'ceo_first_name', 'ceo_last_name', 'contact_person_first_name', 'contact_person_last_name', 'industry', 'description']

            for field in required_fields + optional_fields:
                total_fields += 1
                if field in company and company[field] and str(company[field]).strip():
                    filled_fields += 1

            # Дополнительные контакты
            additional_contacts = company.get('additional_contacts_data', [])
            if isinstance(additional_contacts, str):
                try:
                    additional_contacts = json.loads(additional_contacts)
                except:
                    additional_contacts = []

            return {
                'filled_fields': filled_fields,
                'total_fields': total_fields,
                'completion_percentage': round((filled_fields / total_fields) * 100, 1) if total_fields > 0 else 0,
                'additional_contacts_count': len(additional_contacts) if additional_contacts else 0,
                'created_at': company.get('created_at'),
                'modified_at': company.get('modified_at')
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики компании: {e}")
            return None

    # ✅ НОВЫЙ МЕТОД: Диагностика для отладки
    def debug_company_status(self):
        """Диагностический метод для отладки состояния компании"""
        try:
            collection = self.get_collection()
            if collection is None:
                return {
                    'error': 'Collection unavailable',
                    'has_company': False,
                    'company_data': None
                }

            # Получаем сырые данные
            company_data = collection.find_one({'type': 'company_info'})

            # Проверяем has_company логику
            has_company_result = self.has_company()

            # Возвращаем диагностическую информацию
            return {
                'collection_name': self.company_collection_name,
                'collection_exists': collection is not None,
                'raw_document_found': company_data is not None,
                'has_company_result': has_company_result,
                'company_name': company_data.get('company_name') if company_data else None,
                'legal_form': company_data.get('legal_form') if company_data else None,
                'document_fields': list(company_data.keys()) if company_data else [],
                'all_documents_count': collection.count_documents({}),
                'company_documents_count': collection.count_documents({'type': 'company_info'})
            }

        except Exception as e:
            logger.error(f"Ошибка диагностики: {e}")
            return {
                'error': str(e),
                'has_company': False,
                'company_data': None
            }