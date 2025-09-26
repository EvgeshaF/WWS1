# company/language.py - Enhanced Company Form Texts for 5-step process with banking step

# ========================================
# Company Registration Step 1 (Grunddaten + CEO)
# ========================================
text_company_step1 = {
    'title': "Firma registrieren",
    'header': "Grunddaten der Firma",
    'desc': "Geben Sie die grundlegenden Informationen über Ihre Firma ein:",
    'company_name': "Firmenname:",
    'legal_form': "Rechtsform:",
    'ceo_section': "Geschäftsführer:",
    'btn': "Weiter zu Schritt 2",
    'notification': "* Alle Angaben können später bearbeitet werden."
}

# ========================================
# Company Registration Step 2 (Registrierungsdaten) - ОБНОВЛЕНО: ВСЕ ПОЛЯ ОБЯЗАТЕЛЬНЫ
# ========================================
text_company_step2 = {
    'title': "Registrierungsdaten",
    'header': "Amtliche Registrierungsdaten",
    'desc': "Geben Sie die offiziellen Registrierungsdaten Ihrer Firma ein - alle Felder sind Pflichtfelder:",
    'commercial_register': "Handelsregister:",
    'tax_number': "Steuernummer:",
    'vat_id': "USt-IdNr.:",
    'tax_id': "Steuer-ID:",
    'btn': "Weiter zu Schritt 3",
    'btn_back': "Zurück zu Schritt 1",
    'notification': "* Alle Registrierungsfelder sind jetzt Pflichtfelder für die vollständige Firmenregistrierung."
}

# ========================================
# Company Registration Step 3 (Adressdaten)
# ========================================
text_company_step3 = {
    'title': "Firmenadresse",
    'header': "Anschrift und Standort",
    'desc': "Geben Sie die Geschäftsadresse Ihrer Firma ein:",
    'street': "Straße und Hausnummer:",
    'postal_code': "PLZ:",
    'city': "Stadt:",
    'country': "Land:",
    'address_addition': "Adresszusatz:",
    'po_box': "Postfach:",
    'btn': "Weiter zu Schritt 4",
    'btn_back': "Zurück zu Schritt 2",
    'notification': "* Die Geschäftsadresse wird für offizielle Korrespondenz verwendet."
}

# ========================================
# Company Registration Step 4 (Kontaktdaten)
# ========================================
text_company_step4 = {
    'title': "Kontaktdaten",
    'header': "Kommunikationswege",
    'desc': "Geben Sie die wichtigsten Kontaktdaten Ihrer Firma ein:",
    'email': "Haupt-E-Mail:",
    'phone': "Haupttelefon:",
    'fax': "Fax:",
    'website': "Website:",
    'primary_contact': "Hauptkontakt:",
    'additional_contacts': "Zusätzliche Kontakte:",
    'btn': "Weiter zu Schritt 5",
    'btn_back': "Zurück zu Schritt 3",
    'btn_manage': "Verwalten",
    'notification': "* E-Mail und Telefon sind erforderlich. Zusätzliche Kontakte sind optional."
}

# ========================================
# Company Registration Step 5 (Bankdaten) - НОВЫЙ ШАГЛИНГ банковских данных
# ========================================
text_company_step5 = {
    'title': "Bankverbindung",
    'header': "Bankdaten der Firma",
    'desc': "Geben Sie die Bankverbindungsdaten Ihrer Firma ein (alle Felder sind optional):",
    'main_banking_title': "Hauptbankverbindung:",
    'secondary_banking_title': "Zusätzliche Bankverbindung:",
    'settings_title': "Bankeinstellungen:",
    'bank_name': "Name der Bank:",
    'iban': "IBAN:",
    'bic': "BIC/SWIFT:",
    'account_holder': "Kontoinhaber:",
    'btn': "Firma registrieren",
    'btn_back': "Zurück zu Schritt 4",
    'notification': "* Alle Bankdaten sind optional und können später ergänzt oder bearbeitet werden."
}

# ========================================
# Enhanced Contact Management (Company Version)
# ========================================
text_company_contact_management = {
    'modal_title': "Firmenkontakte verwalten",
    'modal_subtitle': "Erweitern Sie die Kommunikationsmöglichkeiten Ihrer Firma",
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
    'empty_title': "Noch keine zusätzlichen Firmenkontakte hinzugefügt",
    'empty_subtitle': "Zusätzliche Kontakte sind optional und können übersprungen werden.",
    'empty_description': "Sie verbessern jedoch die Erreichbarkeit Ihrer Firma erheblich.",

    # Summary messages
    'summary_none': "Keine zusätzlichen Kontakte hinzugefügt",
    'summary_one': "1 zusätzlicher Kontakt hinzugefügt",
    'summary_multiple': "{count} zusätzliche Kontakte hinzugefügt",

    # Table headers
    'header_type': "Kontakttyp",
    'header_contact_data': "Kontaktdaten",
    'header_department': "Abteilung",
    'header_status': "Status",
    'header_actions': "Aktionen",

    # Status labels
    'status_important': "Wichtig",
    'status_standard': "Standard",
    'status_public': "Öffentlich",
    'status_internal': "Intern",

    # Tips and hints
    'tips_title': "Tipps",
    'tips_email': "E-Mail: Für verschiedene Abteilungen (Vertrieb, Support, etc.)",
    'tips_mobile': "Mobil: Für Notfallkontakt oder Außendienst",
    'tips_departments': "Abteilungs-Telefone: Für direkte Weiterleitung",
    'tips_social': "LinkedIn/XING: Für Unternehmensprofile",

    'hints_title': "Hinweise",
    'hints_optional': "Alle zusätzlichen Kontakte sind optional",
    'hints_departments': "Können nach Abteilungen kategorisiert werden",
    'hints_public': "Öffentliche Kontakte erscheinen auf der Webseite",
    'hints_duplicates': "Duplikate werden automatisch vermieden",

    # Footer messages
    'footer_autosave': "Änderungen werden automatisch gespeichert",
    'footer_notification': "Änderungen werden beim Weiterklicken übernommen"
}

# ========================================
# Add/Edit Company Contact Modal
# ========================================
text_company_contact_form = {
    'add_title': "Firmenkontakt hinzufügen",
    'edit_title': "Firmenkontakt bearbeiten",
    'contact_type': "Kontakttyp",
    'contact_value': "Kontaktdaten",
    'contact_label': "Abteilung/Beschreibung",
    'contact_department': "Abteilung",
    'contact_important': "Als wichtig markieren",
    'contact_public': "Öffentlich sichtbar",

    # Placeholders and hints
    'type_placeholder': "Kontakttyp auswählen...",
    'value_placeholder': "Kontaktdaten eingeben...",
    'label_placeholder': "z.B. Vertrieb, Support, Buchhaltung...",
    'department_placeholder': "Abteilung auswählen...",

    'label_hint': "Abteilung oder Verwendungszweck für diesen Kontakt",
    'important_hint': "Wichtige Kontakte werden bevorzugt angezeigt",
    'public_hint': "Öffentliche Kontakte können auf der Webseite angezeigt werden",
    'general_hint': "Geben Sie die entsprechenden Kontaktdaten ein",

    # Contact type specific hints
    'email_hint': "Geben Sie eine E-Mail-Adresse ein (z.B. vertrieb@firma.de)",
    'phone_hint': "Geben Sie eine Telefonnummer ein (z.B. +49 123 456789)",
    'mobile_hint': "Geben Sie eine Mobilnummer ein (z.B. +49 170 1234567)",
    'fax_hint': "Geben Sie eine Faxnummer ein (z.B. +49 123 456789)",
    'website_hint': "Geben Sie eine Website-URL ein (z.B. https://www.firma.de)",
    'linkedin_hint': "Geben Sie das LinkedIn-Unternehmensprofil ein",
    'xing_hint': "Geben Sie das XING-Unternehmensprofil ein",
    'other_hint': "Geben Sie die entsprechenden Kontaktdaten ein"
}

# ========================================
# НОВЫЕ тексты для банковских данных
# ========================================
text_company_banking = {
    'main_banking_section': "Hauptbankverbindung",
    'secondary_banking_section': "Zusätzliche Bankverbindung",
    'banking_settings': "Einstellungen",
    'banking_notes_section': "Notizen",

    # Field labels and hints
    'bank_name_hint': "Name Ihrer Hausbank (z.B. Deutsche Bank AG)",
    'iban_hint': "Internationale Bankkontonummer (22 Stellen für Deutschland)",
    'bic_hint': "Bank Identifier Code (8-11 Stellen)",
    'account_holder_hint': "Name des Kontoinhabers (meist der Firmenname)",
    'bank_address_hint': "Vollständige Adresse der Bank (optional)",
    'account_type_hint': "Art des Bankkontos für interne Verwaltung",

    # Secondary banking
    'secondary_bank_hint': "Zweite Bankverbindung für Liquidität oder spezielle Zwecke",
    'secondary_iban_hint': "IBAN der Zweitbank",
    'secondary_bic_hint': "BIC der Zweitbank",

    # Settings hints
    'primary_account_hint': "Diese Bankdaten erscheinen auf Rechnungen und Angeboten",
    'sepa_hint': "Ermöglicht den automatischen Einzug von Kundenzahlungen",
    'banking_notes_hint': "Interne Notizen zu den Bankverbindungen",

    # Info messages
    'all_optional': "Alle Bankdaten sind optional",
    'can_edit_later': "Können jederzeit bearbeitet werden",
    'multiple_accounts': "Mehrere Bankverbindungen unterstützt",
    'iban_validation': "IBAN wird automatisch validiert",
    'secure_storage': "Daten werden sicher verschlüsselt gespeichert"
}

# ========================================
# Department Choices
# ========================================
company_departments = {
    'management': 'Geschäftsführung',
    'sales': 'Vertrieb',
    'support': 'Kundensupport',
    'accounting': 'Buchhaltung',
    'hr': 'Personalabteilung',
    'it': 'IT-Abteilung',
    'marketing': 'Marketing',
    'production': 'Produktion',
    'logistics': 'Logistik',
    'purchasing': 'Einkauf',
    'quality': 'Qualitätsmanagement',
    'legal': 'Rechtsabteilung',
    'reception': 'Empfang/Zentrale',
    'other': 'Sonstige'
}

# ========================================
# Contact Type Definitions (Company Version)
# ========================================
company_contact_types = {
    'email': {
        'label': 'E-Mail',
        'icon': '📧',
        'description': 'E-Mail-Adresse',
        'placeholder': 'abteilung@firma.de',
        'pattern': r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
        'hint': 'Geben Sie eine E-Mail-Adresse ein'
    },
    'phone': {
        'label': 'Telefon',
        'icon': '📞',
        'description': 'Telefonnummer',
        'placeholder': '+49 123 456789',
        'pattern': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
        'hint': 'Geben Sie eine Telefonnummer ein'
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
        'placeholder': 'https://www.firma.de',
        'pattern': r'^https?:\/\/.+\..+$|^www\..+\..+$',
        'hint': 'Geben Sie eine Website-URL ein'
    },
    'linkedin': {
        'label': 'LinkedIn',
        'icon': '💼',
        'description': 'LinkedIn Unternehmensprofil',
        'placeholder': 'linkedin.com/company/firmenname',
        'pattern': r'^(https?:\/\/)?(www\.)?linkedin\.com\/company\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$',
        'hint': 'Geben Sie das LinkedIn-Unternehmensprofil ein'
    },
    'xing': {
        'label': 'XING',
        'icon': '🔗',
        'description': 'XING Unternehmensprofil',
        'placeholder': 'xing.com/companies/firmenname',
        'pattern': r'^(https?:\/\/)?(www\.)?xing\.com\/companies\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$',
        'hint': 'Geben Sie das XING-Unternehmensprofil ein'
    },
    'emergency': {
        'label': 'Notfall',
        'icon': '🚨',
        'description': 'Notfallkontakt',
        'placeholder': '+49 170 1234567',
        'pattern': r'^[\+]?[0-9\s\-\(\)]{7,20}$',
        'hint': 'Geben Sie einen Notfallkontakt ein'
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
# Enhanced Success Messages (5 steps) - ОБНОВЛЕНО для банковского шага
# ========================================
company_success_messages = {
    'step1_completed': "Grunddaten für '{company_name}' erfolgreich validiert",
    'step2_completed': "Alle Registrierungsdaten erfolgreich erfasst und validiert",
    'step3_completed': "Adressdaten erfolgreich erfasst",
    'step4_completed': "Kontaktdaten erfolgreich erfasst ({contact_info})",
    'step5_completed': "Bankdaten erfolgreich gespeichert",  # НОВОЕ
    'company_created': "Firma '{company_name}' wurde erfolgreich registriert! Kontakte: {contact_info}",

    # Contact summary formats
    'contacts_basic_only': "Haupt-E-Mail, Haupttelefon",
    'contacts_with_additional': "{main} + {additional} zusätzliche",
    'contacts_total': "{total} Kontakte insgesamt",

    # Banking summary formats - НОВОЕ
    'banking_none': "Keine Bankdaten hinterlegt",
    'banking_main_only': "Hauptbankverbindung hinterlegt",
    'banking_both': "Haupt- und Zweitbankverbindung hinterlegt",
    'banking_iban_added': "IBAN {iban} hinzugefügt",

    # Progress messages
    'company_data_saved': "Firmendaten erfolgreich gespeichert",
    'contacts_processed': "Kontaktdaten erfolgreich verarbeitet",
    'banking_processed': "Bankdaten erfolgreich verarbeitet",  # НОВОЕ
    'validation_passed': "Vollständige Validierung erfolgreich abgeschlossen",
    'registration_data_complete': "Registrierungsdaten vollständig erfasst"
}

# ========================================
# Enhanced Error Messages - ОБНОВЛЕНО для банковских данных
# ========================================
company_error_messages = {
    'mongodb_not_configured': "MongoDB muss zuerst konfiguriert werden",
    'company_exists': "Eine Firma mit diesem Namen existiert bereits",
    'company_creation_error': "Fehler beim Registrieren der Firma",
    'session_expired': "Die Sitzung ist abgelaufen. Bitte beginnen Sie erneut",
    'step_incomplete': "Bitte vollenden Sie die vorherigen Schritte",
    'contact_processing_error': "Fehler beim Verarbeiten der Kontaktdaten",
    'banking_processing_error': "Fehler beim Verarbeiten der Bankdaten",  # НОВОЕ
    'additional_contacts_error': "Fehler beim Verarbeiten der zusätzlichen Kontaktdaten",
    'form_submission_error': "Fehler beim Senden des Formulars",
    'validation_failed': "Validierung fehlgeschlagen",
    'required_field_missing': "Erforderliche Felder fehlen",
    'invalid_format': "Ungültiges Format",
    'server_error': "Serverfehler aufgetreten",
    'network_error': "Netzwerkfehler aufgetreten",
    'unexpected_error': "Ein unerwarteter Fehler ist aufgetreten",

    # Сообщения об ошибках для обязательных полей шага 2
    'commercial_register_required': "Handelsregister ist erforderlich",
    'tax_number_required': "Steuernummer ist erforderlich",
    'vat_id_required': "USt-IdNr. ist erforderlich",
    'tax_id_required': "Steuer-ID ist erforderlich",
    'registration_data_incomplete': "Registrierungsdaten sind unvollständig",
    'all_registration_fields_required': "Alle Registrierungsfelder müssen ausgefüllt werden",

    # НОВЫЕ ошибки для банковских данных
    'invalid_iban': "Ungültiges IBAN-Format",
    'invalid_bic': "Ungültiges BIC-Format",
    'iban_checksum_error': "IBAN-Prüfsumme ist ungültig",
    'bank_data_conflict': "Widersprüchliche Bankdaten"
}

# ========================================
# Validation Messages - ОБНОВЛЕНО для банковских данных
# ========================================
company_validation_messages = {
    'form_invalid': "Das Formular wurde ungültig ausgefüllt. Bitte überprüfen Sie die eingegebenen Daten.",
    'required_field': "Dieses Feld ist erforderlich",
    'company_name_required': "Firmenname ist erforderlich",
    'legal_form_required': "Rechtsform ist erforderlich",
    'email_required': "Haupt-E-Mail ist erforderlich",
    'phone_required': "Haupttelefon ist erforderlich",
    'street_required': "Straße ist erforderlich",
    'postal_code_required': "PLZ ist erforderlich",
    'city_required': "Stadt ist erforderlich",
    'country_required': "Land ist erforderlich",

    # Валидационные сообщения для шага 2
    'commercial_register_required': "Handelsregister ist erforderlich",
    'commercial_register_invalid': "Handelsregister-Format ungültig (HRA12345 oder HRB12345)",
    'tax_number_required': "Steuernummer ist erforderlich",
    'tax_number_invalid': "Steuernummer-Format ungültig (12/345/67890)",
    'vat_id_required': "USt-IdNr. ist erforderlich",
    'vat_id_invalid': "USt-IdNr.-Format ungültig (DE123456789)",
    'tax_id_required': "Steuer-ID ist erforderlich",
    'tax_id_invalid': "Steuer-ID-Format ungültig (11 Ziffern)",

    # НОВЫЕ валидационные сообщения для банковских данных
    'iban_format_invalid': "IBAN-Format ungültig (z.B. DE89370400440532013000)",
    'bic_format_invalid': "BIC-Format ungültig (z.B. DEUTDEFF)",
    'iban_checksum_invalid': "IBAN-Prüfsumme stimmt nicht überein",
    'bank_name_too_long': "Bankname ist zu lang (max. 100 Zeichen)",
    'account_holder_too_long': "Kontoinhabername ist zu lang (max. 100 Zeichen)",

    'max_length': "Maximal {max} Zeichen erlaubt",
    'min_length': "Mindestens {min} Zeichen erforderlich",
    'invalid_email': "Ungültiges E-Mail-Format",
    'invalid_phone': "Ungültiges Telefonformat",
    'invalid_postal_code': "Ungültige PLZ",

    # Общие сообщения
    'all_fields_required_step2': "Alle Felder in Schritt 2 sind Pflichtfelder",
    'complete_registration_required': "Vollständige Registrierungsdaten sind erforderlich",
    'banking_data_optional': "Alle Bankdaten sind optional"  # НОВОЕ
}

# ========================================
# UI Text Elements - ОБНОВЛЕНО с учетом банковских данных
# ========================================
company_ui_texts = {
    # Button labels
    'btn_next': "Weiter",
    'btn_back': "Zurück",
    'btn_save': "Speichern",
    'btn_cancel': "Abbrechen",
    'btn_delete': "Löschen",
    'btn_edit': "Bearbeiten",
    'btn_add': "Hinzufügen",
    'btn_create': "Registrieren",
    'btn_update': "Aktualisieren",
    'btn_finish': "Fertig",
    'btn_close': "Schließen",
    'btn_confirm': "Bestätigen",
    'btn_manage': "Verwalten",
    'btn_validate_iban': "IBAN prüfen",  # НОВОЕ

    # Status labels
    'status_loading': "Wird geladen...",
    'status_saving': "Wird gespeichert...",
    'status_processing': "Wird verarbeitet...",
    'status_validating': "Wird validiert...",
    'status_creating': "Wird registriert...",
    'status_updating': "Wird aktualisiert...",
    'status_deleting': "Wird gelöscht...",
    'status_checking_iban': "IBAN wird geprüft...",  # НОВОЕ

    # Common labels
    'required_field': "Pflichtfeld",
    'optional_field': "Optional",
    'recommended': "Empfohlen",
    'advanced': "Erweitert",
    'basic': "Grundlegend",
    'important': "Wichtig",
    'normal': "Normal",
    'public': "Öffentlich",
    'internal': "Intern",
    'mandatory': "Pflichtfeld",
    'all_required': "Alle erforderlich",
    'banking_optional': "Bankdaten optional",  # НОВОЕ

    # Navigation
    'step_of': "Schritt {current} von {total}",
    'progress': "Fortschritt",
    'completed': "Abgeschlossen",
    'current': "Aktuell",
    'pending': "Ausstehend",
    'validation_passed': "Validierung erfolgreich",
    'validation_failed': "Validierung fehlgeschlagen",
    'iban_valid': "IBAN gültig",  # НОВОЕ
    'iban_invalid': "IBAN ungültig"  # НОВОЕ
}

# ========================================
# Help Text and Tooltips - ОБНОВЛЕНО для банковского шага
# ========================================
company_help_texts = {
    'company_name': "Vollständiger Name Ihrer Firma",
    'legal_form': "Rechtsform Ihres Unternehmens",
    'industry': "Hauptgeschäftsfeld Ihrer Firma",

    # Тексты помощи для шага 2 - обязательные поля
    'commercial_register': "Eintragung im Handelsregister (PFLICHTFELD - Format: HRA12345 oder HRB12345)",
    'tax_number': "Steuernummer vom Finanzamt (PFLICHTFELD - Format: 12/345/67890)",
    'vat_id': "Umsatzsteuer-Identifikationsnummer für EU-Geschäfte (PFLICHTFELD - Format: DE123456789)",
    'tax_id': "11-stellige Steuer-Identifikationsnummer (PFLICHTFELD)",

    'street': "Vollständige Geschäftsadresse",
    'postal_code': "5-stellige Postleitzahl",
    'main_email': "Hauptkommunikations-E-Mail der Firma",
    'main_phone': "Haupttelefonnummer für Kunden",
    'additional_contacts': "Weitere Kontaktmöglichkeiten zur Verbesserung der Erreichbarkeit",
    'ceo_data': "Informationen zum Geschäftsführer/Inhaber",

    # НОВЫЕ тексты помощи для банковских данных
    'banking_main': "Hauptbankverbindung für Geschäftstransaktionen",
    'banking_iban': "Internationale Bankkontonummer (wird automatisch validiert)",
    'banking_bic': "Bank Identifier Code für internationale Überweisungen",
    'banking_holder': "Name des Kontoinhabers (meist Firmenname)",
    'banking_secondary': "Zusätzliche Bankverbindung für Liquidität oder spezielle Zwecke",
    'banking_primary_setting': "Diese Bankdaten erscheinen standardmäßig auf Rechnungen",
    'banking_sepa': "Ermöglicht automatischen Lastschrifteinzug von Kunden",
    'banking_notes': "Interne Notizen zu den Bankverbindungen",

    # Общие тексты помощи
    'registration_complete': "Alle Registrierungsfelder müssen für eine vollständige Firmenregistrierung ausgefüllt werden",
    'official_documents': "Diese Daten werden für offizielle Dokumente und Geschäftskorrespondenz verwendet",
    'legal_compliance': "Vollständige Registrierungsdaten sind für die Rechtskonformität erforderlich",
    'banking_optional_info': "Alle Bankdaten sind optional und können später ergänzt werden"  # НОВОЕ
}

# ========================================
# Accessibility Labels - ОБНОВЛЕНО с банковскими данными
# ========================================
company_aria_labels = {
    'close_modal': "Modal schließen",
    'delete_contact': "Kontakt löschen",
    'edit_contact': "Kontakt bearbeiten",
    'add_contact': "Kontakt hinzufügen",
    'contact_type': "Kontakttyp auswählen",
    'contact_value': "Kontaktdaten eingeben",
    'contact_department': "Abteilung auswählen",
    'contact_important': "Als wichtig markieren",
    'contact_public': "Als öffentlich markieren",
    'form_error': "Formularfehler",
    'required_field': "Pflichtfeld",
    'optional_field': "Optionales Feld",
    'validation_error': "Validierungsfehler",
    'success_message': "Erfolgsmeldung",
    'loading_content': "Inhalt wird geladen",
    'table_header': "Tabellenkopf",
    'table_cell': "Tabellenzelle",
    'pagination': "Seitennavigation",
    'search_field': "Suchfeld",
    'step_navigation': "Schrittnavigation",
    'form_section': "Formularabschnitt",

    # Accessibility labels для обязательных полей
    'required_field_marker': "Pflichtfeld-Kennzeichnung",
    'validation_status': "Validierungsstatus",
    'field_valid': "Feld korrekt ausgefüllt",
    'field_invalid': "Feld fehlerhaft",
    'all_fields_required': "Alle Felder erforderlich",
    'registration_form_section': "Registrierungsdaten-Formularabschnitt",

    # НОВЫЕ accessibility labels для банковских данных
    'banking_form_section': "Bankdaten-Formularabschnitt",
    'iban_field': "IBAN-Eingabefeld",
    'bic_field': "BIC-Eingabefeld",
    'bank_name_field': "Bankname-Eingabefeld",
    'iban_validation_status': "IBAN-Validierungsstatus",
    'banking_settings': "Bankeinstellungen",
    'primary_account_setting': "Hauptkonto-Einstellung",
    'sepa_setting': "SEPA-Einstellung"
}

# ========================================
# НОВЫЕ константы для банковского шага
# ========================================
company_step5_specific = {
    'title_emphasis': "Bankverbindungsdaten (optional)",
    'all_optional_notice': "Alle Felder in diesem Schritt sind optional",
    'can_skip': "Dieser Schritt kann übersprungen werden",
    'banking_importance': "Bankdaten erleichtern die Rechnungsstellung und den Zahlungsverkehr",
    'iban_auto_validation': "IBAN wird automatisch auf Gültigkeit geprüft",
    'secure_storage': "Alle Bankdaten werden sicher verschlüsselt gespeichert",
    'multiple_accounts_support': "Bis zu zwei Bankverbindungen können hinterlegt werden"
}