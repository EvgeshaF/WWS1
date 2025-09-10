# ========================================
# Company Registration Form (Single Company)
# ========================================
text_company_registration = {
    'title': "Firmenregistrierung",
    'header': "Registrieren Sie Ihr Unternehmen",
    'desc': "Registrieren Sie Ihr Unternehmen als primäre Firma im WWS1 System:",
    'btn': "Firma registrieren",
    'btn_reset': "Formular zurücksetzen",
    'notification': "* Das System unterstützt nur eine Firma pro Installation. Nach der Registrierung können Sie die Firmendaten jederzeit bearbeiten."
}

# ========================================
# Company Already Exists Warning
# ========================================
text_company_exists = {
    'title': "Firma bereits registriert",
    'header': "Nur eine Firma pro System",
    'desc': "Es ist bereits eine Firma im System registriert. Das WWS1 System ist für die Verwaltung einer einzelnen Firma konzipiert.",
    'current_company': "Aktuell registrierte Firma:",
    'options_title': "Verfügbare Optionen:",
    'option_details': "Firmendetails anzeigen",
    'option_edit': "Firmendaten bearbeiten",
    'option_delete': "Firma löschen (nur für Administratoren)",
    'warning': "Das Löschen der Firma kann nicht rückgängig gemacht werden!",
    'btn_details': "Firmendetails anzeigen",
    'btn_edit': "Firma bearbeiten",
    'btn_delete': "Firma löschen"
}

# ========================================
# Company Details Page
# ========================================
text_company_details = {
    'title': "Firmendetails",
    'header': "Details Ihrer registrierten Firma",
    'desc': "Vollständige Informationen über Ihr im System registriertes Unternehmen",
    'edit_btn': "Firma bearbeiten",
    'delete_btn': "Firma löschen",
    'print_btn': "Details drucken",

    # Section headers
    'section_basic': "Grunddaten",
    'section_address': "Adresse",
    'section_contact': "Kontaktdaten",
    'section_contact_person': "Ansprechpartner",
    'section_additional': "Zusätzliche Informationen",
    'section_system': "Systemdaten",

    # System information
    'registered_at': "Registriert am:",
    'last_updated': "Zuletzt aktualisiert:",
    'status': "Status:",
    'company_id': "Firmen-ID:",

    # Status labels
    'status_active': "Aktiv",
    'status_inactive': "Inaktiv",
    'status_pending': "Wartend",
    'status_deleted': "Gelöscht",

    # Actions
    'action_edit': "Bearbeiten",
    'action_delete': "Löschen",
    'action_print': "Drucken",
    'action_export': "Exportieren"
}

# ========================================
# Company Edit Form
# ========================================
text_company_edit = {
    'title': "Firma bearbeiten",
    'header': "Firmendaten aktualisieren",
    'desc': "Bearbeiten Sie die Daten Ihrer registrierten Firma:",
    'btn': "Änderungen speichern",
    'btn_cancel': "Abbrechen",
    'notification': "* Alle Änderungen werden sofort in der Datenbank gespeichert."
}

# ========================================
# Company Delete Confirmation
# ========================================
text_company_delete = {
    'title': "Firma löschen",
    'header': "Firma endgültig löschen",
    'warning_title': "⚠️ Warnung: Unwiderrufliche Aktion",
    'warning_text': "Das Löschen der Firma kann nicht rückgängig gemacht werden!",
    'consequences_title': "Folgen der Löschung:",
    'consequences': [
        "Alle Firmendaten werden dauerhaft gelöscht",
        "Alle zugehörigen Dokumente und Berichte werden entfernt",
        "Sie können anschließend eine neue Firma registrieren",
        "Alle Benutzerkonten bleiben erhalten"
    ],
    'confirm_text': "Geben Sie zur Bestätigung den Firmennamen ein:",
    'btn_delete': "Firma endgültig löschen",
    'btn_cancel': "Abbrechen",
    'placeholder': "Firmenname zur Bestätigung eingeben"
}

# ========================================
# System Status Messages
# ========================================
status_messages = {
    'company_registered': "Firma erfolgreich als primäre Firma registriert",
    'company_updated': "Firmendaten erfolgreich aktualisiert",
    'company_deleted': "Firma erfolgreich gelöscht",
    'company_exists': "Es ist bereits eine Firma registriert: '{company_name}'",
    'company_not_found': "Keine Firma im System gefunden",
    'registration_blocked': "Registrierung nicht möglich - bereits eine Firma vorhanden",
    'single_company_system': "Das System unterstützt nur eine Firma pro Installation",
    'can_edit_anytime': "Sie können die Firmendaten jederzeit bearbeiten",
    'delete_requires_admin': "Das Löschen der Firma erfordert Administratorrechte",
    'confirm_delete': "Löschen bestätigen durch Eingabe des Firmennamens",
    'delete_irreversible': "Diese Aktion kann nicht rückgängig gemacht werden"
}

# ========================================
# Navigation and UI Elements
# ========================================
ui_elements = {
    'menu_company': "Firma",
    'menu_details': "Firmendetails",
    'menu_edit': "Bearbeiten",
    'menu_register': "Registrieren",
    'breadcrumb_home': "Startseite",
    'breadcrumb_company': "Firma",
    'breadcrumb_details': "Details",
    'breadcrumb_edit': "Bearbeiten",
    'breadcrumb_register': "Registrieren",

    # Buttons
    'btn_save': "Speichern",
    'btn_cancel': "Abbrechen",
    'btn_edit': "Bearbeiten",
    'btn_delete': "Löschen",
    'btn_register': "Registrieren",
    'btn_back': "Zurück",
    'btn_print': "Drucken",
    'btn_export': "Exportieren",

    # Status indicators
    'status_active': "✅ Aktiv",
    'status_inactive': "❌ Inaktiv",
    'status_pending': "⏳ Wartend",
    'status_deleted': "🗑️ Gelöscht",

    # System info
    'system_info': "Systeminformationen",
    'primary_company': "Primäre Firma",
    'registration_date': "Registrierungsdatum",
    'last_update': "Letzte Aktualisierung",
    'company_id': "Firmen-ID"
}

# ========================================
# Error Messages (Single Company)
# ========================================
error_messages = {
    'system_not_ready': "System ist noch nicht vollständig konfiguriert",
    'database_error': "Datenbankfehler aufgetreten",
    'company_exists': "Es ist bereits eine Firma registriert",
    'no_company_found': "Keine Firma gefunden",
    'registration_failed': "Registrierung fehlgeschlagen",
    'update_failed': "Aktualisierung fehlgeschlagen",
    'delete_failed': "Löschung fehlgeschlagen",
    'access_denied': "Zugriff verweigert",
    'invalid_data': "Ungültige Daten übermittelt",
    'network_error': "Netzwerkfehler aufgetreten",
    'unexpected_error': "Ein unerwarteter Fehler ist aufgetreten",
    'company_name_mismatch': "Firmenname stimmt nicht überein",
    'delete_confirmation_required': "Löschbestätigung erforderlich"
}

# ========================================
# Success Messages (Single Company)
# ========================================
success_messages = {
    'company_registered': "Firma '{company_name}' wurde erfolgreich registriert!",
    'company_updated': "Firmendaten wurden erfolgreich aktualisiert",
    'company_deleted': "Firma wurde erfolgreich gelöscht",
    'data_saved': "Daten erfolgreich gespeichert",
    'changes_applied': "Änderungen wurden übernommen",
    'registration_complete': "Registrierung abgeschlossen",
    'primary_company_set': "Als primäre Firma festgelegt"
}