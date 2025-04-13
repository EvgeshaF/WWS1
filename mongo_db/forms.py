from django import forms

class MongoConnectionForm(forms.Form):
    host = forms.CharField(
        label='Host',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'localhost or mongodb.example.com'
        })
    )
    port = forms.IntegerField(
        label='Port',
        initial=27017,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '27017'
        })
    )
    login = forms.CharField(
        label='Login',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    database = forms.CharField(
        label='Database',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Database name'
        })
    )

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
