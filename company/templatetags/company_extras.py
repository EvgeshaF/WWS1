# company/templatetags/company_extras.py
# Template filter для отображения правовых форм

from django import template

register = template.Library()


@register.filter
def legal_form_display(legal_form_code):
    """Преобразует код правовой формы в человекочитаемое название"""
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

    if not legal_form_code:
        return ''

    return legal_forms.get(legal_form_code, legal_form_code)

# Использование в шаблоне:
# {% load company_extras %}
# {{ legal_form|legal_form_display }}

# Или вы можете просто передавать полное название из view,
# что более эффективно для производительности