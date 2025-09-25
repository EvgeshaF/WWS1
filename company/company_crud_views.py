import datetime
import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from loguru import logger

from company.company_manager import CompanyManager
from company.company_session_views import CompanySessionManager
from company.company_utils import check_mongodb_availability
from mongodb.mongodb_utils import MongoConnection
from mongodb.mongodb_config import MongoConfig


def get_display_value_from_db(collection_name, code_field, code_value, name_field='name'):
    """Получает человекочитаемое значение из MongoDB коллекции"""
    try:
        db = MongoConnection.get_database()
        if db is not None:
            config = MongoConfig.read_config()
            db_name = config.get('db_name')
            if db_name:
                full_collection_name = f"{db_name}_{collection_name}"
                doc = db[full_collection_name].find_one({
                    code_field: code_value,
                    'deleted': {'$ne': True}
                })
                if doc:
                    return doc.get(name_field, code_value)
    except Exception as e:
        logger.warning(f"Ошибка получения значения из {collection_name}: {e}")
    return code_value


def get_legal_form_display(code):
    """Возвращает человекочитаемое название правовой формы"""
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
    return legal_forms.get(code, code) if code else ''


def get_industry_display(code):
    """Возвращает человекочитаемое название отрасли"""
    if not code:
        return ''

    # Сначала пытаемся из БД
    display_value = get_display_value_from_db('industries', 'code', code, 'name')
    if display_value != code:
        return display_value

    # Fallback
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
    return industries.get(code, code)


def get_title_display(code):
    """Возвращает человекочитаемое название титула"""
    if not code:
        return ''

    # Сначала пытаемся из БД
    display_value = get_display_value_from_db('basic_titles', 'code', code, 'name')
    if display_value != code:
        return display_value

    # Fallback
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
    return titles.get(code, code)


def get_salutation_display(code):
    """Возвращает человекочитаемое название приветствия"""
    if not code:
        return ''

    # Сначала пытаемся из БД
    display_value = get_display_value_from_db('basic_salutations', 'salutation', code.title(), 'salutation')
    if display_value != code.title():
        return display_value

    # Fallback
    salutations = {
        'herr': 'Herr',
        'frau': 'Frau',
        'divers': 'Divers',
    }
    return salutations.get(code.lower(), code.title())


def get_country_display(code):
    """Возвращает человекочитаемое название страны"""
    if not code:
        return ''

    # Сначала пытаемся из БД
    display_value = get_display_value_from_db('countries', 'code', code, 'name')
    if display_value != code:
        return display_value

    # Fallback
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
    return countries.get(code, code)


def enrich_company_data(company):
    """Обогащает данные компании человекочитаемыми названиями"""
    if not company:
        return company

    # Создаем копию для безопасности
    enriched = company.copy()

    # Добавляем display-версии полей
    if company.get('legal_form'):
        enriched['legal_form_display'] = get_legal_form_display(company['legal_form'])

    if company.get('industry'):
        enriched['industry_display'] = get_industry_display(company['industry'])

    if company.get('country'):
        enriched['country_display'] = get_country_display(company['country'])

    if company.get('ceo_title'):
        enriched['ceo_title_display'] = get_title_display(company['ceo_title'])

    if company.get('ceo_salutation'):
        enriched['ceo_salutation_display'] = get_salutation_display(company['ceo_salutation'])

    if company.get('contact_person_title'):
        enriched['contact_person_title_display'] = get_title_display(company['contact_person_title'])

    if company.get('contact_person_salutation'):
        enriched['contact_person_salutation_display'] = get_salutation_display(company['contact_person_salutation'])

    return enriched


def company_info(request):
    """Показывает информацию о компании с человекочитаемыми названиями"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Noch keine Firma registriert")
        return redirect('company:register_company_step1')

    # Обогащаем данные компании
    company = enrich_company_data(company)

    # Получаем статистику
    stats = company_manager.get_company_stats()

    # Обрабатываем дополнительные контакты для отображения
    additional_contacts = []
    contacts_data = company.get('additional_contacts_data', '[]')
    if isinstance(contacts_data, str):
        try:
            additional_contacts = json.loads(contacts_data)
        except json.JSONDecodeError:
            logger.warning("Некорректные данные дополнительных контактов в БД")
    elif isinstance(contacts_data, list):
        additional_contacts = contacts_data

    context = {
        'company': company,
        'additional_contacts': additional_contacts,
        'stats': stats
    }
    return render(request, 'company_info.html', context)


def edit_company(request):
    """Редактирование компании - перенаправляет на процесс регистрации с данными"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Keine Firma zum Bearbeiten gefunden")
        return redirect('company:register_company_step1')

    # Очищаем предыдущие данные сессии
    CompanySessionManager.clear_session_data(request)

    # Подготавливаем данные компании для сессии
    session_data = {}

    # Основные данные (шаг 1)
    session_data['company_name'] = company.get('company_name', '')
    session_data['legal_form'] = company.get('legal_form', '')
    session_data['ceo_salutation'] = company.get('ceo_salutation', '')
    session_data['ceo_title'] = company.get('ceo_title', '')
    session_data['ceo_first_name'] = company.get('ceo_first_name', '')
    session_data['ceo_last_name'] = company.get('ceo_last_name', '')

    # Регистрационные данные (шаг 2)
    session_data['commercial_register'] = company.get('commercial_register', '')
    session_data['tax_number'] = company.get('tax_number', '')
    session_data['vat_id'] = company.get('vat_id', '')
    session_data['tax_id'] = company.get('tax_id', '')
    session_data['registration_data_processed'] = True
    session_data['all_registration_fields_complete'] = True

    # Адресные данные (шаг 3)
    session_data['street'] = company.get('street', '')
    session_data['postal_code'] = company.get('postal_code', '')
    session_data['city'] = company.get('city', '')
    session_data['country'] = company.get('country', '')
    session_data['address_addition'] = company.get('address_addition', '')
    session_data['po_box'] = company.get('po_box', '')

    # Контактные данные (шаг 4)
    session_data['email'] = company.get('email', '')
    session_data['phone'] = company.get('phone', '')
    session_data['fax'] = company.get('fax', '')
    session_data['website'] = company.get('website', '')
    session_data['additional_contacts_data'] = company.get('additional_contacts_data', '[]')

    # Настройки (шаг 5)
    session_data['is_primary'] = company.get('is_primary', True)
    session_data['enable_notifications'] = company.get('enable_notifications', True)
    session_data['enable_marketing'] = company.get('enable_marketing', False)
    session_data['data_protection_consent'] = True  # Уже согласие было дано

    # Сохраняем в сессию
    CompanySessionManager.set_session_data(request, session_data)

    messages.info(request, f"Bearbeitung der Firma '{company.get('company_name', 'Unbekannt')}' gestartet")
    logger.info(f"Редактирование компании '{company.get('company_name')}' - данные загружены в сессию")

    return redirect('company:register_company_step1')


@require_http_methods(["POST"])
def delete_company(request):
    """Удаление компании"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Keine Firma zum Löschen gefunden")
        return redirect('home')

    company_name = company.get('company_name', 'Unbekannte Firma')

    try:
        if company_manager.delete_company():
            messages.success(request, f"Firma '{company_name}' wurde erfolgreich gelöscht")
            logger.info(f"Компания '{company_name}' удалена")
        else:
            messages.error(request, f"Fehler beim Löschen der Firma '{company_name}'")
            logger.error(f"Ошибка удаления компании '{company_name}'")
    except Exception as e:
        messages.error(request, f"Kritischer Fehler beim Löschen: {str(e)}")
        logger.error(f"Критическая ошибка удаления компании: {e}")

    return redirect('home')


def set_primary_company(request):
    """Устанавливает компанию как основную (заглушка для совместимости)"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Keine Firma gefunden")
        return redirect('home')

    # Поскольку у нас только одна компания, просто обновляем флаг is_primary
    try:
        updated_data = {'is_primary': True}
        if company_manager.create_or_update_company({**company, **updated_data}):
            messages.success(request, f"Firma '{company.get('company_name')}' als Hauptfirma gesetzt")
        else:
            messages.error(request, "Fehler beim Setzen als Hauptfirma")
    except Exception as e:
        messages.error(request, f"Fehler: {str(e)}")
        logger.error(f"Ошибка установки основной компании: {e}")

    return redirect('company:company_info')