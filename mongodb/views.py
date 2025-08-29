from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from loguru import logger

from .forms import MongoConnectionForm
from .mongodb_config import MongoConfig
from .mongodb_utils import MongoConnection
from . import language


def render_toast_response(request):
    """JSON ответ с сообщениями для HTMX"""
    storage = messages.get_messages(request)
    messages_list = []
    for message in storage:
        messages_list.append({
            'tags': message.tags,
            'text': str(message),
            'delay': 5000
        })

    response = JsonResponse({'messages': messages_list})
    # Важно! Устанавливаем правильный Content-Type
    response['Content-Type'] = 'application/json'
    return response


def mongo_connection(request):
    """Форма конфигурации сервера MongoDB (хост, порт)"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    if request.method == 'POST':
        form = MongoConnectionForm(request.POST)
        if form.is_valid():
            host = form.cleaned_data['host']
            try:
                port = int(form.cleaned_data['port'])
            except (ValueError, TypeError):
                messages.error(request, language.mess_form_invalid)
                return render_toast_response(request) if is_htmx else render(
                    request, 'mongodb/connection_form.html',
                    {'form': form, 'text': language.text_server_conf, 'step': 1}
                )

            # Проверяем соединение с сервером
            if MongoConnection.test_connection(host, port):
                # Сохраняем конфигурацию
                MongoConfig.update_config({'host': host, 'port': port})

                mess = f"{host}:{port} — {language.mess_server_ping_success}"
                logger.success(mess)
                messages.success(request, mess)

                if is_htmx:
                    return render_toast_response(request)
                return redirect('home')  # Перенаправляем на главную после успеха
            else:
                # Детальная диагностика для лучшего сообщения об ошибке
                if host == 'ef-soft.local':
                    error_msg = f"{language.mess_server_ping_error}. Überprüfen Sie, ob ef-soft.local erreichbar ist oder verwenden Sie 'localhost'."
                else:
                    error_msg = f"{language.mess_server_ping_error}. Überprüfen Sie, ob MongoDB auf {host}:{port} läuft."

                messages.error(request, error_msg)
                if is_htmx:
                    return render_toast_response(request)
        else:
            messages.error(request, language.mess_form_invalid)
            if is_htmx:
                return render_toast_response(request)

    else:  # GET-запрос
        config = MongoConfig.read_config() or {}

        if config:
            # Если конфиг есть — используем его (с запасными значениями)
            form = MongoConnectionForm(initial={
                'host': config.get('host', 'localhost'),  # Изменено с ef-soft.local на localhost
                'port': config.get('port', 27017),
            })
        else:
            # Если конфиг отсутствует — используем initial из самой формы
            form = MongoConnectionForm()

        # Если конфиг ещё не полный, показываем предупреждение
        if not config.get('host') or not config.get('port'):
            logger.warning(language.mess_server_configuration_warning)
            messages.warning(request, language.mess_server_configuration_warning)
            messages.info(request, "Standardwerte: localhost:27017. Stellen Sie sicher, dass MongoDB läuft.")
            if is_htmx:
                return render_toast_response(request)

    return render(request, 'mongodb/connection_form.html', {
        'form': form,
        'text': language.text_server_conf,
        'step': 1
    })