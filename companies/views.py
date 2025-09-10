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

# ... (alle deine bisherigen View-Funktionen bleiben unverändert)


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


# ... (Rest deiner Datei unverändert)
