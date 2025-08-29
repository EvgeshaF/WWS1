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

    # Получаем ключ шифрования из переменных окружения
    SECRET_KEY = os.environ.get("MONGO_CONFIG_KEY")
    if not SECRET_KEY:
        raise ValueError(
            "MONGO_CONFIG_KEY environment variable is required. "
            "Please run utils/init_mongodb_key.py to generate a key and add it to your .env file."
        )

    try:
        fernet = Fernet(SECRET_KEY.encode())
    except Exception as e:
        raise ValueError(f"Invalid MONGO_CONFIG_KEY format. Please regenerate the key. Error: {e}")

    @staticmethod
    def config_exists():
        """Проверяет существование файла конфигурации"""
        return os.path.exists(MongoConfig.CONFIG_FILE)

    @staticmethod
    def read_config():
        """Читает и расшифровывает конфигурацию"""
        config = {}
        if MongoConfig.config_exists():
            try:
                with open(MongoConfig.CONFIG_FILE, 'rb') as f:
                    encrypted_data = f.read()

                decrypted_data = MongoConfig.fernet.decrypt(encrypted_data).decode()
                for line in decrypted_data.splitlines():
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value
            except Exception as e:
                logger.error(f"Ошибка чтения файла конфигурации: {e}")
                logger.warning("Возможно, файл поврежден или ключ шифрования неверный")

        return config

    @staticmethod
    def save_config(config_data):
        """Сохраняет зашифрованную конфигурацию"""
        try:
            # Добавляем комментарий и метку времени
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            plain_text = f"# MongoDB Configuration - Created: {timestamp}\n"
            plain_text += "\n".join(f"{key}={value}" for key, value in config_data.items())

            encrypted_data = MongoConfig.fernet.encrypt(plain_text.encode())

            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(MongoConfig.CONFIG_FILE), exist_ok=True)

            with open(MongoConfig.CONFIG_FILE, 'wb') as f:
                f.write(encrypted_data)

            # Устанавливаем безопасные права доступа (только владелец может читать/писать)
            os.chmod(MongoConfig.CONFIG_FILE, 0o600)

        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")
            raise

    @staticmethod
    def update_config(new_data):
        """Обновляет существующую конфигурацию"""
        config = MongoConfig.read_config()
        config.update(new_data)
        MongoConfig.save_config(config)
        logger.info(language.mess_datei_conf_update_succeed)

    @staticmethod
    def validate_config_data(config):
        """Валидация данных конфигурации"""
        required_fields = {
            'host': str,
            'port': int,
        }

        optional_fields = {
            'admin_user': str,
            'admin_password': str,
            'db_name': str,
            'auth_source': str,
        }

        errors = []

        # Проверяем обязательные поля
        for field, expected_type in required_fields.items():
            if field not in config:
                errors.append(f"Отсутствует обязательное поле: {field}")
            else:
                try:
                    if expected_type == int:
                        int(config[field])
                    elif expected_type == str and not config[field].strip():
                        errors.append(f"Поле {field} не может быть пустым")
                except ValueError:
                    errors.append(f"Неверный тип данных для поля {field}")

        # Проверяем порт
        if 'port' in config:
            try:
                port = int(config['port'])
                if not (1 <= port <= 65535):
                    errors.append("Порт должен быть в диапазоне 1-65535")
            except ValueError:
                errors.append("Порт должен быть числом")

        return errors

    @staticmethod
    def check_config_completeness():
        """Проверяет полноту конфигурации и возвращает статус"""
        logger.info("")
        logger.info("--- Start APP ---")

        config = MongoConfig.read_config()

        # Валидируем конфигурацию
        validation_errors = MongoConfig.validate_config_data(config)
        if validation_errors:
            logger.error("Ошибки в конфигурации:")
            for error in validation_errors:
                logger.error(f"  - {error}")

        basic_config = {'host', 'port'}
        full_config = {'host', 'port', 'admin_user', 'admin_password', 'db_name'}

        if not basic_config.issubset(config.keys()):
            logger.error(language.mess_server_configuration_warning)
            return 'connection_required'

        host = config['host']
        try:
            port = int(config['port'])
        except (ValueError, TypeError):
            logger.error("Неверный формат порта в конфигурации")
            return 'connection_required'

        # Тестируем подключение
        try:
            connection_uri = f"mongodb://{host}:{port}/"
            client = MongoClient(connection_uri, serverSelectionTimeoutMS=3000)
            client.admin.command('ping')
            logger.success(f"{host}:{port} — {language.mess_server_ping_success}")
        except ConnectionFailure as e:
            logger.error(f"{host}:{port} — {language.mess_server_ping_error}: {str(e)}")
            return 'ping_failed'

        if not full_config.issubset(config.keys()):
            return 'login_required'

        if config['db_name'].lower() == "admin":
            logger.warning(language.mess_db_name_admin_warning)
            return 'db_required'

        # Тестируем аутентификацию
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

    @staticmethod
    def delete_config():
        """Удаляет файл конфигурации"""
        if MongoConfig.config_exists():
            try:
                os.remove(MongoConfig.CONFIG_FILE)
                logger.info("Файл конфигурации удален")
                return True
            except Exception as e:
                logger.error(f"Ошибка удаления файла конфигурации: {e}")
                return False
        return True