# company/forms/step3.py
# Шаг 3: Адресные данные

from django import forms
from django.core.validators import RegexValidator
from loguru import logger

from .utils import get_countries_from_mongodb


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
        logger.info(f"Загружено {len(country_choices)} стран для формы адреса")