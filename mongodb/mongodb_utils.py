import datetime
import json
import os

import pymongo
#from pymongo import errors
from pymongo.errors import ConnectionFailure, OperationFailure
from urllib.parse import quote_plus

from .mongodb_config import MongoConfig, verify_password #,hash_password,
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
        # cache_key = 'mongodb_client_status'
        # if cache.get(cache_key) and cls._client:
        #     return cls._client
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
        # cache.set(cache_key, True, 300)  # 5 минут
        return cls._client

    @classmethod
    def get_database(cls):
        """Возвращает объект базы данных"""
        client = cls.get_client()
        if client is not None:  # ИСПРАВЛЕНО: используем 'is not None'
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
            # КРИТИЧЕСКАЯ ПРОВЕРКА: не существует ли уже база данных?
            existing_databases = client.list_database_names()
            logger.info(f"📋 Существующие базы данных: {existing_databases}")

            if db_name in existing_databases:
                logger.error(f"❌ База данных '{db_name}' уже существует!")

                # Дополнительная проверка коллекций
                db = client[db_name]
                existing_collections = db.list_collection_names()
                logger.error(f"📂 Существующие коллекции в '{db_name}': {existing_collections}")

                # Проверяем основные коллекции
                users_collection = f"{db_name}_users"
                titles_collection = f"{db_name}_basic_titles"

                if users_collection in existing_collections and titles_collection in existing_collections:
                    users_count = db[users_collection].count_documents({})
                    titles_count = db[titles_collection].count_documents({})

                    logger.error(f"🚫 База данных '{db_name}' уже полностью настроена!")
                    logger.error(f"📊 {users_collection}: {users_count} записей")
                    logger.error(f"📊 {titles_collection}: {titles_count} записей")
                    logger.error("❌ ОТМЕНЯЕМ создание - БД уже существует!")
                    return False

            logger.success(f"✅ База данных '{db_name}' не существует, создаем...")

            # Создаем базу данных
            db = client[db_name]
            now = datetime.datetime.now()

            # Путь к JSON файлам
            base_path = os.path.join('static', 'defaults', 'data')
            logger.info(f"📂 Ищем JSON файлы в: {base_path}")

            if os.path.exists(base_path):
                # Получаем список всех JSON файлов
                json_files = [f for f in os.listdir(base_path) if f.endswith('.json')]
                logger.info(f"📋 Найдено JSON файлов: {json_files}")

                for file_name in json_files:
                    # Создаем имя коллекции: db_name + "_" + имя_файла_без_расширения
                    base_collection_name = file_name.replace('.json', '')
                    collection_name = f"{db_name}_{base_collection_name}"
                    json_path = os.path.join(base_path, file_name)

                    logger.warning(f"🎯 Обрабатываем файл: {file_name} → коллекция: {collection_name}")

                    # КРИТИЧЕСКАЯ ПРОВЕРКА: существует ли уже коллекция?
                    existing_collections = db.list_collection_names()
                    if collection_name in existing_collections:
                        existing_count = db[collection_name].count_documents({})
                        logger.error(f"🚫 Коллекция '{collection_name}' уже существует с {existing_count} записями!")
                        logger.error(f"⏭️ ПРОПУСКАЕМ создание коллекции '{collection_name}'")
                        continue

                    try:
                        with open(json_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)
                        logger.info(f"📖 Загружено {len(data) if isinstance(data, list) else 1} записей из {file_name}")

                        # Создание коллекции с проверкой существования
                        try:
                            logger.info(f"🔨 Создаем коллекцию: {collection_name}")

                            # Двойная проверка перед созданием
                            if collection_name in db.list_collection_names():
                                logger.error(f"🚫 Коллекция '{collection_name}' появилась во время создания! Пропускаем...")
                                continue

                            db.create_collection(collection_name)
                            logger.success(f"✅ Коллекция '{collection_name}' создана")

                        except Exception as create_error:
                            if "already exists" in str(create_error).lower():
                                logger.error(f"🚫 Коллекция '{collection_name}' уже существует (ошибка создания)")
                                continue
                            else:
                                raise create_error

                        # Добавляем метаданные к каждому документу
                        if isinstance(data, list):
                            for item in data:
                                item['created_at'] = now
                                item['modified_at'] = now
                                item['deleted'] = False
                            if data:  # Проверяем что список не пустой
                                result = db[collection_name].insert_many(data)
                                inserted_count = len(result.inserted_ids)
                                logger.success(f"✅ В коллекцию '{collection_name}' вставлено {inserted_count} документов")
                            else:
                                logger.success(f"📝 Пустая коллекция '{collection_name}' создана")
                        else:
                            data['created_at'] = now
                            data['modified_at'] = now
                            data['deleted'] = False
                            result = db[collection_name].insert_one(data)
                            logger.success(f"✅ В коллекцию '{collection_name}' вставлен 1 документ с ID: {result.inserted_id}")

                        # Проверяем финальное количество записей
                        final_count = db[collection_name].count_documents({})
                        logger.warning(f"📊 Финальное количество записей в '{collection_name}': {final_count}")

                    except (FileNotFoundError, json.JSONDecodeError) as e:
                        logger.error(f"Ошибка обработки файла {file_name}: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"Ошибка создания коллекции {collection_name}: {e}")
                        continue

            # Создаем коллекцию пользователей на основе JSON-файла
            users_collection_name = f"{db_name}_users"
            if users_collection_name not in db.list_collection_names():
                # Ищем JSON-файл с пользователями для получения структуры
                users_json_path = os.path.join(base_path, 'users.json')

                if os.path.exists(users_json_path):
                    try:
                        with open(users_json_path, 'r', encoding='utf-8') as file:
                            users_data = json.load(file)

                        # Создаем коллекцию и добавляем данные из JSON
                        db.create_collection(users_collection_name)

                        if isinstance(users_data, list):
                            # Добавляем метаданные к каждому пользователю
                            for user in users_data:
                                user['created_at'] = now
                                user['modified_at'] = now
                                if 'deleted' not in user:
                                    user['deleted'] = False

                            if users_data:  # Если есть данные для вставки
                                db[users_collection_name].insert_many(users_data)
                                logger.success(f"Коллекция '{users_collection_name}' создана с {len(users_data)} пользователями из JSON")
                            else:
                                logger.success(f"Пустая коллекция '{users_collection_name}' создана (пустой массив в JSON)")
                        else:
                            # Если JSON содержит один объект
                            users_data['created_at'] = now
                            users_data['modified_at'] = now
                            if 'deleted' not in users_data:
                                users_data['deleted'] = False
                            db[users_collection_name].insert_one(users_data)
                            logger.success(f"Коллекция '{users_collection_name}' создана с 1 пользователем из JSON")

                    except (FileNotFoundError, json.JSONDecodeError) as e:
                        logger.error(f"Ошибка чтения {users_json_path}: {e}")
                        # Создаем пустую коллекцию если JSON недоступен
                        db.create_collection(users_collection_name)
                        logger.success(f"Создана пустая коллекция '{users_collection_name}' (JSON недоступен)")
                    except Exception as e:
                        logger.error(f"Ошибка создания коллекции пользователей: {e}")
                        return False
                else:
                    # Если файла users.json нет, создаем пустую коллекцию
                    db.create_collection(users_collection_name)
                    logger.success(f"Создана пустая коллекция '{users_collection_name}' (файл users.json не найден)")

                # Создаем базовые индексы для производительности
                users_collection = db[users_collection_name]
                try:
                    # Уникальные индексы (могут не сработать если есть дубликаты в JSON)
                    try:
                        users_collection.create_index("username", unique=True, name="idx_username_unique")
                        logger.success("Создан уникальный индекс для username")
                    except Exception as e:
                        users_collection.create_index("username", name="idx_username")
                        logger.warning(f"Создан обычный индекс для username (не уникальный): {e}")

                    try:
                        users_collection.create_index("profile.email", unique=True, name="idx_email_unique")
                        logger.success("Создан уникальный индекс для email")
                    except Exception as e:
                        users_collection.create_index("profile.email", name="idx_email")
                        logger.warning(f"Создан обычный индекс для email (не уникальный): {e}")

                    # Основные индексы
                    users_collection.create_index([("is_active", 1), ("deleted", 1)], name="idx_active_not_deleted")
                    users_collection.create_index([("is_admin", 1), ("deleted", 1)], name="idx_admin_not_deleted")
                    users_collection.create_index("created_at", name="idx_created_at")

                    logger.success(f"Созданы индексы для коллекции '{users_collection_name}'")

                except Exception as e:
                    logger.warning(f"Частичная ошибка создания индексов: {e}")

            # Создаем системную коллекцию для информации о БД
            system_collection_name = f"{db_name}_system_info"
            db[system_collection_name].insert_one({
                'database_name': db_name,
                'created_at': now,
                'version': '1.0',
                'status': 'active',
                'collections_count': len(db.list_collection_names())
            })

            logger.success(f"{language.mess_server_create_db}{db_name}{language.mess_server_create_db_success2}")

            # Финальная проверка
            final_collections = db.list_collection_names()
            logger.warning(f"🏁 ФИНАЛЬНОЕ состояние БД '{db_name}':")
            for coll_name in final_collections:
                if 'basic_titles' in coll_name:
                    count = db[coll_name].count_documents({})
                    logger.warning(f"📊 {coll_name}: {count} записей")

            return True

        except Exception as e:
            logger.exception(f"{language.mess_server_create_db}{db_name}{language.mess_server_create_db_error2}: {e}")
            return False

    @classmethod
    def authenticate_user(cls, username, password):
        """Аутентификация обычного пользователя"""
        config = MongoConfig.read_config()
        if not config:
            logger.error("Конфигурация не загружена.")
            return False

        client = cls.get_client()
        if client is None:  # ИСПРАВЛЕНО: используем 'is None'
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

            if user and verify_password(password, user['password']):
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
        if client is None:  # ИСПРАВЛЕНО: используем 'is None'
            return False
        try:
            return db_name in client.list_database_names()
        except Exception as e:
            logger.error(f"Ошибка при проверке существования базы '{db_name}': {e}")
            return False
