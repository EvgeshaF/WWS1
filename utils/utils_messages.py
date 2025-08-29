import json
from django.http import HttpResponse
from django.template.loader import render_to_string


def toast_response(content_html: str, message: str, type_: str = "info", delay: int = 4000):
    """
    Универсальная функция для отправки Toast-сообщений с HTMX.

    :param content_html: HTML для подстановки (форма/таблица и т.д.)
    :param message: текст сообщения
    :param type_: тип ('success', 'info', 'warning', 'danger')
    :param delay: задержка показа в мс
    """
    toast_html = render_to_string("partials/toast.html", {
        "message": message,
        "type": type_,
        "delay": delay
    })

    response = HttpResponse(content_html)
    response["HX-Trigger"] = json.dumps({
        "showToast": {"toast_html": toast_html}
    })
    return response
