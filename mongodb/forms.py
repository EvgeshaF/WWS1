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
