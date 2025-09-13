from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from loguru import logger
import datetime
import json

from .forms import CompanyRegistrationForm
from mongodb.mongodb_config import MongoConfig
from mongodb.mongodb_utils import MongoConnection


class CompanyManager:
    """Упрощенный менеджер для работы с единственной компанией"""

    def __init__(self):
        self.db = MongoConnection.get_database()
        if self.db is None:
            logger.error("База данных недоступна")
            self.company_collection_name = None
            return

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не найдено в конфигурации")
            self.company_collection_name = None
        else:
            self.company_collection_name = f"{db_name}_company_info"

    def get_collection(self):
        """Получает коллекцию информации о компании"""
        if self.db is None or not self.company_collection_name:
            return None

        try:
            # Проверяем существование коллекции
            existing_collections = self.db.list_collection_names()
            if self.company_collection_name not in existing_collections:
                # Создаем коллекцию
                collection = self.db.create_collection(self.company_collection_name)
                logger.info(f"Коллекция '{self.company_collection_name}' создана")

            return self.db[self.company_collection_name]
        except Exception as e:
            logger.error(f"Ошибка получения коллекции: {e}")
            return None

    def has_company(self):
        """Проверяет, зарегистрирована ли компания"""
        try:
            collection = self.get_collection()
            if collection is None:
                return False

            # Проверяем наличие записи компании
            company = collection.find_one({'type': 'company_info'})
            return company is not None
        except Exception as e:
            logger.error(f"Ошибка проверки наличия компании: {e}")
            return False

    def get_company(self):
        """Получает данные компании"""
        try:
            collection = self.get_collection()
            if collection is None:
                return None

            company = collection.find_one({'type': 'company_info'})
            return company
        except Exception as e:
            logger.error(f"Ошибка получения данных компании: {e}")
            return None

    def get_primary_company(self):
        """Alias для совместимости - возвращает единственную компанию"""
        return self.get_company()

    def create_or_update_company(self, company_data):
        """Создает или обновляет информацию о компании"""
        try:
            collection = self.get_collection()
            if collection is None:
                logger.error("Коллекция недоступна")
                return False

            # Добавляем служебные поля
            now = datetime.datetime.now()
            company_data.update({
                'type': 'company_info',  # Тип записи для идентификации
                'modified_at': now
            })

            # Проверяем, существует ли уже запись
            existing = collection.find_one({'type': 'company_info'})

            if existing:
                # Обновляем существующую запись
                result = collection.update_one(
                    {'type': 'company_info'},
                    {'$set': company_data}
                )
                if result.modified_count > 0:
                    logger.success(f"Информация о компании '{company_data['company_name']}' обновлена")
                    return True
                else:
                    logger.warning("Данные компании не изменились")
                    return True
            else:
                # Создаем новую запись
                company_data['created_at'] = now
                result = collection.insert_one(company_data)
                if result.inserted_id:
                    logger.success(f"Компания '{company_data['company_name']}' зарегистрирована")
                    return True

            return False

        except Exception as e:
            logger.error(f"Ошибка создания/обновления компании: {e}")
            return False

    def delete_company(self):
        """Удаляет информацию о компании (полное удаление)"""
        try:
            collection = self.get_collection()
            if collection is None:
                return False

            result = collection.delete_one({'type': 'company_info'})
            if result.deleted_count > 0:
                logger.success("Информация о компании удалена")
                return True
            else:
                logger.warning("Компания для удаления не найдена")
                return False

        except Exception as e:
            logger.error(f"Ошибка удаления компании: {e}")
            return False

    def get_company_stats(self):
        """Возвращает статистику по компании"""
        try:
            collection = self.get_collection()
            if collection is None:
                return None

            company = collection.find_one({'type': 'company_info'})
            if not company:
                return None

            # Подсчитываем заполненные поля
            filled_fields = 0
            total_fields = 0
            required_fields = ['company_name', 'legal_form', 'street', 'postal_code', 'city', 'country', 'email', 'phone']
            optional_fields = ['commercial_register', 'tax_number', 'vat_id', 'fax', 'website', 'ceo_name', 'contact_person', 'industry', 'description']

            for field in required_fields + optional_fields:
                total_fields += 1
                if field in company and company[field] and str(company[field]).strip():
                    filled_fields += 1

            # Дополнительные контакты
            additional_contacts = company.get('additional_contacts_data', [])
            if isinstance(additional_contacts, str):
                try:
                    additional_contacts = json.loads(additional_contacts)
                except:
                    additional_contacts = []

            return {
                'filled_fields': filled_fields,
                'total_fields': total_fields,
                'completion_percentage': round((filled_fields / total_fields) * 100, 1) if total_fields > 0 else 0,
                'additional_contacts_count': len(additional_contacts) if additional_contacts else 0,
                'created_at': company.get('created_at'),
                'modified_at': company.get('modified_at')
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики компании: {e}")
            return None


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


def register_company(request):
    """Регистрация компании (создание или редактирование единственной) - MODAL VERSION"""
    # Проверяем конфигурацию MongoDB
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    from_admin = request.GET.get('from_admin') == 'true'

    # Получаем существующие данные компании для предзаполнения формы
    existing_company = company_manager.get_company()
    is_editing = existing_company is not None

    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            # Подготавливаем данные компании
            company_data = form.cleaned_data.copy()

            # Обрабатываем дополнительные контакты
            additional_contacts_data = request.POST.get('additional_contacts_data', '[]')
            try:
                # Проверяем и парсим JSON
                contacts = json.loads(additional_contacts_data) if additional_contacts_data else []
                if isinstance(contacts, list):
                    company_data['additional_contacts_data'] = additional_contacts_data
                    logger.info(f"Обработано {len(contacts)} дополнительных контактов")
                else:
                    company_data['additional_contacts_data'] = '[]'
            except json.JSONDecodeError:
                logger.warning("Некорректные данные дополнительных контактов")
                company_data['additional_contacts_data'] = '[]'

            # Сохраняем данные
            if company_manager.create_or_update_company(company_data):
                action = "aktualisiert" if is_editing else "registriert"
                messages.success(request, f"Firma '{company_data['company_name']}' erfolgreich {action}!")

                return render_with_messages(
                    request,
                    'register_company.html',
                    {'form': form, 'from_admin': from_admin, 'is_editing': is_editing},
                    reverse('home')
                )
            else:
                action = "Aktualisieren" if is_editing else "Registrieren"
                messages.error(request, f"Fehler beim {action} der Firma")
        else:
            messages.error(request, "Bitte korrigieren Sie die Fehler im Formular")
            logger.warning(f"Ошибки формы: {form.errors}")

        context = {'form': form, 'from_admin': from_admin, 'is_editing': is_editing}
        return render_with_messages(request, 'register_company.html', context)

    # GET request - предзаполняем форму существующими данными
    initial_data = {}
    if existing_company:
        # Копируем все поля кроме служебных
        excluded_fields = {'_id', 'type', 'created_at', 'modified_at'}
        initial_data = {k: v for k, v in existing_company.items() if k not in excluded_fields}
        logger.info(f"Предзаполнение формы данными компании: {existing_company.get('company_name', 'N/A')}")

    form = CompanyRegistrationForm(initial=initial_data)

    context = {
        'form': form,
        'from_admin': from_admin,
        'is_editing': is_editing,
        'company_name': existing_company.get('company_name', '') if existing_company else '',
        'modal_page': True  # Флаг для модальной страницы
    }

    return render(request, 'register_company.html', context)


def company_info(request):
    """Показывает информацию о компании"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Noch keine Firma registriert")
        return redirect('company:register_company')

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
    """Редактирование компании (алиас для register_company)"""
    logger.info("Перенаправление на редактирование компании")
    return register_company(request)


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