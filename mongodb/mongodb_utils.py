import datetime
import json
import os
from django.core.cache import cache

import pymongo
from pymongo import errors
from pymongo.errors import ConnectionFailure, OperationFailure
from .mongodb_config import MongoConfig, hash_password
from loguru import logger

from . import language
#from user import language as lang_user


class MongoConnection:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoConnection, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_client(cls):
        cache_key = 'mongodb_client_status'
        if cache.get(cache_key) and cls._client:
            return cls._client
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
                        connection_string = f"mongodb://{admin_user}:{admin_password}@{host}:{port}/admin"
                    else:
                        connection_string = f"mongodb://{host}:{port}/"

                    cls._client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=5000)
                    cls._client.admin.command('ping')  # Проверка соединения
                    logger.success(language.mess_server_auth_success)
                except (ConnectionFailure, OperationFailure) as e:
                    logger.error(f"{language.mess_server_auth_error}: {e}")
                    cls._client = None
        cache.set(cache_key, True, 300)  # 5 минут
        return cls._client

    @classmethod
    def get_database(cls):
        """Возвращает объект базы данных"""
        client = cls.get_client()
        if client is not None:
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
            logger.success(language.mess_server_ping_success)
            return True
        except Exception as e:
            logger.error(f"{language.mess_server_ping_error}: {e}")
            return False

    @classmethod
    def authenticate_admin(cls, username, password):
        """Аутентификация администратора"""
        try:
            config = MongoConfig.read_config()
            host = config.get('host')
            port = config.get('port')

            auth_client = pymongo.MongoClient(
                f"mongodb://{username}:{password}@{host}:{port}/admin",
                serverSelectionTimeoutMS=5000
            )
            auth_client.admin.command('ping')
            return True
        except OperationFailure:
            logger.warning(language.mess_login_admin_error)
            return False
        except Exception as e:
            logger.error(f"Administratorauthentifizierungsfehler: {e}")
            return False

    @classmethod
    def create_database(cls, db_name, admin_user, admin_password):
        """Создает базу данных и администратора"""
        if not all([db_name, admin_user, admin_password]):
            logger.error("Недостаточно данных для создания базы.")
            return False

        client = cls.get_client()
        if not client:
            return False

        try:
            if db_name in client.list_database_names():
                logger.warning(f"{language.mess_server_create_db}{db_name}{language.mess_server_create_db_warning2}")
                return False

            base_path = os.path.join('static', 'defaults', 'data')

            db = client[db_name]
            db.create_collection('users')
            db.create_collection('users_profile')
            db.create_collection('firma_profile')

            # Перебор всех .json-файлов
            for file_name in os.listdir(base_path):

                if not file_name.endswith('.json'):
                    continue

                collection_name = file_name.replace('.json', '')
                json_path = os.path.join(base_path, file_name)

                try:
                    with open(json_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)

                    # Создание коллекции, если не существует
                    if collection_name not in db.list_collection_names():
                        db.create_collection(collection_name)

                    now = datetime.datetime.now()

                    # Вставка данных
                    if isinstance(data, list):
                        for item in data:
                            item['created_at'] = now
                            item['modified_at'] = now
                            item['deleted'] = False
                        db[collection_name].insert_many(data)
                        logger.info(f"{len(data)}{language.mess_default_data_elemente}'{collection_name}'.")
                    else:
                        data['created_at'] = now
                        data['modified_at'] = now
                        data['deleted'] = False
                        db[collection_name].insert_one(data)
                        logger.info(f"1 {language.mess_default_data_elemente}'{collection_name}'.")

                except (FileNotFoundError, json.JSONDecodeError) as e:
                    logger.error(f"[{collection_name}]{language.mess_default_data_reading_error}: {e}")
                except errors.PyMongoError as e:
                    logger.error(f"[{collection_name}]{language.mess_default_data_loaded_error}: {e}")

            hashed_password = sha512_hash(admin_password)
            user_result = db.users.insert_one({
                'username': admin_user,
                'password': hashed_password,
                'is_admin': True,
                'created_at': datetime.datetime.now(),
                'modified_at': datetime.datetime.now(),
                'deleted': False,
            })

            db.users_profile.insert_one({
                'user_id': user_result.inserted_id,
                'salutation_id': None,
                'title_id': None,
                'first_name': '',
                'last_name': '',
                'communications': [],
                'address_id': None,
                'address_data': '',
                'created_at': datetime.datetime.now(),
                'modified_at': datetime.datetime.now(),
                'deleted': False,
            })

            db.firma_profile.insert_one({
                'firma_name': '',
                'communication_id': None,
                'communication_data': '',
                'address_id': None,
                'address_data': '',
                'created_at': datetime.datetime.now(),
                'modified_at': datetime.datetime.now(),
                'deleted': False,
            })

            logger.success(f"{language.mess_server_create_db}{db_name}{language.mess_server_create_db_success2}")
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
        if not client:
            return False

        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не указано в конфигурации.")
            return False

        try:
            db = client[db_name]
            hashed_password = sha512_hash(password)
            user = db.users.find_one({'username': username, 'password': hashed_password})
            if user:
                logger.success(f"{lang_user.mess_login_success1}'{username}'{lang_user.mess_login_success2}")
            else:
                logger.error(lang_user.mess_user_login_error)
            return user is not None
        except Exception as e:
            logger.error(f"Ошибка аутентификации пользователя '{username}': {e}")
            return False

    @classmethod
    def database_exists(cls, db_name):
        """Проверяет наличие базы данных"""
        client = cls.get_client()
        if not client:
            return False
        try:
            return db_name in client.list_database_names()
        except Exception as e:
            logger.error(f"Ошибка при проверке существования базы '{db_name}': {e}")
            return False
