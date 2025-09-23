# company/forms.py - Updated CompanyBasicDataForm with CEO fields

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

    # НОВОЕ: Поля Geschäftsführер
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически загружаем отрасли из MongoDB
        industry_choices = get_industries_from_mongodb()
        self.fields['industry'].choices = industry_choices


# Обновляем CompanyManagementForm - убираем поля CEO, оставляем только контактное лицо
class CompanyManagementForm(forms.Form):
    """Шаг 5: Анспречпартнер и персонал (без CEO)"""

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