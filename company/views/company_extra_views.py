import datetime
import json

from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from loguru import logger

from company.company_manager import CompanyManager
from company.company_utils import check_mongodb_availability


@require_http_methods(["GET"])
def company_stats_json(request):
    """API endpoint для получения статистики компании в JSON формате"""
    if not check_mongodb_availability():
        return JsonResponse({'error': 'MongoDB not available'}, status=500)

    company_manager = CompanyManager()
    stats = company_manager.get_company_stats()

    if stats is None:
        return JsonResponse({'error': 'No company found'}, status=404)

    # Конвертируем datetime объекты в строки
    if stats.get('created_at'):
        stats['created_at'] = stats['created_at'].isoformat()
    if stats.get('modified_at'):
        stats['modified_at'] = stats['modified_at'].isoformat()

    return JsonResponse(stats)

@require_http_methods(["GET"])
def company_status(request):
    """Проверяет статус компании (есть ли зарегистрированная компания)"""
    if not check_mongodb_availability():
        return JsonResponse({
            'has_company': False,
            'mongodb_available': False,
            'error': 'MongoDB not configured'
        })

    company_manager = CompanyManager()
    has_company = company_manager.has_company()
    company = company_manager.get_company() if has_company else None

    return JsonResponse({
        'has_company': has_company,
        'mongodb_available': True,
        'company_name': company.get('company_name') if company else None,
        'is_primary': company.get('is_primary', True) if company else None
    })

@require_http_methods(["GET"])
def debug_company_data(request):
    """Debug endpoint для просмотра данных компании (только в DEBUG режиме)"""
    from django.conf import settings

    if not settings.DEBUG:
        raise Http404("Not available in production")

    if not check_mongodb_availability():
        return JsonResponse({'error': 'MongoDB not available'}, status=500)

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        return JsonResponse({'error': 'No company found'}, status=404)

    # Конвертируем ObjectId и datetime в строки для JSON
    def serialize_mongo_data(obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif hasattr(obj, '__str__'):
            return str(obj)
        return obj

    # Безопасно сериализуем данные
    safe_company = {}
    for key, value in company.items():
        if key == '_id':
            safe_company[key] = str(value)
        elif isinstance(value, datetime.datetime):
            safe_company[key] = value.isoformat()
        else:
            safe_company[key] = value

    return JsonResponse({
        'company_data': safe_company,
        'stats': company_manager.get_company_stats(),
        'collection_name': company_manager.company_collection_name,
        'debug_info': {
            'mongodb_available': True,
            'collection_exists': company_manager.get_collection() is not None
        }
    }, indent=2)

@require_http_methods(["GET"])
def export_company_data(request):
    """Экспорт данных компании в JSON формате"""
    if not check_mongodb_availability():
        return JsonResponse({'error': 'MongoDB not available'}, status=500)

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        return JsonResponse({'error': 'No company found'}, status=404)

    try:
        # Подготавливаем данные для экспорта
        export_data = {}
        for key, value in company.items():
            if key == '_id':
                export_data[key] = str(value)
            elif isinstance(value, datetime.datetime):
                export_data[key] = value.isoformat()
            else:
                export_data[key] = value

        # Добавляем метаданные экспорта
        export_data['export_metadata'] = {
            'export_date': datetime.datetime.now().isoformat(),
            'export_version': '1.0',
            'system_info': 'Company Registration System'
        }

        response = JsonResponse(export_data, json_dumps_params={'indent': 2})
        response['Content-Disposition'] = f'attachment; filename="company_data_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'

        logger.info(f"Экспорт данных компании '{company.get('company_name', 'Unknown')}'")
        return response

    except Exception as e:
        logger.error(f"Ошибка экспорта данных компании: {e}")
        return JsonResponse({'error': 'Export failed'}, status=500)


@require_http_methods(["POST"])
def import_company_data(request):
    """Импорт данных компании из JSON (для восстановления/миграции)"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return JsonResponse({'error': 'MongoDB not available'}, status=500)

    try:
        # Получаем JSON данные из запроса
        if request.content_type == 'application/json':
            import_data = json.loads(request.body)
        else:
            # Попытка получить из form data
            json_data = request.POST.get('company_data')
            if not json_data:
                return JsonResponse({'error': 'No data provided'}, status=400)
            import_data = json.loads(json_data)

        # Валидируем обязательные поля
        required_fields = ['company_name', 'legal_form']
        for field in required_fields:
            if field not in import_data:
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

        # Очищаем служебные поля импорта
        excluded_fields = {'_id', 'export_metadata', 'created_at', 'modified_at'}
        clean_data = {k: v for k, v in import_data.items() if k not in excluded_fields}

        # Создаем/обновляем компанию
        company_manager = CompanyManager()
        if company_manager.create_or_update_company(clean_data):
            logger.success(f"Импорт данных компании '{clean_data['company_name']}' успешен")
            messages.success(request, f"Daten für Firma '{clean_data['company_name']}' erfolgreich importiert")
            return JsonResponse({'success': True, 'message': 'Import successful'})
        else:
            return JsonResponse({'error': 'Failed to save imported data'}, status=500)

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON при импорте: {e}")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Ошибка импорта данных компании: {e}")
        return JsonResponse({'error': 'Import failed'}, status=500)