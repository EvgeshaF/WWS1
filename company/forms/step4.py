# company/forms/step4.py - ОБНОВЛЕНО: динамическая загрузка из MongoDB + дополнительные контакты

from django import forms
from django.core.validators import RegexValidator, EmailValidator
from loguru import logger

from .utils import (
    get_salutations_from_mongodb,
    get_titles_from_mongodb,
    get_communication_types_from_mongodb,  # НОВОЕ
    get_communication_config_from_mongodb,  # НОВОЕ
)


class CompanyContactForm(forms.Form):
    """Шаг 4: Контактные данные - ОБНОВЛЕНО: динамические справочники + дополнительные контакты"""

    # Основные обязательные контакты
    email = forms.EmailField(
        label="E-Mail",
        max_length=100,
        required=True,
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'info@firma.de'
        }),
        error_messages={
            'required': 'E-Mail ist erforderlich',
            'invalid': 'Ungültige E-Mail-Adresse'
        }
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
        }),
        error_messages={
            'required': 'Telefon ist erforderlich'
        }
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
        max_length=200,
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.firma.de'
        })
    )

    # Контактное лицо (опционально)
    contact_person_salutation = forms.ChoiceField(
        label="Anrede Kontaktperson",
        choices=[],  # Заполняется в __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    contact_person_title = forms.ChoiceField(
        label="Titel Kontaktperson",
        choices=[],  # Заполняется в __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    contact_person_first_name = forms.CharField(
        label="Vorname Kontaktperson",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vorname'
        })
    )

    contact_person_last_name = forms.CharField(
        label="Nachname Kontaktperson",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nachname'
        })
    )

    contact_person_position = forms.CharField(
        label="Position Kontaktperson",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Leiter Vertrieb'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Динамически загружаем Anrede из MongoDB
        salutation_choices = get_salutations_from_mongodb()
        self.fields['contact_person_salutation'].choices = salutation_choices
        logger.info(f"Загружено {len(salutation_choices)} вариантов Anrede для контактного лица")

        # Динамически загружаем Titel из MongoDB
        title_choices = get_titles_from_mongodb()
        self.fields['contact_person_title'].choices = title_choices
        logger.info(f"Загружено {len(title_choices)} вариантов Titel для контактного лица")


# НОВАЯ ФОРМА: для дополнительных контактов компании
class CompanyAdditionalContactForm(forms.Form):
    """Форма для дополнительных контактов компании (используется в модальном окне)"""

    contact_type = forms.ChoiceField(
        label="Kontakttyp",
        choices=[],  # Заполняется динамически из MongoDB
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'companyContactType'
        })
    )

    contact_value = forms.CharField(
        label="Kontaktdaten",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kontaktdaten eingeben...',
            'id': 'companyContactValue'
        })
    )

    contact_label = forms.CharField(
        label="Bezeichnung",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Zentrale, Filiale, Hotline...',
            'id': 'companyContactLabel'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Динамически загружаем типы контактов из MongoDB
        contact_type_choices = get_communication_types_from_mongodb()
        self.fields['contact_type'].choices = contact_type_choices
        logger.info(f"Загружено {len(contact_type_choices)} типов контактов для дополнительных контактов компании")