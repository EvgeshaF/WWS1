import datetime
import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from loguru import logger

from company.company_manager import CompanyManager
from company.company_session_views import CompanySessionManager
from company.company_utils import check_mongodb_availability


def company_info(request):
    """Показывает информацию о компании"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Noch keine Firma registriert")
        return redirect('company:register_company_step1')

    # Получаем статистику
    stats = company_manager.get_company_stats()

    # Обрабатываем дополнительные контакты для отображения
    additional_contacts = []
    contacts_data = company.get('additional_contacts_data', '[]')
    if isinstance(contacts_data, str):
        try:
            additional_contacts = json.loads(contacts_data)
        except json.JSONDecodeError:
            logger.warning("Некорректные данные дополнительных контактов в БД")
    elif isinstance(contacts_data, list):
        additional_contacts = contacts_data

    context = {
        'company': company,
        'additional_contacts': additional_contacts,
        'stats': stats
    }
    return render(request, 'company_info.html', context)

def edit_company(request):
    """Редактирование компании - перенаправляет на шаг 1 с предзаполнением"""
    company_manager = CompanyManager()
    existing_company = company_manager.get_company()

    if existing_company:
        # Загружаем существующие данные в сессию
        excluded_fields = {'_id', 'type', 'created_at', 'modified_at'}
        session_data = {k: v for k, v in existing_company.items() if k not in excluded_fields}
        CompanySessionManager.set_session_data(request, session_data)
        logger.info(f"Загружены данные для редактирования компании: {existing_company.get('company_name', 'N/A')}")

    return redirect('company:register_company_step1')

@require_http_methods(["POST"])
def delete_company(request):
    """Удаление информации о компании"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Keine Firma zum Löschen gefunden")
        return redirect('home')

    company_name = company.get('company_name', 'Unbekannte Firma')

    if company_manager.delete_company():
        messages.success(request, f"Firmeninformationen für '{company_name}' erfolgreich gelöscht")
        logger.info(f"Компания '{company_name}' удалена")
        return redirect('home')
    else:
        messages.error(request, "Fehler beim Löschen der Firmeninformationen")
        logger.error(f"Ошибка при удалении компании '{company_name}'")
        return redirect('company:company_info')


@require_http_methods(["POST"])
def set_primary_company(request):
    """Устанавливает компанию как главную (для совместимости со старым API)"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return JsonResponse({'error': 'MongoDB not available'}, status=500)

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        return JsonResponse({'error': 'No company found'}, status=404)

    # В новой системе единственная компания всегда является главной
    try:
        collection = company_manager.get_collection()
        if collection:
            collection.update_one(
                {'type': 'company_info'},
                {'$set': {'is_primary': True, 'modified_at': datetime.datetime.now()}}
            )
            messages.success(request, f"Firma '{company.get('company_name')}' wurde als Hauptfirma festgelegt")
            return JsonResponse({'success': True, 'message': 'Hauptfirma festgelegt'})
    except Exception as e:
        logger.error(f"Ошибка установки главной компании: {e}")
        return JsonResponse({'error': 'Failed to set primary company'}, status=500)

    return JsonResponse({'error': 'Operation failed'}, status=500)
