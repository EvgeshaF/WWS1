from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .forms import MongoConnectionForm, LoginForm
from .mongo import MongoConnection


def index(request):
    # Проверка существования конфигурации MongoDB
    config_exists = MongoConnection.check_mongo_config_exists()

    if config_exists:
        # Проверка подключения
        success, message = MongoConnection.test_connection()

        if message:
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)

        context = {
            'show_login_form': success,
            'show_connection_form': not success,
            'login_form': LoginForm(),
            'connection_form': MongoConnectionForm(),
            'page_title': 'Anmelden' if success else 'Servereinstellungen',
        }
    else:
        messages.warning(request, "MongoDB configuration not found")
        context = {
            'show_login_form': False,
            'show_connection_form': True,
            'login_form': LoginForm(),
            'connection_form': MongoConnectionForm(),
            'page_title': 'Servereinstellungen',
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
            connection_success, connection_message = MongoConnection.test_connection()

            if connection_success:
                messages.success(request, connection_message)  # ✅ показываем сообщение
                return redirect('index')

            messages.error(request, connection_message)  # ❌ ошибка подключения
        else:
            messages.error(request, message)  # ❌ ошибка сохранения

    else:
        messages.error(request, "Invalid form data")

    return render(request, 'mongo_db/connection_form.html', {
        'form': form
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