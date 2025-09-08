# users/language.py - ENHANCED GERMAN TEXTS FOR MODAL CONTACT MANAGEMENT

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
# Create Admin Step 2 (Enhanced Modal Version)
# ========================================
text_create_admin_step2 = {
    'title': "Administrator Profil",
    'header': "Profildaten und Kontakte verwalten",
    'desc': "Vervollständigen Sie das Profil und geben Sie die Kontaktdaten ein:",
    'salutation': "Anrede:",
    'title_field': "Titel:",
    'first_name': "Vorname:",
    'last_name': "Nachname:",
    'email': "System E-Mail:",
    'phone': "System Telefon:",
    'primary_contact': "Hauptkontakt:",
    'additional_contacts': "Zusätzliche Kontakte:",
    'btn': "Weiter zu Schritt 3",
    'btn_back': "Zurück zu Schritt 1",
    'btn_manage': "Verwalten",
    'notification': "* Persönliche Daten und Hauptkontakt sind erforderlich. Zusätzliche Kontakte können optional hinzugefügt werden."
}

# ========================================
# Enhanced Contact Management (Modal Version)
# ========================================
text_contact_management = {
    'modal_title': "Zusätzliche Kontakte verwalten",
    'modal_subtitle': "Erweitern Sie die Kommunikationsmöglichkeiten",
    'toolbar_title': "Kontaktliste",
    'btn_add_contact': "Neuen Kontakt hinzufügen",
    'btn_add_first': "Ersten Kontakt hinzufügen",
    'btn_edit': "Bearbeiten",
    'btn_delete': "Löschen",
    'btn_save': "Speichern",
    'btn_update': "Aktualisieren",
    'btn_cancel': "Abbrechen",
    'btn_done': "Fertig",

    # Empty state messages
    'empty_title': "Noch keine zusätzlichen Kontakte hinzugefügt",
    'empty_subtitle': "Zusätzliche Kontakte sind optional und können übersprungen werden.",
    'empty_description': "Sie verbessern jedoch die Kommunikationsmöglichkeiten erheblich.",

    # Summary messages
    'summary_none': "Keine zusätzlichen Kontakte hinzugefügt",
    'summary_one': "1 zusätzlicher Kontakt hinzugefügt",
    'summary_multiple': "{count} zusätzliche Kontakte hinzugefügt",

    # Table headers
    'header_type': "Typ",
    'header_contact_data': "Kontaktdaten",
    'header_status': "Status",
    'header_actions': "Aktionen",

    # Status labels
    'status_important': "Wichtig",
    'status_standard': "Standard",

    # Tips and hints
    'tips_title': "Tipps",
    'tips_email': "E-Mail: Für zusätzliche Kommunikation",
    'tips_mobile': "Mobil: Für dringende Angelegenheiten",
    'tips_social': "LinkedIn/XING: Für berufliche Vernetzung",

    'hints_title': "Hinweise",
    'hints_optional': "Alle Kontakte sind optional",
    'hints_priority': "Als \"wichtig\" markierte Kontakte werden bevorzugt angezeigt",
    'hints_duplicates': "Duplikate werden automatisch vermieden",

    # Footer messages
    'footer_autosave': "Änderungen werden automatisch gespeichert",
    'footer_notification': "Änderungen werden beim Weiterklicken übernommen"
}

# ========================================
# Add/Edit Contact Modal
# ========================================
text_contact_form = {
    'add_title': "Kontakt hinzufügen",
    'edit_title': "Kontakt bearbeiten",
    'contact_type': "Kontakttyp",
    'contact_value': "Kontaktdaten",
    'contact_label': "Beschreibung",
    'contact_important': "Als wichtig markieren",

    # Placeholders and hints
    'type_placeholder': "Typ auswählen...",
    'value_placeholder': "Kontaktdaten eingeben...",
    'label_placeholder': "z.B. Privat, Geschäftlich...",

    'label_hint': "Optionale Beschreibung für diesen Kontakt",
    'important_hint': "Wichtige Kontakte werden bevorzugt angezeigt",
    'general_hint': "Geben Sie die entsprechenden Kontaktdaten ein",

    # Contact type specific hints
    'email_hint': "Geben Sie eine zusätzliche E-Mail-Adresse ein (z.B. privat@example.com)",
    'mobile_hint': "Geben Sie eine Mobilnummer ein (z.B. +49 170 1234567)",
    'fax_hint': "Geben Sie eine Faxnummer ein (z.B. +49 123 456789)",
    'website_hint': "Geben Sie eine Website-URL ein (z.B. https://www.example.com)",
    'linkedin_hint': "Geben Sie Ihr LinkedIn-Profil ein (z.B. linkedin.com/in/username)",
    'xing_hint': "Geben Sie Ihr XING-Profil ein (z.B. xing.com/profile/username)",
    'other_hint': "Geben Sie die entsprechenden Kontaktdaten ein"
}

# ========================================
# Delete Confirmation Modal
# ========================================
text_delete_confirmation = {
    'title': "Kontakt löschen",
    'question': "Möchten Sie diesen Kontakt wirklich löschen?",
    'warning': "Diese Aktion kann nicht rückgängig gemacht werden.",
    'btn_confirm': "Löschen",
    'btn_cancel': "Abbrechen"
}

# ========================================
# Create Admin Step 3 (Permissions)
# ========================================
text_create_admin_step3 = {
    'title': "Administrator Berechtigungen",
    'header': "Berechtigungen und Sicherheit festlegen",
    'desc': "Definieren Sie die Berechtigungen und Sicherheitseinstellungen:",
    'permissions_title': "Systemberechtigungen",
    'security_title': "Sicherheitseinstellungen",
    'btn': "Administrator erstellen",
    'btn_back': "Zurück zu Schritt 2",
    'notification': "* Diese Berechtigungen können später in den Benutzereinstellungen geändert werden."
}

# ========================================
# Enhanced Contact Messages
# ========================================
contact_messages = {
    'added_success': "Kontakt erfolgreich hinzugefügt",
    'updated_success': "Kontakt erfolgreich aktualisiert",
    'deleted_success': "Kontakt erfolgreich gelöscht",
    'saved_success': "Kontaktdaten erfolgreich gespeichert",

    # Validation messages
    'type_required': "Kontakttyp ist erforderlich",
    'value_required': "Kontaktdaten sind erforderlich",
    'form_invalid': "Bitte korrigieren Sie die Fehler im Formular",

    # Format validation messages
    'invalid_email': "Ungültiges E-Mail-Format",
    'invalid_phone': "Ungültiges Telefonformat",
    'invalid_mobile': "Ungültiges Mobilnummer-Format",
    'invalid_fax': "Ungültiges Faxnummer-Format",
    'invalid_website': "Ungültiges Website-Format (muss mit http:// oder https:// beginnen)",
    'invalid_linkedin': "Ungültiges LinkedIn-Profil-Format",
    'invalid_xing': "Ungültiges XING-Profil-Format",
    'min_length': "Kontaktdaten müssen mindestens 3 Zeichen lang sein",

    # System messages
    'loading': "Wird geladen...",
    'saving': "Wird gespeichert...",
    'processing': "Wird verarbeitet..."
}

# ========================================
# Enhanced Validation Messages
# ========================================
validation_messages = {
    'form_invalid': "Das Formular wurde ungültig ausgefüllt. Bitte überprüfen Sie die eingegebenen Daten.",
    'required_field': "Dieses Feld ist erforderlich",
    'email_required': "System E-Mail ist erforderlich",
    'phone_required': "System Telefon ist erforderlich",
    'primary_contact_required': "Hauptkontakt ist erforderlich",
    'salutation_required': "Anrede ist erforderlich",
    'first_name_required': "Vorname ist erforderlich",
    'last_name_required': "Nachname ist erforderlich",
    'max_length': "Maximal {max} Zeichen erlaubt",
    'min_length': "Mindestens {min} Zeichen erforderlich",

    # Contact specific validation
    'primary_contact_type_required': "Hauptkontakt Typ ist erforderlich",
    'duplicate_system_email': "Hauptkontakt E-Mail darf nicht mit System E-Mail identisch sein",
    'duplicate_system_phone': "Hauptkontakt Telefon darf nicht mit System Telefon identisch sein"
}

# ========================================
# Enhanced Success Messages
# ========================================
success_messages = {
    'step1_completed': "Benutzerdaten für '{username}' erfolgreich validiert",
    'step2_completed': "Profildaten und Kontakte erfolgreich erfasst ({contact_info})",
    'admin_created': "Administrator '{username}' wurde erfolgreich erstellt! Kontakte: {contact_info}",

    # Contact summary formats
    'contacts_system_only': "System-E-Mail, System-Telefon",
    'contacts_with_primary': "System-E-Mail, System-Telefon, Hauptkontakt ({type})",
    'contacts_with_additional': "{main} + {additional} zusätzliche",
    'contacts_total': "{total} Kontakte insgesamt",

    # Progress messages
    'profile_data_saved': "Profildaten erfolgreich gespeichert",
    'contacts_processed': "Kontaktdaten erfolgreich verarbeitet",
    'validation_passed': "Validierung erfolgreich abgeschlossen"
}

# ========================================
# Enhanced Error Messages
# ========================================
error_messages = {
    'mongodb_not_configured': "MongoDB muss zuerst konfiguriert werden",
    'user_exists': "Ein Benutzer mit diesem Namen existiert bereits",
    'user_creation_error': "Fehler beim Erstellen des Administrators",
    'session_expired': "Die Sitzung ist abgelaufen. Bitte beginnen Sie erneut",
    'step_incomplete': "Bitte vollenden Sie die vorherigen Schritte",
    'contact_processing_error': "Fehler beim Verarbeiten der Kontaktdaten",
    'additional_contacts_error': "Fehler beim Verarbeiten der zusätzlichen Kontaktdaten",
    'primary_contact_error': "Fehler beim Verarbeiten des Hauptkontakts",
    'form_submission_error': "Fehler beim Senden des Formulars",
    'server_error': "Serverfehler aufgetreten",
    'network_error': "Netzwerkfehler aufgetreten",
    'unexpected_error': "Ein unerwarteter Fehler ist aufgetreten"
}

# ========================================
# Contact Type Definitions (Enhanced)
# ========================================
contact_types = {
    'email': {
        'label': 'E-Mail',
        'icon': '📧',
        'description': 'Zusätzliche E-Mail-Adresse',
        'placeholder': 'privat@domain.com',
        'pattern': r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
        'hint': 'Geben Sie eine zusätzliche E-Mail-Adresse ein'
    },
    'mobile': {
        'label': 'Mobil',
        'icon': '📱',
        'description': 'Mobiltelefonnummer',
        'placeholder': '+49 170 1234567',
        'pattern': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
        'hint': 'Geben Sie eine Mobilnummer ein'
    },
    'fax': {
        'label': 'Fax',
        'icon': '📠',
        'description': 'Faxnummer',
        'placeholder': '+49 123 456789',
        'pattern': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
        'hint': 'Geben Sie eine Faxnummer ein'
    },
    'website': {
        'label': 'Website',
        'icon': '🌐',
        'description': 'Webseite oder Homepage',
        'placeholder': 'https://www.example.com',
        'pattern': r'^https?:\/\/.+\..+$|^www\..+\..+$',
        'hint': 'Geben Sie eine Website-URL ein'
    },
    'linkedin': {
        'label': 'LinkedIn',
        'icon': '💼',
        'description': 'LinkedIn Profil',
        'placeholder': 'linkedin.com/in/username',
        'pattern': r'^(https?:\/\/)?(www\.)?linkedin\.com\/in\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$',
        'hint': 'Geben Sie Ihr LinkedIn-Profil ein'
    },
    'xing': {
        'label': 'XING',
        'icon': '🔗',
        'description': 'XING Profil',
        'placeholder': 'xing.com/profile/username',
        'pattern': r'^(https?:\/\/)?(www\.)?xing\.com\/profile\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$',
        'hint': 'Geben Sie Ihr XING-Profil ein'
    },
    'other': {
        'label': 'Sonstige',
        'icon': '📝',
        'description': 'Andere Kontaktdaten',
        'placeholder': 'Kontaktdaten eingeben...',
        'pattern': r'.{3,}',
        'hint': 'Geben Sie die entsprechenden Kontaktdaten ein'
    }
}

# ========================================
# UI Text Elements
# ========================================
ui_texts = {
    # Button labels
    'btn_next': "Weiter",
    'btn_back': "Zurück",
    'btn_save': "Speichern",
    'btn_cancel': "Abbrechen",
    'btn_delete': "Löschen",
    'btn_edit': "Bearbeiten",
    'btn_add': "Hinzufügen",
    'btn_create': "Erstellen",
    'btn_update': "Aktualisieren",
    'btn_finish': "Fertig",
    'btn_close': "Schließen",
    'btn_confirm': "Bestätigen",
    'btn_manage': "Verwalten",

    # Status labels
    'status_loading': "Wird geladen...",
    'status_saving': "Wird gespeichert...",
    'status_processing': "Wird verarbeitet...",
    'status_validating': "Wird validiert...",
    'status_creating': "Wird erstellt...",
    'status_updating': "Wird aktualisiert...",
    'status_deleting': "Wird gelöscht...",

    # Common labels
    'required_field': "Pflichtfeld",
    'optional_field': "Optional",
    'recommended': "Empfohlen",
    'advanced': "Erweitert",
    'basic': "Grundlegend",
    'important': "Wichtig",
    'normal': "Normal",

    # Navigation
    'step_of': "Schritt {current} von {total}",
    'progress': "Fortschritt",
    'completed': "Abgeschlossen",
    'current': "Aktuell",
    'pending': "Ausstehend"
}

# ========================================
# Help Text and Tooltips
# ========================================
help_texts = {
    'username': "3-50 Zeichen, beginnt mit Buchstaben, nur Buchstaben, Zahlen und Unterstriche",
    'password': "Mindestens 8 Zeichen mit Groß-/Kleinbuchstaben, Zahlen",
    'system_email': "Wird für wichtige Systembenachrichtigungen verwendet",
    'system_phone': "Für Notfallkontakt und Zwei-Faktor-Authentifizierung",
    'primary_contact': "Dieser Kontakt wird als primärer Kommunikationskanal verwendet",
    'additional_contacts': "Optional: Weitere Kontaktmöglichkeiten zur Verbesserung der Kommunikation",
    'contact_important': "Wichtige Kontakte werden in der Übersicht bevorzugt angezeigt",
    'contact_label': "Kurze Beschreibung oder Kategorie für diesen Kontakt",

    # Security help texts
    'super_admin': "Hat vollständigen Zugriff auf alle Systemfunktionen",
    'password_expires': "Passwort muss regelmäßig geändert werden (empfohlen: 90 Tage)",
    'two_factor': "Erhöht die Sicherheit erheblich (empfohlen für alle Administratoren)",

    # Permission help texts
    'manage_users': "Kann Benutzer erstellen, bearbeiten und löschen",
    'manage_database': "Kann Datenbankeinstellungen ändern und Backups erstellen",
    'view_logs': "Kann Systemlogs und Audit-Trails einsehen",
    'manage_settings': "Kann globale Systemeinstellungen ändern"
}

# ========================================
# Accessibility Labels
# ========================================
aria_labels = {
    'close_modal': "Modal schließen",
    'delete_contact': "Kontakt löschen",
    'edit_contact': "Kontakt bearbeiten",
    'add_contact': "Kontakt hinzufügen",
    'contact_type': "Kontakttyp auswählen",
    'contact_value': "Kontaktdaten eingeben",
    'contact_important': "Als wichtig markieren",
    'form_error': "Formularfehler",
    'required_field': "Pflichtfeld",
    'optional_field': "Optionales Feld",
    'validation_error': "Validierungsfehler",
    'success_message': "Erfolgsmeldung",
    'loading_content': "Inhalt wird geladen",
    'table_header': "Tabellenkopf",
    'table_cell': "Tabellenzelle",
    'pagination': "Seitennavigation",
    'search_field': "Suchfeld"
}