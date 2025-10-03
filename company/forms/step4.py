from django import forms
from django.core.validators import RegexValidator


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