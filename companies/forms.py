# companies/forms.py
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.html import escape
import re
import logging

logger = logging.getLogger(__name__)


class CompanyRegistrationForm(forms.Form):
    """Форма для регистрации новой компании с улучшенной валидацией"""

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
        ('finance', 'Finanzwesen'),
        ('consulting', 'Beratung'),
        ('education', 'Bildung'),
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
        ('IT', 'Italien'),
        ('ES', 'Spanien'),
        ('PL', 'Polen'),
        ('CZ', 'Tschechien'),
        ('other', 'Sonstige'),
    ]

    SALUTATION_CHOICES = [
        ('', '-- Auswählen --'),
        ('herr', 'Herr'),
        ('frau', 'Frau'),
        ('divers', 'Divers'),
    ]

    # Validatoren
    phone_validator = RegexValidator(
        regex=r'^[\+]?[0-9\s\-\(\)]{7,20}$',
        message='Ungültiges Telefonformat. Beispiel: +49 30 12345678'
    )

    tax_number_validator = RegexValidator(
        regex=r'^[0-9\/\-\s]+$',
        message='Steuernummer darf nur Ziffern, Schrägstriche und Bindestriche enthalten'
    )

    vat_number_validator = RegexValidator(
        regex=r'^[A-Z]{2}[0-9A-Z]+$',
        message='Ungültiges USt-IdNr. Format. Beispiel: DE123456789'
    )

    postal_code_validator = RegexValidator(
        regex=r'^[0-9]{4,6}$',
        message='PLZ muss 4-6 Ziffern enthalten'
    )

    # Grunddaten des Unternehmens
    company_name = forms.CharField(
        label="Firmenname",
        max_length=200,
        required=True,
        strip=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Musterfirma GmbH',
            'autocomplete': 'organization',
            'data-validation': 'company-name'
        }),
        help_text="Der vollständige offizielle Name Ihres Unternehmens"
    )

    legal_form = forms.ChoiceField(
        label="Rechtsform",
        choices=LEGAL_FORM_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-validation': 'required'
        })
    )

    tax_number = forms.CharField(
        label="Steuernummer",
        max_length=50,
        required=True,
        strip=True,
        validators=[tax_number_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. 123/456/78901',
            'data-validation': 'tax-number'
        }),
        help_text="Ihre beim Finanzamt registrierte Steuernummer"
    )

    vat_number = forms.CharField(
        label="USt-IdNr.",
        max_length=20,
        required=False,
        strip=True,
        validators=[vat_number_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. DE123456789',
            'data-validation': 'vat-number'
        }),
        help_text="Umsatzsteuer-Identifikationsnummer (bei EU-Geschäften)"
    )

    registration_number = forms.CharField(
        label="Handelsregisternummer",
        max_length=50,
        required=False,
        strip=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. HRB 12345'
        }),
        help_text="Falls im Handelsregister eingetragen"
    )

    industry = forms.ChoiceField(
        label="Branche",
        choices=INDUSTRY_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-validation': 'required'
        })
    )

    # Firmenadresse
    street = forms.CharField(
        label="Straße und Hausnummer",
        max_length=200,
        required=True,
        strip=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Musterstraße 123',
            'autocomplete': 'street-address'
        })
    )

    postal_code = forms.CharField(
        label="PLZ",
        max_length=10,
        required=True,
        strip=True,
        validators=[postal_code_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345',
            'pattern': '[0-9]{4,6}',
            'autocomplete': 'postal-code',
            'data-validation': 'postal-code'
        })
    )

    city = forms.CharField(
        label="Stadt",
        max_length=100,
        required=True,
        strip=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Berlin',
            'autocomplete': 'address-level2'
        })
    )

    country = forms.ChoiceField(
        label="Land",
        choices=COUNTRY_CHOICES,
        required=True,
        initial='DE',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'autocomplete': 'country'
        })
    )

    # Kontaktdaten
    phone = forms.CharField(
        label="Telefon",
        max_length=50,
        required=True,
        strip=True,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+49 30 12345678',
            'type': 'tel',
            'autocomplete': 'tel',
            'data-validation': 'phone'
        })
    )

    fax = forms.CharField(
        label="Fax",
        max_length=50,
        required=False,
        strip=True,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+49 30 12345679',
            'type': 'tel'
        })
    )

    email = forms.EmailField(
        label="E-Mail",
        max_length=150,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'info@musterfirma.de',
            'autocomplete': 'email',
            'data-validation': 'email'
        })
    )

    website = forms.URLField(
        label="Website",
        max_length=200,
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.musterfirma.de',
            'autocomplete': 'url'
        })
    )

    # Ansprechpartner
    contact_salutation = forms.ChoiceField(
        label="Anrede",
        choices=SALUTATION_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    contact_first_name = forms.CharField(
        label="Vorname",
        max_length=100,
        required=True,
        strip=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max',
            'autocomplete': 'given-name'
        })
    )

    contact_last_name = forms.CharField(
        label="Nachname",
        max_length=100,
        required=True,
        strip=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mustermann',
            'autocomplete': 'family-name'
        })
    )

    contact_position = forms.CharField(
        label="Position",
        max_length=100,
        required=False,
        strip=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Geschäftsführer',
            'autocomplete': 'organization-title'
        })
    )

    contact_phone = forms.CharField(
        label="Telefon direkt",
        max_length=50,
        required=False,
        strip=True,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+49 30 12345678',
            'type': 'tel'
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
            'maxlength': 1000,
            'placeholder': 'Kurze Beschreibung Ihres Unternehmens und Ihrer Geschäftstätigkeit...'
        }),
        help_text="Maximal 1000 Zeichen"
    )

    # Datenschutz und Nutzungsbedingungen
    terms_accepted = forms.BooleanField(
        label="Ich akzeptiere die Nutzungsbedingungen und Datenschutzerklärung",
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'data-validation': 'terms'
        })
    )

    newsletter = forms.BooleanField(
        label="Ich möchte den Newsletter erhalten",
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Dynamische Länderliste basierend auf Benutzerstandort
        if self.request and hasattr(self.request, 'user_country'):
            country = self.request.user_country
            if country in dict(self.COUNTRY_CHOICES):
                self.fields['country'].initial = country

    def clean_company_name(self):
        """Validierung des Firmennamens"""
        company_name = self.cleaned_data.get('company_name')
        if not company_name:
            return company_name

        # HTML-Escaping für Sicherheit
        company_name = escape(company_name.strip())

        if len(company_name) < 2:
            raise ValidationError("Firmenname muss mindestens 2 Zeichen lang sein")

        if len(company_name) > 200:
            raise ValidationError("Firmenname darf maximal 200 Zeichen lang sein")

        # Prüfung auf verdächtige Zeichen
        if any(char in company_name for char in ['<', '>', '{', '}', '[', ']']):
            raise ValidationError("Firmenname enthält ungültige Zeichen")

        return company_name

    def clean_tax_number(self):
        """Validierung der Steuernummer"""
        tax_number = self.cleaned_data.get('tax_number')
        if not tax_number:
            return tax_number

        # Entferne alle Leerzeichen und Sonderzeichen für die Validierung
        cleaned = re.sub(r'[^0-9]', '', tax_number)

        if len(cleaned) < 10:
            raise ValidationError("Steuernummer muss mindestens 10 Ziffern enthalten")

        if len(cleaned) > 13:
            raise ValidationError("Steuernummer darf maximal 13 Ziffern enthalten")

        return tax_number.strip()

    def clean_vat_number(self):
        """Validierung der USt-IdNr."""
        vat_number = self.cleaned_data.get('vat_number')
        if not vat_number:
            return vat_number

        vat_number = vat_number.upper().replace(' ', '')

        # Deutsche USt-IdNr. Validierung
        if vat_number.startswith('DE'):
            if len(vat_number) != 11:
                raise ValidationError("Deutsche USt-IdNr. muss 11 Zeichen lang sein (DE + 9 Ziffern)")

            if not vat_number[2:].isdigit():
                raise ValidationError("Deutsche USt-IdNr. muss nach DE 9 Ziffern enthalten")

        # Österreichische USt-IdNr. Validierung
        elif vat_number.startswith('ATU'):
            if len(vat_number) != 11:
                raise ValidationError("Österreichische USt-IdNr. muss 11 Zeichen lang sein")

        # Schweizer MWST-Nummer
        elif vat_number.startswith('CHE'):
            if len(vat_number) != 12:
                raise ValidationError("Schweizer MWST-Nummer muss 12 Zeichen lang sein")

        return vat_number

    def clean_postal_code(self):
        """Validierung der Postleitzahl"""
        postal_code = self.cleaned_data.get('postal_code')
        country = self.cleaned_data.get('country')

        if not postal_code:
            return postal_code

        # Länder-spezifische PLZ-Validierung
        if country == 'DE' and len(postal_code) != 5:
            raise ValidationError("Deutsche PLZ muss 5 Ziffern haben")
        elif country == 'AT' and len(postal_code) != 4:
            raise ValidationError("Österreichische PLZ muss 4 Ziffern haben")
        elif country == 'CH' and len(postal_code) != 4:
            raise ValidationError("Schweizer PLZ muss 4 Ziffern haben")

        return postal_code

    def clean_email(self):
        """Validierung der E-Mail-Adresse"""
        email = self.cleaned_data.get('email')
        if not email:
            return email

        email = email.lower().strip()

        # Zusätzliche E-Mail-Validierung
        if len(email.split('@')[0]) < 2:
            raise ValidationError("E-Mail-Adresse zu kurz vor dem @-Zeichen")

        # Blacklist für Wegwerf-E-Mail-Domains
        disposable_domains = [
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'throwaway.email'
        ]

        domain = email.split('@')[1] if '@' in email else ''
        if domain.lower() in disposable_domains:
            raise ValidationError("Wegwerf-E-Mail-Adressen sind nicht erlaubt")

        return email

    def clean_phone(self):
        """Validierung der Telefonnummer"""
        phone = self.cleaned_data.get('phone')
        if not phone:
            return phone

        # Entferne alle Leerzeichen für die Validierung
        cleaned_phone = re.sub(r'\s', '', phone)

        # Deutsche Telefonnummer-Validierung
        if not cleaned_phone.startswith('+'):
            if cleaned_phone.startswith('0'):
                # Deutsche Nummer ohne Ländercode
                cleaned_phone = '+49' + cleaned_phone[1:]
            else:
                raise ValidationError("Telefonnummer muss mit + oder 0 beginnen")

        return phone.strip()

    def clean(self):
        """Cross-field Validierung"""
        cleaned_data = super().clean()

        # Prüfe ob Haupt-E-Mail und Kontakt-E-Mail nicht identisch sind
        email = cleaned_data.get('email')
        contact_email = cleaned_data.get('contact_email')

        if email and contact_email and email.lower() == contact_email.lower():
            raise ValidationError({
                'contact_email': 'Die Unternehmens-E-Mail und die Kontakt-E-Mail dürfen nicht identisch sein'
            })

        # Prüfe ob Firmentelefon und Kontakttelefon unterschiedlich sind
        phone = cleaned_data.get('phone')
        contact_phone = cleaned_data.get('contact_phone')

        if phone and contact_phone:
            # Normalisiere Telefonnummern für Vergleich
            normalized_phone = re.sub(r'[\s\-\(\)]', '', phone)
            normalized_contact_phone = re.sub(r'[\s\-\(\)]', '', contact_phone)

            if normalized_phone == normalized_contact_phone:
                self.add_error('contact_phone',
                               'Firmentelefon und Kontakttelefon sollten unterschiedlich sein')

        # Validiere dass Vor- und Nachname nicht identisch sind
        first_name = cleaned_data.get('contact_first_name')
        last_name = cleaned_data.get('contact_last_name')

        if first_name and last_name and first_name.lower() == last_name.lower():
            self.add_error('contact_last_name',
                           'Vor- und Nachname dürfen nicht identisch sein')

        return cleaned_data

    def save(self, commit=True):
        """Speichert die Firmendaten nach erfolgreicher Validierung"""
        if not self.is_valid():
            raise ValueError("Formular ist nicht gültig")

        company_data = {
            # Grunddaten
            'company_name': self.cleaned_data['company_name'],
            'legal_form': self.cleaned_data['legal_form'],
            'tax_number': self.cleaned_data['tax_number'],
            'vat_number': self.cleaned_data.get('vat_number', ''),
            'registration_number': self.cleaned_data.get('registration_number', ''),
            'industry': self.cleaned_data['industry'],

            # Adresse
            'address': {
                'street': self.cleaned_data['street'],
                'postal_code': self.cleaned_data['postal_code'],
                'city': self.cleaned_data['city'],
                'country': self.cleaned_data['country']
            },

            # Kontakte
            'contact_info': {
                'phone': self.cleaned_data['phone'],
                'fax': self.cleaned_data.get('fax', ''),
                'email': self.cleaned_data['email'],
                'website': self.cleaned_data.get('website', '')
            },

            # Ansprechpartner
            'contact_person': {
                'salutation': self.cleaned_data['contact_salutation'],
                'first_name': self.cleaned_data['contact_first_name'],
                'last_name': self.cleaned_data['contact_last_name'],
                'position': self.cleaned_data.get('contact_position', ''),
                'phone': self.cleaned_data.get('contact_phone', ''),
                'email': self.cleaned_data.get('contact_email', '')
            },

            # Zusätzliche Daten
            'description': self.cleaned_data.get('description', ''),
            'newsletter_subscription': self.cleaned_data.get('newsletter', False),
            'terms_accepted': self.cleaned_data['terms_accepted'],
            'source': 'web_form'
        }

        logger.info(f"Preparing company data for: {company_data['company_name']}")
        return company_data