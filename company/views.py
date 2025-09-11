# company/views.py - Исправленная версия с обратной совместимостью

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
    """Менеджер для работы с компанией в MongoDB - с обратной совместимостью"""

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
            # Используем старое название коллекции для совместимости
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

                # Создаем только базовые индексы
                try:
                    collection.create_index([("is_active", 1), ("deleted", 1)], name="idx_active_not_deleted")
                    collection.create_index("created_at", name="idx_created_at")
                    collection.create_index("company_name", name="idx_company_name")
                    logger.success("Индексы для компаний созданы")
                except Exception as e:
                    logger.warning(f"Ошибка создания индексов для компаний: {e}")

            return self.db[self.companies_collection_name]

        except Exception as e:
            logger.error(f"Ошибка получения коллекции компаний: {e}")
            return None

    def create_company(self, company_data):
        """Создает компанию"""
        try:
            collection = self.get_collection()
            if collection is None:
                return False

            # Проверяем, что активной компании еще нет (для режима одной компании)
            existing_company = collection.find_one({
                'deleted': {'$ne': True},
                'is_active': True
            })

            if existing_company:
                logger.error("Активная компания уже существует в системе")
                return False

            # Устанавливаем системные поля
            now = datetime.datetime.now()
            company_data.update({
                'created_at': now,
                'modified_at': now,
                'deleted': False,
                'is_active': True,
                'is_primary': True  # Всегда primary для единственной компании
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

    def has_company(self):
        """Проверяет, есть ли активная компания в системе"""
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
            logger.error(f"Ошибка проверки существования компании: {e}")
            return False

    def has_active_company(self):
        """Метод для обратной совместимости - проверяет, есть ли активная компания"""
        return self.has_company()

    def get_company(self):
        """Возвращает активную компанию"""
        try:
            collection = self.get_collection()
            if collection is None:
                return None

            company = collection.find_one({
                'deleted': {'$ne': True},
                'is_active': True
            })

            return company

        except Exception as e:
            logger.error(f"Ошибка получения компании: {e}")
            return None

    def get_primary_company(self):
        """Метод для обратной совместимости - возвращает основную компанию"""
        return self.get_company()

    def list_companies(self, include_deleted=False):
        """Возвращает список компаний (для совместимости)"""
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

    def update_company(self, company_data):
        """Обновляет данные компании"""
        try:
            collection = self.get_collection()
            if collection is None:
                return False

            # Устанавливаем время модификации
            company_data['modified_at'] = datetime.datetime.now()

            # Обновляем единственную активную компанию
            result = collection.update_one(
                {'deleted': {'$ne': True}, 'is_active': True},
                {'$set': company_data}
            )

            if result.modified_count > 0:
                logger.success("Данные компании обновлены")
                return True

            return False

        except Exception as e:
            logger.error(f"Ошибка обновления компании: {e}")
            return False


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
    """Регистрация компании (только если еще не создана)"""
    try:
        # Проверяем, что MongoDB настроен
        config = MongoConfig.read_config()
        if not config.get('setup_completed'):
            messages.error(request, "MongoDB muss zuerst konfiguriert werden")
            return redirect('home')

        company_manager = CompanyManager()

        # Проверяем, что компания еще не создана
        if company_manager.has_company():
            messages.info(request, "Firma ist bereits im System registriert")
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
                if company_manager.create_company(company_data):
                    success_msg = f"Firma '{company_data['company_name']}' wurde erfolgreich registriert!"
                    logger.success(success_msg)
                    messages.success(request, success_msg)

                    # Перенаправляем на главную страницу
                    return render_with_messages(
                        request,
                        'company/register_company.html',
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
            return render_with_messages(request, 'company/register_company.html', context)

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
    """Список компаний (для совместимости - показывает единственную компанию)"""
    try:
        company_manager = CompanyManager()
        company = company_manager.get_company()

        # Создаем список из одной компании для совместимости с шаблонами
        company = [company] if company else []
        primary_company = company

        context = {
            'company': company,
            'primary_company': primary_company,
            'companies_count': len(company),
            'company': company  # Добавляем для совместимости
        }

        return render(request, 'companies/company_list.html', context)

    except Exception as e:
        logger.error(f"Error in company_list: {e}")
        messages.error(request, "Fehler beim Laden der Firmendaten")
        return redirect('home')


@require_http_methods(["GET"])
@never_cache
def company_details(request):
    """Показать детали компании"""
    try:
        company_manager = CompanyManager()
        company = company_manager.get_company()

        if not company:
            messages.warning(request, "Keine Firma im System gefunden")
            return redirect('company:register_company')

        context = {
            'company': company
        }

        return render(request, 'companies/company_details.html', context)

    except Exception as e:
        logger.error(f"Error in company_details: {e}")
        messages.error(request, "Fehler beim Laden der Firmendaten")
        return redirect('home')


@require_http_methods(["GET", "POST"])
@never_cache
def edit_company(request):
    """Редактирование данных компании"""
    try:
        company_manager = CompanyManager()
        company = company_manager.get_company()

        if not company:
            messages.warning(request, "Keine Firma im System gefunden")
            return redirect('company:register_company')

        if request.method == 'POST':
            form = CompanyRegistrationForm(request.POST)
            if form.is_valid():
                company_data = form.cleaned_data.copy()

                if company_manager.update_company(company_data):
                    messages.success(request, "Firmendaten wurden erfolgreich aktualisiert")
                    return redirect('company:company_details')
                else:
                    messages.error(request, "Fehler beim Aktualisieren der Firmendaten")
            else:
                messages.error(request, "Bitte korrigieren Sie die Formularfehler")
        else:
            # Предзаполняем форму данными компании
            initial_data = {key: company.get(key, '') for key in [
                'company_name', 'legal_form', 'commercial_register', 'tax_number', 'vat_id',
                'street', 'postal_code', 'city', 'country', 'email', 'phone', 'fax', 'website',
                'ceo_name', 'contact_person', 'description', 'industry'
            ]}
            form = CompanyRegistrationForm(initial=initial_data)

        context = {
            'form': form,
            'company': company,
            'edit_mode': True
        }

        return render(request, 'companies/edit_company.html', context)

    except Exception as e:
        logger.error(f"Error in edit_company: {e}")
        messages.error(request, "Fehler beim Bearbeiten der Firmendaten")
        return redirect('home')