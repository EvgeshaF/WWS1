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
                        logger.info(f"🔐 Подключение с администратором: {admin_user}")
                    else:
                        connection_string = f"mongodb://{host}:{port}/"
                        logger.warning("⚠️ Подключение БЕЗ аутентификации!")

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
            logger.error("Не удалось получить клиент MongoDB")
            return False

        # ✅ ДОБАВЛЕНО: Проверка наличия администратора в конфиге
        config = MongoConfig.read_config()
        admin_user = config.get('admin_user') if config else None

        if not admin_user:
            logger.error("❌ Администратор не настроен в mongo_config.env.enc!")
            logger.error("💡 Сначала выполните authenticate_admin(username, password)")
            return False

        logger.info(f"🔐 Работаем с администратором: {admin_user}")

        try:
            # ✅ ИСПРАВЛЕНО: Безопасная проверка через коллекции (не требует listDatabases)
            db = client[db_name]

            try:
                existing_collections = db.list_collection_names()
                logger.info(f"📂 Существующие коллекции в '{db_name}': {existing_collections}")
            except OperationFailure as e:
                if e.code == 13:  # Unauthorized
                    logger.error(f"❌ Нет прав для доступа к базе '{db_name}'")
                    logger.error(f"💡 Убедитесь, что '{admin_user}' имеет права на эту базу")
                    return False
                raise
            except Exception as e:
                logger.info(f"📋 База данных '{db_name}' пуста или не существует")
                existing_collections = []

            if existing_collections:
                logger.warning(f"⚠️ База данных '{db_name}' уже существует ({len(existing_collections)} коллекций)")

                # Проверяем обязательные коллекции
                users_collection = f"{db_name}_users"
                titles_collection = f"{db_name}_basic_titles"

                required_collections = [users_collection, titles_collection]
                missing_collections = [col for col in required_collections if col not in existing_collections]

                if not missing_collections:
                    # Дополнительная проверка: есть ли данные в коллекциях
                    users_count = db[users_collection].count_documents({})
                    titles_count = db[titles_collection].count_documents({})

                    if users_count > 0 or titles_count > 0:
                        logger.error(f"🚫 База данных '{db_name}' уже полностью настроена!")
                        logger.error(f"📊 {users_collection}: {users_count} записей")
                        logger.error(f"📊 {titles_collection}: {titles_count} записей")
                        logger.error("❌ ОТМЕНЯЕМ создание - БД уже существует!")
                        return False
                    else:
                        logger.warning(f"⚠️ База существует, но коллекции пусты. Удаляем и создаем заново...")
                        try:
                            client.drop_database(db_name)
                            logger.success(f"✅ Пустая база '{db_name}' удалена")
                        except OperationFailure as e:
                            if e.code == 13:
                                logger.error("❌ Недостаточно прав для удаления базы")
                                return False
                            raise
                else:
                    logger.warning(f"⚠️ Отсутствуют коллекции: {missing_collections}")
                    logger.warning(f"⚠️ Удаляем неполную базу '{db_name}' для чистого старта...")
                    try:
                        client.drop_database(db_name)
                        logger.success(f"✅ Неполная база '{db_name}' удалена")
                    except OperationFailure as e:
                        if e.code == 13:
                            logger.error("❌ Недостаточно прав для удаления базы")
                            return False
                        raise

            # Теперь создаем базу с нуля
            logger.success(f"✅ Создаем новую базу данных '{db_name}'...")
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
                        with open(json_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)
                        logger.info(f"📖 Загружено {len(data) if isinstance(data, list) else 1} записей из {file_name}")

                        # Создаем коллекцию
                        db.create_collection(collection_name)
                        logger.success(f"✅ Коллекция '{collection_name}' создана")

                        # Добавляем метаданные и вставляем данные
                        if isinstance(data, list):
                            if data:  # Только если список не пустой
                                for item in data:
                                    item['created_at'] = now
                                    item['modified_at'] = now
                                    item['deleted'] = False
                                result = db[collection_name].insert_many(data)
                                inserted_count = len(result.inserted_ids)
                                logger.success(f"✅ Вставлено {inserted_count} документов в '{collection_name}'")
                            else:
                                logger.info(f"📝 Пустая коллекция '{collection_name}' создана")
                        else:
                            data['created_at'] = now
                            data['modified_at'] = now
                            data['deleted'] = False
                            result = db[collection_name].insert_one(data)
                            logger.success(f"✅ Вставлен 1 документ в '{collection_name}'")

                        created_collections.append(collection_name)

                        # Проверяем финальное количество
                        final_count = db[collection_name].count_documents({})
                        logger.info(f"📊 Финальное количество записей в '{collection_name}': {final_count}")

                    except Exception as e:
                        logger.error(f"❌ Ошибка при обработке {file_name}: {e}")
                        # В случае ошибки откатываем всё
                        logger.error("🔄 Откатываем создание базы данных...")
                        try:
                            client.drop_database(db_name)
                        except:
                            pass
                        return False

            # Создаем коллекцию пользователей с индексами
            users_collection_name = f"{db_name}_users"
            if users_collection_name not in created_collections:
                logger.warning(f"⚠️ Коллекция users не создана из JSON, создаем вручную...")
                db.create_collection(users_collection_name)
                logger.success(f"✅ Создана пустая коллекция '{users_collection_name}'")

            # Создаем индексы для пользователей
            users_collection = db[users_collection_name]
            try:
                # Уникальные индексы
                try:
                    users_collection.create_index("username", unique=True, name="idx_username_unique")
                    logger.success("✅ Создан уникальный индекс для username")
                except Exception as e:
                    users_collection.create_index("username", name="idx_username")
                    logger.warning(f"⚠️ Создан обычный индекс для username: {e}")

                try:
                    users_collection.create_index("profile.email", unique=True, name="idx_email_unique")
                    logger.success("✅ Создан уникальный индекс для email")
                except Exception as e:
                    users_collection.create_index("profile.email", name="idx_email")
                    logger.warning(f"⚠️ Создан обычный индекс для email: {e}")

                # Основные индексы
                users_collection.create_index([("is_active", 1), ("deleted", 1)], name="idx_active_not_deleted")
                users_collection.create_index([("is_admin", 1), ("deleted", 1)], name="idx_admin_not_deleted")
                users_collection.create_index("created_at", name="idx_created_at")
                logger.success(f"✅ Созданы индексы для '{users_collection_name}'")

            except Exception as e:
                logger.warning(f"⚠️ Частичная ошибка создания индексов: {e}")

            # Создаем системную коллекцию
            system_collection_name = f"{db_name}_system_info"
            db[system_collection_name].insert_one({
                'database_name': db_name,
                'created_at': now,
                'version': '1.0',
                'status': 'active',
                'collections_count': len(db.list_collection_names())
            })
            logger.success(f"✅ Создана системная коллекция '{system_collection_name}'")

            # Финальная проверка
            final_collections = db.list_collection_names()
            logger.success(f"🎉 База данных '{db_name}' успешно создана!")
            logger.info(f"📊 Всего коллекций: {len(final_collections)}")

            for coll_name in final_collections:
                count = db[coll_name].count_documents({})
                logger.info(f"  📂 {coll_name}: {count} записей")

            return True

        except OperationFailure as e:
            if e.code == 13:  # Unauthorized
                logger.error("❌ Недостаточно прав для создания базы данных")
                logger.error(f"💡 Убедитесь, что '{admin_user}' имеет права dbAdmin или root")
            else:
                logger.error(f"❌ Ошибка MongoDB: {e}")

            # Пытаемся откатить
            try:
                client.drop_database(db_name)
                logger.warning(f"🔄 База данных '{db_name}' удалена из-за ошибки")
            except:
                pass
            return False

        except Exception as e:
            logger.exception(f"❌ Критическая ошибка при создании БД '{db_name}': {e}")
            # Пытаемся откатить изменения
            try:
                client.drop_database(db_name)
                logger.warning(f"🔄 База данных '{db_name}' удалена из-за ошибки")
            except:
                pass
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
        """Проверяет наличие базы данных (безопасный метод без прав listDatabases)"""
        client = cls.get_client()
        if client is None:
            logger.error("Не удалось получить клиент MongoDB")
            return False

        try:
            # Вместо list_database_names() проверяем наличие коллекций
            db = client[db_name]
            collections = db.list_collection_names()

            # Если есть хоть одна коллекция, база существует
            exists = len(collections) > 0

            if exists:
                logger.info(f"✅ База данных '{db_name}' существует ({len(collections)} коллекций)")
            else:
                logger.info(f"❌ База данных '{db_name}' не существует или пуста")

            return exists

        except Exception as e:
            logger.error(f"❌ Ошибка при проверке существования базы '{db_name}': {e}")
            return False