from django import forms
import re

class MongoConnectionForm(forms.Form):
    host = forms.CharField(
        label='Host',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'localhost or mongodb.example.com',
            'default': '192.168.178.100'
        }),
        initial='192.168.178.100',
        required=True,
        help_text="Enter the MongoDB host (e.g. localhost, mongodb.example.com)."
    )
    port = forms.IntegerField(
        label='Port',
        initial=27017,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '27017'
        }),
        required=True,
        min_value=1,
        max_value=65535,
        help_text="Port for MongoDB connection (default: 27017)."
    )
    login = forms.CharField(
        label='Login',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        }),
        initial='evgenij',
        required=True,
        help_text="Enter your MongoDB username."
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        initial='16081977',
        required=True,
        help_text="Enter your MongoDB password."
    )
    database = forms.CharField(
        label='Database',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Database name'
        }),
        initial='wws',
        required=True,
        help_text="Enter the name of the MongoDB database."
    )

    # Добавление кастомной валидации для host (IP-адрес или доменное имя)
    def clean_host(self):
        host = self.cleaned_data.get('host')
        # Пример простейшей проверки на формат IP-адреса
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, host) and not re.match(r'^[a-zA-Z0-9.-]+$', host):
            raise forms.ValidationError("Enter a valid IP address or domain name.")
        return host


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        }),
        required=True,
        help_text="Enter your username."
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        required=True,
        help_text="Enter your password."
    )
