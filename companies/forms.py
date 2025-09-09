# companies/forms.py
from django import forms
from django.core.validators import RegexValidator
import re


class CompanyRegistrationForm(forms.Form):
    """Форма для регистрации новой компании"""

    LEGAL_FORM_CHOICES = [
        ('', '-- Rechtsform auswählen --'),
        ('gmbh', 'GmbH - Gesellschaft mit beschränkter Haftung'),
        ('ag', 'AG - Aktiengesellschaft'),
        ('ohg', 'OHG - Offene Handelsgesellschaft'),
        ('kg', 'KG - Kommanditgesellschaft'),
        ('ug', 'UG - Unternehmergesellschaft'),
        ('eg', 'eG - eingetragene Genossenschaft'),
        ('einzelunternehmen', 'Einzelunternehmen'),
        ('freiberufler', 'Freiberufler'),
        ('other', 'Sonstige'),
    ]

    INDUSTRY_CHOICES = [
        ('', '-- Branche auswählen --'),
        ('automotive', 'Automobilindustrie'),
        ('construction', 'Bauwesen'),
        ('chemicals', 'Chemie'),
        ('electronics', 'Elektronik'),
        ('energy', 'Energie'),
        ('food', 'Lebensmittel'),
        ('healthcare', 'Gesundheitswesen'),
        ('it', 'Informationstechnologie'),
        ('logistics', 'Logistik'),
        ('manufacturing', 'Fertigung'),
        ('retail', 'Einzelhandel'),
        ('services', 'Dienstleistungen'),
        ('textiles', 'Textil'),
        ('other', 'Sonstige'),
    ]

    COUNTRY_CHOICES = [
        ('', '-- Land auswählen --'),
        ('DE', 'Deutschland'),
        ('AT', 'Österreich'),
        ('CH', 'Schweiz'),
        ('FR', 'Frankreich'),
        ('NL', 'Niederlande'),
        ('BE', 'Belgien'),
        ('LU', 'Luxemburg'),
        ('DK', 'Dänemark'),
        ('SE', 'Schweden'),
        ('NO', 'Norwegen'),
        ('other', 'Sonstige'),
    ]

    # Grunddaten des Unternehmens
    company_name = forms.CharField(
        label="Firmenname",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Musterfirma GmbH',
            'autofocus': True
        })
    )

    legal_form = forms.ChoiceField(
        label="Rechtsform",
        choices=LEGAL_FORM_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    tax_number = forms.CharField(
        label="Steuernummer",
        max_length=50,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9\/\-\s]+$',
                message='Ungültiges Format der Steuernummer'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. 123/456/78901'
        })
    )

    vat_number = forms.CharField(
        label="USt-IdNr.",
        max_length=20,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2}[0-9A-Z]+$',
                message='Ungültiges Format der USt-IdNr. (z.B. DE123456789)'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. DE123456789'
        })
    )

    registration_number = forms.CharField(
        label="Handelsregisternummer",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. HRB 12345'
        })
    )

    industry = forms.ChoiceField(
        label="Branche",
        choices=INDUSTRY_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    # Firmenadresse
    street = forms.CharField(
        label="Straße und Hausnummer",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Musterstraße 123'
        })
    )

    postal_code = forms.CharField(
        label="PLZ",
        max_length=10,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{4,6}$',
                message='Ungültiges PLZ-Format'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345',
            'pattern': '[0-9]{4,6}'
        })
    )

    city = forms.CharField(
        label="Stadt",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Berlin'
        })
    )

    country = forms.ChoiceField(
        label="Land",
        choices=COUNTRY_CHOICES,
        required=True,
        initial='DE',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    # Kontaktdaten
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
            'placeholder': '+49 30 12345678'
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
            'placeholder': '+49 30 12345679'
        })
    )

    email = forms.EmailField(
        label="E-Mail",
        max_length=150,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'info@musterfirma.de'
        })
    )

    website = forms.URLField(
        label="Website",
        max_length=200,
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.musterfirma.de'
        })
    )

    # Ansprechpartner
    contact_salutation = forms.ChoiceField(
        label="Anrede",
        choices=[
            ('', '-- Auswählen --'),
            ('herr', 'Herr'),
            ('frau', 'Frau'),
            ('divers', 'Divers'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    contact_first_name = forms.CharField(
        label="Vorname",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max'
        })
    )

    contact_last_name = forms.CharField(
        label="Nachname",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mustermann'
        })
    )

    contact_position = forms.CharField(
        label="Position",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Geschäftsführer'
        })
    )

    contact_phone = forms.CharField(
        label="Telefon direkt",
        max_length=50,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[\+]?[0-9\s\-\(\)]{7,20}$',
                message='Ungültiges Telefonformat'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+49 30 12345678'
        })
    )

    contact_email = forms.EmailField(
        label="E-Mail direkt",
        max_length=150,
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'max.mustermann@musterfirma.de'
        })
    )

    # Zusätzliche Informationen
    description = forms.CharField(
        label="Unternehmensbeschreibung",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Kurze Beschreibung Ihres Unternehmens und Ihrer Geschäftstätigkeit...'
        })
    )

    # Datenschutz und Nutzungsbedingungen
    terms_accepted = forms.BooleanField(
        label="Ich akzeptiere die Nutzungsbedingungen und Datenschutzerklärung",
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    newsletter = forms.BooleanField(
        label="Ich möchte den Newsletter erhalten",
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean_tax_number(self):
        tax_number = self.cleaned_data.get('tax_number')
        if tax_number:
            # Entferne alle Leerzeichen und Sonderzeichen für die Validierung
            cleaned = re.sub(r'[^0-9]', '', tax_number)
            if len(cleaned) < 10:
                raise forms.ValidationError("Steuernummer muss mindestens 10 Ziffern enthalten")
        return tax_number

    def clean_vat_number(self):
        vat_number = self.cleaned_data.get('vat_number')
        if vat_number:
            vat_number = vat_number.upper().replace(' ', '')
            # Deutsche USt-IdNr. Validierung
            if vat_number.startswith('DE') and len(vat_number) != 11:
                raise forms.ValidationError("Deutsche USt-IdNr. muss 11 Zeichen lang sein (DE + 9 Ziffern)")
        return vat_number

    def clean(self):
        cleaned_data = super().clean()

        # Prüfe ob Haupt-E-Mail und Kontakt-E-Mail nicht identisch sind
        email = cleaned_data.get('email')
        contact_email = cleaned_data.get('contact_email')

        if email and contact_email and email == contact_email:
            raise forms.ValidationError(
                "Die Unternehmens-E-Mail und die Kontakt-E-Mail können nicht identisch sein"
            )

        return cleaned_data