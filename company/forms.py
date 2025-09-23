# company/forms.py - Updated for 5-step process with CEO fields in step 1

from django import forms
from django.core.validators import RegexValidator
import re
from mongodb.mongodb_utils import MongoConnection
from mongodb.mongodb_config import MongoConfig
from loguru import logger


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

    # Основные идентификационные данные (убрали industry и description)
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

    # БЛОК GESCHÄFTSFÜHRER - поля CEO
    ceo_salutation = forms.ChoiceField(
        label="Anrede",
        choices=[
            ('', '-- Auswählen --'),
            ('herr', 'Herr'),
            ('frau', 'Frau'),
            ('divers', 'Divers'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    ceo_title = forms.CharField(
        label="Titel",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Dr., Prof. (optional)'
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


class CompanyRegistrationForm(forms.Form):
    """Шаг 2: Регистрационные данные"""

    commercial_register = forms.CharField(
        label="Handelsregister",
        max_length=50,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^(HR[AB]\s*\d+|HRA\s*\d+|HRB\s*\d+)$',
                message='Format: HRA12345 oder HRB12345'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. HRB12345'
        })
    )

    tax_number = forms.CharField(
        label="Steuernummer",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Steuernummer eingeben'
        })
    )

    vat_id = forms.CharField(
        label="USt-IdNr.",
        max_length=15,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^DE\d{9}$',
                message='Format: DE123456789'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DE123456789'
        })
    )

    tax_id = forms.CharField(
        label="Steuer-ID",
        max_length=11,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='11-stellige Steuer-ID'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678901'
        })
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


class CompanyOptionsForm(forms.Form):
    """Шаг 5: Финальные настройки (бывший шаг 6)"""

    is_primary = forms.BooleanField(
        label="Als Hauptfirma verwenden",
        required=False,
        initial=True,
        help_text="Diese Firma wird als Standard-Firma im System verwendet",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    enable_notifications = forms.BooleanField(
        label="E-Mail-Benachrichtigungen aktivieren",
        required=False,
        initial=True,
        help_text="Erhalten Sie wichtige Updates und Benachrichtigungen",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    enable_marketing = forms.BooleanField(
        label="Marketing-E-Mails erhalten",
        required=False,
        initial=False,
        help_text="Optional: Newsletter und Produktupdates erhalten",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    data_protection_consent = forms.BooleanField(
        label="Datenschutzerklärung akzeptieren",
        required=True,
        help_text="Ich stimme der Verarbeitung meiner Daten gemäß DSGVO zu",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        error_messages={
            'required': 'Die Datenschutzerklärung muss akzeptiert werden'
        }
    )

# Для обратной совместимости (legacy forms)
class CompanyRegistrationFormLegacy(forms.Form):
    """Legacy форма для совместимости со старым кодом"""
    pass