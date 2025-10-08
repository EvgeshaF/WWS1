# ========== views/step3.py - API endpoints ==========

from django.http import JsonResponse
from mongodb.mongodb_utils import MongoConnection
from mongodb.mongodb_config import MongoConfig
from loguru import logger


def search_plz_ajax(request):
    """API: AJAX поиск PLZ для Select2"""
    query = request.GET.get('q', '').strip()
    page = int(request.GET.get('page', 1))
    page_size = 30  # Результатов на страницу

    try:
        db = MongoConnection.get_database()
        config = MongoConfig.read_config()
        db_name = config.get('db_name')

        plz_collection = db[f"{db_name}_basic_address"]

        # Поиск по PLZ коду или названию города
        if query:
            search_filter = {
                '$or': [
                    {'plz_code': {'$regex': f'^{query}', '$options': 'i'}},
                    {'plz_name': {'$regex': query, '$options': 'i'}}
                ],
                'deleted': {'$ne': True}
            }
        else:
            search_filter = {'deleted': {'$ne': True}}

        # Пагинация
        skip = (page - 1) * page_size

        plz_cursor = plz_collection.find(
            search_filter,
            {'plz_code': 1, 'plz_name_long': 1}
        ).sort('plz_code', 1).skip(skip).limit(page_size)

        # Подсчет общего количества
        total_count = plz_collection.count_documents(search_filter)

        results = []
        for plz_doc in plz_cursor:
            results.append({
                'id': plz_doc.get('plz_code', ''),
                'text': plz_doc.get('plz_name_long', '')
            })

        return JsonResponse({
            'results': results,
            'pagination': {
                'more': (page * page_size) < total_count
            }
        })

    except Exception as e:
        logger.error(f"Ошибка AJAX поиска PLZ: {e}")
        return JsonResponse({'results': [], 'pagination': {'more': False}})


def get_city_by_plz(request):
    """API: получение города по PLZ"""
    plz_code = request.GET.get('plz', '').strip()

    if not plz_code:
        return JsonResponse({'error': 'PLZ не указан'}, status=400)

    try:
        db = MongoConnection.get_database()
        config = MongoConfig.read_config()
        db_name = config.get('db_name')

        plz_collection = db[f"{db_name}_basic_address"]

        plz_doc = plz_collection.find_one(
            {'plz_code': plz_code, 'deleted': {'$ne': True}},
            {'plz_name': 1, 'krs_name': 1, 'lan_name': 1}
        )

        if plz_doc:
            return JsonResponse({
                'success': True,
                'city': plz_doc.get('plz_name', ''),
                'district': plz_doc.get('krs_name', ''),
                'state': plz_doc.get('lan_name', '')
            })
        else:
            return JsonResponse({'error': 'PLZ nicht gefunden'}, status=404)

    except Exception as e:
        logger.error(f"Ошибка получения города по PLZ: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def get_plz_by_city(request):
    """API: получение списка PLZ по названию города"""
    city_name = request.GET.get('city', '').strip()

    if not city_name or len(city_name) < 2:
        return JsonResponse({'error': 'Минимум 2 символа для поиска'}, status=400)

    try:
        db = MongoConnection.get_database()
        config = MongoConfig.read_config()
        db_name = config.get('db_name')

        plz_collection = db[f"{db_name}_basic_address"]

        # Ищем города, содержащие введенный текст (регистронезависимый поиск)
        plz_cursor = plz_collection.find(
            {
                'plz_name': {'$regex': city_name, '$options': 'i'},
                'deleted': {'$ne': True}
            },
            {'plz_code': 1, 'plz_name': 1, 'plz_name_long': 1}
        ).sort('plz_code', 1).limit(50)  # Ограничиваем результаты

        results = []
        for plz_doc in plz_cursor:
            results.append({
                'plz_code': plz_doc.get('plz_code', ''),
                'plz_name': plz_doc.get('plz_name', ''),
                'plz_name_long': plz_doc.get('plz_name_long', '')
            })

        if results:
            return JsonResponse({
                'success': True,
                'count': len(results),
                'results': results
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Keine Städte gefunden'
            })

    except Exception as e:
        logger.error(f"Ошибка получения PLZ по городу: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def search_cities_autocomplete(request):
    """API: автокомплит для поиска городов (для datalist)"""
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 2:
        return JsonResponse({'cities': []})

    try:
        db = MongoConnection.get_database()
        config = MongoConfig.read_config()
        db_name = config.get('db_name')

        plz_collection = db[f"{db_name}_basic_address"]

        # Получаем уникальные названия городов
        pipeline = [
            {
                '$match': {
                    'plz_name': {'$regex': f'^{query}', '$options': 'i'},
                    'deleted': {'$ne': True}
                }
            },
            {
                '$group': {
                    '_id': '$plz_name',
                    'count': {'$sum': 1}
                }
            },
            {'$sort': {'_id': 1}},
            {'$limit': 20}
        ]

        result = plz_collection.aggregate(pipeline)
        cities = [doc['_id'] for doc in result]

        return JsonResponse({'cities': cities})

    except Exception as e:
        logger.error(f"Ошибка автокомплита городов: {e}")
        return JsonResponse({'cities': []})
