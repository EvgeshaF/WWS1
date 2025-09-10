# companies/language.py - ОБНОВЛЕННАЯ ВЕРСИЯ

# ========================================
# Company Registration Form (Single Company)
# ========================================
text_company_registration = {
    'title': "Firmenregistrierung",
    'header': "Registrieren Sie Ihr Unternehmen",
    'desc': "Registrieren Sie Ihr Unternehmen als primäre Firma im WWS1 System:",
    'btn': "Firma registrieren",
    'btn_reset': "Formular zurücksetzen",
    'notification': "* Das System unterstützt nur eine Firma pro Installation. Nach der Registrierung können Sie die Firmendaten jederzeit bearbeiten.",
    'success_redirect_info': "Nach erfolgreicher Registrierung ist das System vollständig konfiguriert."
}

# ========================================
# Company Already Exists Warning
# ========================================
text_company_exists = {
    'title': "Firma bereits registriert",
    'header': "System vollständig konfiguriert",
    'desc': "Es ist bereits eine Firma im System registriert. Das WWS1 System ist vollständig eingerichtet und einsatzbereit.",
    'current_company': "Registrierte Firma:",
    'options_title': "Verfügbare Optionen:",
    'option_details': "Firmendetails anzeigen",
    'option_edit': "Firmendaten bearbeiten",
    'option_delete': "Firma löschen (nur für Administratoren)",
    'warning': "Das Löschen der Firma kann nicht rückgängig gemacht werden!",
    'btn_details': "Firmendetails anzeigen",
    'btn_edit': "Firma bearbeiten",
    'btn_delete': "Firma löschen",
    'btn_dashboard': "Zur Hauptseite"
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
    'delete_irreversible': "Diese Aktion kann nicht rückgängig gemacht werden",
    'system_configured': "System ist jetzt vollständig konfiguriert und einsatzbereit!",
    'setup_complete': "🎉 Systemeinrichtung erfolgreich abgeschlossen!",
    'admin_first': "Bitte erstellen Sie zuerst einen Administrator",
    'company_after_admin': "Registrieren Sie jetzt Ihre Firma, um die Konfiguration abzuschließen"
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
    'btn_home': "Zur Hauptseite",
    'btn_continue': "Weiter",

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
    'company_id': "Firmen-ID",
    'setup_status': "Einrichtungsstatus",
    'configuration_complete': "Konfiguration abgeschlossen"
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
    'delete_confirmation_required': "Löschbestätigung erforderlich",
    'admin_required': "Administrator-Rechte erforderlich",
    'mongodb_not_configured': "MongoDB ist nicht konfiguriert",
    'no_admin_found': "Kein Administrator im System gefunden"
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
    'primary_company_set': "Als primäre Firma festgelegt",
    'system_ready': "System ist jetzt vollständig eingerichtet und einsatzbereit!",
    'configuration_complete': "Systemkonfiguration erfolgreich abgeschlossen",
    'setup_finished': "Einrichtung beendet - Sie können nun mit der Arbeit beginnen"
}

# ========================================
# Setup Flow Messages
# ========================================
setup_flow = {
    'step1_mongodb': "Schritt 1: MongoDB konfigurieren",
    'step2_admin': "Schritt 2: Administrator erstellen",
    'step3_company': "Schritt 3: Firma registrieren",
    'step4_complete': "Schritt 4: System bereit!",

    'flow_description': "Das WWS1 System wird in 3 einfachen Schritten eingerichtet:",
    'flow_steps': [
        "MongoDB-Datenbankverbindung konfigurieren",
        "Ersten Administrator-Account erstellen",
        "Firma als primäres Unternehmen registrieren"
    ],

    'current_step': "Aktueller Schritt:",
    'next_step': "Nächster Schritt:",
    'completed_steps': "Abgeschlossene Schritte:",
    'remaining_steps': "Verbleibende Schritte:",

    'progress_mongodb': "MongoDB ✅",
    'progress_admin': "Administrator ✅",
    'progress_company': "Firma ✅",
    'progress_complete': "System bereit ✅"
}

# ========================================
# Company Registration Success Flow
# ========================================
success_flow = {
    'registration_success_title': "Firmenregistrierung erfolgreich!",
    'registration_success_message': "Ihre Firma wurde erfolgreich als primäres Unternehmen registriert.",
    'system_ready_title': "System vollständig konfiguriert",
    'system_ready_message': "Das WWS1 Warehouse Management System ist jetzt einsatzbereit.",
    'next_steps_title': "Empfohlene nächste Schritte:",
    'next_steps': [
        "Erkunden Sie die Lagerverwaltungsfunktionen",
        "Fügen Sie weitere Benutzer hinzu (optional)",
        "Konfigurieren Sie Produktkategorien",
        "Importieren Sie bestehende Lagerbestände"
    ],
    'btn_get_started': "System erkunden",
    'btn_dashboard': "Zum Dashboard"
}