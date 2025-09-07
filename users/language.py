# users/language.py - Обновленные немецкие тексты для форм создания администратора

# ========================================
# Create Admin Step 1 (Benutzerdaten)
# ========================================
text_create_admin_step1 = {
    'title': "Administrator erstellen",
    'header': "Neuen Administrator anlegen",
    'desc': "Geben Sie die Benutzerdaten für den neuen Administrator ein:",
    'username': "Benutzername:",
    'password': "Passwort:",
    'password_confirm': "Passwort bestätigen:",
    'btn': "Weiter zu Schritt 2",
    'notification': "* Der Benutzername muss eindeutig sein und kann später nicht geändert werden."
}

# ========================================
# Create Admin Step 2 (Profil + Hauptkontakte)
# ========================================
text_create_admin_step2 = {
    'title': "Administrator Profil",
    'header': "Profildaten und Hauptkontakte",
    'desc': "Vervollständigen Sie das Profil und geben Sie die Hauptkontakte ein:",
    'salutation': "Anrede:",
    'title_field': "Titel:",
    'first_name': "Vorname:",
    'last_name': "Nachname:",
    'email': "Haupt-E-Mail:",
    'phone': "Haupttelefon:",
    'additional_contacts': "Zusätzliche Kontakte:",
    'btn': "Weiter zu Schritt 3",
    'btn_back': "Zurück zu Schritt 1",
    'btn_additional': "Zusätzliche Kontakte",
    'notification': "* Die Hauptkontakte sind erforderlich. Zusätzliche Kontakte können optional hinzugefügt werden."
}

# ========================================
# Create Admin Step 2.1 (Zusätzliche Kontakte)
# ========================================
text_create_admin_step2_1 = {
    'title': "Zusätzliche Kontakte",
    'header': "Weitere Kontaktmöglichkeiten hinzufügen",
    'desc': "Hier können Sie weitere Kontaktdaten hinzufügen (optional):",
    'examples': "Beispiele: Weitere E-Mails, Mobile, Fax, Website, LinkedIn, XING",
    'btn_add': "Kontakt hinzufügen",
    'btn_done': "Fertig",
    'empty_title': "Noch keine zusätzlichen Kontakte hinzugefügt",
    'empty_desc': "Diese sind optional und können übersprungen werden",
    'empty_hint': "Zusätzliche Kontakte verbessern die Kommunikationsmöglichkeiten"
}

# ========================================
# Create Admin Step 3 (Berechtinungen)
# ========================================
text_create_admin_step3 = {
    'title': "Administrator Berechtigungen",
    'header': "Berechtigungen festlegen",
    'desc': "Definieren Sie die Berechtigungen für den Administrator:",
    'permissions_title': "Systemberechtigungen:",
    'security_title': "Sicherheitseinstellungen:",
    'btn': "Administrator erstellen",
    'btn_back': "Zurück zu Schritt 2",
    'notification': "* Diese Berechtigungen können später in den Benutzereinstellungen geändert werden."
}

# ========================================
# Contact Management Messages
# ========================================
contact_messages = {
    'added_success': "Kontakt erfolgreich hinzugefügt",
    'updated_success': "Kontakt erfolgreich aktualisiert",
    'deleted_success': "Kontakt erfolgreich gelöscht",
    'type_required': "Kontakttyp ist erforderlich",
    'value_required': "Kontaktdaten sind erforderlich",
    'invalid_email': "Ungültiges E-Mail-Format",
    'invalid_phone': "Ungültiges Telefonformat",
    'invalid_mobile': "Ungültiges Mobilnummer-Format",
    'invalid_fax': "Ungültiges Faxnummer-Format",
    'invalid_website': "Ungültiges Website-Format (muss mit http:// oder https:// beginnen)",
    'invalid_linkedin': "Ungültiges LinkedIn-Profil-Format",
    'invalid_xing': "Ungültiges XING-Profil-Format",
    'min_length': "Kontaktdaten müssen mindestens 3 Zeichen lang sein",
    'confirm_delete_title': "Kontakt löschen",
    'confirm_delete_text': "Möchten Sie diesen Kontakt wirklich löschen?",
    'confirm_delete_warning': "Diese Aktion kann nicht rückgängig gemacht werden."
}

# ========================================
# Form Validation Messages
# ========================================
validation_messages = {
    'form_invalid': "Das Formular wurde ungültig ausgefüllt. Bitte überprüfen Sie die eingegebenen Daten.",
    'required_field': "Dieses Feld ist erforderlich",
    'email_required': "Haupt-E-Mail ist erforderlich",
    'phone_required': "Haupttelefon ist erforderlich",
    'salutation_required': "Anrede ist erforderlich",
    'first_name_required': "Vorname ist erforderlich",
    'last_name_required': "Nachname ist erforderlich",
    'max_length': "Maximal {max} Zeichen erlaubt",
    'min_length': "Mindestens {min} Zeichen erforderlich"
}

# ========================================
# General Messages
# ========================================
mess_form_invalid = "Das Formular wurde ungültig ausgefüllt. Bitte überprüfen Sie die eingegebenen Daten."
mess_mongodb_not_configured = "MongoDB muss zuerst konfiguriert werden, bevor Benutzer erstellt werden können."
mess_user_exists = "Ein Benutzer mit diesem Namen existiert bereits."
mess_user_created_success = "Administrator erfolgreich erstellt."
mess_user_creation_error = "Fehler beim Erstellen des Administrators."
mess_session_expired = "Die Sitzung ist abgelaufen. Bitte beginnen Sie erneut."
mess_step_incomplete = "Bitte vollenden Sie die vorherigen Schritte."
mess_profile_saved = "Profildaten erfolgreich gespeichert."
mess_contacts_saved = "Kontaktdaten erfolgreich gespeichert."
mess_additional_contacts_processing_error = "Fehler beim Verarbeiten der zusätzlichen Kontaktdaten."

# ========================================
# Success Messages
# ========================================
success_messages = {
    'step1_completed': "Benutzerdaten für '{username}' erfolgreich validiert",
    'step2_completed': "Profildaten und Kontakte erfolgreich erfasst ({contact_info})",
    'admin_created': "Administrator '{username}' wurde erfolgreich erstellt! Kontakte: {contact_info}",
    'main_contacts_format': "{count} Hauptkontakte",
    'additional_contacts_format': "{main} Hauptkontakte + {additional} zusätzliche = {total} insgesamt",
    'total_contacts_format': "{total} Kontakte insgesamt"
}

# ========================================
# Form Help Texts
# ========================================
help_text_username = "3-50 Zeichen, beginnt mit Buchstaben, nur Buchstaben, Zahlen und Unterstriche"
help_text_password = "Mindestens 8 Zeichen mit Groß-/Kleinbuchstaben, Zahlen und Sonderzeichen"
help_text_email = "Wird für wichtige Systembenachrichtigungen verwendet"
help_text_phone = "Für Notfallkontakt und 2FA"
help_text_additional_contacts = "Optional: Weitere Kontaktmöglichkeiten hinzufügen"
help_text_super_admin = "Hat vollständigen Zugriff auf alle Systemfunktionen"
help_text_password_expires = "Passwort muss regelmäßig geändert werden (empfohlen: 90 Tage)"
help_text_two_factor = "Erhöht die Sicherheit erheblich (empfohlen für alle Administratoren)"

# ========================================
# Contact Type Labels (German)
# ========================================
contact_type_labels = {
    'email': 'E-Mail (zusätzlich)',
    'phone': 'Telefon (Hauptanschluss)',
    'mobile': 'Mobil',
    'fax': 'Fax',
    'website': 'Website',
    'linkedin': 'LinkedIn',
    'xing': 'XING',
    'other': 'Sonstige'
}

# ========================================
# Contact Validation Patterns
# ========================================
contact_patterns = {
    'email': r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
    'phone': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
    'mobile': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
    'fax': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
    'website': r'^https?:\/\/.+\..+$|^www\..+\..+$',
    'linkedin': r'^(https?:\/\/)?(www\.)?linkedin\.com\/in\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$',
    'xing': r'^(https?:\/\/)?(www\.)?xing\.com\/profile\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$'
}

# ========================================
# Contact Hints (German)
# ========================================
contact_hints = {
    'email': 'Geben Sie eine weitere E-Mail-Adresse ein (z.B. privat@example.com)',
    'mobile': 'Geben Sie eine Mobilnummer ein (z.B. +49 170 1234567)',
    'fax': 'Geben Sie eine Faxnummer ein (z.B. +49 123 456789)',
    'website': 'Geben Sie eine Website-URL ein (z.B. https://www.example.com)',
    'linkedin': 'Geben Sie Ihr LinkedIn-Profil ein (z.B. linkedin.com/in/username)',
    'xing': 'Geben Sie Ihr XING-Profil ein (z.B. xing.com/profile/username)',
    'other': 'Geben Sie die entsprechenden Kontaktdaten ein'
}

# ========================================
# Contact Placeholders (German)
# ========================================
contact_placeholders = {
    'email': 'privat@domain.com',
    'mobile': '+49 170 1234567',
    'fax': '+49 123 456789',
    'website': 'https://www.example.com',
    'linkedin': 'linkedin.com/in/username',
    'xing': 'xing.com/profile/username',
    'other': 'Kontaktdaten eingeben...'
}

# ========================================
# Button Labels
# ========================================
button_labels = {
    'next': "Weiter",
    'back': "Zurück",
    'save': "Speichern",
    'cancel': "Abbrechen",
    'delete': "Löschen",
    'edit': "Bearbeiten",
    'add': "Hinzufügen",
    'create': "Erstellen",
    'finish': "Fertig",
    'close': "Schließen",
    'confirm': "Bestätigen",
    'update': "Aktualisieren"
}

# ========================================
# Status Messages
# ========================================
status_messages = {
    'processing': "Wird verarbeitet...",
    'saving': "Wird gespeichert...",
    'creating': "Wird erstellt...",
    'updating': "Wird aktualisiert...",
    'deleting': "Wird gelöscht...",
    'validating': "Wird validiert...",
    'loading': "Wird geladen...",
    'connecting': "Verbindung wird hergestellt...",
    'authenticating': "Authentifizierung läuft..."
}

# ========================================
# Error Categories
# ========================================
error_categories = {
    'validation': "Validierungsfehler",
    'network': "Netzwerkfehler",
    'server': "Serverfehler",
    'authentication': "Authentifizierungsfehler",
    'authorization': "Berechtigungsfehler",
    'database': "Datenbankfehler",
    'session': "Sitzungsfehler",
    'unexpected': "Unerwarteter Fehler"
}