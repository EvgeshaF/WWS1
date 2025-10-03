

class LoginForm(forms.Form):
    """Форма аутентификации пользователя"""

    username = forms.CharField(
        label="Benutzername",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autofocus': True,
            'placeholder': 'Benutzername eingeben',
            'autocomplete': 'username'
        })
    )

    password = forms.CharField(
        label="Passwort",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Passwort eingeben',
            'autocomplete': 'current-password'
        })
    )

    remember_me = forms.BooleanField(
        label="Angemeldet bleiben",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("Benutzername ist erforderlich")
        return username.strip()

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("Passwort ist erforderlich")
        return password