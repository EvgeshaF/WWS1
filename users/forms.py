from django import forms
from django.core.validators import RegexValidator
import re


class CreateAdminUserForm(forms.Form):
    """Шаг 1: Основные учетные данные администратора"""

    username = forms.CharField(
        label="Benutzername",
        max_length=50,
        min_length=3,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z][a-zA-Z0-9_]*$',
                message='Benutzername muss mit einem Buchstaben beginnen und darf nur Buchstaben, Zahlen und Unterstriche enthalten'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autofocus': True,
            'placeholder': 'z.B. admin_user',
            'pattern': '[a-zA-Z][a-zA-Z0-9_]*',
            'title': 'Beginnt mit Buchstaben, nur Buchstaben, Zahlen und Unterstriche'
        })
    )

    password = forms.CharField(
        label="Passwort",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sicheres Passwort eingeben'
        })
    )

    password_confirm = forms.CharField(
        label="Passwort bestätigen",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Passwort wiederholen'
        })
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')

        # Проверяем сложность пароля
        if len(password) < 8:
            raise forms.ValidationError("Passwort muss mindestens 8 Zeichen lang sein")

        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Passwort muss mindestens einen Großbuchstaben enthalten")

        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Passwort muss mindestens einen Kleinbuchstaben enthalten")

        if not re.search(r'\d', password):
            raise forms.ValidationError("Passwort muss mindestens eine Ziffer enthalten")

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwörter stimmen nicht überein")

        return cleaned_data


class AdminProfileForm(forms.Form):
    """Шаг 2: Профильные данные администратора"""

    SALUTATION_CHOICES = [
        ('', '-- Auswählen --'),
        ('herr', 'Herr'),
        ('frau', 'Frau'),
        ('divers', 'Divers'),
    ]

    TITLE_CHOICES = [
        ('', '-- Kein Titel --'),
        ('dr', 'Dr.'),
        ('prof', 'Prof.'),
        ('prof_dr', 'Prof. Dr.'),
    ]

    salutation = forms.ChoiceField(
        label="Anrede",
        choices=SALUTATION_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    title = forms.ChoiceField(
        label="Titel",
        choices=TITLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    first_name = forms.CharField(
        label="Vorname",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vorname eingeben'
        })
    )

    last_name = forms.CharField(
        label="Nachname",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nachname eingeben'
        })
    )

    email = forms.EmailField(
        label="E-Mail",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        })
    )

    phone = forms.CharField(
        label="Telefon",
        max_length=20,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[\+]?[0-9\s\-\(\)]{7,20}$',
                message='Ungültiges Telefonformat'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+49 123 456789 (optional)'
        })
    )


class AdminPermissionsForm(forms.Form):
    """Шаг 3: Разрешения и безопасность"""

    # Системные разрешения
    is_super_admin = forms.BooleanField(
        label="Super Administrator",
        required=False,
        initial=True,
        help_text="Hat vollständigen Zugriff auf alle Systemfunktionen",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    can_manage_users = forms.BooleanField(
        label="Benutzer verwalten",
        required=False,
        initial=True,
        help_text="Kann Benutzer erstellen, bearbeiten und löschen",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    can_manage_database = forms.BooleanField(
        label="Datenbank verwalten",
        required=False,
        initial=True,
        help_text="Kann Datenbankeinstellungen ändern und Backups erstellen",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    can_view_logs = forms.BooleanField(
        label="Logs einsehen",
        required=False,
        initial=True,
        help_text="Kann Systemlogs und Audit-Trails einsehen",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    can_manage_settings = forms.BooleanField(
        label="Systemeinstellungen",
        required=False,
        initial=True,
        help_text="Kann globale Systemeinstellungen ändern",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    # Sicherheitseinstellungen
    password_expires = forms.BooleanField(
        label="Passwort läuft ab",
        required=False,
        initial=True,
        help_text="Passwort muss regelmäßig geändert werden (90 Tage)",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    two_factor_required = forms.BooleanField(
        label="Zwei-Faktor-Authentifizierung",
        required=False,
        initial=True,
        help_text="Erhöht die Sicherheit erheblich (empfohlen)",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )