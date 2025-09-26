# company/forms.py - НОВЫЙ ФАЙЛ: формы для регистрации компании

from django import forms
from django.core.validators import RegexValidator
import re
from mongodb.mongodb_utils import MongoConnection
from mongodb.mongodb_config import MongoConfig
from loguru import logger


def get_salutations_from_mongodb():
    """Загружает салютации (Anrede) из MongoDB коллекции basic_salutations"""
    try:
        logger.info("Загружаем salutations из MongoDB (for company)")
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

        logger.success(f"Успешно загружено {count} salutations для компании")
        return choices

    except Exception as e:
        logger.error(f"Ошибка загрузки salutations из MongoDB (company): {e}")
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
        logger.info("Загружаем titles из MongoDB (for company)")
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

        logger.success(f"Успешно загружено {count} titles для компании")
        return choices

    except Exception as e:
        logger.error(f"Ошибка загрузки titles из MongoDB (company): {e}")
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
        ('ba', 'B.A.'),
        ('bsc', 'B.Sc.'),
        ('beng', 'B.Eng.'),
    ]


def get_communication_types_from_mongodb():
    """Загружает типы коммуникации из MongoDB коллекции basic_communications"""
    try:
        logger.info("Загружаем типы коммуникации из MongoDB (for company)")
        db = MongoConnection.get_database()
        if db is None:
            logger.error("База данных недоступна")
            return get_default_contact_type_choices()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не найдено в конфигурации")
            return get_default_contact_type_choices()

        communications_collection_name = f"{db_name}_basic_communications"
        collections = db.list_collection_names()
        if communications_collection_name not in collections:
            logger.warning(f"Коллекция '{communications_collection_name}' не найдена")
            return get_default_contact_type_choices()

        communications_collection = db[communications_collection_name]
        communications_cursor = communications_collection.find(
            {'deleted': {'$ne': True}, 'active': {'$ne': False}},
            {
                'type': 1, 'icon': 1, 'required_format': 1, 'display_order': 1,
                'validation_pattern': 1, 'placeholder': 1, 'hint_de': 1
            }
        ).sort('display_order', 1)

        choices = [('', '-- Kontakttyp auswählen --')]
        count = 0

        # Мапинг иконок Bootstrap Icons для компании
        icon_mapping = {
            'envelope': '📧',
            'phone': '📞',
            'mobile': '📱',
            'printer': '📠',
            'globe': '🌐',
            'linkedin': '💼',
            'person-badge': '🔗',
            'exclamation-triangle': '🚨',
            'question-circle': '📝'
        }

        for comm_doc in communications_cursor:
            comm_type = comm_doc.get('type', '').strip()
            icon = comm_doc.get('icon', 'question-circle')
            required_format = comm_doc.get('required_format', '').lower()

            if comm_type:
                # Используем required_format как ключ (например, email, mobile, fax)
                # Если required_format пустой, используем type в нижнем регистре
                key = required_format if required_format else comm_type.lower().replace('-', '_')

                # Добавляем эмодзи к тексту
                emoji = icon_mapping.get(icon, '📝')

                # АДАПТАЦИЯ для компании: разные тексты
                if key == 'email':
                    display_text = f"{emoji} {comm_type} (Abteilung)"
                elif key == 'phone':
                    display_text = f"{emoji} Telefon (Abteilung)"
                elif key == 'mobile':
                    display_text = f"{emoji} Mobil"
                elif key == 'emergency':
                    display_text = f"{emoji} Notfallkontakt"
                else:
                    display_text = f"{emoji} {comm_type}"

                choices.append((key, display_text))
                count += 1

                logger.debug(f"Добавлен тип коммуникации для компании: {key} -> {display_text}")

        logger.success(f"Успешно загружено {count} типов коммуникации для компании из коллекции")
        return choices

    except Exception as e:
        logger.error(f"Ошибка загрузки типов коммуникации из MongoDB (company): {e}")
        return get_default_contact_type_choices()


def get_default_contact_type_choices():
    """Возвращает статичный список типов контактов как fallback для компании"""
    return [
        ('', '-- Kontakttyp auswählen --'),
        ('email', '📧 E-Mail (Abteilung)'),
        ('phone', '📞 Telefon (Abteilung)'),
        ('mobile', '📱 Mobil'),
        ('fax', '📠 Fax'),
        ('website', '🌐 Website'),
        ('linkedin', '💼 LinkedIn (Unternehmen)'),
        ('xing', '🔗 XING (Unternehmen)'),
        ('emergency', '🚨 Notfallkontakt'),
        ('other', '📝 Sonstige'),
    ]


def get_communication_config_from_mongodb():
    """Загружает полную конфигурацию типов коммуникации для JavaScript (компания)"""
    try:
        logger.info("Загружаем конфигурацию коммуникации для JavaScript (company)")
        db = MongoConnection.get_database()
        if db is None:
            return get_default_communication_config()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            return get_default_communication_config()

        communications_collection_name = f"{db_name}_basic_communications"
        collections = db.list_collection_names()
        if communications_collection_name not in collections:
            return get_default_communication_config()

        communications_collection = db[communications_collection_name]
        communications_cursor = communications_collection.find(
            {'deleted': {'$ne': True}, 'active': {'$ne': False}},
            {
                'type': 1, 'icon': 1, 'required_format': 1, 'display_order': 1,
                'validation_pattern': 1, 'placeholder': 1, 'hint_de': 1
            }
        ).sort('display_order', 1)

        config_dict = {}

        for comm_doc in communications_cursor:
            comm_type = comm_doc.get('type', '').strip()
            icon = comm_doc.get('icon', 'question-circle')
            required_format = comm_doc.get('required_format', '').lower()
            validation_pattern = comm_doc.get('validation_pattern', '')
            placeholder = comm_doc.get('placeholder', '')
            hint_de = comm_doc.get('hint_de', '')

            if comm_type:
                # Используем required_format как ключ
                key = required_format if required_format else comm_type.lower().replace('-', '_')

                # Мапинг иконок для Bootstrap Icons класса
                icon_class_mapping = {
                    'envelope': 'bi-envelope',
                    'phone': 'bi-telephone',
                    'mobile': 'bi-phone',
                    'printer': 'bi-printer',
                    'globe': 'bi-globe',
                    'linkedin': 'bi-linkedin',
                    'person-badge': 'bi-person-badge',
                    'exclamation-triangle': 'bi-exclamation-triangle',
                    'question-circle': 'bi-question-circle'
                }

                # АДАПТАЦИЯ для компании: компанийские подсказки и плейсхолдеры
                company_placeholders = {
                    'email': 'vertrieb@firma.de',
                    'phone': '+49 123 456789',
                    'mobile': '+49 170 1234567',
                    'fax': '+49 123 456789',
                    'website': 'https://www.firma.de',
                    'linkedin': 'linkedin.com/company/firmenname',
                    'xing': 'xing.com/companies/firmenname',
                    'emergency': '+49 170 1234567'
                }

                company_hints = {
                    'email': 'Geben Sie eine E-Mail-Adresse ein (z.B. vertrieb@firma.de)',
                    'phone': 'Geben Sie eine Telefonnummer ein (z.B. +49 123 456789)',
                    'mobile': 'Geben Sie eine Mobilnummer ein (z.B. +49 170 1234567)',
                    'fax': 'Geben Sie eine Faxnummer ein (z.B. +49 123 456789)',
                    'website': 'Geben Sie eine Website-URL ein (z.B. https://www.firma.de)',
                    'linkedin': 'Geben Sie das LinkedIn-Unternehmensprofil ein',
                    'xing': 'Geben Sie das XING-Unternehmensprofil ein',
                    'emergency': 'Geben Sie einen Notfallkontakt ein',
                    'other': 'Geben Sie die entsprechenden Kontaktdaten ein'
                }

                config_dict[key] = {
                    'label': comm_type,
                    'icon_class': icon_class_mapping.get(icon, 'bi-question-circle'),
                    'validation_pattern': validation_pattern,
                    'placeholder': company_placeholders.get(key, placeholder or f"{comm_type} eingeben..."),
                    'hint': company_hints.get(key, hint_de or f"Geben Sie {comm_type} ein")
                }

        logger.success(f"Конфигурация для компании загружена для {len(config_dict)} типов коммуникации")
        return config_dict

    except Exception as e:
        logger.error(f"Ошибка загрузки конфигурации коммуникации для компании: {e}")
        return get_default_communication_config()


def get_default_communication_config():
    """Возвращает статичную конфигурацию типов коммуникации как fallback для компании"""
    return {
        'email': {
            'label': 'E-Mail',
            'icon_class': 'bi-envelope',
            'validation_pattern': '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$',
            'placeholder': 'vertrieb@firma.de',
            'hint': 'Geben Sie eine E-Mail-Adresse ein (z.B. vertrieb@firma.de)'
        },
        'phone': {
            'label': 'Telefon',
            'icon_class': 'bi-telephone',
            'validation_pattern': '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$',
            'placeholder': '+49 123 456789',
            'hint': 'Geben Sie eine Telefonnummer ein'
        },
        'mobile': {
            'label': 'Mobil',
            'icon_class': 'bi-phone',
            'validation_pattern': '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$',
            'placeholder': '+49 170 1234567',
            'hint': 'Geben Sie eine Mobilnummer ein'
        },
        'fax': {
            'label': 'Fax',
            'icon_class': 'bi-printer',
            'validation_pattern': '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$',
            'placeholder': '+49 123 456789',
            'hint': 'Geben Sie eine Faxnummer ein'
        },
        'website': {
            'label': 'Website',
            'icon_class': 'bi-globe',
            'validation_pattern': '^https?:\\/\\/.+\\..+$|^www\\..+\\..+$',
            'placeholder': 'https://www.firma.de',
            'hint': 'Geben Sie eine Website-URL ein'
        },
        'linkedin': {
            'label': 'LinkedIn',
            'icon_class': 'bi-linkedin',
            'validation_pattern': '^(https?:\\/\\/)?(www\\.)?linkedin\\.com\\/company\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$',
            'placeholder': 'linkedin.com/company/firmenname',
            'hint': 'Geben Sie das LinkedIn-Unternehmensprofil ein'
        },
        'xing': {
            'label': 'XING',
            'icon_class': 'bi-person-badge',
            'validation_pattern': '^(https?:\\/\\/)?(www\\.)?xing\\.com\\/companies\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$',
            'placeholder': 'xing.com/companies/firmenname',
            'hint': 'Geben Sie das XING-Unternehmensprofil ein'
        },
        'emergency': {
            'label': 'Notfall',
            'icon_class': 'bi-exclamation-triangle',
            'validation_pattern': '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$',
            'placeholder': '+49 170 1234567',
            'hint': 'Geben Sie einen Notfallkontakt ein'
        },
        'other': {
            'label': 'Sonstige',
            'icon_class': 'bi-question-circle',
            'validation_pattern': '.{3,}',
            'placeholder': 'Kontaktdaten eingeben...',
            'hint': 'Geben Sie die entsprechenden Kontaktdaten ein'
        }
    }


# Функция для удобного доступа к choices (для компании)
def get_contact_type_choices():
    """Получает типы контактов из MongoDB или возвращает fallback (для компании)"""
    return get_communication_types_from_mongodb()


def get_countries_from_mongodb():
    """Загружает страны из MongoDB коллекции"""
    try:
        logger.info("Загружаем страны из MongoDB")
        db = MongoConnection.get_database()
        if db is None:
            logger.error("База данных недоступна")
            return get_default_country_choices()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не найдено в конфигурации")
            return get_default_country_choices()

        countries_collection_name = f"{db_name}_countries"
        collections = db.list_collection_names()
        if countries_collection_name not in collections:
            logger.warning(f"Коллекция '{countries_collection_name}' не найдена")
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

        logger.success(f"Успешно загружено {count} стран из коллекции")
        return choices

    except Exception as e:
        logger.error(f"Ошибка загрузки стран из MongoDB: {e}")
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
    """Загружает отрасли из MongoDB коллекции"""
    try:
        logger.info("Загружаем отрасли из MongoDB")
        db = MongoConnection.get_database()
        if db is None:
            logger.error("База данных недоступна")
            return get_default_industry_choices()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не найдено в конфигурации")
            return get_default_industry_choices()

        industries_collection_name = f"{db_name}_industries"
        collections = db.list_collection_names()
        if industries_collection_name not in collections:
            logger.warning(f"Коллекция '{industries_collection_name}' не найдена")
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

        logger.success(f"Успешно загружено {count} отраслей из коллекции")
        return choices

    except Exception as e:
        logger.error(f"Ошибка загрузки отраслей из MongoDB: {e}")
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
        ('grosshandel', 'Grosshandel'),
        ('landwirtschaft', 'Landwirtschaft'),
        ('rechtswesen', 'Rechtswesen'),
        ('sonstige', 'Sonstige'),
    ]


# ==================== ФОРМЫ ====================

class CompanyBasicDataForm(forms.Form):
    """Шаг 1: Основные данные компании + Geschäftsführer"""

    LEGAL_FORM_CHOICES = [
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

    # Основные идентификационные данные
    company_name = forms.CharField(
        label="Firmenname",
        max_length=100,
        min_length=2,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-ZäöüÄÖÜß0-9\s\.\-&,]+$',
                message='Firmenname darf nur Buchstaben, Zahlen und gängige Sonderzeichen enthalten'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vollständiger Firmenname eingeben',
            'autofocus': True
        })
    )

    legal_form = forms.ChoiceField(
        label="Rechtsform",
        choices=LEGAL_FORM_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    # БЛОК GESCHÄFTSFÜHRER
    ceo_salutation = forms.ChoiceField(
        label="Anrede",
        choices=[],  # Заполняется динамически из MongoDB
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    ceo_title = forms.ChoiceField(
        label="Titel",
        choices=[],  # Заполняется динамически из MongoDB
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    ceo_first_name = forms.CharField(
        label="Vorname",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vorname eingeben'
        })
    )

    ceo_last_name = forms.CharField(
        label="Nachname",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nachname eingeben'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Динамически загружаем salutations из MongoDB
        salutation_choices = get_salutations_from_mongodb()
        self.fields['ceo_salutation'].choices = salutation_choices
        logger.info(f"Загружено {len(salutation_choices)} вариантов CEO salutation")

        # Динамически загружаем titles из MongoDB
        title_choices = get_titles_from_mongodb()
        self.fields['ceo_title'].choices = title_choices
        logger.info(f"Загружено {len(title_choices)} вариантов CEO title")


class CompanyRegistrationForm(forms.Form):
    """Шаг 2: Регистрационные данные - ВСЕ ПОЛЯ ОБЯЗАТЕЛЬНЫ"""

    commercial_register = forms.CharField(
        label="Handelsregister",
        max_length=50,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^(HR[AB]\s*\d+|HRA\s*\d+|HRB\s*\d+)$',
                message='Format: HRA12345 oder HRB12345'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. HRB12345'
        }),
        error_messages={
            'required': 'Handelsregister ist erforderlich'
        }
    )

    tax_number = forms.CharField(
        label="Steuernummer",
        max_length=20,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d{1,3}/\d{3}/\d{4,5}$',
                message="Geben Sie eine gültige Steuernummer ein (Format: 12/345/67890)."
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12/345/67890'
        }),
        error_messages={
            'required': 'Steuernummer ist erforderlich'
        }
    )

    vat_id = forms.CharField(
        label="USt-IdNr.",
        max_length=15,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^DE\d{9}$',
                message='Format: DE123456789'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DE123456789'
        }),
        error_messages={
            'required': 'USt-IdNr. ist erforderlich'
        }
    )

    tax_id = forms.CharField(
        label="Steuer-ID",
        max_length=11,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='11-stellige Steuer-ID erforderlich'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678901'
        }),
        error_messages={
            'required': 'Steuer-ID ist erforderlich'
        }
    )


class CompanyAddressForm(forms.Form):
    """Шаг 3: Адресные данные"""

    street = forms.CharField(
        label="Straße und Hausnummer",
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-ZäöüÄÖÜß0-9\s\.\-,]+$',
                message='Straße darf nur Buchstaben, Zahlen und gängige Zeichen enthalten'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Musterstraße 123'
        })
    )

    postal_code = forms.CharField(
        label="PLZ",
        max_length=5,
        min_length=5,
        validators=[
            RegexValidator(
                regex=r'^\d{5}$',
                message='PLZ muss 5 Ziffern haben'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345'
        })
    )

    city = forms.CharField(
        label="Stadt",
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-ZäöüÄÖÜß\s\-]+$',
                message='Stadt darf nur Buchstaben, Leerzeichen und Bindestriche enthalten'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Musterstadt'
        })
    )

    country = forms.ChoiceField(
        label="Land",
        choices=[],  # Заполняется динамически
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    address_addition = forms.CharField(
        label="Adresszusatz",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. 2. Stock, Gebäude A (optional)'
        })
    )

    po_box = forms.CharField(
        label="Postfach",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Postfach 123456 (optional)'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически загружаем страны из MongoDB
        country_choices = get_countries_from_mongodb()
        self.fields['country'].choices = country_choices


class CompanyContactForm(forms.Form):
    """Шаг 4: Контактные данные"""

    email = forms.EmailField(
        label="Haupt-E-Mail",
        max_length=100,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'kontakt@firma.de'
        })
    )

    phone = forms.CharField(
        label="Haupttelefon",
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[\+]?[0-9\s\-\(\)]{7,20}$',
                message='Ungültiges Telefonformat'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+49 123 456789'
        })
    )

    fax = forms.CharField(
        label="Fax",
        max_length=20,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[\+]?[0-9\s\-\(\)]{7,20}$',
                message='Ungültiges Faxformat'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+49 123 456789'
        })
    )

    website = forms.URLField(
        label="Website",
        max_length=200,
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.firma.de'
        })
    )


class CompanyBankingForm(forms.Form):
    """Шаг 5 - Банковские данные"""

    # Основной банковский счет
    bank_name = forms.CharField(
        label="Name der Bank",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Deutsche Bank AG'
        })
    )

    iban = forms.CharField(
        label="IBAN",
        max_length=34,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$',
                message='Ungültiges IBAN-Format (z.B. DE89370400440532013000)'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DE89370400440532013000',
            'style': 'text-transform: uppercase;'
        })
    )

    bic = forms.CharField(
        label="BIC/SWIFT",
        max_length=11,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$',
                message='Ungültiges BIC-Format (z.B. DEUTDEFF)'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DEUTDEFF',
            'style': 'text-transform: uppercase;'
        })
    )

    account_holder = forms.CharField(
        label="Kontoinhaber",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name des Kontoinhabers'
        })
    )

    # Zusätzliche Informationen
    bank_address = forms.CharField(
        label="Adresse der Bank",
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Straße, PLZ Stadt (optional)'
        })
    )

    account_type = forms.ChoiceField(
        label="Kontotyp",
        choices=[
            ('', '-- Auswählen --'),
            ('geschaeft', 'Geschäftskonto'),
            ('haupt', 'Hauptkonto'),
            ('liquiditaet', 'Liquiditätskonto'),
            ('kredit', 'Kreditkonto'),
            ('tagesgeld', 'Tagesgeldkonto'),
            ('sonstige', 'Sonstige'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    # Sekundäre Bankverbindung (falls vorhanden)
    secondary_bank_name = forms.CharField(
        label="Zweitbank (optional)",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Commerzbank AG'
        })
    )

    secondary_iban = forms.CharField(
        label="IBAN (Zweitbank)",
        max_length=34,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$',
                message='Ungültiges IBAN-Format'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DE89370400440532013001',
            'style': 'text-transform: uppercase;'
        })
    )

    secondary_bic = forms.CharField(
        label="BIC/SWIFT (Zweitbank)",
        max_length=11,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$',
                message='Ungültiges BIC-Format'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'COBADEFF',
            'style': 'text-transform: uppercase;'
        })
    )

    # Einstellungen
    is_primary_account = forms.BooleanField(
        label="Als Hauptkonto für Rechnungen verwenden",
        required=False,
        initial=True,
        help_text="Diese Bankverbindung wird standardmäßig auf Rechnungen angezeigt",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    enable_sepa = forms.BooleanField(
        label="SEPA-Lastschriftverfahren aktiviert",
        required=False,
        initial=False,
        help_text="Ermöglicht Lastschrifteinzug von Kunden",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    banking_notes = forms.CharField(
        label="Notizen zu Bankverbindungen",
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Zusätzliche Informationen zu den Bankverbindungen (optional)'
        })
    )

    def clean_iban(self):
        iban = self.cleaned_data.get('iban', '').replace(' ', '').upper()
        if iban and not self.validate_iban_checksum(iban):
            raise forms.ValidationError('IBAN-Prüfsumme ist ungültig')
        return iban

    def clean_secondary_iban(self):
        iban = self.cleaned_data.get('secondary_iban', '').replace(' ', '').upper()
        if iban and not self.validate_iban_checksum(iban):
            raise forms.ValidationError('IBAN-Prüfsumme ist ungültig')
        return iban

    def validate_iban_checksum(self, iban):
        """Einfache IBAN-Validierung (Mod-97-Prüfung)"""
        if len(iban) < 15:
            return False

        try:
            # Bewege die ersten 4 Zeichen ans Ende
            rearranged = iban[4:] + iban[:4]

            # Ersetze Buchstaben durch Zahlen (A=10, B=11, etc.)
            numeric = ''
            for char in rearranged:
                if char.isdigit():
                    numeric += char
                else:
                    numeric += str(ord(char) - ord('A') + 10)

            # Mod 97 Prüfung
            return int(numeric) % 97 == 1
        except:
            return False


# Дополнительная форма для модального окна дополнительных контактов
class AdditionalCompanyContactForm(forms.Form):
    """Форма для дополнительных контактов компании (используется в модальном окне)"""

    contact_type = forms.ChoiceField(
        label="Kontakttyp",
        choices=[],  # Заполняется динамически из MongoDB
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'contactType'
        })
    )

    contact_value = forms.CharField(
        label="Kontaktdaten",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kontaktdaten eingeben...',
            'id': 'contactValue'
        })
    )

    contact_department = forms.ChoiceField(
        label="Abteilung",
        choices=[
            ('', '-- Abteilung auswählen --'),
            ('management', 'Geschäftsführung'),
            ('sales', 'Vertrieb'),
            ('support', 'Kundensupport'),
            ('accounting', 'Buchhaltung'),
            ('hr', 'Personalabteilung'),
            ('it', 'IT-Abteilung'),
            ('marketing', 'Marketing'),
            ('production', 'Produktion'),
            ('logistics', 'Logistik'),
            ('purchasing', 'Einkauf'),
            ('quality', 'Qualitätsmanagement'),
            ('legal', 'Rechtsabteilung'),
            ('reception', 'Empfang/Zentrale'),
            ('other', 'Sonstige')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'contactLabel'
        })
    )

    contact_important = forms.BooleanField(
        label="Als wichtig markieren",
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'contactImportant'
        })
    )

    contact_public = forms.BooleanField(
        label="Öffentlich sichtbar",
        required=False,
        help_text="Kann auf der Webseite angezeigt werden",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'contactPublic'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Динамически загружаем типы контактов из MongoDB
        contact_type_choices = get_communication_types_from_mongodb()
        self.fields['contact_type'].choices = contact_type_choices