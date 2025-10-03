from django import template
from mongodb.mongodb_utils import MongoConnection
from mongodb.mongodb_config import MongoConfig
from loguru import logger

register = template.Library()


@register.filter
def legal_form_display(legal_form_code):
    """Преобразует код правовой формы в человекочитаемое название"""
    logger.info(f"🏷️ Вызван legal_form_display для: '{legal_form_code}'")

    legal_forms = {
        'gmbh': 'GmbH',
        'ag': 'AG',
        'ug': 'UG (haftungsbeschränkt)',
        'ohg': 'OHG',
        'kg': 'KG',
        'gbr': 'GbR',
        'eg': 'eG',
        'einzelunternehmen': 'Einzelunternehmen',
        'freiberufler': 'Freiberufler',
        'se': 'SE (Societas Europaea)',
        'ltd': 'Ltd.',
        'sonstige': 'Sonstige'
    }

    if not legal_form_code:
        logger.info("🏷️ legal_form_code пустой, возвращаем пустую строку")
        return ''

    result = legal_forms.get(legal_form_code, legal_form_code)
    logger.info(f"🏷️ legal_form_display результат: '{legal_form_code}' -> '{result}'")
    return result


@register.filter
def title_display(title_code):
    """Преобразует код титула в человекочитаемое название из MongoDB или fallback"""
    if not title_code:
        return ''

    try:
        # Пытаемся получить из MongoDB
        db = MongoConnection.get_database()
        if db is not None:
            config = MongoConfig.read_config()
            db_name = config.get('db_name')
            if db_name:
                titles_collection_name = f"{db_name}_basic_titles"
                title_doc = db[titles_collection_name].find_one({
                    'code': title_code,
                    'deleted': {'$ne': True}
                })
                if title_doc:
                    return title_doc.get('name', title_code)
    except Exception as e:
        logger.warning(f"Ошибка получения титула из БД: {e}")

    # Fallback статический словарь
    titles = {
        'dr': 'Dr.',
        'prof': 'Prof.',
        'prof_dr': 'Prof. Dr.',
        'dipl_ing': 'Dipl.-Ing.',
        'dipl_kfm': 'Dipl.-Kfm.',
        'dipl_oec': 'Dipl.-Oec.',
        'mag': 'Mag.',
        'mba': 'MBA',
        'msc': 'M.Sc.',
        'ma': 'M.A.',
        'ba': 'B.A.',
        'bsc': 'B.Sc.',
        'beng': 'B.Eng.',
    }

    return titles.get(title_code, title_code)


@register.filter
def salutation_display(salutation_code):
    """Преобразует код приветствия в человекочитаемое название"""
    if not salutation_code:
        return ''

    try:
        # Пытаемся получить из MongoDB
        db = MongoConnection.get_database()
        if db is not None:
            config = MongoConfig.read_config()
            db_name = config.get('db_name')
            if db_name:
                salutations_collection_name = f"{db_name}_basic_salutations"
                salutation_doc = db[salutations_collection_name].find_one({
                    'salutation': salutation_code.title(),  # В БД хранится с большой буквы
                    'deleted': {'$ne': True}
                })
                if salutation_doc:
                    return salutation_doc.get('salutation', salutation_code.title())
    except Exception as e:
        logger.warning(f"Ошибка получения приветствия из БД: {e}")

    # Fallback статический словарь
    salutations = {
        'herr': 'Herr',
        'frau': 'Frau',
        'divers': 'Divers',
    }

    return salutations.get(salutation_code.lower(), salutation_code.title())


@register.filter
def industry_display(industry_code):
    """Преобразует код отрасли в человекочитаемое название"""
    if not industry_code:
        return ''

    try:
        # Пытаемся получить из MongoDB
        db = MongoConnection.get_database()
        if db is not None:
            config = MongoConfig.read_config()
            db_name = config.get('db_name')
            if db_name:
                industries_collection_name = f"{db_name}_industries"
                industry_doc = db[industries_collection_name].find_one({
                    'code': industry_code,
                    'deleted': {'$ne': True}
                })
                if industry_doc:
                    return industry_doc.get('name', industry_code)
    except Exception as e:
        logger.warning(f"Ошибка получения отрасли из БД: {e}")

    # Fallback статический словарь
    industries = {
        'handel': 'Handel',
        'dienstleistung': 'Dienstleistung',
        'produktion': 'Produktion',
        'it_software': 'IT/Software',
        'beratung': 'Beratung',
        'finanzwesen': 'Finanzwesen',
        'gesundheitswesen': 'Gesundheitswesen',
        'bildung': 'Bildung',
        'tourismus': 'Tourismus',
        'transport_logistik': 'Transport/Logistik',
        'bau': 'Bau',
        'immobilien': 'Immobilien',
        'energie': 'Energie',
        'medien': 'Medien',
        'gastronomie': 'Gastronomie',
        'einzelhandel': 'Einzelhandel',
        'grosshandel': 'Grosshandel',
        'landwirtschaft': 'Landwirtschaft',
        'rechtswesen': 'Rechtswesen',
        'sonstige': 'Sonstige',
    }

    return industries.get(industry_code, industry_code)


@register.filter
def country_display(country_code):
    """Преобразует код страны в человекочитаемое название"""
    if not country_code:
        return ''

    try:
        # Пытаемся получить из MongoDB
        db = MongoConnection.get_database()
        if db is not None:
            config = MongoConfig.read_config()
            db_name = config.get('db_name')
            if db_name:
                countries_collection_name = f"{db_name}_countries"
                country_doc = db[countries_collection_name].find_one({
                    'code': country_code,
                    'deleted': {'$ne': True}
                })
                if country_doc:
                    return country_doc.get('name', country_code)
    except Exception as e:
        logger.warning(f"Ошибка получения страны из БД: {e}")

    # Fallback статический словарь
    countries = {
        'deutschland': 'Deutschland',
        'oesterreich': 'Österreich',
        'schweiz': 'Schweiz',
        'niederlande': 'Niederlande',
        'belgien': 'Belgien',
        'frankreich': 'Frankreich',
        'italien': 'Italien',
        'spanien': 'Spanien',
        'portugal': 'Portugal',
        'polen': 'Polen',
        'tschechien': 'Tschechien',
        'ungarn': 'Ungarn',
        'daenemark': 'Dänemark',
        'schweden': 'Schweden',
        'norwegen': 'Norwegen',
        'sonstige': 'Sonstige',
    }

    return countries.get(country_code, country_code)