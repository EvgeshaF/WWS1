import datetime
import json

from loguru import logger

from mongodb.mongodb_config import MongoConfig
from mongodb.mongodb_utils import MongoConnection


class CompanyManager:
    """Упрощенный менеджер для работы с единственной компанией"""

    def __init__(self):
        self.db = MongoConnection.get_database()
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
        if self.db is None or not self.company_collection_name:
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
            if collection is None:
                return False

            # Проверяем наличие записи компании
            company = collection.find_one({'type': 'company_info'})
            return company is not None
        except Exception as e:
            logger.error(f"Ошибка проверки наличия компании: {e}")
            return False

    def get_company(self):
        """Получает данные компании"""
        try:
            collection = self.get_collection()
            if collection is None:
                return None

            company = collection.find_one({'type': 'company_info'})
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
            if collection is None:
                logger.error("Коллекция недоступна")
                return False

            # Добавляем служебные поля
            now = datetime.datetime.now()
            company_data.update({
                'type': 'company_info',  # Тип записи для идентификации
                'modified_at': now
            })

            # Проверяем, существует ли уже запись
            existing = collection.find_one({'type': 'company_info'})

            if existing:
                # Обновляем существующую запись
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
                company_data['created_at'] = now
                result = collection.insert_one(company_data)
                if result.inserted_id:
                    logger.success(f"Компания '{company_data['company_name']}' зарегистрирована")
                    return True

            return False

        except Exception as e:
            logger.error(f"Ошибка создания/обновления компании: {e}")
            return False

    def delete_company(self):
        """Удаляет информацию о компании (полное удаление)"""
        try:
            collection = self.get_collection()
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
            if collection is None:
                return None

            company = collection.find_one({'type': 'company_info'})
            if not company:
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