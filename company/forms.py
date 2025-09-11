# company/forms.py - Упрощенная форма для одной компании

from django import forms
from django.core.validators import RegexValidator
import re


class CompanyRegistrationForm(forms.Form):
    """Форма для регистрации единственной компании"""

    # Основная информация о компании
    company_name = forms.CharField(
        label="Firmenname",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name Ihrer Firma eingeben...',
            'autofocus': True
        })
    )

    legal_form = forms.ChoiceField(
        label="Rechtsform",
        choices=[
            ('', '-- Rechtsform auswählen --'),
            ('gmbh', 'GmbH'),
            ('ag', 'AG'),
            ('kg', 'KG'),
            ('ohg', 'OHG'),
            ('eg', 'eG'),
            ('einzelunternehmen', 'Einzelunternehmen'),
            ('gbr', 'GbR'),
            ('ug', 'UG (haftungsbeschränkt)'),
            ('other', 'Sonstige')
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    # Handelsregister
    commercial_register = forms.CharField(
        label="Handelsregisternummer",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. HRB 12345'
        })
    )

    tax_number = forms.CharField(
        label="Steuernummer",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. 123/456/78901'
        })
    )

    vat_id = forms.CharField(
        label="Umsatzsteuer-ID",
        max_length=20,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^DE[0-9]{9}$',
                message='Ungültiges Format (DE + 9 Ziffern)'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DE123456789'
        })
    )

    # Adresse
    street = forms.CharField(
        label="Straße und Hausnummer",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Musterstraße 123'
        })
    )

    postal_code = forms.CharField(
        label="Postleitzahl",
        max_length=10,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{5}$',
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
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Musterstadt'
        })
    )

    country = forms.CharField(
        label="Land",
        max_length=100,
        initial='Deutschland',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    # Kontaktdaten
    email = forms.EmailField(
        label="Firmen E-Mail",
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'info@firma.de'
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

    # Geschäftsführer/Ansprechpartner
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
            'placeholder': 'Name des Ansprechpartners'
        })
    )

    # Zusätzliche Informationen
    description = forms.CharField(
        label="Firmenbeschreibung",
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Kurze Beschreibung der Geschäftstätigkeit...'
        })
    )

    industry = forms.CharField(
        label="Branche",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. IT-Dienstleistungen, Handel, Produktion...'
        })
    )

    def clean_vat_id(self):
        """Validiert die Umsatzsteuer-ID"""
        vat_id = self.cleaned_data.get('vat_id')
        if vat_id:
            vat_id = vat_id.upper().replace(' ', '')
            if not re.match(r'^DE[0-9]{9}$', vat_id):
                raise forms.ValidationError(
                    "Ungültiges Format. Erwartetes Format: DE123456789"
                )
        return vat_id

    def clean_commercial_register(self):
        """Validiert die Handelsregisternummer"""
        hr_number = self.cleaned_data.get('commercial_register')
        if hr_number:
            hr_number = hr_number.upper().replace(' ', '')
            # Basis-Validierung für deutsche HR-Nummern
            if not re.match(r'^HR[AB][0-9]+$', hr_number):
                # Warnung, aber nicht kritisch
                pass
        return hr_number

    def clean_phone(self):
        """Bereinigt die Telefonnummer"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Entfernt überschüssige Leerzeichen
            phone = ' '.join(phone.split())
        return phone