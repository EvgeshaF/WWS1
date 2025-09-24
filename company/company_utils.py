from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render

from mongodb.mongodb_config import MongoConfig


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
    response['Content-Type'] = 'application/json'
    return response


def render_with_messages(request, template_name, context, success_redirect=None):
    """Универсальная функция для рендеринга с поддержкой HTMX"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    if is_htmx:
        response = render_toast_response(request)
        if success_redirect:
            response['HX-Redirect'] = success_redirect
        return response
    else:
        if success_redirect:
            return redirect(success_redirect)
        return render(request, template_name, context)


def check_mongodb_availability():
    """Проверяет доступность MongoDB"""
    config_status = MongoConfig.check_config_completeness()
    return config_status == 'complete'

def get_legal_form_display_name(legal_form_code):
    """Возвращает человекочитаемое название правовой формы"""
    legal_forms = {
        'gmbh': 'GmbH',
        'ag': 'AG',
        'ug': 'UG (haftungsbeschränkt)',
        'ohg': 'OHG',
        'kg': 'KG',
        'gbr': 'GbR',
        'eg': 'eG',
        'einzelunternehmen': 'Einzelunternehmen',
        'freiberufler': 'Freiberufler',
        'se': 'SE (Societas Europaea)',
        'ltd': 'Ltd.',
        'sonstige': 'Sonstige'
    }
    return legal_forms.get(legal_form_code, legal_form_code)

