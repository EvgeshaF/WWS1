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

            # Проверяем наличие записи компании
            logger.info("🔍 Выполняем find_one({'type': 'company_info'}) в has_company()")
            company = collection.find_one({'type': 'company_info'})
            result = company is not None  # ✅ ИСПРАВЛЕНО: Правильная проверка
            logger.info(f"🔍 has_company() результат: найден документ = {result}")

            if company is not None:
                logger.info(f"🔍 Найдена компания: {company.get('company_name', 'Без названия')}")
            else:
                logger.info("🔍 Документ компании не найден")

            return result

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

            if company is not None:  # ✅ ИСПРАВЛЕНО: Правильная проверка
                logger.info(f"🔍 get_company() найдена компания: {company.get('company_name', 'Без названия')}")
                logger.info(f"🔍 Основные поля: email={company.get('email')}, phone={company.get('phone')}")

                # ✅ ОБРАТНОЕ ПРЕОБРАЗОВАНИЕ: Конвертируем массив дополнительных контактов в JSON-строку для совместимости
                if 'additional_contacts' in company and isinstance(company['additional_contacts'], list):
                    company['additional_contacts_data'] = json.dumps(company['additional_contacts'])
                    logger.info(f"Преобразовано {len(company['additional_contacts'])} дополнительных контактов в JSON-строку")

                # ✅ ОБРАТНОЕ ПРЕОБРАЗОВАНИЕ: Конвертируем массив банковских счетов в плоские поля для совместимости
                if 'banking_accounts' in company and isinstance(company['banking_accounts'], list):
                    banking_accounts = company['banking_accounts']

                    # Находим основной счёт
                    primary_account = next((acc for acc in banking_accounts if acc.get('is_primary')), None)
                    if not primary_account and banking_accounts:
                        primary_account = banking_accounts[0]

                    if primary_account:
                        company['bank_name'] = primary_account.get('bank_name', '')
                        company['iban'] = primary_account.get('iban', '')
                        company['bic'] = primary_account.get('bic', '')
                        company['account_holder'] = primary_account.get('account_holder', '')
                        company['bank_address'] = primary_account.get('bank_address', '')
                        company['account_type'] = primary_account.get('account_type', '')
                        company['banking_notes'] = primary_account.get('notes', '')

                    # Находим вторичный счёт
                    secondary_accounts = [acc for acc in banking_accounts if not acc.get('is_primary')]
                    if secondary_accounts:
                        secondary_account = secondary_accounts[0]
                        company['secondary_bank_name'] = secondary_account.get('bank_name', '')
                        company['secondary_iban'] = secondary_account.get('iban', '')
                        company['secondary_bic'] = secondary_account.get('bic', '')
                        company['secondary_account_holder'] = secondary_account.get('account_holder', '')

                    logger.info(f"Преобразовано {len(banking_accounts)} банковских счетов в плоские поля")

            else:
                logger.info("🔍 get_company() компания не найдена")

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

            # ✅ ПРЕОБРАЗОВАНИЕ: Конвертируем дополнительные контакты из JSON-строки в массив
            if 'additional_contacts_data' in company_data:
                additional_contacts_str = company_data.get('additional_contacts_data', '[]')
                try:
                    if isinstance(additional_contacts_str, str):
                        additional_contacts = json.loads(additional_contacts_str)
                    elif isinstance(additional_contacts_str, list):
                        additional_contacts = additional_contacts_str
                    else:
                        additional_contacts = []

                    # Очищаем от _id и других MongoDB полей
                    cleaned_contacts = []
                    for contact in additional_contacts:
                        if isinstance(contact, dict):
                            clean_contact = {k: v for k, v in contact.items() if k != '_id'}
                            cleaned_contacts.append(clean_contact)

                    company_data['additional_contacts'] = cleaned_contacts
                    logger.info(f"Преобразовано {len(cleaned_contacts)} дополнительных контактов")

                    # Удаляем старое поле со строкой
                    del company_data['additional_contacts_data']
                except json.JSONDecodeError:
                    logger.warning("Не удалось распарсить additional_contacts_data")
                    company_data['additional_contacts'] = []
                    if 'additional_contacts_data' in company_data:
                        del company_data['additional_contacts_data']

            # ✅ ПРЕОБРАЗОВАНИЕ: Конвертируем банковские данные из плоских полей в массив
            banking_accounts = []

            # Основной банковский счёт
            if company_data.get('bank_name') or company_data.get('iban'):
                main_account = {}
                if company_data.get('bank_name'):
                    main_account['bank_name'] = company_data.get('bank_name')
                if company_data.get('iban'):
                    main_account['iban'] = company_data.get('iban')
                if company_data.get('bic'):
                    main_account['bic'] = company_data.get('bic')
                if company_data.get('account_holder'):
                    main_account['account_holder'] = company_data.get('account_holder')
                if company_data.get('bank_address'):
                    main_account['bank_address'] = company_data.get('bank_address')
                if company_data.get('account_type'):
                    main_account['account_type'] = company_data.get('account_type')

                main_account['is_primary'] = True
                main_account['notes'] = company_data.get('banking_notes', '')

                if 'bank_name' in main_account and 'iban' in main_account:
                    banking_accounts.append(main_account)

                # Удаляем старые плоские поля основного счёта
                for field in ['bank_name', 'iban', 'bic', 'account_holder', 'bank_address', 'account_type', 'banking_notes']:
                    if field in company_data:
                        del company_data[field]

            # Вторичный банковский счёт
            if company_data.get('secondary_bank_name') or company_data.get('secondary_iban'):
                secondary_account = {}
                if company_data.get('secondary_bank_name'):
                    secondary_account['bank_name'] = company_data.get('secondary_bank_name')
                if company_data.get('secondary_iban'):
                    secondary_account['iban'] = company_data.get('secondary_iban')
                if company_data.get('secondary_bic'):
                    secondary_account['bic'] = company_data.get('secondary_bic')
                if company_data.get('secondary_account_holder'):
                    secondary_account['account_holder'] = company_data.get('secondary_account_holder')

                secondary_account['is_primary'] = False
                secondary_account['notes'] = ''

                if 'bank_name' in secondary_account and 'iban' in secondary_account:
                    banking_accounts.append(secondary_account)

                # Удаляем старые плоские поля вторичного счёта
                for field in ['secondary_bank_name', 'secondary_iban', 'secondary_bic', 'secondary_account_holder']:
                    if field in company_data:
                        del company_data[field]

            if banking_accounts:
                company_data['banking_accounts'] = banking_accounts
                logger.info(f"Преобразовано {len(banking_accounts)} банковских счетов")

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

            # Подсчитываем ТОЛЬКО обязательные поля
            filled_fields = 0
            total_fields = 0

            # Базовые обязательные поля (Шаги 1-3)
            required_fields = [
                'company_name', 'legal_form', 'street', 'postal_code', 'city', 'country', 'email', 'phone'
            ]

            # Банковские обязательные поля (Шаг 5)
            # Проверяем, есть ли banking_accounts (новый формат) или старые плоские поля
            if 'banking_accounts' in company and company['banking_accounts']:
                banking_accounts = company['banking_accounts']

                # Основной счёт (обязательный)
                primary_account = next((acc for acc in banking_accounts if acc.get('is_primary')), None)
                if not primary_account and banking_accounts:
                    primary_account = banking_accounts[0]

                if primary_account:
                    # Обязательные банковские поля основного счёта
                    banking_required = ['bank_name', 'iban', 'bic', 'account_holder']
                    for field in banking_required:
                        total_fields += 1
                        if field in primary_account and primary_account[field] and str(primary_account[field]).strip():
                            filled_fields += 1
                else:
                    # Если нет основного счёта, всё равно считаем 4 пустых обязательных поля
                    total_fields += 4
            else:
                # Старый формат (плоские поля) - для обратной совместимости
                banking_required_old = ['bank_name', 'iban', 'bic', 'account_holder']

                for field in banking_required_old:
                    total_fields += 1
                    if field in company and company[field] and str(company[field]).strip():
                        filled_fields += 1

            # Базовые обязательные поля компании
            for field in required_fields:
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