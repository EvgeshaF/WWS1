# home/context_processors.py - ПРОСТОЙ ВАРИАНТ
from loguru import logger


def company_name(request):
    """Простой context processor для получения названия компании и правовой формы"""
    try:
        from company.company_manager import CompanyManager

        company_manager = CompanyManager()
        company = company_manager.get_company()

        if company and company.get('company_name'):
            # Получаем правовую форму и преобразуем в читаемый вид
            legal_form = company.get('legal_form', '')
            legal_form_display = get_legal_form_display(legal_form) if legal_form else ''

            return {
                'company_name': company['company_name'],
                'company_legal_form': legal_form_display
            }
        else:
            return {
                'company_name': 'WWS1',
                'company_legal_form': ''
            }

    except Exception as e:
        logger.error(f"Ошибка получения данных компании: {e}")
        return {
            'company_name': 'WWS1',
            'company_legal_form': ''
        }


def get_legal_form_display(legal_form_code):
    """Преобразует код правовой формы в читаемое название"""
    legal_forms = {
        'gmbh': 'GmbH',
        'ag': 'AG',
        'ug': 'UG',
        'ohg': 'OHG',
        'kg': 'KG',
        'gbr': 'GbR',
        'eg': 'eG',
        'einzelunternehmen': 'Einzelunternehmen',
        'freiberufler': 'Freiberufler',
        'se': 'SE',
        'ltd': 'Ltd.',
        'sonstige': 'Sonstige'
    }
    return legal_forms.get(legal_form_code, legal_form_code)