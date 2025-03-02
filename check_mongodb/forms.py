from django import forms
from django.core.exceptions import ValidationError
import re

class DBSettingsForm(forms.Form):
    username = forms.CharField(label="Имя пользователя", max_length=100, required=True, initial="evgenij")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput, required=True)
    host = forms.CharField(label="Хост", max_length=255, required=True, initial="192.168.178.100")
    port = forms.IntegerField(label="Порт", initial=27017, required=True, min_value=1, max_value=65535)
    auth_source = forms.CharField(label="База аутентификации", max_length=100, required=True, initial="admin")

    def clean_host(self):
        """Проверяем, что host — это корректный IP-адрес"""
        host = self.cleaned_data["host"]
        ip_pattern = re.compile(
            r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"  # IPv4 проверка
        )
        if not ip_pattern.match(host):
            raise ValidationError("Введите корректный IP-адрес (например, 192.168.1.1)")
        return host
