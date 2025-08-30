from django import forms
from django.core.validators import RegexValidator


class MongoConnectionForm(forms.Form):
    """Форма для настройки соединения с MongoDB"""
    host = forms.CharField(
        label="Host",
        max_length=100,
        initial='ef-soft.local',  # дефолт
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9.-]+$',
                message='Ungültiges Hostformat'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autofocus': True,
            'placeholder': 'zum Beispiel, localhost oder IP'
        })
    )
    port = forms.IntegerField(
        label="Port",
        initial=27017,  # дефолт
        min_value=1,
        max_value=65535,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '27017'
        })
    )


class MongoLoginForm(forms.Form):
    """Форма для авторизации администратора MongoDB"""
    admin_user = forms.CharField(
        label="Serveradministrator",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autofocus': True,
            'placeholder': 'Administrator Benutzername'
        })
    )
    admin_password = forms.CharField(
        label="Administrator Passwort",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Administrator Passwort'
        })
    )
    db_name = forms.CharField(
        label="Datenbankname",
        max_length=50,
        initial='admin',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Standard: admin',
            'readonly': True
        })
    )