from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from loguru import logger
import datetime
import json
import re

# Импортируем все формы для многошагового процесса (теперь 5 шагов)
from .forms import (
    CompanyBasicDataForm,
    CompanyRegistrationForm as CompanyRegistrationFormStep2,
    CompanyAddressForm,
    CompanyContactForm,
    CompanyOptionsForm,
    CompanyRegistrationFormLegacy, CompanyRegistrationForm  # Для обратной совместимости
)
from .language import (
    text_company_step1,
    text_company_step2,
    text_company_step3,
    text_company_step4,
    text_company_step5,  # Теперь это финальные настройки (бывший step6)
    company_success_messages,
    company_error_messages
)
from mongodb.mongodb_config import MongoConfig
from mongodb.mongodb_utils import MongoConnection


class CompanySessionManager:
    """Менеджер для управления данными многошагового процесса регистрации"""

    SESSION_KEY = 'company_registration_data'

    @staticmethod
    def get_session_data(request):
        """Получает данные из сессии"""
        return request.session.get(CompanySessionManager.SESSION_KEY, {})

    @staticmethod
    def set_session_data(request, data):
        """Сохраняет данные в сессию"""
        request.session[CompanySessionManager.SESSION_KEY] = data
        request.session.modified = True

    @staticmethod
    def update_session_data(request, step_data):
        """Обновляет данные конкретного шага"""
        session_data = CompanySessionManager.get_session_data(request)
        session_data.update(step_data)
        CompanySessionManager.set_session_data(request, session_data)

    @staticmethod
    def clear_session_data(request):
        """Очищает данные сессии"""
        if CompanySessionManager.SESSION_KEY in request.session:
            del request.session[CompanySessionManager.SESSION_KEY]
            request.session.modified = True

    @staticmethod
    def get_completion_status(request):
        """Возвращает статус завершения шагов (теперь 5 шагов) - ОБНОВЛЕНО для шага 2"""
        session_data = CompanySessionManager.get_session_data(request)
        return {
            'step1_complete': 'company_name' in session_data and 'legal_form' in session_data,
            'step2_complete': (
                    'registration_data_processed' in session_data and
                    'all_registration_fields_complete' in session_data and
                    all([
                        session_data.get('commercial_register'),
                        session_data.get('tax_number'),
                        session_data.get('vat_id'),
                        session_data.get('tax_id')
                    ])
            ),
            'step3_complete': 'street' in session_data and 'city' in session_data,
            'step4_complete': 'email' in session_data and 'phone' in session_data,
            'step5_complete': 'data_protection_consent' in session_data  # Финальный шаг
        }


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
            optional_fields = ['commercial_register', 'tax_number', 'vat_id', 'tax_id', 'fax', 'website', 'ceo_first_name', 'ceo_last_name', 'contact_person_first_name', 'contact_person_last_name', 'industry', 'description']

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


# =============================================================================
# МНОГОШАГОВАЯ РЕГИСТРАЦИЯ КОМПАНИИ (5 ШАГОВ)
# =============================================================================

def register_company(request):
    """Стартовая страница регистрации - перенаправляет на шаг 1"""
    # Очищаем предыдущие данные сессии
    CompanySessionManager.clear_session_data(request)
    logger.info("Начало процесса регистрации компании")
    return redirect('company:register_company_step1')


def register_company_step1(request):
    """Шаг 1: Основные данные компании"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    # Получаем данные из сессии для предзаполнения
    session_data = CompanySessionManager.get_session_data(request)

    if request.method == 'POST':
        form = CompanyBasicDataForm(request.POST)
        if form.is_valid():
            # Сохраняем данные шага в сессию
            step_data = form.cleaned_data.copy()
            CompanySessionManager.update_session_data(request, step_data)

            company_name = step_data.get('company_name', '')
            messages.success(
                request,
                company_success_messages['step1_completed'].format(company_name=company_name)
            )

            return render_with_messages(
                request,
                'register_company_step1.html',
                {'form': form, 'step': 1, 'text': text_company_step1},
                reverse('company:register_company_step2')
            )
        else:
            messages.error(request, company_error_messages['form_submission_error'])
    else:
        # GET запрос - предзаполняем форму данными из сессии
        form = CompanyBasicDataForm(initial=session_data)

    context = {
        'form': form,
        'step': 1,
        'text': text_company_step1
    }
    return render(request, 'register_company_step1.html', context)


def register_company_step2(request):
    """Шаг 2: Регистрационные данные - ОБНОВЛЕНО: ВСЕ ПОЛЯ ОБЯЗАТЕЛЬНЫ с улучшенной валидацией"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    # Проверяем, завершен ли предыдущий шаг
    completion = CompanySessionManager.get_completion_status(request)
    if not completion['step1_complete']:
        messages.warning(request, "Bitte vollenden Sie zuerst Schritt 1")
        return redirect('company:register_company_step1')

    session_data = CompanySessionManager.get_session_data(request)
    company_name = session_data.get('company_name', '')
    legal_form = session_data.get('legal_form', '')

    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)

        # НОВАЯ: Дополнительная валидация для обязательных полей
        additional_errors = []

        # Проверяем, что все обязательные поля заполнены
        required_fields = {
            'commercial_register': 'Handelsregister',
            'tax_number': 'Steuernummer',
            'vat_id': 'USt-IdNr.',
            'tax_id': 'Steuer-ID'
        }

        for field_name, field_label in required_fields.items():
            field_value = request.POST.get(field_name, '').strip()
            if not field_value:
                additional_errors.append(f"{field_label} ist erforderlich")

        # Проверяем форматы полей
        commercial_register = request.POST.get('commercial_register', '').strip()
        if commercial_register and not re.match(r'^(HR[AB]\s*\d+|HRA\s*\d+|HRB\s*\d+)$', commercial_register):
            additional_errors.append("Handelsregister: Format HRA12345 oder HRB12345 erforderlich")

        tax_number = request.POST.get('tax_number', '').strip()
        if tax_number and not re.match(r'^\d{1,3}/\d{3}/\d{4,5}$', tax_number):
            additional_errors.append("Steuernummer: Format 12/345/67890 erforderlich")

        vat_id = request.POST.get('vat_id', '').strip()
        if vat_id and not re.match(r'^DE\d{9}$', vat_id):
            additional_errors.append("USt-IdNr.: Format DE123456789 erforderlich")

        tax_id = request.POST.get('tax_id', '').strip()
        if tax_id and not re.match(r'^\d{11}$', tax_id):
            additional_errors.append("Steuer-ID: 11-stellige Nummer erforderlich")

        # Если есть дополнительные ошибки, добавляем их в форму
        if additional_errors:
            for error in additional_errors:
                messages.error(request, error)
            logger.warning(f"Валидационные ошибки шага 2: {additional_errors}")

        if form.is_valid() and not additional_errors:
            # Сохраняем данные шага в сессию
            step_data = form.cleaned_data.copy()
            step_data['registration_data_processed'] = True
            step_data['all_registration_fields_complete'] = True  # НОВОЕ: флаг полноты
            CompanySessionManager.update_session_data(request, step_data)

            logger.success(f"Шаг 2 завершен для компании '{company_name}': все регистрационные данные валидны")
            messages.success(request, company_success_messages['step2_completed'])

            return render_with_messages(
                request,
                'register_company_step2.html',
                {
                    'form': form, 'step': 2, 'text': text_company_step2,
                    'company_name': company_name, 'legal_form': legal_form
                },
                reverse('company:register_company_step3')
            )
        else:
            # Логируем конкретные ошибки формы
            if form.errors:
                for field, errors in form.errors.items():
                    logger.error(f"Ошибка поля {field}: {errors}")
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

            if additional_errors:
                messages.error(request, "Alle Registrierungsfelder müssen korrekt ausgefüllt werden")
            else:
                messages.error(request, company_error_messages['form_submission_error'])
    else:
        # GET запрос - предзаполняем форму данными из сессии
        form = CompanyRegistrationForm(initial=session_data)

    context = {
        'form': form,
        'step': 2,
        'text': text_company_step2,
        'company_name': company_name,
        'legal_form': legal_form
    }
    return render(request, 'register_company_step2.html', context)


def register_company_step3(request):
    """Шаг 3: Адресные данные"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    # Проверяем предыдущие шаги
    completion = CompanySessionManager.get_completion_status(request)
    if not completion['step1_complete']:
        messages.warning(request, "Bitte vollenden Sie zuerst Schritt 1")
        return redirect('company:register_company_step1')

    session_data = CompanySessionManager.get_session_data(request)
    company_name = session_data.get('company_name', '')
    legal_form = session_data.get('legal_form', '')

    if request.method == 'POST':
        form = CompanyAddressForm(request.POST)
        if form.is_valid():
            step_data = form.cleaned_data.copy()
            CompanySessionManager.update_session_data(request, step_data)

            messages.success(request, company_success_messages['step3_completed'])

            return render_with_messages(
                request,
                'register_company_step3.html',
                {
                    'form': form, 'step': 3, 'text': text_company_step3,
                    'company_name': company_name, 'legal_form': legal_form
                },
                reverse('company:register_company_step4')
            )
        else:
            messages.error(request, company_error_messages['form_submission_error'])
    else:
        form = CompanyAddressForm(initial=session_data)

    context = {
        'form': form,
        'step': 3,
        'text': text_company_step3,
        'company_name': company_name,
        'legal_form': legal_form
    }
    return render(request, 'register_company_step3.html', context)


def register_company_step4(request):
    """Шаг 4: Контактные данные"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    # Проверяем предыдущие шаги
    completion = CompanySessionManager.get_completion_status(request)
    if not completion['step1_complete'] or not completion['step3_complete']:
        messages.warning(request, "Bitte vollenden Sie die vorherigen Schritte")
        return redirect('company:register_company_step1')

    session_data = CompanySessionManager.get_session_data(request)
    company_name = session_data.get('company_name', '')
    legal_form = session_data.get('legal_form', '')

    # Получаем существующие дополнительные контакты из сессии
    existing_additional_contacts = session_data.get('additional_contacts_data', '[]')
    if isinstance(existing_additional_contacts, str):
        try:
            existing_additional_contacts = json.loads(existing_additional_contacts)
        except:
            existing_additional_contacts = []

    if request.method == 'POST':
        form = CompanyContactForm(request.POST)
        if form.is_valid():
            step_data = form.cleaned_data.copy()

            # Обрабатываем дополнительные контакты
            additional_contacts_data = request.POST.get('additional_contacts_data', '[]')
            try:
                contacts = json.loads(additional_contacts_data) if additional_contacts_data else []
                if isinstance(contacts, list):
                    step_data['additional_contacts_data'] = additional_contacts_data
                    logger.info(f"Обработано {len(contacts)} дополнительных контактов")
                else:
                    step_data['additional_contacts_data'] = '[]'
            except json.JSONDecodeError:
                logger.warning("Некорректные данные дополнительных контактов")
                step_data['additional_contacts_data'] = '[]'

            CompanySessionManager.update_session_data(request, step_data)

            # Формируем информацию о контактах для сообщения
            main_contacts = f"{step_data.get('email', '')}, {step_data.get('phone', '')}"
            additional_count = len(contacts) if contacts else 0

            if additional_count > 0:
                contact_info = f"{main_contacts} + {additional_count} zusätzliche"
            else:
                contact_info = main_contacts

            messages.success(
                request,
                company_success_messages['step4_completed'].format(contact_info=contact_info)
            )

            return render_with_messages(
                request,
                'register_company_step4.html',
                {
                    'form': form, 'step': 4, 'text': text_company_step4,
                    'company_name': company_name, 'legal_form': legal_form,
                    'existing_additional_contacts': json.dumps(contacts) if contacts else '[]'
                },
                reverse('company:register_company_step5')
            )
        else:
            messages.error(request, company_error_messages['form_submission_error'])
    else:
        form = CompanyContactForm(initial=session_data)

    context = {
        'form': form,
        'step': 4,
        'text': text_company_step4,
        'company_name': company_name,
        'legal_form': legal_form,
        'existing_additional_contacts': json.dumps(existing_additional_contacts)
    }
    return render(request, 'register_company_step4.html', context)


def register_company_step5(request):
    """Шаг 5: Финальные настройки и создание компании"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    # Проверяем предыдущие шаги
    completion = CompanySessionManager.get_completion_status(request)
    if not completion['step4_complete']:
        messages.warning(request, "Bitte vollenden Sie die vorherigen Schritte")
        return redirect('company:register_company_step4')

    session_data = CompanySessionManager.get_session_data(request)
    company_name = session_data.get('company_name', '')
    legal_form = session_data.get('legal_form', '')
    primary_email = session_data.get('email', '')

    # Подсчитываем контакты
    additional_contacts = session_data.get('additional_contacts_data', '[]')
    if isinstance(additional_contacts, str):
        try:
            additional_contacts = json.loads(additional_contacts)
        except:
            additional_contacts = []

    contact_count = 2  # email + phone
    if session_data.get('fax'):
        contact_count += 1
    if session_data.get('website'):
        contact_count += 1
    contact_count += len(additional_contacts)

    if request.method == 'POST':
        form = CompanyOptionsForm(request.POST)
        if form.is_valid():
            # Объединяем все данные из всех шагов
            final_data = session_data.copy()
            final_data.update(form.cleaned_data)

            # Создаем компанию в базе данных
            company_manager = CompanyManager()
            if company_manager.create_or_update_company(final_data):
                # Очищаем сессию после успешного создания
                CompanySessionManager.clear_session_data(request)

                total_contacts = f"{contact_count} Kontakte"
                success_message = company_success_messages['company_created'].format(
                    company_name=company_name,
                    contact_info=total_contacts
                )
                messages.success(request, success_message)

                return render_with_messages(
                    request,
                    'register_company_step5.html',
                    {
                        'form': form, 'step': 5, 'text': text_company_step5,
                        'company_name': company_name, 'legal_form': legal_form,
                        'primary_email': primary_email, 'contact_count': contact_count
                    },
                    reverse('home')
                )
            else:
                messages.error(request, company_error_messages['company_creation_error'])
        else:
            messages.error(request, company_error_messages['validation_failed'])
    else:
        form = CompanyOptionsForm(initial=session_data)

    context = {
        'form': form,
        'step': 5,
        'text': text_company_step5,
        'company_name': company_name,
        'legal_form': legal_form,
        'primary_email': primary_email,
        'contact_count': contact_count
    }
    return render(request, 'register_company_step5.html', context)


# =============================================================================
# ОСТАЛЬНЫЕ ФУНКЦИИ
# =============================================================================

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


@require_http_methods(["GET"])
def company_validation_check(request):
    """Улучшенная проверка валидности данных компании с учетом обязательных полей шага 2"""
    if not check_mongodb_availability():
        return JsonResponse({'error': 'MongoDB not available'}, status=500)

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        return JsonResponse({'error': 'No company found'}, status=404)

    # Валидируем данные компании
    validation_results = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'completeness': 0,
        'step_status': {
            'step1': {'complete': False, 'errors': []},
            'step2': {'complete': False, 'errors': []},  # НОВОЕ: отдельная валидация шага 2
            'step3': {'complete': False, 'errors': []},
            'step4': {'complete': False, 'errors': []},
            'step5': {'complete': False, 'errors': []}
        }
    }

    # Проверяем обязательные поля по шагам
    step1_fields = {
        'company_name': 'Firmenname',
        'legal_form': 'Rechtsform'
    }

    # ОБНОВЛЕНО: Все поля шага 2 теперь обязательны
    step2_fields = {
        'commercial_register': 'Handelsregister',
        'tax_number': 'Steuernummer',
        'vat_id': 'USt-IdNr.',
        'tax_id': 'Steuer-ID'
    }

    step3_fields = {
        'street': 'Straße',
        'postal_code': 'PLZ',
        'city': 'Stadt',
        'country': 'Land'
    }

    step4_fields = {
        'email': 'E-Mail',
        'phone': 'Telefon'
    }

    all_required_fields = {**step1_fields, **step2_fields, **step3_fields, **step4_fields}

    filled_count = 0
    total_count = len(all_required_fields)

    # Валидируем каждый шаг отдельно
    for step, fields in [('step1', step1_fields), ('step2', step2_fields),
                         ('step3', step3_fields), ('step4', step4_fields)]:
        step_complete = True
        step_errors = []

        for field, label in fields.items():
            if not company.get(field) or not str(company.get(field)).strip():
                step_complete = False
                step_errors.append(f'{label} fehlt')
                validation_results['errors'].append(f'{label} fehlt')
                validation_results['is_valid'] = False
            else:
                filled_count += 1

                # НОВАЯ: Дополнительная валидация форматов для шага 2
                if step == 'step2':
                    field_value = str(company.get(field, '')).strip()
                    if field == 'commercial_register' and not re.match(r'^(HR[AB]\s*\d+|HRA\s*\d+|HRB\s*\d+)$', field_value):
                        step_errors.append(f'{label}: Format HRA12345 oder HRB12345 erforderlich')
                        validation_results['warnings'].append(f'{label}: Ungültiges Format')
                    elif field == 'tax_number' and not re.match(r'^\d{1,3}/\d{3}/\d{4,5}$', field_value):
                        step_errors.append(f'{label}: Format 12/345/67890 erforderlich')
                        validation_results['warnings'].append(f'{label}: Ungültiges Format')
                    elif field == 'vat_id' and not re.match(r'^DE\d{9}$', field_value):
                        step_errors.append(f'{label}: Format DE123456789 erforderlich')
                        validation_results['warnings'].append(f'{label}: Ungültiges Format')
                    elif field == 'tax_id' and not re.match(r'^\d{11}$', field_value):
                        step_errors.append(f'{label}: 11-stellige Nummer erforderlich')
                        validation_results['warnings'].append(f'{label}: Ungültiges Format')

        validation_results['step_status'][step]['complete'] = step_complete
        validation_results['step_status'][step]['errors'] = step_errors

    # Подсчитываем полноту заполнения
    validation_results['completeness'] = round((filled_count / total_count) * 100, 1) if total_count > 0 else 0

    # Дополнительные проверки форматов (существующий код)
    if company.get('email'):
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, company.get('email', '')):
            validation_results['warnings'].append('E-Mail-Format möglicherweise ungültig')

    if company.get('postal_code'):
        if not re.match(r'^[0-9]{5}$', company.get('postal_code', '')):
            validation_results['warnings'].append('PLZ-Format möglicherweise ungültig')

    return JsonResponse(validation_results)


# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

def get_legal_form_display_name(legal_form_code):
    """Возвращает человекочитаемое название правовой формы"""
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
    return legal_forms.get(legal_form_code, legal_form_code)


def validate_registration_data(data):
    """Валидирует регистрационные данные компании"""
    errors = []

    # Проверяем обязательные поля шага 2
    required_fields = {
        'commercial_register': 'Handelsregister',
        'tax_number': 'Steuernummer',
        'vat_id': 'USt-IdNr.',
        'tax_id': 'Steuer-ID'
    }

    for field, label in required_fields.items():
        if not data.get(field) or not str(data[field]).strip():
            errors.append(f"{label} ist erforderlich")

    # Проверяем форматы
    if data.get('commercial_register'):
        if not re.match(r'^(HR[AB]\s*\d+|HRA\s*\d+|HRB\s*\d+)$', data['commercial_register']):
            errors.append("Handelsregister: Format HRA12345 oder HRB12345 erforderlich")

    if data.get('tax_number'):
        if not re.match(r'^\d{1,3}/\d{3}/\d{4,5}$', data['tax_number']):
            errors.append("Steuernummer: Format 12/345/67890 erforderlich")

    if data.get('vat_id'):
        if not re.match(r'^DE\d{9}$', data['vat_id']):
            errors.append("USt-IdNr.: Format DE123456789 erforderlich")

    if data.get('tax_id'):
        if not re.match(r'^\d{11}$', data['tax_id']):
            errors.append("Steuer-ID: 11-stellige Nummer erforderlich")

    return errors