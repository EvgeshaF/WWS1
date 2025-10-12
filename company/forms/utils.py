# company/forms/utils.py - ОБНОВЛЕНО: добавлена загрузка правовых форм из MongoDB

from loguru import logger
from mongodb.mongodb_utils import MongoConnection
from mongodb.mongodb_config import MongoConfig


def get_salutations_from_mongodb():
    """Загружает салютации (Anrede) из MongoDB коллекции basic_salutations"""
    try:
        logger.info("Загружаем salutations из MongoDB для компании")
        db = MongoConnection.get_database()
        if db is None:
            logger.error("База данных недоступна")
            return get_default_salutation_choices()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не найдено в конфигурации")
            return get_default_salutation_choices()

        salutations_collection_name = f"{db_name}_basic_salutations"
        collections = db.list_collection_names()
        if salutations_collection_name not in collections:
            logger.warning(f"Коллекция '{salutations_collection_name}' не найдена")
            return get_default_salutation_choices()

        salutations_collection = db[salutations_collection_name]

        salutations_cursor = salutations_collection.find(
            {'deleted': {'$ne': True}},
            {'salutation': 1}
        ).sort('salutation', 1)

        choices = [('', '-- Auswählen --')]
        count = 0
        seen_salutations = set()

        for salutation_doc in salutations_cursor:
            salutation_value = salutation_doc.get('salutation', '').strip()

            if salutation_value and salutation_value not in seen_salutations:
                code = salutation_value.lower()
                display_name = salutation_value

                choices.append((code, display_name))
                seen_salutations.add(salutation_value)
                count += 1

        logger.success(f"Успешно загружено {count} salutations из коллекции")
        return choices

    except Exception as e:
        logger.error(f"Ошибка загрузки salutations из MongoDB: {e}")
        return get_default_salutation_choices()


def get_default_salutation_choices():
    """Возвращает статичный список салютаций как fallback"""
    return [
        ('', '-- Auswählen --'),
        ('herr', 'Herr'),
        ('frau', 'Frau'),
        ('divers', 'Divers'),
    ]


def get_titles_from_mongodb():
    """Загружает titles из MongoDB коллекции"""
    try:
        logger.info("Загружаем titles из MongoDB для компании")
        db = MongoConnection.get_database()
        if db is None:
            logger.error("База данных недоступна")
            return get_default_title_choices()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не найдено в конфигурации")
            return get_default_title_choices()

        titles_collection_name = f"{db_name}_basic_titles"
        collections = db.list_collection_names()
        if titles_collection_name not in collections:
            logger.warning(f"Коллекция '{titles_collection_name}' не найдена")
            return get_default_title_choices()

        titles_collection = db[titles_collection_name]
        titles_cursor = titles_collection.find(
            {'deleted': {'$ne': True}, 'active': {'$ne': False}},
            {'code': 1, 'name': 1, 'display_order': 1}
        ).sort('display_order', 1)

        choices = [('', '-- Kein Titel --')]
        count = 0

        for title_doc in titles_cursor:
            code = title_doc.get('code', '').strip()
            name = title_doc.get('name', code).strip()

            if code:
                choices.append((code, name))
                count += 1

        logger.success(f"Успешно загружено {count} titles из коллекции")
        return choices

    except Exception as e:
        logger.error(f"Ошибка загрузки titles из MongoDB: {e}")
        return get_default_title_choices()


def get_default_title_choices():
    """Возвращает статичный список титулов как fallback"""
    return [
        ('', '-- Kein Titel --'),
        ('dr', 'Dr.'),
        ('prof', 'Prof.'),
        ('prof_dr', 'Prof. Dr.'),
        ('dipl_ing', 'Dipl.-Ing.'),
        ('dipl_kfm', 'Dipl.-Kfm.'),
        ('dipl_oec', 'Dipl.-Oec.'),
        ('mag', 'Mag.'),
        ('mba', 'MBA'),
        ('msc', 'M.Sc.'),
        ('ma', 'M.A.'),
        ('ba', 'B.A.'),
        ('bsc', 'B.Sc.'),
        ('beng', 'B.Eng.'),
    ]


# НОВОЕ: Функция для загрузки правовых форм из MongoDB
def get_legal_forms_from_mongodb():
    """Загружает правовые формы (Rechtsform) из MongoDB коллекции basic_legal_forms"""
    try:
        logger.info("Загружаем legal forms из MongoDB")
        db = MongoConnection.get_database()
        if db is None:
            logger.error("База данных недоступна")
            return get_default_legal_form_choices()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не найдено в конфигурации")
            return get_default_legal_form_choices()

        legal_forms_collection_name = f"{db_name}_basic_legal_forms"
        collections = db.list_collection_names()
        if legal_forms_collection_name not in collections:
            logger.warning(f"Коллекция '{legal_forms_collection_name}' не найдена")
            return get_default_legal_form_choices()

        legal_forms_collection = db[legal_forms_collection_name]
        legal_forms_cursor = legal_forms_collection.find(
            {'deleted': {'$ne': True}, 'active': {'$ne': False}},
            {'code': 1, 'name': 1, 'display_order': 1}
        ).sort('display_order', 1)

        choices = [('', '-- Rechtsform auswählen --')]
        count = 0

        for legal_form_doc in legal_forms_cursor:
            code = legal_form_doc.get('code', '').strip()
            name = legal_form_doc.get('name', code).strip()

            if code:
                choices.append((code, name))
                count += 1

        logger.success(f"Успешно загружено {count} legal forms из коллекции")
        return choices

    except Exception as e:
        logger.error(f"Ошибка загрузки legal forms из MongoDB: {e}")
        return get_default_legal_form_choices()


def get_default_legal_form_choices():
    """Возвращает статичный список правовых форм как fallback"""
    return [
        ('', '-- Rechtsform auswählen --'),
        ('gmbh', 'GmbH'),
        ('ag', 'AG'),
        ('ug', 'UG (haftungsbeschränkt)'),
        ('ohg', 'OHG'),
        ('kg', 'KG'),
        ('gbr', 'GbR'),
        ('eg', 'eG'),
        ('einzelunternehmen', 'Einzelunternehmen'),
        ('freiberufler', 'Freiberufler'),
        ('se', 'SE (Societas Europaea)'),
        ('ltd', 'Ltd.'),
        ('sonstige', 'Sonstige'),
    ]


def get_countries_from_mongodb():
    """Загружает страны из MongoDB коллекции basic_countrys"""
    try:
        logger.info("Загружаем countries из MongoDB")
        db = MongoConnection.get_database()
        if db is None:
            logger.error("База данных недоступна")
            return get_default_country_choices()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не найдено в конфигурации")
            return get_default_country_choices()

        # ИСПРАВЛЕНО: используем basic_countrys вместо countries
        countries_collection_name = f"{db_name}_basic_countrys"
        collections = db.list_collection_names()
        if countries_collection_name not in collections:
            logger.warning(f"Коллекция '{countries_collection_name}' не найдена")
            return get_default_country_choices()

        countries_collection = db[countries_collection_name]

        # ИСПРАВЛЕНО: используем поле 'country' вместо code/name/display_order
        countries_cursor = countries_collection.find(
            {'deleted': {'$ne': True}},  # Фильтруем по deleted
            {'country': 1}  # Выбираем только поле country
        ).sort('country', 1)  # Сортируем по алфавиту

        choices = [('', '-- Land auswählen --')]
        count = 0
        seen_countries = set()

        for country_doc in countries_cursor:
            country_value = country_doc.get('country', '').strip()

            # Проверяем что страна не пустая и не дублируется
            if country_value and country_value not in seen_countries:
                # Используем название страны и как код, и как отображаемое имя
                choices.append((country_value, country_value))
                seen_countries.add(country_value)
                count += 1

        logger.success(f"Успешно загружено {count} countries из коллекции")
        return choices

    except Exception as e:
        logger.error(f"Ошибка загрузки countries из MongoDB: {e}")
        return get_default_country_choices()


def get_default_country_choices():
    """Возвращает статичный список стран как fallback"""
    return [
        ('', '-- Land auswählen --'),
        ('deutschland', 'Deutschland'),
        ('oesterreich', 'Österreich'),
        ('schweiz', 'Schweiz'),
        ('niederlande', 'Niederlande'),
        ('belgien', 'Belgien'),
        ('frankreich', 'Frankreich'),
        ('italien', 'Italien'),
        ('spanien', 'Spanien'),
        ('portugal', 'Portugal'),
        ('polen', 'Polen'),
        ('tschechien', 'Tschechien'),
        ('ungarn', 'Ungarn'),
        ('daenemark', 'Dänemark'),
        ('schweden', 'Schweden'),
        ('norwegen', 'Norwegen'),
        ('sonstige', 'Sonstige'),
    ]


def get_industries_from_mongodb():
    """Загружает отрасли из MongoDB"""
    try:
        logger.info("Загружаем industries из MongoDB")
        db = MongoConnection.get_database()
        if db is None:
            return get_default_industry_choices()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            return get_default_industry_choices()

        industries_collection_name = f"{db_name}_industries"
        collections = db.list_collection_names()
        if industries_collection_name not in collections:
            return get_default_industry_choices()

        industries_collection = db[industries_collection_name]
        industries_cursor = industries_collection.find(
            {'deleted': {'$ne': True}, 'active': {'$ne': False}},
            {'code': 1, 'name': 1, 'display_order': 1}
        ).sort('display_order', 1)

        choices = [('', '-- Branche auswählen --')]
        count = 0

        for industry_doc in industries_cursor:
            code = industry_doc.get('code', '').strip()
            name = industry_doc.get('name', code).strip()

            if code:
                choices.append((code, name))
                count += 1

        logger.success(f"Успешно загружено {count} industries из коллекции")
        return choices

    except Exception as e:
        logger.error(f"Ошибка загрузки industries из MongoDB: {e}")
        return get_default_industry_choices()


def get_default_industry_choices():
    """Возвращает статичный список отраслей как fallback"""
    return [
        ('', '-- Branche auswählen --'),
        ('handel', 'Handel'),
        ('dienstleistung', 'Dienstleistung'),
        ('produktion', 'Produktion'),
        ('it_software', 'IT/Software'),
        ('beratung', 'Beratung'),
        ('finanzwesen', 'Finanzwesen'),
        ('gesundheitswesen', 'Gesundheitswesen'),
        ('bildung', 'Bildung'),
        ('tourismus', 'Tourismus'),
        ('transport_logistik', 'Transport/Logistik'),
        ('bau', 'Bau'),
        ('immobilien', 'Immobilien'),
        ('energie', 'Energie'),
        ('medien', 'Medien'),
        ('gastronomie', 'Gastronomie'),
        ('einzelhandel', 'Einzelhandel'),
        ('grosshandel', 'Großhandel'),
        ('landwirtschaft', 'Landwirtschaft'),
        ('rechtswesen', 'Rechtswesen'),
        ('sonstige', 'Sonstige'),
    ]


# company/forms/utils.py - ДОБАВИТЬ функцию get_communication_config_from_mongodb

def get_communication_config_from_mongodb():
    """Получает полную конфигурацию коммуникаций из MongoDB"""
    try:
        logger.info("Загружаем конфигурацию коммуникаций из MongoDB")
        db = MongoConnection.get_database()
        if db is None:
            return get_default_communication_config()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            return get_default_communication_config()

        comm_types_collection_name = f"{db_name}_basic_communication_types"
        collections = db.list_collection_names()

        if comm_types_collection_name not in collections:
            logger.warning(f"Коллекция '{comm_types_collection_name}' не найдена")
            return get_default_communication_config()

        comm_types_collection = db[comm_types_collection_name]

        # Получаем полную конфигурацию для каждого типа
        types_cursor = comm_types_collection.find(
            {'deleted': {'$ne': True}, 'active': {'$ne': False}},
            {
                'code': 1, 'label': 1, 'icon_class': 1,
                'validation_pattern': 1, 'placeholder': 1, 'hint': 1
            }
        )

        config_dict = {}
        for type_doc in types_cursor:
            code = type_doc.get('code', '').strip()
            if code:
                config_dict[code] = {
                    'label': type_doc.get('label', code),
                    'icon_class': type_doc.get('icon_class', 'bi-question-circle'),
                    'validation_pattern': type_doc.get('validation_pattern', '.{3,}'),
                    'placeholder': type_doc.get('placeholder', 'Kontaktdaten eingeben...'),
                    'hint': type_doc.get('hint', 'Geben Sie die entsprechenden Kontaktdaten ein')
                }

        if config_dict:
            logger.success(f"Загружена конфигурация для {len(config_dict)} типов коммуникации")
            return config_dict
        else:
            return get_default_communication_config()

    except Exception as e:
        logger.error(f"Ошибка загрузки конфигурации коммуникаций: {e}")
        return get_default_communication_config()


def get_default_communication_config():
    """Возвращает статичную конфигурацию коммуникаций как fallback"""
    return {
        'email': {
            'label': 'E-Mail',
            'icon_class': 'bi-envelope',
            'validation_pattern': r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
            'placeholder': 'info@firma.de',
            'hint': 'Geben Sie eine gültige E-Mail-Adresse ein'
        },
        'mobile': {
            'label': 'Mobil',
            'icon_class': 'bi-phone',
            'validation_pattern': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
            'placeholder': '+49 170 1234567',
            'hint': 'Geben Sie eine Mobilnummer ein'
        },
        'fax': {
            'label': 'Fax',
            'icon_class': 'bi-printer',
            'validation_pattern': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
            'placeholder': '+49 123 456789',
            'hint': 'Geben Sie eine Faxnummer ein'
        },
        'website': {
            'label': 'Website',
            'icon_class': 'bi-globe',
            'validation_pattern': r'^https?:\/\/.+\..+$',
            'placeholder': 'https://www.firma.de',
            'hint': 'Geben Sie eine Website-URL ein'
        },
        'linkedin': {
            'label': 'LinkedIn',
            'icon_class': 'bi-linkedin',
            'validation_pattern': r'^(https?:\/\/)?(www\.)?linkedin\.com\/(company|in)\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$',
            'placeholder': 'linkedin.com/company/firma',
            'hint': 'Geben Sie das LinkedIn-Unternehmensprofil ein'
        },
        'xing': {
            'label': 'XING',
            'icon_class': 'bi-person-badge',
            'validation_pattern': r'^(https?:\/\/)?(www\.)?xing\.com\/(companies|profile)\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$',
            'placeholder': 'xing.com/companies/firma',
            'hint': 'Geben Sie das XING-Unternehmensprofil ein'
        },
        'emergency': {
            'label': 'Notfall',
            'icon_class': 'bi-exclamation-triangle',
            'validation_pattern': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
            'placeholder': '+49 170 1234567',
            'hint': 'Geben Sie einen Notfallkontakt ein'
        },
        'other': {
            'label': 'Sonstige',
            'icon_class': 'bi-question-circle',
            'validation_pattern': r'.{3,}',
            'placeholder': 'Kontaktdaten eingeben...',
            'hint': 'Geben Sie die entsprechenden Kontaktdaten ein'
        }
    }


# ДОБАВИТЬ экспорт в конец файла
def get_communication_types_from_mongodb():
    """Получает типы коммуникаций из MongoDB (для Django choices)"""
    try:
        logger.info("Загружаем типы коммуникаций из MongoDB для Django choices")
        db = MongoConnection.get_database()
        if db is None:
            return get_default_communication_type_choices()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            return get_default_communication_type_choices()

        comm_types_collection_name = f"{db_name}_basic_communication_types"
        collections = db.list_collection_names()

        if comm_types_collection_name not in collections:
            return get_default_communication_type_choices()

        comm_types_collection = db[comm_types_collection_name]

        # Получаем активные типы коммуникации
        types_cursor = comm_types_collection.find(
            {'deleted': {'$ne': True}, 'active': {'$ne': False}},
            {'code': 1, 'label': 1, 'display_order': 1}
        ).sort('display_order', 1)

        choices = [('', '-- Auswählen --')]
        count = 0

        for type_doc in types_cursor:
            code = type_doc.get('code', '').strip()
            label = type_doc.get('label', code).strip()

            if code:
                choices.append((code, label))
                count += 1

        logger.success(f"Загружено {count} типов коммуникаций из MongoDB")
        return choices

    except Exception as e:
        logger.error(f"Ошибка загрузки типов коммуникаций: {e}")
        return get_default_communication_type_choices()


def get_default_communication_type_choices():
    """Возвращает статичный список типов коммуникаций как fallback"""
    return [
        ('', '-- Auswählen --'),
        ('email', 'E-Mail'),
        ('mobile', 'Mobil'),
        ('fax', 'Fax'),
        ('website', 'Website'),
        ('linkedin', 'LinkedIn'),
        ('xing', 'XING'),
        ('emergency', 'Notfall'),
        ('other', 'Sonstige')
    ]