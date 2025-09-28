# company/forms/step5.py
# Шаг 5: Банковские данные - ОБНОВЛЕНО: Hauptbankverbindung обязательны

from django import forms
from django.core.validators import RegexValidator


class CompanyBankingForm(forms.Form):
    """ОБНОВЛЕНО: Шаг 5 - Банковские данные с обязательными основными полями"""

    # ==================== HAUPTBANKVERBINDUNG (ОБЯЗАТЕЛЬНЫ) ====================
    bank_name = forms.CharField(
        label="Name der Bank",
        max_length=100,
        required=True,  # ИЗМЕНЕНО: Теперь обязательно
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Deutsche Bank AG'
        }),
        error_messages={
            'required': 'Name der Bank ist erforderlich'
        }
    )

    iban = forms.CharField(
        label="IBAN",
        max_length=34,
        required=True,  # ИЗМЕНЕНО: Теперь обязательно
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$',
                message='Ungültiges IBAN-Format (z.B. DE89370400440532013000)'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DE89370400440532013000',
            'style': 'text-transform: uppercase;'
        }),
        error_messages={
            'required': 'IBAN ist erforderlich'
        }
    )

    bic = forms.CharField(
        label="BIC/SWIFT",
        max_length=11,
        required=True,  # ИЗМЕНЕНО: Теперь обязательно
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$',
                message='Ungültiges BIC-Format (z.B. DEUTDEFF)'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DEUTDEFF',
            'style': 'text-transform: uppercase;'
        }),
        error_messages={
            'required': 'BIC/SWIFT ist erforderlich'
        }
    )

    account_holder = forms.CharField(
        label="Kontoinhaber",
        max_length=100,
        required=True,  # ИЗМЕНЕНО: Теперь обязательно
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name des Kontoinhabers'
        }),
        error_messages={
            'required': 'Kontoinhaber ist erforderlich'
        }
    )

    # ==================== ZUSÄTZLICHE INFORMATIONEN (OPTIONAL) ====================
    bank_address = forms.CharField(
        label="Adresse der Bank",
        max_length=200,
        required=False,  # Остается опциональным
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Straße, PLZ Stadt (optional)'
        })
    )

    account_type = forms.ChoiceField(
        label="Kontotyp",
        choices=[
            ('', '-- Auswählen --'),
            ('geschaeft', 'Geschäftskonto'),
            ('haupt', 'Hauptkonto'),
            ('liquiditaet', 'Liquiditätskonto'),
            ('kredit', 'Kreditkonto'),
            ('tagesgeld', 'Tagesgeldkonto'),
            ('sonstige', 'Sonstige'),
        ],
        required=False,  # Остается опциональным
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    # ==================== SEKUNDÄRE BANKVERBINDUNG (OPTIONAL) ====================
    secondary_bank_name = forms.CharField(
        label="Zweitbank (optional)",
        max_length=100,
        required=False,  # Остается опциональным
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Commerzbank AG'
        })
    )

    secondary_iban = forms.CharField(
        label="IBAN (Zweitbank)",
        max_length=34,
        required=False,  # Остается опциональным
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$',
                message='Ungültiges IBAN-Format'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DE89370400440532013001',
            'style': 'text-transform: uppercase;'
        })
    )

    secondary_bic = forms.CharField(
        label="BIC/SWIFT (Zweitbank)",
        max_length=11,
        required=False,  # Остается опциональным
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$',
                message='Ungültiges BIC-Format'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'COBADEFF',
            'style': 'text-transform: uppercase;'
        })
    )

    # ==================== EINSTELLUNGEN (OPTIONAL) ====================
    is_primary_account = forms.BooleanField(
        label="Als Hauptkonto für Rechnungen verwenden",
        required=False,
        initial=True,
        help_text="Diese Bankverbindung wird standardmäßig auf Rechnungen angezeigt",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    enable_sepa = forms.BooleanField(
        label="SEPA-Lastschriftverfahren aktiviert",
        required=False,
        initial=False,
        help_text="Ermöglicht Lastschrifteinzug von Kunden",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    banking_notes = forms.CharField(
        label="Notizen zu Bankverbindungen",
        max_length=500,
        required=False,  # Остается опциональным
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Zusätzliche Informationen zu den Bankverbindungen (optional)'
        })
    )

    def clean_iban(self):
        iban = self.cleaned_data.get('iban', '').replace(' ', '').upper()
        if iban and not self.validate_iban_checksum(iban):
            raise forms.ValidationError('IBAN-Prüfsumme ist ungültig')
        return iban

    def clean_secondary_iban(self):
        iban = self.cleaned_data.get('secondary_iban', '').replace(' ', '').upper()
        if iban and not self.validate_iban_checksum(iban):
            raise forms.ValidationError('IBAN-Prüfsumme ist ungültig')
        return iban

    def validate_iban_checksum(self, iban):
        """Einfache IBAN-Validierung (Mod-97-Prüfung)"""
        if len(iban) < 15:
            return False

        try:
            # Bewege die ersten 4 Zeichen ans Ende
            rearranged = iban[4:] + iban[:4]

            # Ersetze Buchstaben durch Zahlen (A=10, B=11, etc.)
            numeric = ''
            for char in rearranged:
                if char.isdigit():
                    numeric += char
                else:
                    numeric += str(ord(char) - ord('A') + 10)

            # Mod 97 Prüfung
            return int(numeric) % 97 == 1
        except:
            return False


# Для обратной совместимости (legacy forms)
class CompanyRegistrationFormLegacy(forms.Form):
    """Legacy форма для совместимости со старым кодом"""
    pass