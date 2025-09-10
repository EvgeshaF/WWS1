# companies/views.py - ERWEITERTE VERSION mit Einschränkung auf eine Firma

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


class CompanyManager:
    """Erweiterte Verwaltung für Firmen mit Einschränkung auf eine Firma"""

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

                    # NEUER INDEX: Für die Einschränkung auf eine aktive Firma
                    collection.create_index([("is_active", 1), ("deleted", 1), ("is_primary", 1)],
                                            name="idx_primary_company")

                    logger.success("Индексы для коллекции компаний созданы")
                except Exception as e:
                    logger.warning(f"Ошибка создания индексов: {e}")

            return self.db[self.companies_collection_name]

        except Exception as e:
            logger.error(f"Ошибка получения коллекции компаний: {e}")
            return None

    def has_active_company(self) -> bool:
        """
        Prüft, ob bereits eine aktive Firma registriert ist

        Returns:
            bool: True wenn bereits eine aktive Firma existiert
        """
        try:
            collection = self.get_collection()
            if collection is None:
                return False

            # Zählt aktive, nicht gelöschte Firmen
            active_companies_count = collection.count_documents({
                'is_active': True,
                'deleted': {'$ne': True}
            })

            logger.info(f"Anzahl aktiver Firmen: {active_companies_count}")
            return active_companies_count > 0

        except Exception as e:
            logger.error(f"Fehler beim Prüfen auf bestehende Firma: {e}")
            return False

    def get_primary_company(self) -> dict:
        """
        Holt die primäre (einzige) aktive Firma

        Returns:
            dict: Firmendaten oder None
        """
        try:
            collection = self.get_collection()
            if collection is None:
                return None

            primary_company = collection.find_one({
                'is_active': True,
                'deleted': {'$ne': True}
            }, sort=[('created_at', 1)])  # Erste registrierte Firma

            return primary_company

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der primären Firma: {e}")
            return None

    def create_company(self, company_data):
        """
        Erstellt eine neue Firma (nur wenn noch keine existiert)

        Args:
            company_data (dict): Firmendaten

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            collection = self.get_collection()
            if collection is None:
                return False, "Datenbankfehler"

            # KRITISCHE PRÜFUNG: Gibt es bereits eine aktive Firma?
            if self.has_active_company():
                existing_company = self.get_primary_company()
                company_name = existing_company.get('company_name', 'Unbekannt')

                logger.warning(f"Versuch, zweite Firma zu registrieren. Existierende Firma: {company_name}")
                return False, f"Es ist bereits eine Firma registriert: '{company_name}'. " \
                              f"Das System unterstützt nur eine Firma pro Installation."

            # Prüfung auf doppelte Steuernummer oder E-Mail (zusätzliche Sicherheit)
            if self.company_exists(company_data.get('tax_number'), company_data.get('email')):
                logger.warning(f"Firma mit gleichen Daten bereits vorhanden")
                return False, "Eine Firma mit dieser Steuernummer oder E-Mail existiert bereits"

            # Bereite Daten vor
            now = datetime.datetime.now()
            insert_data = company_data.copy()
            insert_data.update({
                'created_at': now,
                'modified_at': now,
                'deleted': False,
                'is_active': True,
                'is_primary': True,  # NEU: Markiert als primäre Firma
                'status': 'active',  # Sofort aktiv (da es nur eine gibt)
                'registration_source': 'web_form',
                'company_id': 1  # NEU: Eindeutige ID (immer 1 für die einzige Firma)
            })

            # Firma einfügen
            result = collection.insert_one(insert_data)

            if result.inserted_id:
                logger.success(f"Einzige Firma '{company_data.get('company_name')}' erfolgreich registriert mit ID: {result.inserted_id}")
                return True, f"Firma '{company_data.get('company_name')}' wurde erfolgreich als primäre Firma registriert"

            return False, "Unbekannter Fehler beim Speichern"

        except Exception as e:
            logger.error(f"Kritischer Fehler beim Erstellen der Firma: {e}")
            return False, f"Systemfehler: {str(e)}"

    def update_company(self, company_data):
        """
        Aktualisiert die bestehende (einzige) Firma

        Args:
            company_data (dict): Neue Firmendaten

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            collection = self.get_collection()
            if collection is None:
                return False, "Datenbankfehler"

            # Finde die bestehende Firma
            existing_company = self.get_primary_company()
            if not existing_company:
                return False, "Keine Firma zum Aktualisieren gefunden"

            # Bereite Update-Daten vor
            update_data = company_data.copy()
            update_data.update({
                'modified_at': datetime.datetime.now(),
                'last_updated_by': 'admin'  # TODO: Echter Benutzer
            })

            # Aktualisiere die Firma
            result = collection.update_one(
                {'_id': existing_company['_id']},
                {'$set': update_data}
            )

            if result.modified_count > 0:
                logger.success(f"Firma '{existing_company.get('company_name')}' erfolgreich aktualisiert")
                return True, f"Firma erfolgreich aktualisiert"

            return False, "Keine Änderungen vorgenommen"

        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der Firma: {e}")
            return False, f"Fehler beim Aktualisieren: {str(e)}"

    def company_exists(self, tax_number=None, email=None):
        """Prüft Existenz anhand Steuernummer oder E-Mail"""
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
            logger.error(f"Fehler bei der Existenzprüfung: {e}")
            return False

    def delete_company(self, soft_delete=True):
        """
        Löscht die einzige Firma (Soft- oder Hard-Delete)

        Args:
            soft_delete (bool): Wenn True, nur als gelöscht markieren

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            collection = self.get_collection()
            if collection is None:
                return False, "Datenbankfehler"

            existing_company = self.get_primary_company()
            if not existing_company:
                return False, "Keine Firma zum Löschen gefunden"

            company_name = existing_company.get('company_name', 'Unbekannt')

            if soft_delete:
                # Soft Delete: Als gelöscht markieren
                result = collection.update_one(
                    {'_id': existing_company['_id']},
                    {
                        '$set': {
                            'deleted': True,
                            'deleted_at': datetime.datetime.now(),
                            'is_active': False,
                            'status': 'deleted'
                        }
                    }
                )
                success = result.modified_count > 0
                action = "als gelöscht markiert"
            else:
                # Hard Delete: Komplett entfernen
                result = collection.delete_one({'_id': existing_company['_id']})
                success = result.deleted_count > 0
                action = "vollständig gelöscht"

            if success:
                logger.success(f"Firma '{company_name}' wurde {action}")
                return True, f"Firma '{company_name}' wurde erfolgreich {action}"

            return False, "Löschung fehlgeschlagen"

        except Exception as e:
            logger.error(f"Fehler beim Löschen der Firma: {e}")
            return False, f"Fehler beim Löschen: {str(e)}"

    def get_company_stats(self):
        """
        Holt Statistiken über die Firma

        Returns:
            dict: Statistiken
        """
        try:
            collection = self.get_collection()
            if collection is None:
                return {}

            total_count = collection.count_documents({})
            active_count = collection.count_documents({'is_active': True, 'deleted': {'$ne': True}})
            deleted_count = collection.count_documents({'deleted': True})

            primary_company = self.get_primary_company()

            stats = {
                'total_companies': total_count,
                'active_companies': active_count,
                'deleted_companies': deleted_count,
                'has_primary_company': primary_company is not None,
                'primary_company_name': primary_company.get('company_name') if primary_company else None,
                'registration_allowed': active_count == 0  # Neue Registrierung nur erlaubt wenn keine aktive Firma
            }

            return stats

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Statistiken: {e}")
            return {}


# ==================== ERWEITERTE VIEW FUNCTIONS ====================

# companies/views.py - ОБНОВЛЕННАЯ ФУНКЦИЯ register_company

@ratelimit(key='ip', rate='3/m', method='POST')
@require_http_methods(["GET", "POST"])
@never_cache
def register_company(request):
    """Firmenregistrierung с проверкой завершенности настройки системы"""
    try:
        # Проверяем, что MongoDB кonfigурiert
        config = MongoConfig.read_config()
        if not config.get('setup_completed'):
            messages.error(request, "System ist noch nicht vollständig konfiguriert")
            return redirect('home')

        # НОВАЯ ПРОВЕРКА: есть ли администраторы в системе
        from users.user_utils import UserManager
        user_manager = UserManager()
        admin_count = user_manager.get_admin_count()

        if admin_count == 0:
            messages.warning(request, "Bitte erstellen Sie zuerst einen Administrator")
            return redirect('users:create_admin_step1')

        company_manager = CompanyManager()

        # КРИТИЧЕСКАЯ ПРОВЕРКА: Bereits registrierte Firma?
        if company_manager.has_active_company():
            existing_company = company_manager.get_primary_company()
            company_name = existing_company.get('company_name', 'Unbekannt')

            logger.warning(f"Versuch der Neuregistrierung blockiert. Existierende Firma: {company_name}")

            messages.info(
                request,
                f"Firma '{company_name}' ist bereits registriert. "
                f"Das System ist vollständig konfiguriert."
            )

            # Umleitung zur Hauptseite - система полностью настроена
            return redirect('home')

        if request.method == 'POST':
            logger.info("Verarbeitung der Firmenregistrierung")

            form = CompanyRegistrationForm(request.POST)

            if form.is_valid():
                logger.info(f"Formular gültig für Firma: {form.cleaned_data.get('company_name')}")

                # Firmendaten vorbereiten
                company_data = {
                    # Grunddaten
                    'company_name': form.cleaned_data['company_name'],
                    'legal_form': form.cleaned_data['legal_form'],
                    'tax_number': form.cleaned_data['tax_number'],
                    'vat_number': form.cleaned_data.get('vat_number', ''),
                    'registration_number': form.cleaned_data.get('registration_number', ''),
                    'industry': form.cleaned_data['industry'],

                    # Adresse
                    'address': {
                        'street': form.cleaned_data['street'],
                        'postal_code': form.cleaned_data['postal_code'],
                        'city': form.cleaned_data['city'],
                        'country': form.cleaned_data['country']
                    },

                    # Kontakte
                    'contact_info': {
                        'phone': form.cleaned_data['phone'],
                        'fax': form.cleaned_data.get('fax', ''),
                        'email': form.cleaned_data['email'],
                        'website': form.cleaned_data.get('website', '')
                    },

                    # Ansprechpartner
                    'contact_person': {
                        'salutation': form.cleaned_data['contact_salutation'],
                        'first_name': form.cleaned_data['contact_first_name'],
                        'last_name': form.cleaned_data['contact_last_name'],
                        'position': form.cleaned_data.get('contact_position', ''),
                        'phone': form.cleaned_data.get('contact_phone', ''),
                        'email': form.cleaned_data.get('contact_email', '')
                    },

                    # Zusätzliche Daten
                    'description': form.cleaned_data.get('description', ''),
                    'newsletter_subscription': form.cleaned_data.get('newsletter', False),
                    'email': form.cleaned_data['email']  # Для Einzigartigkeit
                }

                # Firma erstellen
                success, message = company_manager.create_company(company_data)

                if success:
                    # Erfolgreiche Registrierung - СИСТЕМА ПОЛНОСТЬЮ НАСТРОЕНА
                    request.session['registered_company'] = {
                        'name': company_data['company_name'],
                        'email': company_data['email'],
                        'registration_time': datetime.datetime.now().isoformat()
                    }
                    request.session.modified = True

                    logger.success(message)
                    messages.success(request, message)
                    messages.success(
                        request,
                        "🎉 System ist jetzt vollständig konfiguriert und einsatzbereit!"
                    )

                    # ПЕРЕНАПРАВЛЯЕМ НА ГЛАВНУЮ СТРАНИЦУ - всё готово!
                    return render_with_messages(
                        request,
                        'companies/register_company.html',
                        {'form': form, 'text': language.text_company_registration},
                        reverse('home')  # ИЗМЕНЕНО: теперь на главную после успеха
                    )
                else:
                    # Registrierung fehlgeschlagen
                    messages.error(request, message)

            else:
                logger.error(f"Formular ungültig: {form.errors}")
                messages.error(request, "Formular ist ungültig. Bitte überprüfen Sie die Eingaben.")

            # Formular mit Fehlern anzeigen
            context = {'form': form, 'text': language.text_company_registration}
            return render_with_messages(request, 'companies/register_company.html', context)

        # GET-Anfrage - показываем форму регистрации
        form = CompanyRegistrationForm()

        # Проверяем, идет ли пользователь после создания админа
        came_from_admin_creation = request.GET.get('from_admin') == 'true'
        if came_from_admin_creation:
            messages.info(
                request,
                "Administrator erfolgreich erstellt! Jetzt registrieren Sie Ihre Firma, um die Systemkonfiguration abzuschließen."
            )

        context = {
            'form': form,
            'text': language.text_company_registration,
            'came_from_admin': came_from_admin_creation
        }
        return render(request, 'companies/register_company.html', context)

    except Exception as e:
        logger.error(f"Fehler bei der Firmenregistrierung: {e}")
        messages.error(request, "Ein unerwarteter Fehler ist aufgetreten")
        return redirect('home')

# Дополнительные методы для companies/views.py

@require_http_methods(["GET"])
def company_details(request):
    """Показывает детали зарегистрированной компании"""
    try:
        company_manager = CompanyManager()

        if not company_manager.has_active_company():
            messages.info(request, "Noch keine Firma registriert.")
            return redirect('companies:register_company')

        primary_company = company_manager.get_primary_company()
        stats = company_manager.get_company_stats()

        context = {
            'company': primary_company,
            'stats': stats,
            'text': language.text_company_details
        }

        return render(request, 'companies/company_details.html', context)

    except Exception as e:
        logger.error(f"Fehler beim Anzeigen der Firmendetails: {e}")
        messages.error(request, "Fehler beim Laden der Firmendaten")
        return redirect('home')


@ratelimit(key='ip', rate='3/m', method='POST')
@require_http_methods(["GET", "POST"])
@never_cache
def company_edit(request):
    """Редактирование данных компании"""
    try:
        company_manager = CompanyManager()

        if not company_manager.has_active_company():
            messages.error(request, "Keine Firma zum Bearbeiten gefunden")
            return redirect('companies:register_company')

        primary_company = company_manager.get_primary_company()

        if request.method == 'POST':
            # Загружаем форму с существующими данными
            form_data = {
                'company_name': request.POST.get('company_name'),
                'legal_form': request.POST.get('legal_form'),
                'tax_number': request.POST.get('tax_number'),
                'vat_number': request.POST.get('vat_number', ''),
                'registration_number': request.POST.get('registration_number', ''),
                'industry': request.POST.get('industry'),
                'street': request.POST.get('street'),
                'postal_code': request.POST.get('postal_code'),
                'city': request.POST.get('city'),
                'country': request.POST.get('country'),
                'phone': request.POST.get('phone'),
                'fax': request.POST.get('fax', ''),
                'email': request.POST.get('email'),
                'website': request.POST.get('website', ''),
                'contact_salutation': request.POST.get('contact_salutation'),
                'contact_first_name': request.POST.get('contact_first_name'),
                'contact_last_name': request.POST.get('contact_last_name'),
                'contact_position': request.POST.get('contact_position', ''),
                'contact_phone': request.POST.get('contact_phone', ''),
                'contact_email': request.POST.get('contact_email', ''),
                'description': request.POST.get('description', ''),
                'newsletter': request.POST.get('newsletter') == 'on'
            }

            form = CompanyRegistrationForm(form_data)

            if form.is_valid():
                # Подготавливаем обновленные данные
                updated_data = {
                    'company_name': form.cleaned_data['company_name'],
                    'legal_form': form.cleaned_data['legal_form'],
                    'tax_number': form.cleaned_data['tax_number'],
                    'vat_number': form.cleaned_data.get('vat_number', ''),
                    'registration_number': form.cleaned_data.get('registration_number', ''),
                    'industry': form.cleaned_data['industry'],
                    'address': {
                        'street': form.cleaned_data['street'],
                        'postal_code': form.cleaned_data['postal_code'],
                        'city': form.cleaned_data['city'],
                        'country': form.cleaned_data['country']
                    },
                    'contact_info': {
                        'phone': form.cleaned_data['phone'],
                        'fax': form.cleaned_data.get('fax', ''),
                        'email': form.cleaned_data['email'],
                        'website': form.cleaned_data.get('website', '')
                    },
                    'contact_person': {
                        'salutation': form.cleaned_data['contact_salutation'],
                        'first_name': form.cleaned_data['contact_first_name'],
                        'last_name': form.cleaned_data['contact_last_name'],
                        'position': form.cleaned_data.get('contact_position', ''),
                        'phone': form.cleaned_data.get('contact_phone', ''),
                        'email': form.cleaned_data.get('contact_email', '')
                    },
                    'description': form.cleaned_data.get('description', ''),
                    'newsletter_subscription': form.cleaned_data.get('newsletter', False)
                }

                success, message = company_manager.update_company(updated_data)

                if success:
                    messages.success(request, message)
                    return redirect('companies:company_details')
                else:
                    messages.error(request, message)
            else:
                messages.error(request, "Bitte korrigieren Sie die Formularfehler")

        else:
            # GET request - заполняем форму существующими данными
            initial_data = {
                'company_name': primary_company.get('company_name', ''),
                'legal_form': primary_company.get('legal_form', ''),
                'tax_number': primary_company.get('tax_number', ''),
                'vat_number': primary_company.get('vat_number', ''),
                'registration_number': primary_company.get('registration_number', ''),
                'industry': primary_company.get('industry', ''),
            }

            # Добавляем адрес
            address = primary_company.get('address', {})
            initial_data.update({
                'street': address.get('street', ''),
                'postal_code': address.get('postal_code', ''),
                'city': address.get('city', ''),
                'country': address.get('country', ''),
            })

            # Добавляем контакты
            contact_info = primary_company.get('contact_info', {})
            initial_data.update({
                'phone': contact_info.get('phone', ''),
                'fax': contact_info.get('fax', ''),
                'email': contact_info.get('email', ''),
                'website': contact_info.get('website', ''),
            })

            # Добавляем контактное лицо
            contact_person = primary_company.get('contact_person', {})
            initial_data.update({
                'contact_salutation': contact_person.get('salutation', ''),
                'contact_first_name': contact_person.get('first_name', ''),
                'contact_last_name': contact_person.get('last_name', ''),
                'contact_position': contact_person.get('position', ''),
                'contact_phone': contact_person.get('phone', ''),
                'contact_email': contact_person.get('email', ''),
            })

            # Дополнительные поля
            initial_data.update({
                'description': primary_company.get('description', ''),
                'newsletter': primary_company.get('newsletter_subscription', False)
            })

            form = CompanyRegistrationForm(initial=initial_data)

        context = {
            'form': form,
            'text': language.text_company_edit,
            'company': primary_company
        }

        return render(request, 'companies/company_edit.html', context)

    except Exception as e:
        logger.error(f"Fehler beim Bearbeiten der Firmendaten: {e}")
        messages.error(request, "Fehler beim Laden der Bearbeitungsseite")
        return redirect('companies:company_details')


@ratelimit(key='ip', rate='2/m', method='POST')
@require_http_methods(["GET", "POST"])
@never_cache
def company_delete(request):
    """Удаление компании с подтверждением"""
    try:
        company_manager = CompanyManager()

        if not company_manager.has_active_company():
            messages.error(request, "Keine Firma zum Löschen gefunden")
            return redirect('home')

        primary_company = company_manager.get_primary_company()
        company_name = primary_company.get('company_name', 'Unbekannt')

        if request.method == 'POST':
            # Проверяем подтверждение
            confirmation_name = request.POST.get('confirmation_name', '').strip()

            if confirmation_name != company_name:
                messages.error(request, "Firmenname stimmt nicht überein")
                context = {
                    'company': primary_company,
                    'text': language.text_company_delete
                }
                return render(request, 'companies/company_delete.html', context)

            # Выполняем удаление
            success, message = company_manager.delete_company(soft_delete=True)

            if success:
                # Очищаем сессию если есть
                if 'registered_company' in request.session:
                    del request.session['registered_company']
                    request.session.modified = True

                messages.success(request, message)
                messages.info(request, "Sie können jetzt eine neue Firma registrieren")
                return redirect('companies:register_company')
            else:
                messages.error(request, message)

        # GET request - показываем форму подтверждения
        context = {
            'company': primary_company,
            'text': language.text_company_delete
        }

        return render(request, 'companies/company_delete.html', context)

    except Exception as e:
        logger.error(f"Fehler beim Löschen der Firma: {e}")
        messages.error(request, "Fehler beim Löschen der Firma")
        return redirect('companies:company_details')


@require_http_methods(["GET"])
def company_status_api(request):
    """API endpoint для получения статуса компании"""
    try:
        company_manager = CompanyManager()
        stats = company_manager.get_company_stats()

        if company_manager.has_active_company():
            primary_company = company_manager.get_primary_company()
            response_data = {
                'has_company': True,
                'company_name': primary_company.get('company_name', ''),
                'company_email': primary_company.get('contact_info', {}).get('email', ''),
                'registration_date': primary_company.get('created_at').isoformat() if primary_company.get('created_at') else None,
                'stats': stats,
                'status': 'active'
            }
        else:
            response_data = {
                'has_company': False,
                'company_name': None,
                'stats': stats,
                'status': 'not_registered'
            }

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Firmenstatus: {e}")
        return JsonResponse({
            'error': 'Fehler beim Abrufen des Status',
            'has_company': False,
            'status': 'error'
        }, status=500)


@require_http_methods(["POST"])
def validate_company_data(request):
    """API endpoint для валидации данных компании"""
    try:
        # Получаем данные из запроса
        field_name = request.POST.get('field_name')
        field_value = request.POST.get('field_value', '').strip()

        if not field_name or not field_value:
            return JsonResponse({
                'is_valid': False,
                'error': 'Feldname und Wert sind erforderlich'
            })

        # Выполняем валидацию в зависимости от поля
        is_valid = True
        error_message = ''

        if field_name == 'company_name':
            if len(field_value) < 2:
                is_valid = False
                error_message = 'Firmenname muss mindestens 2 Zeichen lang sein'
            elif len(field_value) > 200:
                is_valid = False
                error_message = 'Firmenname darf maximal 200 Zeichen lang sein'

        elif field_name == 'tax_number':
            import re
            clean_number = re.sub(r'[^0-9]', '', field_value)
            if len(clean_number) < 10:
                is_valid = False
                error_message = 'Steuernummer muss mindestens 10 Ziffern enthalten'
            elif not re.match(r'^[0-9\/\-\s]+$', field_value):
                is_valid = False
                error_message = 'Ungültiges Format der Steuernummer'

        elif field_name == 'email':
            import re
            email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_pattern, field_value):
                is_valid = False
                error_message = 'Ungültiges E-Mail-Format'

        elif field_name == 'postal_code':
            if not field_value.isdigit() or len(field_value) not in [4, 5, 6]:
                is_valid = False
                error_message = 'PLZ muss 4-6 Ziffern enthalten'

        return JsonResponse({
            'is_valid': is_valid,
            'error': error_message,
            'field_name': field_name
        })

    except Exception as e:
        logger.error(f"Fehler bei der Feldvalidierung: {e}")
        return JsonResponse({
            'is_valid': False,
            'error': 'Validierungsfehler aufgetreten'
        }, status=500)

def render_toast_response(request):
    """JSON-Antwort mit Nachrichten für HTMX"""
    try:
        storage = messages.get_messages(request)
        messages_list = []

        for message in storage:
            messages_list.append({
                'tags': message.tags,
                'text': str(message),
                'delay': 5000
            })

        logger.info(f"Sende JSON-Antwort mit {len(messages_list)} Nachrichten")

        response_data = {
            'messages': messages_list,
            'status': 'success' if any(msg['tags'] == 'success' for msg in messages_list) else 'error'
        }

        response = JsonResponse(response_data, safe=False)
        response['Content-Type'] = 'application/json; charset=utf-8'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'

        return response

    except Exception as e:
        logger.error(f"Fehler beim Erstellen der JSON-Antwort: {e}")
        return JsonResponse({
            'messages': [{'tags': 'error', 'text': 'Ein unerwarteter Fehler ist aufgetreten', 'delay': 5000}],
            'status': 'error'
        })


def render_with_messages(request, template_name, context, success_redirect=None):
    """Universelle Funktion für das Rendern mit HTMX-Unterstützung"""
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