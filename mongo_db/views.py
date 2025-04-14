from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .forms import MongoConnectionForm, LoginForm
from .mongo import MongoConnection


def index(request):
    # Check if MongoDB configuration exists
    config_exists = MongoConnection.check_mongo_config_exists()

    if config_exists:
        # Test the connection
        success, message = MongoConnection.test_connection()

        context = {
            'show_login_form': success,
            'show_connection_form': not success,
            'connection_message': message,
            'login_form': LoginForm(),
            'connection_form': MongoConnectionForm(),
        }
    else:
        # Configuration doesn't exist
        context = {
            'show_login_form': False,
            'show_connection_form': True,
            'connection_message': "MongoDB configuration not found",
            'login_form': LoginForm(),
            'connection_form': MongoConnectionForm(),
        }

    return render(request, 'mongo_db/index.html', context)


@require_POST
def save_mongo_config(request):
    form = MongoConnectionForm(request.POST)

    if form.is_valid():
        host = form.cleaned_data['host']
        port = form.cleaned_data['port']
        login = form.cleaned_data['login']
        password = form.cleaned_data['password']
        database = form.cleaned_data['database']

        success, message = MongoConnection.save_connection_config(
            host, port, login, password, database
        )

        if success:
            # Test connection with new configuration
            connection_success, connection_message = MongoConnection.test_connection()

            if connection_success:
                return render(request, 'mongo_db/login_form.html', {
                    'form': LoginForm(),
                    'connection_message': connection_message
                })

        # If we got here, either saving failed or connection test failed
        return render(request, 'mongo_db/connection_form.html', {
            'form': form,
            'connection_message': message if not success else connection_message
        })

    # Form validation failed
    return render(request, 'mongo_db/connection_form.html', {
        'form': form,
        'connection_message': "Invalid form data"
    })


@require_POST
def login(request):
    form = LoginForm(request.POST)

    if form.is_valid():
        # Here you would implement actual login logic
        # For now, just return a success message
        return HttpResponse(
            '<div id="login-result" class="alert alert-success">Login successful!</div>'
        )

    return render(request, 'mongo_db/login_form.html', {'form': form})