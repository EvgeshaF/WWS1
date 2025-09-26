# company/company_crud_views.py - ОБНОВЛЕНО: добавлены функции редактирования отдельных шагов

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


def get_account_type_display(code):
    """НОВОЕ: Возвращает человекочитаемое название типа счета"""
    if not code:
        return ''

    account_types = {
        'geschaeft': 'Geschäftskonto',
        'haupt': 'Hauptkonto',
        'liquiditaet': 'Liquiditätskonto',
        'kredit': 'Kreditkonto',
        'tagesgeld': 'Tagesgeldkonto',
        'sonstige': 'Sonstige',
    }
    return account_types.get(code, code)


def enrich_company_data(company):
    """Обогащает данные компании человекочитаемыми названиями - ОБНОВЛЕНО с банковскими данными"""
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

    # НОВОЕ: Обогащение банковских данных
    if company.get('account_type'):
        enriched['account_type_display'] = get_account_type_display(company['account_type'])

    # Форматируем IBAN для отображения (с пробелами)
    if company.get('iban'):
        iban = company['iban'].replace(' ', '').upper()
        if len(iban) >= 4:
            formatted_iban = ' '.join([iban[i:i + 4] for i in range(0, len(iban), 4)])
            enriched['iban_formatted'] = formatted_iban
        else:
            enriched['iban_formatted'] = iban

    if company.get('secondary_iban'):
        iban = company['secondary_iban'].replace(' ', '').upper()
        if len(iban) >= 4:
            formatted_iban = ' '.join([iban[i:i + 4] for i in range(0, len(iban), 4)])
            enriched['secondary_iban_formatted'] = formatted_iban
        else:
            enriched['secondary_iban_formatted'] = iban

    return enriched


def company_info(request):
    """Показывает информацию о компании с человекочитаемыми названиями - ОБНОВЛЕНО с банковскими данными"""
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

    # НОВОЕ: Проверяем наличие банковских данных
    has_banking_data = any([
        company.get('bank_name'),
        company.get('iban'),
        company.get('bic'),
        company.get('secondary_bank_name'),
        company.get('secondary_iban')
    ])

    context = {
        'company': company,
        'additional_contacts': additional_contacts,
        'stats': stats,
        'has_banking_data': has_banking_data  # НОВОЕ
    }
    return render(request, 'company_info.html', context)


def edit_company(request):
    """Редактирование всей компании - все шаги сразу (старый способ)"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Keine Firma zum Bearbeiten gefunden")
        return redirect('company:register_company_step1')

    # Загружаем все данные компании в сессию
    _load_all_company_data_to_session(request, company)

    messages.info(request, f"Vollständige Bearbeitung der Firma '{company.get('company_name', 'Unbekannt')}' gestartet")
    logger.info(f"Полное редактирование компании '{company.get('company_name')}' - все данные загружены в сессию")

    return redirect('company:register_company_step1')


# ==================== НОВЫЕ ФУНКЦИИ: Редактирование отдельных шагов ====================

def edit_company_step1(request):
    """НОВОЕ: Редактирование только Grunddaten (шаг 1)"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Keine Firma zum Bearbeiten gefunden")
        return redirect('company:register_company_step1')

    # Очищаем сессию и загружаем только данные шага 1
    CompanySessionManager.clear_session_data(request)

    session_data = {
        # Только данные шага 1
        'company_name': company.get('company_name', ''),
        'legal_form': company.get('legal_form', ''),
        'ceo_salutation': company.get('ceo_salutation', ''),
        'ceo_title': company.get('ceo_title', ''),
        'ceo_first_name': company.get('ceo_first_name', ''),
        'ceo_last_name': company.get('ceo_last_name', ''),

        # Загружаем ВСЕ остальные данные, чтобы они не потерялись при сохранении
        **_get_all_company_data_except_step1(company)
    }

    CompanySessionManager.set_session_data(request, session_data)

    messages.info(request, f"Bearbeitung der Grunddaten für '{company.get('company_name', 'Unbekannt')}'")
    logger.info(f"Редактирование шага 1 (Grunddaten) для компании '{company.get('company_name')}'")

    return redirect('company:register_company_step1')


def edit_company_step2(request):
    """НОВОЕ: Редактирование только Registrierungsdaten (шаг 2)"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Keine Firma zum Bearbeiten gefunden")
        return redirect('company:register_company_step1')

    # Очищаем сессию и загружаем данные для шага 2
    CompanySessionManager.clear_session_data(request)

    session_data = {
        # Данные шага 1 (чтобы пройти валидацию)
        'company_name': company.get('company_name', ''),
        'legal_form': company.get('legal_form', ''),
        'ceo_salutation': company.get('ceo_salutation', ''),
        'ceo_title': company.get('ceo_title', ''),
        'ceo_first_name': company.get('ceo_first_name', ''),
        'ceo_last_name': company.get('ceo_last_name', ''),

        # Данные шага 2 (редактируемые)
        'commercial_register': company.get('commercial_register', ''),
        'tax_number': company.get('tax_number', ''),
        'vat_id': company.get('vat_id', ''),
        'tax_id': company.get('tax_id', ''),
        'registration_data_processed': True,
        'all_registration_fields_complete': True,

        # Все остальные данные
        **_get_all_company_data_except_steps(company, [1, 2])
    }

    CompanySessionManager.set_session_data(request, session_data)

    messages.info(request, f"Bearbeitung der Registrierungsdaten für '{company.get('company_name', 'Unbekannt')}'")
    logger.info(f"Редактирование шага 2 (Registrierungsdaten) для компании '{company.get('company_name')}'")

    return redirect('company:register_company_step2')


def edit_company_step3(request):
    """НОВОЕ: Редактирование только Adressdaten (шаг 3)"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Keine Firma zum Bearbeiten gefunden")
        return redirect('company:register_company_step1')

    # Очищаем сессию и загружаем данные для шага 3
    CompanySessionManager.clear_session_data(request)

    session_data = {
        # Данные предыдущих шагов (для прохождения валидации)
        **_get_steps_1_and_2_data(company),

        # Данные шага 3 (редактируемые)
        'street': company.get('street', ''),
        'postal_code': company.get('postal_code', ''),
        'city': company.get('city', ''),
        'country': company.get('country', ''),
        'address_addition': company.get('address_addition', ''),
        'po_box': company.get('po_box', ''),

        # Все остальные данные
        **_get_all_company_data_except_steps(company, [1, 2, 3])
    }

    CompanySessionManager.set_session_data(request, session_data)

    messages.info(request, f"Bearbeitung der Adressdaten für '{company.get('company_name', 'Unbekannt')}'")
    logger.info(f"Редактирование шага 3 (Adressdaten) для компании '{company.get('company_name')}'")

    return redirect('company:register_company_step3')


def edit_company_step4(request):
    """НОВОЕ: Редактирование только Kontaktdaten (шаг 4)"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Keine Firma zum Bearbeiten gefunden")
        return redirect('company:register_company_step1')

    # Очищаем сессию и загружаем данные для шага 4
    CompanySessionManager.clear_session_data(request)

    session_data = {
        # Данные предыдущих шагов
        **_get_steps_1_2_3_data(company),

        # Данные шага 4 (редактируемые)
        'email': company.get('email', ''),
        'phone': company.get('phone', ''),
        'fax': company.get('fax', ''),
        'website': company.get('website', ''),
        'additional_contacts_data': company.get('additional_contacts_data', '[]'),

        # Остальные данные (шаг 5)
        **_get_step_5_data(company)
    }

    CompanySessionManager.set_session_data(request, session_data)

    messages.info(request, f"Bearbeitung der Kontaktdaten für '{company.get('company_name', 'Unbekannt')}'")
    logger.info(f"Редактирование шага 4 (Kontaktdaten) для компании '{company.get('company_name')}'")

    return redirect('company:register_company_step4')


def edit_company_step5(request):
    """НОВОЕ: Редактирование только Bankdaten (шаг 5)"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Keine Firma zum Bearbeiten gefunden")
        return redirect('company:register_company_step1')

    # Очищаем сессию и загружаем данные для шага 5
    CompanySessionManager.clear_session_data(request)

    session_data = {
        # Данные всех предыдущих шагов
        **_get_steps_1_2_3_4_data(company),

        # Данные шага 5 (редактируемые)
        **_get_step_5_data(company)
    }

    CompanySessionManager.set_session_data(request, session_data)

    messages.info(request, f"Bearbeitung der Bankdaten für '{company.get('company_name', 'Unbekannt')}'")
    logger.info(f"Редактирование шага 5 (Bankdaten) для компании '{company.get('company_name')}'")

    return redirect('company:register_company_step5')


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def _load_all_company_data_to_session(request, company):
    """Загружает все данные компании в сессию (для полного редактирования)"""
    CompanySessionManager.clear_session_data(request)

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

    # Банковские данные (шаг 5)
    session_data.update(_get_step_5_data(company))

    # Стандартные настройки
    session_data.update({
        'is_primary': company.get('is_primary', True),
        'enable_notifications': company.get('enable_notifications', True),
        'enable_marketing': company.get('enable_marketing', False),
        'data_protection_consent': True
    })

    CompanySessionManager.set_session_data(request, session_data)


def _get_steps_1_and_2_data(company):
    """Возвращает данные шагов 1 и 2"""
    return {
        'company_name': company.get('company_name', ''),
        'legal_form': company.get('legal_form', ''),
        'ceo_salutation': company.get('ceo_salutation', ''),
        'ceo_title': company.get('ceo_title', ''),
        'ceo_first_name': company.get('ceo_first_name', ''),
        'ceo_last_name': company.get('ceo_last_name', ''),
        'commercial_register': company.get('commercial_register', ''),
        'tax_number': company.get('tax_number', ''),
        'vat_id': company.get('vat_id', ''),
        'tax_id': company.get('tax_id', ''),
        'registration_data_processed': True,
        'all_registration_fields_complete': True,
    }


def _get_steps_1_2_3_data(company):
    """Возвращает данные шагов 1, 2 и 3"""
    return {
        **_get_steps_1_and_2_data(company),
        'street': company.get('street', ''),
        'postal_code': company.get('postal_code', ''),
        'city': company.get('city', ''),
        'country': company.get('country', ''),
        'address_addition': company.get('address_addition', ''),
        'po_box': company.get('po_box', ''),
    }


def _get_steps_1_2_3_4_data(company):
    """Возвращает данные шагов 1, 2, 3 и 4"""
    return {
        **_get_steps_1_2_3_data(company),
        'email': company.get('email', ''),
        'phone': company.get('phone', ''),
        'fax': company.get('fax', ''),
        'website': company.get('website', ''),
        'additional_contacts_data': company.get('additional_contacts_data', '[]'),
    }


def _get_step_5_data(company):
    """Возвращает данные шага 5 (банковские данные)"""
    return {
        'bank_name': company.get('bank_name', ''),
        'iban': company.get('iban', ''),
        'bic': company.get('bic', ''),
        'account_holder': company.get('account_holder', ''),
        'bank_address': company.get('bank_address', ''),
        'account_type': company.get('account_type', ''),
        'secondary_bank_name': company.get('secondary_bank_name', ''),
        'secondary_iban': company.get('secondary_iban', ''),
        'secondary_bic': company.get('secondary_bic', ''),
        'is_primary_account': company.get('is_primary_account', True),
        'enable_sepa': company.get('enable_sepa', False),
        'banking_notes': company.get('banking_notes', ''),
        'is_primary': company.get('is_primary', True),
        'enable_notifications': company.get('enable_notifications', True),
        'enable_marketing': company.get('enable_marketing', False),
        'data_protection_consent': True
    }


def _get_all_company_data_except_step1(company):
    """Возвращает все данные компании кроме шага 1"""
    return {
        **_get_steps_1_and_2_data(company),
        **_get_steps_1_2_3_data(company),
        **_get_steps_1_2_3_4_data(company),
        **_get_step_5_data(company)
    }


def _get_all_company_data_except_steps(company, exclude_steps):
    """Возвращает все данные компании кроме указанных шагов"""
    data = {}

    if 1 not in exclude_steps:
        data.update({
            'company_name': company.get('company_name', ''),
            'legal_form': company.get('legal_form', ''),
            'ceo_salutation': company.get('ceo_salutation', ''),
            'ceo_title': company.get('ceo_title', ''),
            'ceo_first_name': company.get('ceo_first_name', ''),
            'ceo_last_name': company.get('ceo_last_name', ''),
        })

    if 2 not in exclude_steps:
        data.update({
            'commercial_register': company.get('commercial_register', ''),
            'tax_number': company.get('tax_number', ''),
            'vat_id': company.get('vat_id', ''),
            'tax_id': company.get('tax_id', ''),
            'registration_data_processed': True,
            'all_registration_fields_complete': True,
        })

    if 3 not in exclude_steps:
        data.update({
            'street': company.get('street', ''),
            'postal_code': company.get('postal_code', ''),
            'city': company.get('city', ''),
            'country': company.get('country', ''),
            'address_addition': company.get('address_addition', ''),
            'po_box': company.get('po_box', ''),
        })

    if 4 not in exclude_steps:
        data.update({
            'email': company.get('email', ''),
            'phone': company.get('phone', ''),
            'fax': company.get('fax', ''),
            'website': company.get('website', ''),
            'additional_contacts_data': company.get('additional_contacts_data', '[]'),
        })

    if 5 not in exclude_steps:
        data.update(_get_step_5_data(company))

    return data


# ==================== ОСТАЛЬНЫЕ ФУНКЦИИ (без изменений) ====================

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