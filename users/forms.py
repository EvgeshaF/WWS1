from django import forms
from django.core.validators import RegexValidator
import re
from mongodb.mongodb_utils import MongoConnection
from mongodb.mongodb_config import MongoConfig
from loguru import logger


def get_titles_from_mongodb():
    """Загружает titles из MongoDB коллекции"""
    try:
        logger.info("Загружаем titles из MongoDB")
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
        ('ba', 'B.A.'),
        ('bsc', 'B.Sc.'),
        ('beng', 'B.Eng.'),
    ]


def get_contact_types_from_mongodb():
    """Загружает типы контактов из MongoDB коллекции с кэшированием"""
    try:
        logger.info("Загружаем типы контактов из MongoDB")
        db = MongoConnection.get_database()
        if db is None:
            logger.error("База данных недоступна")
            return get_default_contact_type_choices()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не найдено в конфигурации")
            return get_default_contact_type_choices()

        contact_types_collection_name = f"{db_name}_basic_contact_types"
        collections = db.list_collection_names()
        if contact_types_collection_name not in collections:
            logger.warning(f"Коллекция '{contact_types_collection_name}' не найдена")
            return get_default_contact_type_choices()

        contact_types_collection = db[contact_types_collection_name]

        # Получаем типы контактов с дополнительными полями
        contact_types_cursor = contact_types_collection.find(
            {'deleted': {'$ne': True}, 'active': {'$ne': False}},
            {
                'type': 1,
                'icon': 1,
                'required_format': 1,
                'display_order': 1,
                'validation_pattern': 1,
                'placeholder': 1,
                'hint_de': 1
            }
        ).sort('display_order', 1)

        choices = [('', '-- Typ auswählen --')]
        count = 0

        for contact_type_doc in contact_types_cursor:
            type_code = contact_type_doc.get('type', '').strip()
            icon = contact_type_doc.get('icon', '')

            if type_code:
                # Создаем читаемое название на основе типа
                display_name = get_contact_type_display_name(type_code, icon)

                # Используем нормализованный код для value
                normalized_code = type_code.lower().replace('-', '').replace('_', '')
                choices.append((normalized_code, display_name))
                count += 1

        logger.success(f"Успешно загружено {count} типов контактов из коллекции")
        return choices

    except Exception as e:
        logger.error(f"Ошибка загрузки типов контактов из MongoDB: {e}")
        return get_default_contact_type_choices()


def get_contact_type_display_name(type_code, icon=''):
    """Возвращает отображаемое название типа контакта с эмодзи"""

    # Маппинг типов на отображаемые названия
    type_mapping = {
        'E-Mail': 'E-Mail',
        'Email': 'E-Mail',
        'email': 'E-Mail',
        'Telefon': 'Telefon',
        'Phone': 'Telefon',
        'telefon': 'Telefon',
        'Mobil': 'Mobil',
        'Mobile': 'Mobil',
        'mobil': 'Mobil',
        'Fax': 'Fax',
        'fax': 'Fax',
        'Website': 'Website',
        'Web': 'Website',
        'website': 'Website',
        'LinkedIn': 'LinkedIn',
        'linkedin': 'LinkedIn',
        'XING': 'XING',
        'Xing': 'XING',
        'xing': 'XING',
        'Sonstige': 'Sonstige',
        'Other': 'Sonstige',
        'sonstige': 'Sonstige',
        'other': 'Sonstige'
    }

    # Эмодзи для типов контактов
    emoji_mapping = {
        'E-Mail': '📧',
        'Telefon': '📞',
        'Mobil': '📱',
        'Fax': '📠',
        'Website': '🌐',
        'LinkedIn': '💼',
        'XING': '🔗',
        'Sonstige': '📝'
    }

    # Получаем отображаемое название
    display_name = type_mapping.get(type_code, type_code)

    # Получаем эмодзи
    emoji = emoji_mapping.get(display_name, '📋')

    return f"{emoji} {display_name}"


def get_default_contact_type_choices():
    """Возвращает статичный список типов контактов как fallback"""
    return [
        ('', '-- Typ auswählen --'),
        ('email', '📧 E-Mail'),
        ('telefon', '📞 Telefon'),
        ('mobil', '📱 Mobil'),
        ('fax', '📠 Fax'),
        ('website', '🌐 Website'),
        ('linkedin', '💼 LinkedIn'),
        ('xing', '🔗 XING'),
        ('sonstige', '📝 Sonstige'),
    ]


def get_contact_validation_config(contact_type):
    """Возвращает конфигурацию валидации для типа контакта"""
    validation_config = {
        'email': {
            'pattern': r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
            'placeholder': 'beispiel@domain.com',
            'hint': 'Geben Sie eine gültige E-Mail-Adresse ein',
            'error_message': 'Ungültiges E-Mail-Format'
        },
        'telefon': {
            'pattern': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
            'placeholder': '+49 123 456789',
            'hint': 'Geben Sie eine Telefonnummer ein (z.B. +49 123 456789)',
            'error_message': 'Ungültiges Telefonformat'
        },
        'mobil': {
            'pattern': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
            'placeholder': '+49 170 1234567',
            'hint': 'Geben Sie eine Mobilnummer ein (z.B. +49 170 1234567)',
            'error_message': 'Ungültiges Mobilnummer-Format'
        },
        'fax': {
            'pattern': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
            'placeholder': '+49 123 456789',
            'hint': 'Geben Sie eine Faxnummer ein (z.B. +49 123 456789)',
            'error_message': 'Ungültiges Faxnummer-Format'
        },
        'website': {
            'pattern': r'^https?:\/\/.+\..+$|^www\..+\..+$',
            'placeholder': 'https://www.example.com',
            'hint': 'Geben Sie eine Website-URL ein (z.B. https://www.example.com)',
            'error_message': 'Ungültiges Website-Format (muss mit http:// oder https:// beginnen)'
        },
        'linkedin': {
            'pattern': r'^(https?:\/\/)?(www\.)?linkedin\.com\/in\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$',
            'placeholder': 'linkedin.com/in/username',
            'hint': 'Geben Sie Ihr LinkedIn-Profil ein (z.B. linkedin.com/in/username)',
            'error_message': 'Ungültiges LinkedIn-Profil-Format'
        },
        'xing': {
            'pattern': r'^(https?:\/\/)?(www\.)?xing\.com\/profile\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$',
            'placeholder': 'xing.com/profile/username',
            'hint': 'Geben Sie Ihr XING-Profil ein (z.B. xing.com/profile/username)',
            'error_message': 'Ungültiges XING-Profil-Format'
        },
        'sonstige': {
            'pattern': r'.{3,}',
            'placeholder': 'Kontaktdaten eingeben...',
            'hint': 'Geben Sie die entsprechenden Kontaktdaten ein',
            'error_message': 'Kontaktdaten müssen mindestens 3 Zeichen lang sein'
        }
    }

    return validation_config.get(contact_type.lower(), validation_config['sonstige'])


class CreateAdminUserForm(forms.Form):
    """Шаг 1: Основные учетные данные администратора"""

    username = forms.CharField(
        label="Benutzername",
        max_length=50,
        min_length=3,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z][a-zA-Z0-9_]*$',
                message='Benutzername muss mit einem Buchstaben beginnen und darf nur Buchstaben, Zahlen und Unterstriche enthalten'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autofocus': True,
            'placeholder': 'z.B. admin_user',
            'pattern': '[a-zA-Z][a-zA-Z0-9_]*',
            'title': 'Beginnt mit Buchstaben, nur Buchstaben, Zahlen und Unterstriche'
        })
    )

    password = forms.CharField(
        label="Passwort",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sicheres Passwort eingeben'
        })
    )

    password_confirm = forms.CharField(
        label="Passwort bestätigen",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Passwort wiederholen'
        })
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            raise forms.ValidationError("Passwort muss mindestens 8 Zeichen lang sein")

        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Passwort muss mindestens einen Großbuchstaben enthalten")

        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Passwort muss mindestens einen Kleinbuchstaben enthalten")

        if not re.search(r'\d', password):
            raise forms.ValidationError("Passwort muss mindestens eine Ziffer enthalten")

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwörter stimmen nicht überein")

        return cleaned_data


class AdminProfileForm(forms.Form):
    """Шаг 2: Профильные данные администратора С основными контактами"""

    SALUTATION_CHOICES = [
        ('', '-- Auswählen --'),
        ('herr', 'Herr'),
        ('frau', 'Frau'),
        ('divers', 'Divers'),
    ]

    salutation = forms.ChoiceField(
        label="Anrede",
        choices=SALUTATION_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    title = forms.ChoiceField(
        label="Titel",
        choices=[],  # Заполняется динамически
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    first_name = forms.CharField(
        label="Vorname",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vorname eingeben'
        })
    )

    last_name = forms.CharField(
        label="Nachname",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nachname eingeben'
        })
    )

    # НОВОЕ ПОЛЕ: Тип основного контакта
    primary_contact_type = forms.ChoiceField(
        label="Hauptkontakt Typ",
        choices=[],  # Заполняется динамически из MongoDB
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-live-search': 'true'
        })
    )

    # Основной контакт (универсальное поле)
    primary_contact_value = forms.CharField(
        label="Hauptkontakt",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control contact-type-transition',
            'placeholder': 'Kontaktdaten eingeben'
        })
    )

    # Обязательные system поля
    email = forms.EmailField(
        label="System E-Mail",
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'beispiel@domain.com'
        })
    )

    phone = forms.CharField(
        label="System Telefon",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Динамически загружаем titles из MongoDB
        title_choices = get_titles_from_mongodb()
        self.fields['title'].choices = title_choices

        # Динамически загружаем типы контактов из MongoDB
        contact_type_choices = get_contact_types_from_mongodb()
        self.fields['primary_contact_type'].choices = contact_type_choices

    def clean_primary_contact_value(self):
        """Улучшенная валидация основного контакта в зависимости от типа"""
        contact_type = self.cleaned_data.get('primary_contact_type', '').lower()
        contact_value = self.cleaned_data.get('primary_contact_value', '').strip()

        if not contact_value:
            raise forms.ValidationError("Hauptkontakt ist erforderlich")

        # Получаем конфигурацию валидации для выбранного типа
        validation_config = get_contact_validation_config(contact_type)

        # Проверяем по паттерну
        pattern = validation_config.get('pattern')
        if pattern and not re.match(pattern, contact_value):
            error_message = validation_config.get('error_message', 'Ungültiges Format')
            raise forms.ValidationError(error_message)

        return contact_value

    def clean(self):
        """Дополнительная кросс-валидация полей"""
        cleaned_data = super().clean()

        # Проверяем, что главный контакт не дублирует system контакты
        primary_contact_type = cleaned_data.get('primary_contact_type', '').lower()
        primary_contact_value = cleaned_data.get('primary_contact_value', '')
        system_email = cleaned_data.get('email', '')
        system_phone = cleaned_data.get('phone', '')

        if primary_contact_type == 'email' and primary_contact_value == system_email:
            raise forms.ValidationError({
                'primary_contact_value': 'Hauptkontakt E-Mail darf nicht mit System E-Mail identisch sein'
            })

        if primary_contact_type in ['telefon', 'phone'] and primary_contact_value == system_phone:
            raise forms.ValidationError({
                'primary_contact_value': 'Hauptkontakt Telefon darf nicht mit System Telefon identisch sein'
            })

        return cleaned_data


class AdminPermissionsForm(forms.Form):
    """Шаг 3: Разрешения и безопасность"""

    # Системные разрешения
    is_super_admin = forms.BooleanField(
        label="Super Administrator",
        required=False,
        initial=True,
        help_text="Hat vollständigen Zugriff auf alle Systemfunktionen",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    can_manage_users = forms.BooleanField(
        label="Benutzer verwalten",
        required=False,
        initial=True,
        help_text="Kann Benutzer erstellen, bearbeiten und löschen",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    can_manage_database = forms.BooleanField(
        label="Datenbank verwalten",
        required=False,
        initial=True,
        help_text="Kann Datenbankeinstellungen ändern und Backups erstellen",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    can_view_logs = forms.BooleanField(
        label="Logs einsehen",
        required=False,
        initial=True,
        help_text="Kann Systemlogs und Audit-Trails einsehen",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    can_manage_settings = forms.BooleanField(
        label="Systemeinstellungen",
        required=False,
        initial=True,
        help_text="Kann globale Systemeinstellungen ändern",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    # Sicherheitseinstellungen
    password_expires = forms.BooleanField(
        label="Passwort läuft ab",
        required=False,
        initial=True,
        help_text="Passwort muss regelmäßig geändert werden (90 Tage)",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    two_factor_required = forms.BooleanField(
        label="Zwei-Faktor-Authentifizierung",
        required=False,
        initial=True,
        help_text="Erhöht die Sicherheit erheblich (empfohlen)",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )