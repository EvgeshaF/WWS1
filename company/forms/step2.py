from django import forms
from django.core.validators import RegexValidator


class CompanyRegistrationForm(forms.Form):
    """Шаг 2: Регистрационные данные - ОБНОВЛЕНО: ВСЕ ПОЛЯ ОБЯЗАТЕЛЬНЫ"""

    commercial_register = forms.CharField(
        label="Handelsregister",
        max_length=50,
        required=True,  # ИЗМЕНЕНО: теперь обязательно
        validators=[
            RegexValidator(
                regex=r'^(HR[AB]\s*\d+|HRA\s*\d+|HRB\s*\d+)$',
                message='Format: HRA12345 oder HRB12345'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. HRB12345'
        }),
        error_messages={
            'required': 'Handelsregister ist erforderlich'
        }
    )

    tax_number = forms.CharField(
        label="Steuernummer",
        max_length=20,
        required=True,  # ИЗМЕНЕНО: теперь обязательно
        validators=[
            RegexValidator(
                regex=r'^\d{1,3}/\d{3}/\d{4,5}$',
                message="Geben Sie eine gültige Steuernummer ein (Format: 12/345/67890)."
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12/345/67890'
        }),
        error_messages={
            'required': 'Steuernummer ist erforderlich'
        }
    )

    vat_id = forms.CharField(
        label="USt-IdNr.",
        max_length=15,
        required=True,  # ИЗМЕНЕНО: теперь обязательно
        validators=[
            RegexValidator(
                regex=r'^DE\d{9}$',
                message='Format: DE123456789'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DE123456789'
        }),
        error_messages={
            'required': 'USt-IdNr. ist erforderlich'
        }
    )

    tax_id = forms.CharField(
        label="Steuer-ID",
        max_length=11,
        required=True,  # ИЗМЕНЕНО: теперь обязательно
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='11-stellige Steuer-ID erforderlich'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678901'
        }),
        error_messages={
            'required': 'Steuer-ID ist erforderlich'
        }
    )