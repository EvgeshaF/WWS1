from django import forms
from django.core.validators import RegexValidator
import re


class CompanyRegistrationForm(forms.Form):
    """Форма регистрации компании"""

    LEGAL_FORM_CHOICES = [
        ('', '-- Auswählen --'),
        ('gmbh', 'GmbH'),
        ('ag', 'AG'),
        ('ug', 'UG (haftungsbeschränkt)'),
        ('ohg', 'OHG'),
        ('kg', 'KG'),
        ('gbr', 'GbR'),
        ('eg', 'eG'),
        ('einzelunternehmen', 'Einzelunternehmen'),
        ('freiberufler', 'Freiberufler'),
        ('sonstige', 'Sonstige'),
    ]

    COUNTRY_CHOICES = [
        ('', '-- Land auswählen --'),
        ('deutschland', 'Deutschland'),
        ('oesterreich', 'Österreich'),
        ('schweiz', 'Schweiz'),
        ('niederlande', 'Niederlande'),
        ('belgien', 'Belgien'),
        ('frankreich', 'Frankreich'),
        ('sonstige', 'Sonstige'),
    ]

    # Grunddaten
    company_name = forms.CharField(
        label="Firmenname",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Firmenname eingeben'
        })
    )

    legal_form = forms.ChoiceField(
        label="Rechtsform",
        choices=LEGAL_FORM_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    # Registrierungsdaten
    commercial_register = forms.CharField(
        label="Handelsregister",
        max_length=50,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^HR[AB][0-9]+$',
                message='Format: HRA12345 oder HRB12345'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. HRB12345'
        })
    )

    tax_number = forms.CharField(
        label="Steuernummer",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Steuernummer'
        })
    )

    vat_id = forms.CharField(
        label="USt-IdNr.",
        max_length=15,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^DE[0-9]{9}$',
                message='Format: DE123456789'
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
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Straße und Hausnummer'
        })
    )

    postal_code = forms.CharField(
        label="PLZ",
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{5}$',
                message='PLZ muss aus 5 Ziffern bestehen'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345'
        })
    )

    city = forms.CharField(
        label="Stadt",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Stadt'
        })
    )

    country = forms.ChoiceField(
        label="Land",
        choices=COUNTRY_CHOICES,
        initial='deutschland',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    # Kontaktdaten
    email = forms.EmailField(
        label="E-Mail",
        max_length=100,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'firma@domain.com'
        })
    )

    phone = forms.CharField(
        label="Telefon",
        max_length=50,
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

    # Details
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
            'placeholder': 'Hauptansprechpartner'
        })
    )

    industry = forms.CharField(
        label="Branche",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Handel, Dienstleistung'
        })
    )

    description = forms.CharField(
        label="Beschreibung",
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Kurze Beschreibung der Geschäftstätigkeit'
        })
    )

    is_primary = forms.BooleanField(
        label="Als Hauptfirma festlegen",
        required=False,
        initial=True,
        help_text="Diese Firma wird als primäre Firma im System verwendet",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean_vat_id(self):
        vat_id = self.cleaned_data.get('vat_id', '').strip().upper()
        if vat_id and not re.match(r'^DE[0-9]{9}$', vat_id):
            raise forms.ValidationError('USt-IdNr. muss im Format DE123456789 sein')
        return vat_id

    def clean_commercial_register(self):
        hr = self.cleaned_data.get('commercial_register', '').strip().upper()
        if hr and not re.match(r'^HR[AB][0-9]+$', hr):
            raise forms.ValidationError('Handelsregister muss im Format HRA12345 oder HRB12345 sein')
        return hr