# company/forms/step1.py
# Шаг 1: Основные данные компании + Geschäftsführer

from django import forms
from django.core.validators import RegexValidator
from loguru import logger

from .utils import get_salutations_from_mongodb, get_titles_from_mongodb


class CompanyBasicDataForm(forms.Form):
    """Шаг 1: Основные данные компании + Geschäftsführer - UPDATED WITH DYNAMIC LOADING"""

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

    # БЛОК GESCHÄFTSFÜHRER - UPDATED WITH DYNAMIC LOADING
    ceo_salutation = forms.ChoiceField(
        label="Anrede",
        choices=[],  # CHANGED: Заполняется динамически из MongoDB
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    ceo_title = forms.ChoiceField(
        label="Titel",
        choices=[],  # CHANGED: Заполняется динамически из MongoDB
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

        # НОВОЕ: Динамически загружаем salutations из MongoDB - SAME AS USERS
        salutation_choices = get_salutations_from_mongodb()
        self.fields['ceo_salutation'].choices = salutation_choices
        logger.info(f"Загружено {len(salutation_choices)} вариантов CEO salutation")

        # НОВОЕ: Динамически загружаем titles из MongoDB - SAME AS USERS
        title_choices = get_titles_from_mongodb()
        self.fields['ceo_title'].choices = title_choices
        logger.info(f"Загружено {len(title_choices)} вариантов CEO title")