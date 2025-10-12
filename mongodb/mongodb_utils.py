# mongodb/mongodb_utils.py - ИСПРАВЛЕНО: все проверки MongoDB объектов

import datetime
import json
import os

import pymongo
from pymongo.errors import ConnectionFailure, OperationFailure
from urllib.parse import quote_plus

from .mongodb_config import MongoConfig, verify_password
from loguru import logger

from . import language


class MongoConnection:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoConnection, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_client(cls):
        """Получает клиент MongoDB из конфигурации"""
        if cls._client is None:
            config = MongoConfig.read_config()
            if not config:
                logger.error("Konfigurationsdatei für die Datenbankverbindung nicht gefunden")
                return None

            host = config.get('host')
            port = config.get('port')
            admin_user = config.get('admin_user')
            admin_password = config.get('admin_password')
            db_name = config.get('db_name')

            if host and port:
                try:
                    if admin_user and admin_password:
                        # Экранируем пароль для URL
                        escaped_password = quote_plus(admin_password)
                        connection_string = f"mongodb://{admin_user}:{escaped_password}@{host}:{port}/admin"
                    else:
                        connection_string = f"mongodb://{host}:{port}/"

                    cls._client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=5000)
                    cls._client.admin.command('ping')  # Проверка соединения
                    logger.success(language.mess_server_auth_success)
                except (ConnectionFailure, OperationFailure) as e:
                    logger.error(f"{language.mess_server_auth_error}: {e}")
                    cls._client = None
        return cls._client

    @classmethod
    def get_database(cls):
        """Возвращает объект базы данных"""
        client = cls.get_client()
        if client is not None:  # ✅ ИСПРАВЛЕНО: правильная проверка клиента
            config = MongoConfig.read_config()
            db_name = config.get('db_name')
            if db_name:
                return client[db_name]
            logger.error("Имя базы данных не указано в конфигурации.")
        return None

    @classmethod
    def test_connection(cls, host, port):
        """Тестирует соединение с сервером MongoDB"""
        try:
            client = pymongo.MongoClient(f"mongodb://{host}:{port}/", serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            logger.success(f"{host}:{port} — {language.mess_server_ping_success}")
            return True
        except Exception as e:
            logger.error(f"{host}:{port} — {language.mess_server_ping_error}: {e}")
            return False

    @classmethod
    def authenticate_admin(cls, username, password):
        """Аутентификация администратора"""
        try:
            config = MongoConfig.read_config()
            host = config.get('host')
            port = config.get('port')

            if not host or not port:
                logger.error("Host и Port должны быть настроены перед авторизацией")
                return False

            # Экранируем пароль и имя пользователя для URL
            escaped_username = quote_plus(username)
            escaped_password = quote_plus(password)

            auth_client = pymongo.MongoClient(
                f"mongodb://{escaped_username}:{escaped_password}@{host}:{port}/admin",
                serverSelectionTimeoutMS=5000
            )

            # Проверяем подключение
            auth_client.admin.command('ping')

            # Дополнительно проверяем права администратора
            try:
                # Пытаемся получить список баз данных (требует админских прав)
                databases = auth_client.list_database_names()
                logger.success(f"Администратор '{username}' успешно авторизован. Доступных БД: {len(databases)}")
                return True
            except OperationFailure as e:
                logger.warning(f"Пользователь '{username}' авторизован, но без админских прав: {e}")
                return True  # Возвращаем True, так как авторизация прошла

        except OperationFailure as e:
            error_code = e.details.get('code', 0) if hasattr(e, 'details') else 0
            if error_code == 18:  # Authentication failed
                logger.warning(f"Неверные учетные данные для '{username}': {language.mess_login_admin_error}")
            else:
                logger.error(f"Ошибка авторизации '{username}': {e}")
            return False
        except ConnectionFailure as e:
            logger.error(f"Ошибка подключения при авторизации '{username}': {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при авторизации '{username}': {e}")
            return False

    @classmethod
    def create_database_step3(cls, db_name):
        """Создает базу данных с коллекциями из JSON файлов"""
        logger.warning(f"🚀 === НАЧАЛО create_database_step3 для БД: {db_name} ===")

        if not db_name:
            logger.error("Имя базы данных обязательно")
            return False

        client = cls.get_client()
        if client is None:
            return False

        try:
            # ЕДИНСТВЕННАЯ ПРОВЕРКА существования БД в начале
            existing_databases = client.list_database_names()
            logger.info(f"📋 Существующие базы данных: {existing_databases}")

            if db_name in existing_databases:
                logger.error(f"❌ База данных '{db_name}' уже существует!")
                return False

            logger.success(f"✅ База данных '{db_name}' не существует, создаем...")

            # Создаем базу данных
            db = client[db_name]
            now = datetime.datetime.now()

            # Путь к JSON файлам
            base_path = os.path.join('static', 'defaults', 'data')
            logger.info(f"📂 Ищем JSON файлы в: {base_path}")

            created_collections = []

            if os.path.exists(base_path):
                json_files = [f for f in os.listdir(base_path) if f.endswith('.json')]
                logger.info(f"📋 Найдено JSON файлов: {json_files}")

                for file_name in json_files:
                    base_collection_name = file_name.replace('.json', '')
                    collection_name = f"{db_name}_{base_collection_name}"
                    json_path = os.path.join(base_path, file_name)

                    logger.warning(f"🎯 Обрабатываем файл: {file_name} → коллекция: {collection_name}")

                    try:
                        # Читаем JSON
                        with open(json_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)

                        logger.info(f"📖 Загружено {len(data) if isinstance(data, list) else 1} записей из {file_name}")

                        # Создаем коллекцию
                        db.create_collection(collection_name)
                        logger.success(f"✅ Коллекция '{collection_name}' создана")

                        # Добавляем метаданные и вставляем данные
                        if isinstance(data, list):
                            for item in data:
                                item['created_at'] = now
                                item['modified_at'] = now
                                item['deleted'] = False

                            if data:
                                result = db[collection_name].insert_many(data)
                                logger.success(f"✅ В коллекцию '{collection_name}' вставлено {len(result.inserted_ids)} документов")
                            else:
                                logger.success(f"📝 Пустая коллекция '{collection_name}' создана")
                        else:
                            data['created_at'] = now
                            data['modified_at'] = now
                            data['deleted'] = False
                            result = db[collection_name].insert_one(data)
                            logger.success(f"✅ В коллекцию '{collection_name}' вставлен 1 документ")

                        created_collections.append(collection_name)

                        # Создаем индексы для коллекции users
                        if base_collection_name == 'users':
                            users_collection = db[collection_name]
                            try:
                                users_collection.create_index("username", unique=True, name="idx_username_unique")
                                users_collection.create_index("profile.email", unique=True, name="idx_email_unique")
                                users_collection.create_index([("is_active", 1), ("deleted", 1)], name="idx_active_not_deleted")
                                users_collection.create_index([("is_admin", 1), ("deleted", 1)], name="idx_admin_not_deleted")
                                users_collection.create_index("created_at", name="idx_created_at")
                                logger.success(f"📊 Индексы созданы для коллекции '{collection_name}'")
                            except Exception as e:
                                logger.warning(f"⚠️ Частичная ошибка создания индексов: {e}")

                    except FileNotFoundError:
                        logger.error(f"❌ Файл не найден: {json_path}")
                        continue
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Ошибка JSON в файле {file_name}: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"❌ Ошибка создания коллекции {collection_name}: {e}")
                        # ROLLBACK: удаляем базу данных при ошибке
                        client.drop_database(db_name)
                        logger.error(f"🔄 База данных '{db_name}' удалена из-за ошибки")
                        return False

            # Финальная проверка
            final_collections = db.list_collection_names()
            logger.warning(f"🏁 ФИНАЛЬНОЕ состояние БД '{db_name}': {len(final_collections)} коллекций")
            for coll_name in final_collections:
                count = db[coll_name].count_documents({})
                logger.info(f"📊 {coll_name}: {count} записей")

            logger.success(f"✅ База данных '{db_name}' успешно создана с {len(created_collections)} коллекциями")
            return True

        except Exception as e:
            logger.exception(f"❌ Критическая ошибка создания БД '{db_name}': {e}")
            # ROLLBACK
            try:
                client.drop_database(db_name)
                logger.error(f"🔄 База данных '{db_name}' удалена из-за критической ошибки")
            except:
                pass
            return False

    @classmethod
    def create_users_collection(cls, db_name: str):
        """Создает коллекцию пользователей программно (без users.json)"""
        logger.warning(f"🚀 Создание коллекции пользователей программно для БД: {db_name}")

        client = cls.get_client()
        if client is None:
            logger.error("❌ Нет подключения к MongoDB")
            return False

        try:
            db = client[db_name]
            users_collection_name = f"{db_name}_users"

            # Проверяем, существует ли коллекция
            if users_collection_name in db.list_collection_names():
                logger.warning(f"⚠️ Коллекция '{users_collection_name}' уже существует — пропуск создания.")
                return True

            # JSON Schema валидатор (структура как в users.json)
            validator = {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "username", "password", "profile",
                        "is_active", "created_at", "modified_at", "deleted"
                    ],
                    "properties": {
                        "username": {"bsonType": "string"},
                        "password": {"bsonType": "string"},
                        "is_admin": {"bsonType": "bool"},
                        "is_active": {"bsonType": "bool"},
                        "created_at": {"bsonType": "date"},
                        "modified_at": {"bsonType": "date"},
                        "deleted": {"bsonType": "bool"},
                        "last_login": {"bsonType": ["date", "null"]},
                        "password_changed_at": {"bsonType": ["date", "null"]},
                        "profile": {
                            "bsonType": "object",
                            "required": ["first_name", "last_name", "email"],
                            "properties": {
                                "salutation": {"bsonType": ["string", "null"]},
                                "title": {"bsonType": ["string", "null"]},
                                "first_name": {"bsonType": "string"},
                                "last_name": {"bsonType": "string"},
                                "email": {"bsonType": "string"},
                                "phone": {"bsonType": ["string", "null"]},
                                "contacts": {
                                    "bsonType": "array",
                                    "items": {
                                        "bsonType": "object",
                                        "required": ["type", "value", "is_primary"],
                                        "properties": {
                                            "type": {"bsonType": "string"},
                                            "value": {"bsonType": "string"},
                                            "note": {"bsonType": ["string", "null"]},
                                            "is_primary": {"bsonType": "bool"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            db.create_collection(users_collection_name, validator=validator)
            logger.success(f"✅ Коллекция '{users_collection_name}' успешно создана программно")

            # Индексы (как в твоём коде)
            users_collection = db[users_collection_name]
            users_collection.create_index("username", unique=True, name="idx_username_unique")
            users_collection.create_index("profile.email", unique=True, name="idx_email_unique")
            users_collection.create_index([("is_active", 1), ("deleted", 1)], name="idx_active_not_deleted")
            users_collection.create_index([("is_admin", 1), ("deleted", 1)], name="idx_admin_not_deleted")
            users_collection.create_index("created_at", name="idx_created_at")

            logger.success(f"📊 Индексы созданы для коллекции '{users_collection_name}'")
            return True

        except Exception as e:
            logger.exception(f"Ошибка при создании коллекции пользователей: {e}")
            return False

    @classmethod
    def authenticate_user(cls, username, password):
        """Аутентификация обычного пользователя"""
        config = MongoConfig.read_config()
        if not config:
            logger.error("Конфигурация не загружена.")
            return False

        client = cls.get_client()
        if client is None:  # ✅ ИСПРАВЛЕНО: правильная проверка клиента
            return False

        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не указано в конфигурации.")
            return False

        try:
            db = client[db_name]

            # Используем правильное имя коллекции пользователей
            users_collection_name = f"{db_name}_users"
            user = db[users_collection_name].find_one({'username': username, 'deleted': False})

            if user is not None and verify_password(password, user['password']):  # ✅ ИСПРАВЛЕНО
                logger.success(f"Пользователь '{username}' успешно авторизован.")
                return user
            else:
                logger.error("Неверное имя пользователя или пароль.")
                return None
        except Exception as e:
            logger.error(f"Ошибка аутентификации пользователя '{username}': {e}")
            return False

    @classmethod
    def database_exists(cls, db_name):
        """Проверяет наличие базы данных"""
        client = cls.get_client()
        if client is None:  # ✅ ИСПРАВЛЕНО: правильная проверка клиента
            return False
        try:
            return db_name in client.list_database_names()
        except Exception as e:
            logger.error(f"Ошибка при проверке существования базы '{db_name}': {e}")
            return False