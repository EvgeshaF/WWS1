# company/language.py - Enhanced Company Form Texts

# ========================================
# Company Registration Step 1 (Grunddaten)
# ========================================
text_company_step1 = {
    'title': "Firma registrieren",
    'header': "Grunddaten der Firma",
    'desc': "Geben Sie die grundlegenden Informationen über Ihre Firma ein:",
    'company_name': "Firmenname:",
    'legal_form': "Rechtsform:",
    'industry': "Branche:",
    'description': "Geschäftsbeschreibung:",
    'btn': "Weiter zu Schritt 2",
    'notification': "* Alle Angaben können später bearbeitet werden."
}

# ========================================
# Company Registration Step 2 (Registrierungsdaten)
# ========================================
text_company_step2 = {
    'title': "Registrierungsdaten",
    'header': "Amtliche Registrierungsdaten",
    'desc': "Geben Sie die offiziellen Registrierungsdaten Ihrer Firma ein:",
    'commercial_register': "Handelsregister:",
    'tax_number': "Steuernummer:",
    'vat_id': "USt-IdNr.:",
    'tax_id': "Steuer-ID:",
    'btn': "Weiter zu Schritt 3",
    'btn_back': "Zurück zu Schritt 1",
    'notification': "* Registrierungsdaten sind optional, erhöhen aber die Glaubwürdigkeit."
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
# Company Registration Step 5 (Management und Personal)
# ========================================
text_company_step5 = {
    'title': "Management & Personal",
    'header': "Geschäftsführung und Ansprechpartner",
    'desc': "Geben Sie Informationen zur Geschäftsführung und zu Ansprechpartnern ein:",
    'ceo_data': "Geschäftsführer:",
    'contact_person_data': "Hauptansprechpartner:",
    'employee_count': "Mitarbeiteranzahl:",
    'btn': "Weiter zu Schritt 6",
    'btn_back': "Zurück zu Schritt 4",
    'notification': "* Diese Angaben sind optional, erleichtern aber die Kommunikation."
}

# ========================================
# Company Registration Step 6 (Optionen und Einstellungen)
# ========================================
text_company_step6 = {
    'title': "Einstellungen",
    'header': "Finale Einstellungen und Bestätigung",
    'desc': "Legen Sie die finalen Einstellungen für Ihre Firma fest:",
    'options_title': "Firmeneinstellungen:",
    'privacy_title': "Datenschutz und Benachrichtigungen:",
    'btn': "Firma registrieren",
    'btn_back': "Zurück zu Schritt 5",
    'notification': "* Die Datenschutzerklärung muss akzeptiert werden, um fortzufahren."
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
# Enhanced Success Messages
# ========================================
company_success_messages = {
    'step1_completed': "Grunddaten für '{company_name}' erfolgreich validiert",
    'step2_completed': "Registrierungsdaten erfolgreich erfasst",
    'step3_completed': "Adressdaten erfolgreich erfasst",
    'step4_completed': "Kontaktdaten erfolgreich erfasst ({contact_info})",
    'step5_completed': "Management-Daten erfolgreich erfasst",
    'company_created': "Firma '{company_name}' wurde erfolgreich registriert! Kontakte: {contact_info}",

    # Contact summary formats
    'contacts_basic_only': "Haupt-E-Mail, Haupttelefon",
    'contacts_with_additional': "{main} + {additional} zusätzliche",
    'contacts_total': "{total} Kontakte insgesamt",

    # Progress messages
    'company_data_saved': "Firmendaten erfolgreich gespeichert",
    'contacts_processed': "Kontaktdaten erfolgreich verarbeitet",
    'validation_passed': "Validierung erfolgreich abgeschlossen"
}

# ========================================
# Enhanced Error Messages
# ========================================
company_error_messages = {
    'mongodb_not_configured': "MongoDB muss zuerst konfiguriert werden",
    'company_exists': "Eine Firma mit diesem Namen existiert bereits",
    'company_creation_error': "Fehler beim Registrieren der Firma",
    'session_expired': "Die Sitzung ist abgelaufen. Bitte beginnen Sie erneut",
    'step_incomplete': "Bitte vollenden Sie die vorherigen Schritte",
    'contact_processing_error': "Fehler beim Verarbeiten der Kontaktdaten",
    'additional_contacts_error': "Fehler beim Verarbeiten der zusätzlichen Kontaktdaten",
    'form_submission_error': "Fehler beim Senden des Formulars",
    'validation_failed': "Validierung fehlgeschlagen",
    'required_field_missing': "Erforderliche Felder fehlen",
    'invalid_format': "Ungültiges Format",
    'server_error': "Serverfehler aufgetreten",
    'network_error': "Netzwerkfehler aufgetreten",
    'unexpected_error': "Ein unerwarteter Fehler ist aufgetreten"
}

# ========================================
# Validation Messages
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
    'max_length': "Maximal {max} Zeichen erlaubt",
    'min_length': "Mindestens {min} Zeichen erforderlich",
    'invalid_email': "Ungültiges E-Mail-Format",
    'invalid_phone': "Ungültiges Telefonformat",
    'invalid_postal_code': "Ungültige PLZ",
    'invalid_vat_id': "Ungültige USt-IdNr.",
    'invalid_commercial_register': "Ungültiges Handelsregister-Format",
    'data_protection_required': "Datenschutzerklärung muss akzeptiert werden"
}

# ========================================
# UI Text Elements
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

    # Status labels
    'status_loading': "Wird geladen...",
    'status_saving': "Wird gespeichert...",
    'status_processing': "Wird verarbeitet...",
    'status_validating': "Wird validiert...",
    'status_creating': "Wird registriert...",
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
    'public': "Öffentlich",
    'internal': "Intern",

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
company_help_texts = {
    'company_name': "Vollständiger Name Ihrer Firma",
    'legal_form': "Rechtsform Ihres Unternehmens",
    'industry': "Hauptgeschäftsfeld Ihrer Firma",
    'commercial_register': "Eintragung im Handelsregister (falls vorhanden)",
    'tax_number': "Steuernummer vom Finanzamt",
    'vat_id': "Umsatzsteuer-Identifikationsnummer für EU-Geschäfte",
    'street': "Vollständige Geschäftsadresse",
    'postal_code': "5-stellige Postleitzahl",
    'main_email': "Hauptkommunikations-E-Mail der Firma",
    'main_phone': "Haupttelefonnummer für Kunden",
    'additional_contacts': "Weitere Kontaktmöglichkeiten zur Verbesserung der Erreichbarkeit",
    'ceo_data': "Informationen zum Geschäftsführer/Inhaber",
    'contact_person': "Hauptansprechpartner für Anfragen",
    'employee_count': "Ungefähre Anzahl der Mitarbeiter",
    'is_primary': "Diese Firma als Standardfirma im System verwenden",
    'data_protection': "Zustimmung zur Verarbeitung der Firmendaten gemäß DSGVO"
}

# ========================================
# Accessibility Labels
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
    'form_section': "Formularabschnitt"
}