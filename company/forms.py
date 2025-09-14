# company/forms.py - Enhanced Company Registration Form

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
    """Шаг 1: Основные данные компании"""

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

    industry = forms.ChoiceField(
        label="Branche",
        choices=[],  # Заполняется динамически
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    description = forms.CharField(
        label="Geschäftsbeschreibung",
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Kurze Beschreibung der Geschäftstätigkeit (optional)'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически загружаем отрасли из MongoDB
        industry_choices = get_industries_from_mongodb()
        self.fields['industry'].choices = industry_choices


class CompanyRegistrationForm(forms.Form):
    """Шаг 2: Регистрационные данные"""

    commercial_register = forms.CharField(
        label="Handelsregister",
        max_length=50,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^HR[AB][0-9]+$',
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
        max_length=50,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[0-9\/\s\-]{8,20}$',
                message='Ungültiges Format der Steuernummer'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. 123/456/78901'
        })
    )

    vat_id = forms.CharField(
        label="USt-IdNr.",
        max_length=15,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^DE[0-9]{9}$',
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
        max_length=15,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{11}$',
                message='Steuer-ID muss aus 11 Ziffern bestehen'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678901'
        })
    )

    def clean_vat_id(self):
        vat_id = self.cleaned_data.get('vat_id', '').strip().upper()
        if vat_id and not re.match(r'^DE[0-9]{9}$', vat_id):
            raise forms.ValidationError('USt-IdNr. muss im Format DE123456789 sein')
        return vat_id

    def clean_commercial_register(self):
        hr = self.cleaned_data.get('commercial_register', '').strip().upper()
        if hr and not re.match(r'^HR[AB][0-9]+$', hr):
            raise forms.ValidationError('Handelsregister muss im Format HRA12345 oder HRB12345 sein')
        return hr


class CompanyAddressForm(forms.Form):
    """Шаг 3: Адресные данные"""

    street = forms.CharField(
        label="Straße und Hausnummer",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Hauptstraße 123'
        })
    )

    postal_code = forms.CharField(
        label="PLZ",
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{5}$',
                message='PLZ muss aus 5 Ziffern bestehen'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345'
        })
    )

    city = forms.CharField(
        label="Stadt",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Stadt eingeben'
        })
    )

    country = forms.ChoiceField(
        label="Land",
        choices=[],  # Заполняется динамически
        initial='deutschland',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    # Дополнительные адресные поля
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
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Postfach 1234 (optional)'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически загружаем страны из MongoDB
        country_choices = get_countries_from_mongodb()
        self.fields['country'].choices = country_choices


class CompanyContactForm(forms.Form):
    """Шаг 4: Основные контактные данные (как у пользователя)"""

    # Основные контакты (обязательные)
    email = forms.EmailField(
        label="Haupt-E-Mail",
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'info@firma.de'
        })
    )

    phone = forms.CharField(
        label="Haupttelefon",
        max_length=50,
        required=True,
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

    # Дополнительные контакты (опциональные)
    fax = forms.CharField(
        label="Fax",
        max_length=50,
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
        max_length=100,
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.firma.de'
        })
    )


class CompanyManagementForm(forms.Form):
    """Шаг 5: Управление и персонал"""

    ceo_salutation = forms.ChoiceField(
        label="Anrede Geschäftsführer",
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
        label="Titel Geschäftsführer",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Dr., Prof. (optional)'
        })
    )

    ceo_first_name = forms.CharField(
        label="Vorname Geschäftsführer",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vorname eingeben'
        })
    )

    ceo_last_name = forms.CharField(
        label="Nachname Geschäftsführer",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nachname eingeben'
        })
    )

    contact_person_salutation = forms.ChoiceField(
        label="Anrede Ansprechpartner",
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

    contact_person_title = forms.CharField(
        label="Titel Ansprechpartner",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Dr., Prof. (optional)'
        })
    )

    contact_person_first_name = forms.CharField(
        label="Vorname Ansprechpartner",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vorname eingeben'
        })
    )

    contact_person_last_name = forms.CharField(
        label="Nachname Ansprechpartner",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nachname eingeben'
        })
    )

    contact_person_position = forms.CharField(
        label="Position Ansprechpartner",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Leiter Vertrieb, Sekretariat (optional)'
        })
    )

    employee_count = forms.ChoiceField(
        label="Mitarbeiteranzahl",
        choices=[
            ('', '-- Auswählen --'),
            ('1', '1 (Einzelunternehmer)'),
            ('2-5', '2-5 Mitarbeiter'),
            ('6-10', '6-10 Mitarbeiter'),
            ('11-20', '11-20 Mitarbeiter'),
            ('21-50', '21-50 Mitarbeiter'),
            ('51-100', '51-100 Mitarbeiter'),
            ('101-250', '101-250 Mitarbeiter'),
            ('251-500', '251-500 Mitarbeiter'),
            ('500+', 'Über 500 Mitarbeiter'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class CompanyOptionsForm(forms.Form):
    """Шаг 6: Дополнительные настройки"""

    is_primary = forms.BooleanField(
        label="Als Hauptfirma festlegen",
        required=False,
        initial=True,
        help_text="Diese Firma wird als primäre Firma im System verwendet",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    enable_notifications = forms.BooleanField(
        label="E-Mail-Benachrichtigungen aktivieren",
        required=False,
        initial=True,
        help_text="Benachrichtigungen über wichtige Systemereignisse",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    enable_marketing = forms.BooleanField(
        label="Marketing-E-Mails erlauben",
        required=False,
        initial=False,
        help_text="Informationen über neue Features und Updates",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    data_protection_consent = forms.BooleanField(
        label="Datenschutzerklärung akzeptieren",
        required=True,
        help_text="Ich stimme der Verarbeitung der Firmendaten gemäß Datenschutzerklärung zu",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean_data_protection_consent(self):
        consent = self.cleaned_data.get('data_protection_consent')
        if not consent:
            raise forms.ValidationError(
                'Die Zustimmung zur Datenschutzerklärung ist erforderlich'
            )
        return consent


# Объединенная форма для совместимости (упрощенная версия)
class CompanyRegistrationFormLegacy(forms.Form):
    """Объединенная форма для обратной совместимости"""

    # Базовые данные
    company_name = forms.CharField(
        label="Firmenname",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Firmenname eingeben'
        })
    )

    legal_form = forms.ChoiceField(
        label="Rechtsform",
        choices=CompanyBasicDataForm.LEGAL_FORM_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    # Регистрационные данные
    commercial_register = forms.CharField(
        label="Handelsregister",
        max_length=50,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^HR[AB][0-9]+$',
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
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Steuernummer'
        })
    )

    vat_id = forms.CharField(
        label="USt-IdNr.",
        max_length=15,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^DE[0-9]{9}$',
                message='Format: DE123456789'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DE123456789'
        })
    )

    # Адрес
    street = forms.CharField(
        label="Straße und Hausnummer",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Straße und Hausnummer'
        })
    )

    postal_code = forms.CharField(
        label="PLZ",
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{5}$',
                message='PLZ muss aus 5 Ziffern bestehen'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345'
        })
    )

    city = forms.CharField(
        label="Stadt",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Stadt'
        })
    )

    country = forms.ChoiceField(
        label="Land",
        choices=[],  # Заполняется динамически
        initial='deutschland',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    # Контактные данные
    email = forms.EmailField(
        label="E-Mail",
        max_length=100,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'firma@domain.com'
        })
    )

    phone = forms.CharField(
        label="Telefon",
        max_length=50,
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
        max_length=50,
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
        max_length=100,
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.firma.de'
        })
    )

    # Дополнительные данные
    ceo_name = forms.CharField(
        label="Geschäftsführer",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name des Geschäftsführers'
        })
    )

    contact_person = forms.CharField(
        label="Ansprechpartner",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Hauptansprechpartner'
        })
    )

    industry = forms.CharField(
        label="Branche",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Handel, Dienstleistung'
        })
    )

    description = forms.CharField(
        label="Beschreibung",
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Kurze Beschreibung der Geschäftstätigkeit'
        })
    )

    is_primary = forms.BooleanField(
        label="Als Hauptfirma festlegen",
        required=False,
        initial=True,
        help_text="Diese Firma wird als primäre Firma im System verwendet",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически загружаем страны из MongoDB
        country_choices = get_countries_from_mongodb()
        self.fields['country'].choices = country_choices

    def clean_vat_id(self):
        vat_id = self.cleaned_data.get('vat_id', '').strip().upper()
        if vat_id and not re.match(r'^DE[0-9]{9}$', vat_id):
            raise forms.ValidationError('USt-IdNr. muss im Format DE123456789 sein')
        return vat_id

    def clean_commercial_register(self):
        hr = self.cleaned_data.get('commercial_register', '').strip().upper()
        if hr and not re.match(r'^HR[AB][0-9]+$', hr):
            raise forms.ValidationError('Handelsregister muss im Format HRA12345 oder HRB12345 sein')
        return hr