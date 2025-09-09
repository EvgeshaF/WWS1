# companies/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import make_password
from loguru import logger
import datetime
import json

from .forms import CompanyRegistrationForm
from mongodb.mongodb_config import MongoConfig
from mongodb.mongodb_utils import MongoConnection
from . import language
from django_ratelimit.decorators import ratelimit


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

        logger.info(f"Отправляем JSON ответ с {len(messages_list)} сообщениями")

        response_data = {
            'messages': messages_list,
            'status': 'success' if any(msg['tags'] == 'success' for msg in messages_list) else 'error'
        }

        response = JsonResponse(response_data, safe=False)
        response['Content-Type'] = 'application/json; charset=utf-8'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'

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
        """Получает коллекцию компаний с проверками"""
        if self.db is None or not self.companies_collection_name:
            return None

        try:
            existing_collections = self.db.list_collection_names()

            if self.companies_collection_name not in existing_collections:
                logger.info(f"Создаем коллекцию: {self.companies_collection_name}")
                collection = self.db.create_collection(self.companies_collection_name)

                # Создаем индексы
                try:
                    collection.create_index("company_name", name="idx_company_name")
                    collection.create_index("tax_number", unique=True, name="idx_tax_number_unique")
                    collection.create_index("email", unique=True, name="idx_email_unique")
                    collection.create_index([("is_active", 1), ("deleted", 1)], name="idx_active_not_deleted")
                    collection.create_index("created_at", name="idx_created_at")
                    logger.success("Индексы для коллекции компаний созданы")
                except Exception as e:
                    logger.warning(f"Ошибка создания индексов: {e}")

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

            # Проверяем уникальность
            if self.company_exists(company_data.get('tax_number'), company_data.get('email')):
                logger.warning(f"Компания уже существует: {company_data.get('company_name')}")
                return False

            # Подготавливаем данные
            now = datetime.datetime.now()
            insert_data = company_data.copy()
            insert_data.update({
                'created_at': now,
                'modified_at': now,
                'deleted': False,
                'is_active': True,
                'status': 'pending_approval'  # Ожидает одобрения
            })

            # Вставляем компанию
            result = collection.insert_one(insert_data)

            if result.inserted_id:
                logger.success(f"Компания '{company_data.get('company_name')}' создана с ID: {result.inserted_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Ошибка создания компании: {e}")
            return False

    def company_exists(self, tax_number=None, email=None):
        """Проверяет существование компании по налоговому номеру или email"""
        try:
            collection = self.get_collection()
            if collection is None:
                return False

            query = {'deleted': {'$ne': True}}

            if tax_number:
                query['tax_number'] = tax_number
            elif email:
                query['email'] = email
            else:
                return False

            existing = collection.find_one(query)
            return existing is not None

        except Exception as e:
            logger.error(f"Ошибка проверки существования компании: {e}")
            return False


@ratelimit(key='ip', rate='3/m', method='POST')
@require_http_methods(["GET", "POST"])
@never_cache
def register_company(request):
    """Регистрация новой компании"""
    try:
        # Проверяем, настроен ли MongoDB
        config = MongoConfig.read_config()
        if not config.get('setup_completed'):
            messages.error(request, "System ist noch nicht vollständig konfiguriert")
            return redirect('home')

        if request.method == 'POST':
            logger.info("Обработка POST запроса для регистрации компании")

            form = CompanyRegistrationForm(request.POST)

            if form.is_valid():
                logger.info(f"Форма валидна для компании: {form.cleaned_data.get('company_name')}")

                # Проверяем уникальность
                company_manager = CompanyManager()

                if company_manager.company_exists(
                        tax_number=form.cleaned_data.get('tax_number'),
                        email=form.cleaned_data.get('email')
                ):
                    messages.error(request, "Eine Firma mit dieser Steuernummer oder E-Mail existiert bereits")
                    context = {'form': form, 'text': language.text_company_registration}
                    return render_with_messages(request, 'companies/register_company.html', context)

                # Подготавливаем данные компании
                company_data = {
                    # Основные данные
                    'company_name': form.cleaned_data['company_name'],
                    'legal_form': form.cleaned_data['legal_form'],
                    'tax_number': form.cleaned_data['tax_number'],
                    'vat_number': form.cleaned_data.get('vat_number', ''),
                    'registration_number': form.cleaned_data.get('registration_number', ''),
                    'industry': form.cleaned_data['industry'],

                    # Адрес
                    'address': {
                        'street': form.cleaned_data['street'],
                        'postal_code': form.cleaned_data['postal_code'],
                        'city': form.cleaned_data['city'],
                        'country': form.cleaned_data['country']
                    },

                    # Контакты
                    'contact_info': {
                        'phone': form.cleaned_data['phone'],
                        'fax': form.cleaned_data.get('fax', ''),
                        'email': form.cleaned_data['email'],
                        'website': form.cleaned_data.get('website', '')
                    },

                    # Анспречпартнер
                    'contact_person': {
                        'salutation': form.cleaned_data['contact_salutation'],
                        'first_name': form.cleaned_data['contact_first_name'],
                        'last_name': form.cleaned_data['contact_last_name'],
                        'position': form.cleaned_data.get('contact_position', ''),
                        'phone': form.cleaned_data.get('contact_phone', ''),
                        'email': form.cleaned_data.get('contact_email', '')
                    },

                    # Дополнительно
                    'description': form.cleaned_data.get('description', ''),
                    'newsletter_subscription': form.cleaned_data.get('newsletter', False),
                    'email': form.cleaned_data['email']  # Для уникальности
                }

                # Создаем компанию
                if company_manager.create_company(company_data):
                    # Сохраняем данные регистрации в сессии для подтверждения
                    request.session['registered_company'] = {
                        'name': company_data['company_name'],
                        'email': company_data['email'],
                        'registration_time': datetime.datetime.now().isoformat()
                    }
                    request.session.modified = True

                    success_msg = f"Firma '{company_data['company_name']}' wurde erfolgreich registriert!"
                    logger.success(success_msg)
                    messages.success(request, success_msg)
                    messages.info(request, "Sie erhalten in Kürze eine Bestätigungs-E-Mail mit weiteren Informationen.")

                    return render_with_messages(
                        request,
                        'companies/register_company.html',
                        {'form': form, 'text': language.text_company_registration},
                        reverse('companies:registration_success')
                    )
                else:
                    messages.error(request, "Fehler beim Registrieren der Firma")

            else:
                logger.error(f"Form invalid: {form.errors}")
                messages.error(request, "Formular ist ungültig. Bitte überprüfen Sie die Eingaben.")

            # Форма с ошибками
            context = {'form': form, 'text': language.text_company_registration}
            return render_with_messages(request, 'companies/register_company.html', context)

        # GET запрос
        form = CompanyRegistrationForm()
        context = {'form': form, 'text': language.text_company_registration}
        return render(request, 'companies/register_company.html', context)

    except Exception as e:
        logger.error(f"Ошибка в register_company: {e}")
        messages.error(request, "Ein unerwarteter Fehler ist aufgetreten")
        return redirect('home')


@never_cache
def registration_success(request):
    """Страница успешной регистрации"""
    try:
        registered_company = request.session.get('registered_company')

        if not registered_company:
            messages.warning(request, "Keine Registrierungsdaten gefunden")
            return redirect('companies:register_company')

        context = {
            'company_name': registered_company.get('name', ''),
            'company_email': registered_company.get('email', ''),
            'text': language.text_registration_success
        }

        # Очищаем сессию после показа
        if 'registered_company' in request.session:
            del request.session['registered_company']
            request.session.modified = True

        return render(request, 'companies/registration_success.html', context)

    except Exception as e:
        logger.error(f"Ошибка в registration_success: {e}")
        messages.error(request, "Ein Fehler ist aufgetreten")
        return redirect('home')


@require_http_methods(["GET"])
def company_list(request):
    """Список всех компаний (для администраторов)"""
    try:
        company_manager = CompanyManager()
        collection = company_manager.get_collection()

        if collection is None:
            companies = []
        else:
            # Получаем все активные компании
            companies = list(collection.find(
                {'deleted': {'$ne': True}},
                {'_id': 0}  # Исключаем _id из результата
            ).sort('created_at', -1).limit(50))

        context = {
            'companies': companies,
            'total_count': len(companies),
            'text': language.text_company_list
        }

        return render(request, 'companies/company_list.html', context)

    except Exception as e:
        logger.error(f"Ошибка получения списка компаний: {e}")
        messages.error(request, "Fehler beim Laden der Firmenliste")
        return redirect('home')