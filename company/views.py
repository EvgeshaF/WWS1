from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from loguru import logger
import datetime

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
            return False

        except Exception as e:
            logger.error(f"Ошибка удаления компании: {e}")
            return False


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


def register_company(request):
    """Регистрация компании (создание или редактирование единственной)"""
    # Проверяем конфигурацию MongoDB
    config_status = MongoConfig.check_config_completeness()
    if config_status != 'complete':
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

            if company_manager.create_or_update_company(company_data):
                action = "aktualisiert" if is_editing else "registriert"
                messages.success(request, f"Firma '{company_data['company_name']}' erfolgreich {action}!")

                return render_with_messages(
                    request,
                    'company/register_company.html',
                    {'form': form, 'from_admin': from_admin, 'is_editing': is_editing},
                    reverse('home')
                )
            else:
                action = "Aktualisieren" if is_editing else "Registrieren"
                messages.error(request, f"Fehler beim {action} der Firma")
        else:
            messages.error(request, "Bitte korrigieren Sie die Fehler im Formular")

        context = {'form': form, 'from_admin': from_admin, 'is_editing': is_editing}
        return render_with_messages(request, 'company/register_company.html', context)

    # GET request - предзаполняем форму существующими данными
    initial_data = {}
    if existing_company:
        # Копируем все поля кроме служебных
        excluded_fields = {'_id', 'type', 'created_at', 'modified_at'}
        initial_data = {k: v for k, v in existing_company.items() if k not in excluded_fields}

    form = CompanyRegistrationForm(initial=initial_data)
    context = {
        'form': form,
        'from_admin': from_admin,
        'is_editing': is_editing,
        'company_name': existing_company.get('company_name', '') if existing_company else ''
    }
    return render(request, 'company/register_company.html', context)


def company_info(request):
    """Показывает информацию о компании"""
    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        messages.warning(request, "Noch keine Firma registriert")
        return redirect('company:register_company')

    context = {'company': company}
    return render(request, 'company/company_info.html', context)


def edit_company(request):
    """Редактирование компании (алиас для register_company)"""
    return register_company(request)


def delete_company(request):
    """Удаление информации о компании"""
    if request.method == 'POST':
        company_manager = CompanyManager()
        if company_manager.delete_company():
            messages.success(request, "Firmeninformationen erfolgreich gelöscht")
            return redirect('home')
        else:
            messages.error(request, "Fehler beim Löschen der Firmeninformationen")

    return redirect('company:company_info')