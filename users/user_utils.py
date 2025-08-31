import datetime
from typing import Optional, Dict, Any, List
from loguru import logger
from django.contrib.auth.hashers import make_password, check_password
from mongodb.mongodb_config import MongoConfig
from mongodb.mongodb_utils import MongoConnection


class UserManager:
    """Менеджер для работы с пользователями в MongoDB"""

    def __init__(self):
        self.db = MongoConnection.get_database()
        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не найдено в конфигурации")
            self.users_collection_name = None
        else:
            self.users_collection_name = f"{db_name}_users"

    def get_collection(self):
        """Получает коллекцию пользователей"""
        if not self.db:
            logger.error("База данных недоступна")
            return None

        if not self.users_collection_name:
            logger.error("Имя коллекции пользователей не определено")
            return None

        try:
            collection = self.db[self.users_collection_name]

            # Проверяем, существует ли коллекция
            if self.users_collection_name not in self.db.list_collection_names():
                logger.warning(f"Коллекция '{self.users_collection_name}' не существует. Создаем...")
                self.db.create_collection(self.users_collection_name)

            return collection
        except Exception as e:
            logger.error(f"Ошибка получения коллекции '{self.users_collection_name}': {e}")
            return None

    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """
        Создает нового пользователя

        Args:
            user_data: Словарь с данными пользователя

        Returns:
            bool: True если пользователь создан успешно
        """
        try:
            collection = self.get_collection()
            if not collection:
                logger.error("Коллекция пользователей недоступна")
                return False

            # Проверяем обязательные поля
            required_fields = ['username']
            for field in required_fields:
                if not user_data.get(field):
                    logger.error(f"Обязательное поле '{field}' отсутствует")
                    return False

            # Проверяем, что пользователь с таким именем не существует
            existing_user = collection.find_one({
                'username': user_data['username'],
                'deleted': False
            })

            if existing_user:
                logger.error(f"Пользователь '{user_data['username']}' уже существует")
                return False

            # Добавляем системные поля
            now = datetime.datetime.now()
            user_data.update({
                'created_at': now,
                'modified_at': now,
                'deleted': False,
                'last_login': None,
                'failed_login_attempts': 0,
                'locked_until': None,
                'password_changed_at': now
            })

            # Логируем данные перед вставкой (без пароля)
            log_data = {k: v for k, v in user_data.items() if k != 'password'}
            logger.info(f"Создание пользователя: {log_data}")

            result = collection.insert_one(user_data)

            if result.inserted_id:
                logger.success(f"Пользователь '{user_data.get('username')}' создан с ID: {result.inserted_id}")

                # Проверяем, что пользователь действительно создан
                verification = collection.find_one({'_id': result.inserted_id})
                if verification:
                    logger.success("Создание пользователя подтверждено")
                    return True
                else:
                    logger.error("Пользователь не найден после создания")
                    return False
            else:
                logger.error("Не удалось получить ID созданного пользователя")
                return False

        except Exception as e:
            logger.exception(f"Ошибка создания пользователя: {e}")
            return False

    def find_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Находит пользователя по имени

        Args:
            username: Имя пользователя

        Returns:
            Dict с данными пользователя или None
        """
        try:
            collection = self.get_collection()
            if not collection:
                logger.warning("Коллекция пользователей недоступна")
                return None

            user = collection.find_one({
                'username': username,
                'deleted': False
            })

            if user:
                logger.debug(f"Пользователь '{username}' найден")
            else:
                logger.debug(f"Пользователь '{username}' не найден")

            return user

        except Exception as e:
            logger.error(f"Ошибка поиска пользователя '{username}': {e}")
            return None

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Находит пользователя по email

        Args:
            email: Email пользователя

        Returns:
            Dict с данными пользователя или None
        """
        try:
            collection = self.get_collection()
            if not collection:
                return None

            user = collection.find_one({
                'profile.email': email,
                'deleted': False
            })
            return user

        except Exception as e:
            logger.error(f"Ошибка поиска пользователя по email '{email}': {e}")
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Аутентифицирует пользователя

        Args:
            username: Имя пользователя
            password: Пароль (незашифрованный)

        Returns:
            Dict с данными пользователя или None
        """
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
                # Обновляем последний вход и сбрасываем счетчик неудачных попыток
                self._update_login_success(username)
                logger.success(f"Пользователь '{username}' успешно авторизован")
                return user
            else:
                # Увеличиваем счетчик неудачных попыток
                self._update_login_failure(username)
                logger.warning(f"Неверный пароль для пользователя '{username}'")
                return None

        except Exception as e:
            logger.error(f"Ошибка аутентификации пользователя '{username}': {e}")
            return None

    def update_user(self, username: str, update_data: Dict[str, Any]) -> bool:
        """
        Обновляет данные пользователя

        Args:
            username: Имя пользователя
            update_data: Данные для обновления

        Returns:
            bool: True если обновление успешно
        """
        try:
            collection = self.get_collection()
            if not collection:
                return False

            update_data['modified_at'] = datetime.datetime.now()

            result = collection.update_one(
                {'username': username, 'deleted': False},
                {'$set': update_data}
            )

            if result.modified_count > 0:
                logger.success(f"Данные пользователя '{username}' обновлены")
                return True
            return False

        except Exception as e:
            logger.error(f"Ошибка обновления пользователя '{username}': {e}")
            return False

    def delete_user(self, username: str, soft_delete: bool = True) -> bool:
        """
        Удаляет пользователя (мягкое или жесткое удаление)

        Args:
            username: Имя пользователя
            soft_delete: True для мягкого удаления (установка флага deleted)

        Returns:
            bool: True если удаление успешно
        """
        try:
            collection = self.get_collection()
            if not collection:
                return False

            if soft_delete:
                result = collection.update_one(
                    {'username': username, 'deleted': False},
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
                logger.success(f"Пользователь '{username}' {action}")
                return True
            return False

        except Exception as e:
            logger.error(f"Ошибка удаления пользователя '{username}': {e}")
            return False

    def list_users(self, include_deleted: bool = False,
                   admin_only: bool = False,
                   active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Получает список пользователей с фильтрацией

        Args:
            include_deleted: Включить удаленных пользователей
            admin_only: Только администраторы
            active_only: Только активные пользователи

        Returns:
            List: Список пользователей
        """
        try:
            collection = self.get_collection()
            if not collection:
                return []

            # Формируем фильтр
            query = {}
            if not include_deleted:
                query['deleted'] = False
            if admin_only:
                query['is_admin'] = True
            if active_only:
                query['is_active'] = True

            users = list(collection.find(
                query,
                {'password': 0}  # Исключаем пароль из результата
            ).sort('username', 1))

            return users

        except Exception as e:
            logger.error(f"Ошибка получения списка пользователей: {e}")
            return []

    def _update_login_success(self, username: str):
        """Обновляет данные успешного входа"""
        try:
            collection = self.get_collection()
            if collection:
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
            logger.error(f"Ошибка обновления данных входа для '{username}': {e}")

    def _update_login_failure(self, username: str):
        """Обновляет данные неудачного входа"""
        try:
            collection = self.get_collection()
            if collection:
                # Увеличиваем счетчик
                result = collection.update_one(
                    {'username': username},
                    {'$inc': {'failed_login_attempts': 1}}
                )

                # Проверяем, нужно ли блокировать пользователя
                if result.modified_count > 0:
                    user = collection.find_one({'username': username})
                    if user and user.get('failed_login_attempts', 0) >= 5:
                        # Блокируем на 15 минут после 5 неудачных попыток
                        locked_until = datetime.datetime.now() + datetime.timedelta(minutes=15)
                        collection.update_one(
                            {'username': username},
                            {'$set': {'locked_until': locked_until}}
                        )
                        logger.warning(f"Пользователь '{username}' заблокирован до {locked_until}")

        except Exception as e:
            logger.error(f"Ошибка обновления данных неудачного входа для '{username}': {e}")

    def get_admin_count(self) -> int:
        """Возвращает количество администраторов"""
        try:
            collection = self.get_collection()
            if not collection:
                logger.error("Коллекция недоступна для подсчета администраторов")
                return 0

            count = collection.count_documents({
                'is_admin': True,
                'deleted': False,
                'is_active': True
            })

            logger.info(f"Найдено администраторов: {count}")
            return count

        except Exception as e:
            logger.error(f"Ошибка подсчета администраторов: {e}")
            return 0

    def debug_collection_info(self):
        """Отладочная информация о коллекции"""
        try:
            if not self.db:
                logger.error("База данных недоступна")
                return

            logger.info(f"Имя коллекции: {self.users_collection_name}")

            # Список всех коллекций
            collections = self.db.list_collection_names()
            logger.info(f"Доступные коллекции: {collections}")

            # Проверяем существование коллекции пользователей
            if self.users_collection_name in collections:
                collection = self.db[self.users_collection_name]
                count = collection.count_documents({})
                logger.info(f"Коллекция '{self.users_collection_name}' содержит {count} документов")

                # Показываем один документ как пример структуры
                sample = collection.find_one({})
                if sample:
                    # Убираем пароль из вывода
                    if 'password' in sample:
                        sample['password'] = '***скрыто***'
                    logger.info(f"Пример документа: {sample}")
            else:
                logger.warning(f"Коллекция '{self.users_collection_name}' не найдена")

        except Exception as e:
            logger.error(f"Ошибка получения отладочной информации: {e}")