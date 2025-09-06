# users/user_utils.py - ПОЛНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ

import datetime
from typing import Optional, Dict, Any, List
from loguru import logger
from django.contrib.auth.hashers import make_password, check_password
from mongodb.mongodb_config import MongoConfig
from mongodb.mongodb_utils import MongoConnection
from pymongo.errors import DuplicateKeyError, ConnectionFailure, OperationFailure


class UserManager:
    """Менеджер для работы с пользователями в MongoDB"""

    def __init__(self):
        logger.debug("🔧 Инициализация UserManager")

        # Получаем подключение к БД
        self.db = MongoConnection.get_database()
        if self.db is None:
            logger.error("❌ База данных недоступна")
            self.users_collection_name = None
            return

        # Определяем имя коллекции
        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("❌ Имя базы данных не найдено в конфигурации")
            self.users_collection_name = None
        else:
            self.users_collection_name = f"{db_name}_users"
            logger.info(f"✅ Имя коллекции: {self.users_collection_name}")

    def get_collection(self):
        """Получает коллекцию пользователей с проверками"""
        if self.db is None:
            logger.error("❌ База данных недоступна")
            return None

        if not self.users_collection_name:
            logger.error("❌ Имя коллекции пользователей не определено")
            return None

        try:
            # Получаем список существующих коллекций
            existing_collections = self.db.list_collection_names()
            logger.debug(f"📋 Существующие коллекции: {existing_collections}")

            # Проверяем, существует ли наша коллекция
            if self.users_collection_name not in existing_collections:
                logger.warning(f"⚠️  Коллекция '{self.users_collection_name}' не существует. Создаем...")

                # Создаем коллекцию
                collection = self.db.create_collection(self.users_collection_name)
                logger.info(f"✅ Коллекция '{self.users_collection_name}' создана")

                # Создаем индексы
                try:
                    collection.create_index("username", unique=True, name="idx_username_unique")
                    collection.create_index("profile.email", unique=True, sparse=True, name="idx_email_unique")
                    collection.create_index([("is_active", 1), ("deleted", 1)], name="idx_active_not_deleted")
                    collection.create_index([("is_admin", 1), ("deleted", 1)], name="idx_admin_not_deleted")
                    collection.create_index("created_at", name="idx_created_at")
                    logger.success("✅ Индексы созданы")
                except Exception as e:
                    logger.warning(f"⚠️  Ошибка создания индексов: {e}")
            else:
                logger.debug(f"✅ Коллекция '{self.users_collection_name}' существует")

            # Возвращаем коллекцию
            collection = self.db[self.users_collection_name]

            # Проверяем доступность коллекции
            try:
                collection.count_documents({})
                logger.debug(f"✅ Коллекция '{self.users_collection_name}' доступна")
            except Exception as e:
                logger.error(f"❌ Коллекция недоступна: {e}")
                return None

            return collection

        except ConnectionFailure as e:
            logger.error(f"❌ Ошибка подключения к MongoDB: {e}")
            return None
        except OperationFailure as e:
            logger.error(f"❌ Ошибка операции MongoDB: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка получения коллекции '{self.users_collection_name}': {e}")
            return None

    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Создает нового пользователя с расширенной диагностикой"""
        try:
            logger.info(f"🚀 НАЧАЛО создания пользователя: {user_data.get('username')}")

            # Получаем коллекцию
            collection = self.get_collection()
            if collection is None:
                logger.error("❌ Коллекция пользователей недоступна")
                return False

            # Проверяем обязательные поля
            if not user_data.get('username'):
                logger.error("❌ Отсутствует обязательное поле: username")
                return False

            username = user_data['username']

            # Проверяем, что пользователь с таким именем не существует
            logger.info(f"🔍 Проверяем существование пользователя: {username}")
            existing_user = collection.find_one({
                'username': username,
                'deleted': {'$ne': True}
            })

            if existing_user:
                logger.error(f"❌ Пользователь '{username}' уже существует")
                return False

            # Логируем данные (без пароля)
            log_data = {k: v for k, v in user_data.items() if k != 'password'}
            logger.info(f"📝 Данные пользователя (без пароля): {log_data}")

            # Подготавливаем данные для вставки
            insert_data = user_data.copy()

            # Убеждаемся, что системные поля установлены
            now = datetime.datetime.now()
            if 'created_at' not in insert_data:
                insert_data['created_at'] = now
            if 'modified_at' not in insert_data:
                insert_data['modified_at'] = now
            if 'deleted' not in insert_data:
                insert_data['deleted'] = False
            if 'last_login' not in insert_data:
                insert_data['last_login'] = None
            if 'failed_login_attempts' not in insert_data:
                insert_data['failed_login_attempts'] = 0
            if 'locked_until' not in insert_data:
                insert_data['locked_until'] = None
            if 'password_changed_at' not in insert_data:
                insert_data['password_changed_at'] = now

            logger.info(f"💾 Выполняем вставку в коллекцию: {collection.name}")

            # ВСТАВЛЯЕМ ПОЛЬЗОВАТЕЛЯ
            result = collection.insert_one(insert_data)

            logger.info(f"📋 Результат вставки - inserted_id: {result.inserted_id}")

            if result.inserted_id:
                # КРИТИЧЕСКАЯ ПРОВЕРКА №1: поиск по ID
                logger.info(f"🔍 Проверяем сохранение по _id: {result.inserted_id}")
                verification_by_id = collection.find_one({'_id': result.inserted_id})

                if verification_by_id:
                    logger.success(f"✅ НАЙДЕН по _id! Username: {verification_by_id.get('username')}")

                    # КРИТИЧЕСКАЯ ПРОВЕРКА №2: поиск по username
                    logger.info(f"🔍 Проверяем поиск по username: {username}")
                    verification_by_name = collection.find_one({
                        'username': username,
                        'deleted': {'$ne': True}
                    })

                    if verification_by_name:
                        logger.success(f"✅ НАЙДЕН по username! ID: {verification_by_name.get('_id')}")

                        # ПРОВЕРЯЕМ КОЛИЧЕСТВО ЗАПИСЕЙ
                        total_users = collection.count_documents({})
                        active_users = collection.count_documents({'deleted': {'$ne': True}})
                        admin_users = collection.count_documents({
                            'is_admin': True,
                            'deleted': {'$ne': True},
                            'is_active': True
                        })

                        logger.info(f"📊 Статистика: всего={total_users}, активных={active_users}, админов={admin_users}")

                        return True
                    else:
                        logger.error(f"❌ НЕ НАЙДЕН по username '{username}' после создания!")
                else:
                    logger.error(f"❌ НЕ НАЙДЕН по _id {result.inserted_id} после создания!")
            else:
                logger.error("❌ Не удалось получить inserted_id")

            return False

        except DuplicateKeyError as e:
            logger.error(f"❌ Дублирование ключа при создании пользователя '{username}': {e}")
            return False
        except ConnectionFailure as e:
            logger.error(f"❌ Ошибка подключения при создании пользователя '{username}': {e}")
            return False
        except OperationFailure as e:
            logger.error(f"❌ Ошибка операции при создании пользователя '{username}': {e}")
            return False
        except Exception as e:
            logger.exception(f"💥 КРИТИЧЕСКАЯ ОШИБКА создания пользователя '{username}': {e}")
            return False

    def find_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Находит пользователя по имени с диагностикой"""
        try:
            logger.debug(f"🔍 Поиск пользователя: {username}")

            collection = self.get_collection()
            if collection is None:
                logger.error("❌ Коллекция недоступна для поиска")
                return None

            user = collection.find_one({
                'username': username,
                'deleted': {'$ne': True}
            })

            if user:
                logger.debug(f"✅ Пользователь '{username}' найден")
                return user
            else:
                logger.debug(f"❌ Пользователь '{username}' не найден")

                # Дополнительная диагностика
                all_users = list(collection.find({}, {'username': 1, 'deleted': 1}))
                logger.debug(f"🔍 Все пользователи в коллекции: {[u.get('username') for u in all_users]}")

                return None

        except Exception as e:
            logger.error(f"❌ Ошибка поиска пользователя '{username}': {e}")
            return None

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Находит пользователя по email в profile.email"""
        try:
            collection = self.get_collection()
            if collection is None:
                return None

            user = collection.find_one({
                'profile.email': email,  # ИСПРАВЛЕНО: поиск в profile.email
                'deleted': {'$ne': True}
            })
            return user

        except Exception as e:
            logger.error(f"Ошибка поиска пользователя по email '{email}': {e}")
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Аутентифицирует пользователя"""
        try:
            user = self.find_user_by_username(username)
            if not user:
                logger.warning(f"Пользователь '{username}' не найден")
                return None

            if not user.get('is_active', False):
                logger.warning(f"Пользователь '{username}' заблокирован")
                return None

            # Проверяем блокировку
            locked_until = user.get('locked_until')
            if locked_until and locked_until > datetime.datetime.now():
                logger.warning(f"Пользователь '{username}' временно заблокирован до {locked_until}")
                return None

            # Проверяем пароль
            if check_password(password, user['password']):
                self._update_login_success(username)
                logger.success(f"Пользователь '{username}' успешно авторизован")
                return user
            else:
                self._update_login_failure(username)
                logger.warning(f"Неверный пароль для пользователя '{username}'")
                return None

        except Exception as e:
            logger.error(f"Ошибка аутентификации пользователя '{username}': {e}")
            return None

    def get_admin_count(self) -> int:
        """Возвращает количество администраторов с диагностикой"""
        try:
            logger.debug("Подсчет администраторов...")

            collection = self.get_collection()
            if collection is None:
                logger.error("Коллекция недоступна для подсчета")
                return 0

            # Подсчитываем активных администраторов
            admin_query = {
                'is_admin': True,
                'deleted': {'$ne': True},
                'is_active': True
            }

            count = collection.count_documents(admin_query)
            logger.info(f"Найдено активных администраторов: {count}")

            # Дополнительная диагностика
            total_count = collection.count_documents({})
            admin_all_count = collection.count_documents({'is_admin': True})
            active_count = collection.count_documents({'is_active': True, 'deleted': {'$ne': True}})

            logger.debug(f"Статистика: всего={total_count}, админов_всего={admin_all_count}, активных={active_count}")

            return count

        except Exception as e:
            logger.error(f"Ошибка подсчета администраторов: {e}")
            return 0

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Аутентифицирует пользователя"""
        try:
            user = self.find_user_by_username(username)
            if not user:
                logger.warning(f"❌ Пользователь '{username}' не найден")
                return None

            if not user.get('is_active', False):
                logger.warning(f"❌ Пользователь '{username}' заблокирован")
                return None

            # Проверяем блокировку
            locked_until = user.get('locked_until')
            if locked_until and locked_until > datetime.datetime.now():
                logger.warning(f"❌ Пользователь '{username}' временно заблокирован до {locked_until}")
                return None

            # Проверяем пароль
            if check_password(password, user['password']):
                self._update_login_success(username)
                logger.success(f"✅ Пользователь '{username}' успешно авторизован")
                return user
            else:
                self._update_login_failure(username)
                logger.warning(f"❌ Неверный пароль для пользователя '{username}'")
                return None

        except Exception as e:
            logger.error(f"❌ Ошибка аутентификации пользователя '{username}': {e}")
            return None

    def update_user(self, username: str, update_data: Dict[str, Any]) -> bool:
        """Обновляет данные пользователя"""
        try:
            collection = self.get_collection()
            if collection is None:
                return False

            update_data['modified_at'] = datetime.datetime.now()

            result = collection.update_one(
                {'username': username, 'deleted': {'$ne': True}},
                {'$set': update_data}
            )

            if result.modified_count > 0:
                logger.success(f"✅ Данные пользователя '{username}' обновлены")
                return True
            return False

        except Exception as e:
            logger.error(f"❌ Ошибка обновления пользователя '{username}': {e}")
            return False

    def delete_user(self, username: str, soft_delete: bool = True) -> bool:
        """Удаляет пользователя"""
        try:
            collection = self.get_collection()
            if collection is None:
                return False

            if soft_delete:
                result = collection.update_one(
                    {'username': username, 'deleted': {'$ne': True}},
                    {
                        '$set': {
                            'deleted': True,
                            'modified_at': datetime.datetime.now(),
                            'is_active': False
                        }
                    }
                )
                success = result.modified_count > 0
                action = "помечен как удаленный"
            else:
                result = collection.delete_one({'username': username})
                success = result.deleted_count > 0
                action = "удален"

            if success:
                logger.success(f"✅ Пользователь '{username}' {action}")
                return True
            return False

        except Exception as e:
            logger.error(f"❌ Ошибка удаления пользователя '{username}': {e}")
            return False

    def list_users(self, include_deleted: bool = False,
                   admin_only: bool = False,
                   active_only: bool = True) -> List[Dict[str, Any]]:
        """Получает список пользователей с фильтрацией"""
        try:
            collection = self.get_collection()
            if collection is None:
                return []

            # Формируем фильтр
            query = {}
            if not include_deleted:
                query['deleted'] = {'$ne': True}
            if admin_only:
                query['is_admin'] = True
            if active_only:
                query['is_active'] = True

            users = list(collection.find(
                query,
                {'password': 0}  # Исключаем пароль
            ).sort('username', 1))

            logger.debug(f"📊 Найдено пользователей: {len(users)}")
            return users

        except Exception as e:
            logger.error(f"❌ Ошибка получения списка пользователей: {e}")
            return []

    def _update_login_success(self, username: str):
        """Обновляет данные успешного входа"""
        try:
            collection = self.get_collection()
            if collection is not None:
                collection.update_one(
                    {'username': username},
                    {
                        '$set': {
                            'last_login': datetime.datetime.now(),
                            'failed_login_attempts': 0,
                            'locked_until': None
                        }
                    }
                )
        except Exception as e:
            logger.error(f"❌ Ошибка обновления данных входа для '{username}': {e}")

    def _update_login_failure(self, username: str):
        """Обновляет данные неудачного входа"""
        try:
            collection = self.get_collection()
            if collection is not None:
                result = collection.update_one(
                    {'username': username},
                    {'$inc': {'failed_login_attempts': 1}}
                )

                if result.modified_count > 0:
                    user = collection.find_one({'username': username})
                    if user and user.get('failed_login_attempts', 0) >= 5:
                        locked_until = datetime.datetime.now() + datetime.timedelta(minutes=15)
                        collection.update_one(
                            {'username': username},
                            {'$set': {'locked_until': locked_until}}
                        )
                        logger.warning(f"⚠️  Пользователь '{username}' заблокирован до {locked_until}")

        except Exception as e:
            logger.error(f"❌ Ошибка обновления данных неудачного входа для '{username}': {e}")

    def get_admin_count(self) -> int:
        """Возвращает количество администраторов с диагностикой"""
        try:
            logger.debug("📊 Подсчет администраторов...")

            collection = self.get_collection()
            if collection is None:
                logger.error("❌ Коллекция недоступна для подсчета")
                return 0

            # Подсчитываем активных администраторов
            admin_query = {
                'is_admin': True,
                'deleted': {'$ne': True},
                'is_active': True
            }

            count = collection.count_documents(admin_query)
            logger.info(f"📊 Найдено активных администраторов: {count}")

            # Дополнительная диагностика
            total_count = collection.count_documents({})
            admin_all_count = collection.count_documents({'is_admin': True})
            active_count = collection.count_documents({'is_active': True, 'deleted': {'$ne': True}})

            logger.debug(f"📈 Статистика: всего={total_count}, админов_всего={admin_all_count}, активных={active_count}")

            return count

        except Exception as e:
            logger.error(f"❌ Ошибка подсчета администраторов: {e}")
            return 0

    def get_collection_stats(self) -> Dict[str, int]:
        """Возвращает статистику коллекции"""
        try:
            collection = self.get_collection()
            if collection is None:
                return {}

            stats = {
                'total_users': collection.count_documents({}),
                'active_users': collection.count_documents({'is_active': True, 'deleted': {'$ne': True}}),
                'admin_users': collection.count_documents({'is_admin': True, 'deleted': {'$ne': True}, 'is_active': True}),
                'deleted_users': collection.count_documents({'deleted': True}),
                'locked_users': collection.count_documents({'locked_until': {'$gt': datetime.datetime.now()}})
            }

            logger.info(f"📊 Статистика коллекции: {stats}")
            return stats

        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return {}

    def reset_failed_attempts(self, username: str) -> bool:
        """Сбрасывает неудачные попытки входа"""
        try:
            collection = self.get_collection()
            if not collection:
                return False

            result = collection.update_one(
                {'username': username},
                {
                    '$set': {
                        'failed_login_attempts': 0,
                        'locked_until': None
                    }
                }
            )

            if result.modified_count > 0:
                logger.success(f"✅ Неудачные попытки для '{username}' сброшены")
                return True
            return False

        except Exception as e:
            logger.error(f"❌ Ошибка сброса неудачных попыток для '{username}': {e}")
            return False

    def change_password(self, username: str, new_password: str) -> bool:
        """Изменяет пароль пользователя"""
        try:
            collection = self.get_collection()
            if not collection:
                return False

            hashed_password = make_password(new_password)
            result = collection.update_one(
                {'username': username, 'deleted': {'$ne': True}},
                {
                    '$set': {
                        'password': hashed_password,
                        'password_changed_at': datetime.datetime.now(),
                        'modified_at': datetime.datetime.now()
                    }
                }
            )

            if result.modified_count > 0:
                logger.success(f"✅ Пароль для '{username}' изменен")
                return True
            return False

        except Exception as e:
            logger.error(f"❌ Ошибка изменения пароля для '{username}': {e}")
            return False
