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
    """Загружает страны из MongoDB"""
    try:
        logger.info("Загружаем countries из MongoDB")
        db = MongoConnection.get_database()
        if db is None:
            return get_default_country_choices()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            return get_default_country_choices()

        countries_collection_name = f"{db_name}_countries"
        collections = db.list_collection_names()
        if countries_collection_name not in collections:
            return get_default_country_choices()

        countries_collection = db[countries_collection_name]
        countries_cursor = countries_collection.find(
            {'deleted': {'$ne': True}, 'active': {'$ne': False}},
            {'code': 1, 'name': 1, 'display_order': 1}
        ).sort('display_order', 1)

        choices = [('', '-- Land auswählen --')]
        count = 0

        for country_doc in countries_cursor:
            code = country_doc.get('code', '').strip()
            name = country_doc.get('name', code).strip()

            if code:
                choices.append((code, name))
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