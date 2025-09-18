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
    """Загружает типы коммуникаций из MongoDB коллекции _basic_communications"""
    try:
        logger.info("Загружаем типы коммуникаций из MongoDB")
        db = MongoConnection.get_database()
        if db is None:
            logger.error("База данных недоступна")
            return get_default_communication_choices()

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не найдено в конфигурации")
            return get_default_communication_choices()

        communications_collection_name = f"{db_name}_basic_communications"
        collections = db.list_collection_names()
        if communications_collection_name not in collections:
            logger.warning(f"Коллекция '{communications_collection_name}' не найдена")
            return get_default_communication_choices()

        communications_collection = db[communications_collection_name]
        communications_cursor = communications_collection.find(
            {
                'deleted': {'$ne': True},
                'active': {'$ne': False}
            },
            {
                'type': 1,
                'icon': 1,
                'required_format': 1,
                'validation_pattern': 1,
                'placeholder': 1,
                'hint_de': 1,
                'display_order': 1
            }
        ).sort('display_order', 1)

        choices = [('', '-- Kontakttyp auswählen --')]
        communication_data = {}
        count = 0

        for comm_doc in communications_cursor:
            type_name = comm_doc.get('type', '').strip()
            icon_name = comm_doc.get('icon', 'envelope')

            # Преобразуем Bootstrap Icons в эмодзи или оставляем как есть
            icon_mapping = {
                'envelope': '📧',
                'envelope-plus': '📧',
                'phone': '📱',
                'telephone': '📞',
                'printer': '📠',
                'globe': '🌐',
                'globe2': '🌐',
                'linkedin': '💼',
                'person-badge': '🔗',
                'person-vcard': '🔗',
                'chat': '💬',
                'chat-dots': '💬',
                'whatsapp': '📲',
                'camera-video': '🎥',
                'camera-video-fill': '🎥',
                'skype': '🎥',
                'pencil': '📝',
                'pencil-square': '📝',
                'telegram': '💬',
                'instagram': '📸',
                'facebook': '📘',
                'twitter': '🐦',
                'youtube': '📹',
                'tiktok': '🎵',
                'discord': '🎮',
                'snapchat': '👻',
                'pinterest': '📌',
                'reddit': '🔴',
                'tumblr': '📝',
                'medium': '📝',
                'behance': '🎨',
                'dribbble': '🏀',
                'github': '💻',
                'stack-overflow': '📚',
                'twitch': '🎮',
                'steam': '🎮'
            }

            display_icon = icon_mapping.get(icon_name, '📞')

            if type_name:
                # Создаем код из типа (приводим к нижнему регистру и заменяем пробелы)
                code = type_name.lower().replace(' ', '_').replace('-', '_')

                # Создаем выбор с иконкой
                display_text = f"{display_icon} {type_name}"
                choices.append((code, display_text))

                # Сохраняем дополнительные данные для JavaScript
                communication_data[code] = {
                    'name': type_name,
                    'icon': display_icon,
                    'validation_pattern': comm_doc.get('validation_pattern', ''),
                    'placeholder_text': comm_doc.get('placeholder', f'{type_name} eingeben...'),
                    'hint_text': comm_doc.get('hint_de', f'Geben Sie {type_name.lower()} ein')
                }
                count += 1

        logger.success(f"Успешно загружено {count} типов коммуникаций из коллекции")
        return choices, communication_data

    except Exception as e:
        logger.error(f"Ошибка загрузки типов коммуникаций из MongoDB: {e}")
        return get_default_communication_choices()


def get_default_communication_choices():
    """Возвращает статичный список типов коммуникаций как fallback"""
    choices = [
        ('', '-- Kontakttyp auswählen --'),
        ('e_mail', '📧 E-Mail'),
        ('mobile', '📱 Mobile'),
        ('fax', '📠 Fax'),
        ('website', '🌐 Website'),
        ('linkedin', '💼 LinkedIn'),
        ('xing', '🔗 XING'),
        ('sonstige', '📝 Sonstige')
    ]

    communication_data = {
        'e_mail': {
            'name': 'E-Mail',
            'icon': '📧',
            'validation_pattern': r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
            'placeholder_text': 'beispiel@domain.com',
            'hint_text': 'Geben Sie eine gültige E-Mail-Adresse ein'
        },
        'mobile': {
            'name': 'Mobile',
            'icon': '📱',
            'validation_pattern': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
            'placeholder_text': '+49 170 1234567',
            'hint_text': 'Geben Sie eine Mobilnummer ein'
        },
        'fax': {
            'name': 'Fax',
            'icon': '📠',
            'validation_pattern': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
            'placeholder_text': '+49 123 456789',
            'hint_text': 'Geben Sie eine Faxnummer ein'
        },
        'website': {
            'name': 'Website',
            'icon': '🌐',
            'validation_pattern': r'^https?:\/\/.+\..+$|^www\..+\..+$',
            'placeholder_text': 'https://www.example.com',
            'hint_text': 'Geben Sie eine Website-URL ein'
        },
        'linkedin': {
            'name': 'LinkedIn',
            'icon': '💼',
            'validation_pattern': r'^(https?:\/\/)?(www\.)?linkedin\.com\/in\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$',
            'placeholder_text': 'linkedin.com/in/username',
            'hint_text': 'Geben Sie Ihr LinkedIn-Profil ein'
        },
        'xing': {
            'name': 'XING',
            'icon': '🔗',
            'validation_pattern': r'^(https?:\/\/)?(www\.)?xing\.com\/profile\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$',
            'placeholder_text': 'xing.com/profile/username',
            'hint_text': 'Geben Sie Ihr XING-Profil ein'
        },
        'sonstige': {
            'name': 'Sonstige',
            'icon': '📝',
            'validation_pattern': r'.{3,}',
            'placeholder_text': 'Kontaktdaten eingeben...',
            'hint_text': 'Geben Sie die entsprechenden Kontaktdaten ein'
        }
    }

    return choices, communication_data


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

        if not password:
            raise forms.ValidationError("Passwort ist erforderlich")

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
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vorname eingeben'
        })
    )

    last_name = forms.CharField(
        label="Nachname",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nachname eingeben'
        })
    )

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
        try:
            title_choices = get_titles_from_mongodb()
            self.fields['title'].choices = title_choices
        except Exception as e:
            logger.error(f"Ошибка загрузки titles в AdminProfileForm: {e}")
            # Используем fallback choices
            self.fields['title'].choices = get_default_title_choices()


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