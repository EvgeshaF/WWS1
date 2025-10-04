# company/forms/step1.py - ОБНОВЛЕНО: динамическая загрузка из MongoDB

from django import forms
from django.core.validators import RegexValidator
from loguru import logger

from .utils import (
    get_salutations_from_mongodb,
    get_titles_from_mongodb,
    get_legal_forms_from_mongodb,  # НОВОЕ
)


class CompanyBasicDataForm(forms.Form):
    """Шаг 1: Основные данные компании - ОБНОВЛЕНО: все справочники из MongoDB"""

    company_name = forms.CharField(
        label="Firmenname",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Musterfirma GmbH',
            'autofocus': True
        }),
        error_messages={
            'required': 'Firmenname ist erforderlich'
        }
    )

    # ИЗМЕНЕНО: теперь choices загружаются динамически
    legal_form = forms.ChoiceField(
        label="Rechtsform",
        choices=[],  # Заполняется в __init__
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        error_messages={
            'required': 'Rechtsform ist erforderlich'
        }
    )

    # ИЗМЕНЕНО: теперь choices загружаются динамически
    ceo_salutation = forms.ChoiceField(
        label="Anrede Geschäftsführer",
        choices=[],  # Заполняется в __init__
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        error_messages={
            'required': 'Anrede ist erforderlich'
        }
    )

    # ИЗМЕНЕНО: теперь choices загружаются динамически
    ceo_title = forms.ChoiceField(
        label="Titel Geschäftsführer",
        choices=[],  # Заполняется в __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    ceo_first_name = forms.CharField(
        label="Vorname Geschäftsführer",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vorname'
        }),
        error_messages={
            'required': 'Vorname ist erforderlich'
        }
    )

    ceo_last_name = forms.CharField(
        label="Nachname Geschäftsführer",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nachname'
        }),
        error_messages={
            'required': 'Nachname ist erforderlich'
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Динамически загружаем Rechtsform из MongoDB
        legal_form_choices = get_legal_forms_from_mongodb()
        self.fields['legal_form'].choices = legal_form_choices
        logger.info(f"Загружено {len(legal_form_choices)} вариантов Rechtsform")

        # Динамически загружаем Anrede из MongoDB
        salutation_choices = get_salutations_from_mongodb()
        self.fields['ceo_salutation'].choices = salutation_choices
        logger.info(f"Загружено {len(salutation_choices)} вариантов Anrede")

        # Динамически загружаем Titel из MongoDB
        title_choices = get_titles_from_mongodb()
        self.fields['ceo_title'].choices = title_choices
        logger.info(f"Загружено {len(title_choices)} вариантов Titel")