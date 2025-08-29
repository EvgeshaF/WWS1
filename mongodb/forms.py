from django import forms

class MongoConnectionForm(forms.Form):
    """Форма для настройки соединения с MongoDB"""
    host = forms.CharField(
        label="Host",
        max_length=100,
        initial='ef-soft.local',  # дефолт
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autofocus': True,
            'placeholder': 'например, localhost или IP'
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
