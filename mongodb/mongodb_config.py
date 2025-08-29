import os
import hashlib
from urllib.parse import quote_plus
from pymongo.errors import ConnectionFailure, OperationFailure
from loguru import logger
from pymongo import MongoClient
from cryptography.fernet import Fernet
from . import language


def sha512_hash(password):
    """Хеширование пароля по алгоритму SHA-512"""
    return hashlib.sha512(password.encode('utf-8')).hexdigest()


class MongoConfig:
    CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mongo_config.env.enc')
    # 🔑 ключ лучше хранить в settings.py или переменной окружения
    SECRET_KEY = os.environ.get("MONGO_CONFIG_KEY", "2EjI8q7MTgP1FUbmNUc1HZCSd_G1RGbTjaNGuonlm8c=").encode()
    fernet = Fernet(SECRET_KEY)

    @staticmethod
    def config_exists():
        return os.path.exists(MongoConfig.CONFIG_FILE)

    @staticmethod
    def read_config():
        """Читает и расшифровывает конфигурацию"""
        config = {}
        if MongoConfig.config_exists():
            with open(MongoConfig.CONFIG_FILE, 'rb') as f:
                encrypted_data = f.read()
            try:
                decrypted_data = MongoConfig.fernet.decrypt(encrypted_data).decode()
                for line in decrypted_data.splitlines():
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        config[key] = value
            except Exception as e:
                logger.error(f"Ошибка расшифровки файла конфигурации: {e}")
        return config

    @staticmethod
    def save_config(config_data):
        """Сохраняет зашифрованную конфигурацию"""
        plain_text = "\n".join(f"{key}={value}" for key, value in config_data.items())
        encrypted_data = MongoConfig.fernet.encrypt(plain_text.encode())
        with open(MongoConfig.CONFIG_FILE, 'wb') as f:
            f.write(encrypted_data)

    @staticmethod
    def update_config(new_data):
        config = MongoConfig.read_config()
        config.update(new_data)
        MongoConfig.save_config(config)
        logger.info(language.mess_datei_conf_update_succeed)

    @staticmethod
    def check_config_completeness():
        logger.info("")
        logger.info("--- Start APP ---")

        config = MongoConfig.read_config()

        basic_config = {'host', 'port'}
        full_config = {'host', 'port', 'admin_user', 'admin_password', 'db_name'}

        if not basic_config.issubset(config.keys()):
            logger.error(language.mess_server_configuration_warning)
            return 'connection_required'

        host = config['host']
        port = config['port']

        try:
            connection_uri = f"mongodb://{host}:{port}/"
            client = MongoClient(connection_uri, serverSelectionTimeoutMS=3000)
            client.admin.command('ping')
            logger.success(f"{host}:{port} — {language.mess_server_ping_success}")
        except ConnectionFailure:
            # logger.error(f"{host}:{port} — {language.mess_server_ping_error}")
            return 'ping_failed'

        if not full_config.issubset(config.keys()):
            return 'login_required'

        if config['db_name'].lower() == "admin":
            logger.warning(language.mess_db_name_admin_warning)
            return 'db_required'

        db_name = config['db_name']

        try:
            username = config['admin_user']
            password = quote_plus(config['admin_password'])
            auth_db = config.get('auth_source', 'admin')
            connection_uri = f"mongodb://{username}:{password}@{host}:{port}/{db_name}?authSource={auth_db}"
            client = MongoClient(connection_uri, serverSelectionTimeoutMS=3000)
            client.admin.command('ping')
            logger.success(language.mess_server_auth_success)
        except (ConnectionFailure, OperationFailure) as e:
            logger.error(f"{language.mess_server_auth_error}: {str(e)}")
            return 'login_failed'

        return 'complete'
