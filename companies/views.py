# companies/views.py - Views для управления компаниями

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from loguru import logger
import datetime

from .forms import CompanyRegistrationForm
from mongodb.mongodb_config import MongoConfig
from mongodb.mongodb_utils import MongoConnection
from django_ratelimit.decorators import ratelimit


class CompanyManager:
    """Менеджер для работы с компаниями в MongoDB"""

    def __init__(self):
        self.db = MongoConnection.get_database()
        if self.db is None:
            logger.error("База данных недоступна")
            self.companies_collection_name = None
            return

        config = MongoConfig.read_config()
        db_name = config.get('db_name')
        if not db_name:
            logger.error("Имя базы данных не найдено в конфигурации")
            self.companies_collection_name = None
        else:
            self.companies_collection_name = f"{db_name}_companies"
            logger.info(f"Коллекция компаний: {self.companies_collection_name}")

    def get_collection(self):
        """Получает коллекцию компаний с созданием при необходимости"""
        if self.db is None or not self.companies_collection_name:
            return None

        try:
            existing_collections = self.db.list_collection_names()

            if self.companies_collection_name not in existing_collections:
                logger.info(f"Создаем коллекцию компаний: {self.companies_collection_name}")
                collection = self.db.create_collection(self.companies_collection_name)

                # Создаем индексы
                try:
                    collection.create_index("company_name", unique=True, name="idx_company_name_unique")
                    collection.create_index([("is_active", 1), ("deleted", 1)], name="idx_active_not_deleted")
                    collection.create_index([("is_primary", 1), ("deleted", 1)], name="idx_primary_not_deleted")
                    collection.create_index("created_at", name="idx_created_at")
                    logger.success("Индексы для компаний созданы")
                except Exception as e:
                    logger.warning(f"Ошибка создания индексов для компаний: {e}")

            return self.db[self.companies_collection_name]

        except Exception as e:
            logger.error(f"Ошибка получения коллекции компаний: {e}")
            return None

    def create_company(self, company_data):
        """Создает новую компанию"""
        try:
            collection = self.get_collection()
            if collection is None:
                return False

            # Проверяем, что компания с таким именем не существует
            existing_company = collection.find_one({
                'company_name': company_data['company_name'],
                'deleted': {'$ne': True}
            })

            if existing_company:
                logger.error(f"Компания '{company_data['company_name']}' уже существует")
                return False

            # Если это первая компания или установлен флаг is_primary
            if company_data.get('is_primary', False):
                # Снимаем флаг primary с других компаний
                collection.update_many(
                    {'is_primary': True, 'deleted': {'$ne': True}},
                    {'$set': {'is_primary': False, 'modified_at': datetime.datetime.now()}}
                )

            # Проверяем, есть ли вообще активные компании
            active_companies_count = collection.count_documents({
                'deleted': {'$ne': True},
                'is_active': True
            })

            # Если это первая активная компания, делаем её primary
            if active_companies_count == 0:
                company_data['is_primary'] = True
                logger.info("Это первая компания - устанавливаем как primary")

            # Устанавливаем системные поля
            now = datetime.datetime.now()
            company_data.update({
                'created_at': now,
                'modified_at': now,
                'deleted': False,
                'is_active': True
            })

            # Создаем компанию
            result = collection.insert_one(company_data)

            if result.inserted_id:
                logger.success(f"Компания '{company_data['company_name']}' создана с ID: {result.inserted_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Ошибка создания компании: {e}")
            return False

    def has_active_company(self):
        """Проверяет, есть ли активные компании"""
        try:
            collection = self.get_collection()
            if collection is None:
                return False

            count = collection.count_documents({
                'deleted': {'$ne': True},
                'is_active': True
            })

            return count > 0

        except Exception as e:
            logger.error(f"Ошибка проверки активных компаний: {e}")
            return False

    def get_primary_company(self):
        """Возвращает основную компанию"""
        try:
            collection = self.get_collection()
            if collection is None:
                return None

            company = collection.find_one({
                'is_primary': True,
                'deleted': {'$ne': True},
                'is_active': True
            })

            return company

        except Exception as e:
            logger.error(f"Ошибка получения основной компании: {e}")
            return None

    def list_companies(self, include_deleted=False):
        """Возвращает список компаний"""
        try:
            collection = self.get_collection()
            if collection is None:
                return []

            query = {}
            if not include_deleted:
                query['deleted'] = {'$ne': True}

            companies = list(collection.find(query).sort('company_name', 1))
            return companies

        except Exception as e:
            logger.error(f"Ошибка получения списка компаний: {e}")
            return []


@never_cache
def render_toast_response(request):
    """JSON response with messages for HTMX"""
    try:
        storage = messages.get_messages(request)
        messages_list = []

        for message in storage:
            messages_list.append({
                'tags': message.tags,
                'text': str(message),
                'delay': 5000
            })

        response_data = {
            'messages': messages_list,
            'status': 'success' if any(msg['tags'] == 'success' for msg in messages_list) else 'error'
        }

        response = JsonResponse(response_data, safe=False)
        response['Content-Type'] = 'application/json; charset=utf-8'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return response

    except Exception as e:
        logger.error(f"Ошибка создания JSON ответа: {e}")
        return JsonResponse({
            'messages': [{'tags': 'error', 'text': 'Ein unerwarteter Fehler ist aufgetreten', 'delay': 5000}],
            'status': 'error'
        })


@never_cache
def render_with_messages(request, template_name, context, success_redirect=None):
    """Universal function for rendering with HTMX support"""
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


@ratelimit(key='ip', rate='3/m', method='POST')
@require_http_methods(["GET", "POST"])
@never_cache
def register_company(request):
    """Регистрация новой компании"""
    try:
        # Проверяем, что MongoDB настроен
        config = MongoConfig.read_config()
        if not config.get('setup_completed'):
            messages.error(request, "MongoDB muss zuerst konfiguriert werden")
            return redirect('home')

        # Проверяем параметр from_admin для показа специального сообщения
        from_admin = request.GET.get('from_admin') == 'true'

        if request.method == 'POST':
            logger.info("Processing company registration POST request")

            form = CompanyRegistrationForm(request.POST)
            if form.is_valid():
                company_data = form.cleaned_data.copy()

                logger.info(f"Creating company: {company_data['company_name']}")

                # Создаем компанию
                company_manager = CompanyManager()
                if company_manager.create_company(company_data):
                    success_msg = f"Firma '{company_data['company_name']}' wurde erfolgreich registriert!"
                    logger.success(success_msg)
                    messages.success(request, success_msg)

                    # Перенаправляем на главную страницу
                    return render_with_messages(
                        request,
                        'companies/register_company.html',
                        {'form': form, 'from_admin': from_admin},
                        reverse('home')
                    )
                else:
                    messages.error(request, "Fehler beim Registrieren der Firma")
            else:
                logger.error(f"Company form invalid: {form.errors}")
                messages.error(request, "Bitte korrigieren Sie die Formularfehler")

            # Рендерим форму с ошибками
            context = {'form': form, 'from_admin': from_admin}
            return render_with_messages(request, 'companies/register_company.html', context)

        # GET request
        form = CompanyRegistrationForm()
        context = {
            'form': form,
            'from_admin': from_admin
        }
        return render(request, 'companies/register_company.html', context)

    except Exception as e:
        logger.error(f"Error in register_company: {e}")
        messages.error(request, "Ein unerwarteter Fehler ist aufgetreten")
        return redirect('home')


@require_http_methods(["GET"])
@never_cache
def company_list(request):
    """Список компаний"""
    try:
        company_manager = CompanyManager()
        companies = company_manager.list_companies()
        primary_company = company_manager.get_primary_company()

        context = {
            'companies': companies,
            'primary_company': primary_company,
            'companies_count': len(companies)
        }

        return render(request, 'companies/company_list.html', context)

    except Exception as e:
        logger.error(f"Error in company_list: {e}")
        messages.error(request, "Fehler beim Laden der Firmenliste")
        return redirect('home')