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


def get_communication_types_from_mongodb():
    """Загружает типы коммуникации из MongoDB коллекции basic_communications"""
    try:
        logger.info("Загружаем типы коммуникации из MongoDB")
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

        # Мапинг иконок Bootstrap Icons
        icon_mapping = {
            'envelope': '📧',
            'phone': '📱',
            'printer': '📠',
            'globe': '🌐',
            'linkedin': '💼',
            'person-badge': '🔗',
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
                display_text = f"{emoji} {comm_type}"

                choices.append((key, display_text))
                count += 1

                logger.debug(f"Добавлен тип коммуникации: {key} -> {display_text}")

        logger.success(f"Успешно загружено {count} типов коммуникации из коллекции")
        return choices

    except Exception as e:
        logger.error(f"Ошибка загрузки типов коммуникации из MongoDB: {e}")
        return get_default_contact_type_choices()


def get_default_contact_type_choices():
    """Возвращает статичный список типов контактов как fallback"""
    return [
        ('', '-- Kontakttyp auswählen --'),
        ('email', '📧 E-Mail'),
        ('mobile', '📱 Mobil'),
        ('fax', '📠 Fax'),
        ('website', '🌐 Website'),
        ('linkedin', '💼 LinkedIn'),
        ('xing', '🔗 XING'),
        ('other', '📝 Sonstige'),
    ]


def get_communication_config_from_mongodb():
    """Загружает полную конфигурацию типов коммуникации для JavaScript"""
    try:
        logger.info("Загружаем конфигурацию коммуникации для JavaScript")
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
                    'envelope': 'bi-envelope-plus',
                    'phone': 'bi-phone',
                    'printer': 'bi-printer',
                    'globe': 'bi-globe',
                    'linkedin': 'bi-linkedin',
                    'person-badge': 'bi-person-badge',
                    'question-circle': 'bi-question-circle'
                }

                config_dict[key] = {
                    'label': comm_type,
                    'icon_class': icon_class_mapping.get(icon, 'bi-question-circle'),
                    'validation_pattern': validation_pattern,
                    'placeholder': placeholder or f"{comm_type} eingeben...",
                    'hint': hint_de or f"Geben Sie {comm_type} ein"
                }

        logger.success(f"Конфигурация загружена для {len(config_dict)} типов коммуникации")
        return config_dict

    except Exception as e:
        logger.error(f"Ошибка загрузки конфигурации коммуникации: {e}")
        return get_default_communication_config()


def get_default_communication_config():
    """Возвращает статичную конфигурацию типов коммуникации как fallback"""
    return {
        'email': {
            'label': 'E-Mail',
            'icon_class': 'bi-envelope-plus',
            'validation_pattern': '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$',
            'placeholder': 'beispiel@domain.com',
            'hint': 'Geben Sie eine gültige E-Mail-Adresse ein'
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
            'placeholder': 'https://www.example.com',
            'hint': 'Geben Sie eine Website-URL ein'
        },
        'linkedin': {
            'label': 'LinkedIn',
            'icon_class': 'bi-linkedin',
            'validation_pattern': '^(https?:\\/\\/)?(www\\.)?linkedin\\.com\\/in\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$',
            'placeholder': 'linkedin.com/in/username',
            'hint': 'Geben Sie Ihr LinkedIn-Profil ein'
        },
        'xing': {
            'label': 'XING',
            'icon_class': 'bi-person-badge',
            'validation_pattern': '^(https?:\\/\\/)?(www\\.)?xing\\.com\\/profile\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$',
            'placeholder': 'xing.com/profile/username',
            'hint': 'Geben Sie Ihr XING-Profil ein'
        },
        'other': {
            'label': 'Sonstige',
            'icon_class': 'bi-question-circle',
            'validation_pattern': '.{3,}',
            'placeholder': 'Kontaktdaten eingeben...',
            'hint': 'Geben Sie die entsprechenden Kontaktdaten ein'
        }
    }


# Новая функция для удобного доступа к choices
def get_contact_type_choices():
    """Получает типы контактов из MongoDB или возвращает fallback"""
    return get_communication_types_from_mongodb()


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
        choices=[],  # Заполняется динамически из MongoDB
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

    # ДОБАВЛЕНЫ обязательные поля email и phone
    email = forms.EmailField(
        label="E-Mail",
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'beispiel@domain.com'
        })
    )

    phone = forms.CharField(
        label="Telefon",
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


class AdditionalContactForm(forms.Form):
    """Форма для дополнительных контактов (используется в модальном окне)"""

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

    contact_label = forms.CharField(
        label="Bezeichnung",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Privat, Geschäftlich...',
            'id': 'contactLabel'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Динамически загружаем типы контактов из MongoDB
        contact_type_choices = get_communication_types_from_mongodb()
        self.fields['contact_type'].choices = contact_type_choices


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