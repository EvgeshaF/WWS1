# companies/language.py

# ========================================
# Company Registration Form
# ========================================
text_company_registration = {
    'title': "Firmenregistrierung",
    'header': "Registrieren Sie Ihr Unternehmen",
    'desc': "Füllen Sie alle erforderlichen Felder aus, um Ihr Unternehmen im WWS1 System zu registrieren:",
    'btn': "Firma registrieren",
    'btn_reset': "Formular zurücksetzen",
    'notification': "* Mit einem Stern markierte Felder sind Pflichtfelder und müssen ausgefüllt werden."
}

# ========================================
# Registration Success Page
# ========================================
text_registration_success = {
    'title': "Registrierung erfolgreich",
    'header': "Ihre Firma wurde erfolgreich registriert!",
    'desc': "Vielen Dank für Ihre Registrierung. Ihre Daten wurden erfolgreich übermittelt.",
    'next_steps_title': "Nächste Schritte",
    'next_steps': [
        "Sie erhalten in Kürze eine Bestätigungs-E-Mail an die angegebene Adresse",
        "Unser Team wird Ihre Angaben prüfen und sich binnen 24 Stunden bei Ihnen melden",
        "Nach der Genehmigung erhalten Sie Ihre Zugangsdaten für das WWS1 System",
        "Bei Fragen können Sie sich jederzeit an unseren Support wenden"
    ],
    'btn_home': "Zur Startseite",
    'btn_new_registration': "Weitere Firma registrieren"
}

# ========================================
# Company List Page
# ========================================
text_company_list = {
    'title': "Registrierte Firmen",
    'header': "Übersicht aller Unternehmen",
    'desc': "Hier finden Sie eine Übersicht aller im System registrierten Unternehmen:",
    'search_placeholder': "Firma suchen...",
    'btn_search': "Suchen",
    'btn_export': "Als CSV exportieren",
    'btn_new_company': "Neue Firma registrieren",

    # Table headers
    'table_company': "Firmenname",
    'table_legal_form': "Rechtsform",
    'table_industry': "Branche",
    'table_city': "Stadt",
    'table_status': "Status",
    'table_created': "Registriert",
    'table_actions': "Aktionen",

    # Status labels
    'status_pending': "Wartend",
    'status_approved': "Genehmigt",
    'status_rejected': "Abgelehnt",
    'status_active': "Aktiv",
    'status_inactive': "Inaktiv",

    # Actions
    'action_view': "Anzeigen",
    'action_edit': "Bearbeiten",
    'action_approve': "Genehmigen",
    'action_reject': "Ablehnen",
    'action_delete': "Löschen"
}

# ========================================
# Form Field Labels and Help Texts
# ========================================
form_labels = {
    # Basic company info
    'company_name': "Firmenname",
    'legal_form': "Rechtsform",
    'tax_number': "Steuernummer",
    'vat_number': "USt-IdNr.",
    'registration_number': "Handelsregisternummer",
    'industry': "Branche",

    # Address
    'street': "Straße und Hausnummer",
    'postal_code': "PLZ",
    'city': "Stadt",
    'country': "Land",

    # Contact info
    'phone': "Telefon",
    'fax': "Fax",
    'email': "E-Mail",
    'website': "Website",

    # Contact person
    'contact_salutation': "Anrede",
    'contact_first_name': "Vorname",
    'contact_last_name': "Nachname",
    'contact_position': "Position",
    'contact_phone': "Telefon direkt",
    'contact_email': "E-Mail direkt",

    # Additional
    'description': "Unternehmensbeschreibung",
    'terms_accepted': "Nutzungsbedingungen akzeptiert",
    'newsletter': "Newsletter abonnieren"
}

# ========================================
# Form Help Texts
# ========================================
form_help_texts = {
    'company_name': "Der vollständige offizielle Name Ihres Unternehmens",
    'legal_form': "Wählen Sie die passende Rechtsform Ihres Unternehmens",
    'tax_number': "Ihre beim Finanzamt registrierte Steuernummer",
    'vat_number': "Umsatzsteuer-Identifikationsnummer (bei EU-Geschäften)",
    'registration_number': "Falls im Handelsregister eingetragen",
    'industry': "Wählen Sie die Branche, die am besten zu Ihrem Unternehmen passt",
    'street': "Vollständige Geschäftsadresse mit Hausnummer",
    'postal_code': "Postleitzahl des Geschäftssitzes",
    'city': "Stadt des Geschäftssitzes",
    'country': "Land des Geschäftssitzes",
    'phone': "Haupttelefonnummer des Unternehmens",
    'fax': "Faxnummer (optional)",
    'email': "Haupt-E-Mail-Adresse des Unternehmens",
    'website': "Unternehmens-Website (falls vorhanden)",
    'contact_first_name': "Vorname des Hauptansprechpartners",
    'contact_last_name': "Nachname des Hauptansprechpartners",
    'contact_position': "Position/Funktion im Unternehmen",
    'contact_phone': "Direkte Telefonnummer des Ansprechpartners",
    'contact_email': "Direkte E-Mail-Adresse des Ansprechpartners",
    'description': "Kurze Beschreibung Ihres Unternehmens und Ihrer Geschäftstätigkeit",
    'terms_accepted': "Bestätigung der Nutzungsbedingungen und Datenschutzerklärung",
    'newsletter': "Regelmäßige Informationen über Updates und Neuigkeiten"
}

# ========================================
# Validation Messages
# ========================================
validation_messages = {
    'required_field': "Dieses Feld ist erforderlich",
    'invalid_format': "Ungültiges Format",
    'email_invalid': "Ungültige E-Mail-Adresse",
    'phone_invalid': "Ungültiges Telefonformat",
    'url_invalid': "Ungültige Website-URL",
    'tax_number_invalid': "Ungültiges Format der Steuernummer",
    'vat_number_invalid': "Ungültiges Format der USt-IdNr.",
    'postal_code_invalid': "Ungültige Postleitzahl",
    'company_exists': "Eine Firma mit diesen Daten existiert bereits",
    'email_duplicate': "Diese E-Mail-Adresse wird bereits verwendet",
    'tax_number_duplicate': "Diese Steuernummer wird bereits verwendet",
    'terms_required': "Sie müssen die Nutzungsbedingungen akzeptieren",
    'email_mismatch': "Unternehmens-E-Mail und Kontakt-E-Mail dürfen nicht identisch sein"
}

# ========================================
# Success Messages
# ========================================
success_messages = {
    'company_registered': "Firma erfolgreich registriert",
    'data_saved': "Daten erfolgreich gespeichert",
    'email_sent': "Bestätigungs-E-Mail versendet",
    'form_validated': "Alle Eingaben sind gültig"
}

# ========================================
# Error Messages
# ========================================
error_messages = {
    'system_not_ready': "System ist noch nicht vollständig konfiguriert",
    'database_error': "Datenbankfehler aufgetreten",
    'registration_failed': "Registrierung fehlgeschlagen",
    'form_invalid': "Formular enthält ungültige Daten",
    'unexpected_error': "Ein unerwarteter Fehler ist aufgetreten",
    'network_error': "Netzwerkfehler aufgetreten",
    'company_creation_failed': "Fehler beim Erstellen der Firma",
    'duplicate_entry': "Eintrag bereits vorhanden",
    'validation_failed': "Datenvalidierung fehlgeschlagen"
}

# ========================================
# Progress Steps
# ========================================
progress_steps = {
    'validating': "Daten werden validiert...",
    'checking_duplicates': "Prüfe auf Duplikate...",
    'saving_data': "Daten werden gespeichert...",
    'creating_company': "Firma wird erstellt...",
    'sending_confirmation': "Bestätigungs-E-Mail wird versendet...",
    'finalizing': "Registrierung wird abgeschlossen...",
    'completed': "Registrierung erfolgreich abgeschlossen!"
}

# ========================================
# UI Elements
# ========================================
ui_elements = {
    'required_marker': "*",
    'loading_text': "Wird geladen...",
    'saving_text': "Wird gespeichert...",
    'processing_text': "Wird verarbeitet...",
    'search_placeholder': "Suchen...",
    'no_results': "Keine Ergebnisse gefunden",
    'show_more': "Mehr anzeigen",
    'show_less': "Weniger anzeigen",
    'back_to_top': "Nach oben",
    'print_page': "Seite drucken",
    'export_data': "Daten exportieren"
}

# ========================================
# Section Headers
# ========================================
section_headers = {
    'basic_info': "Grunddaten des Unternehmens",
    'address_info': "Firmenadresse",
    'contact_info': "Kontaktdaten",
    'contact_person': "Ansprechpartner",
    'additional_info': "Zusätzliche Informationen",
    'terms_privacy': "Nutzungsbedingungen und Datenschutz"
}

# ========================================
# Tooltips and Hints
# ========================================
tooltips = {
    'required_field': "Dieses Feld ist erforderlich",
    'optional_field': "Dieses Feld ist optional",
    'format_hint': "Bitte beachten Sie das erforderliche Format",
    'unique_field': "Dieser Wert muss eindeutig sein",
    'confidential': "Diese Daten werden vertraulich behandelt",
    'help_available': "Hilfe verfügbar - klicken Sie auf das Info-Symbol"
}

# ========================================
# Legal Forms (Extended)
# ========================================
legal_forms = {
    'gmbh': {
        'full_name': 'Gesellschaft mit beschränkter Haftung',
        'abbreviation': 'GmbH',
        'description': 'Kapitalgesellschaft mit beschränkter Haftung'
    },
    'ag': {
        'full_name': 'Aktiengesellschaft',
        'abbreviation': 'AG',
        'description': 'Kapitalgesellschaft mit Aktionären'
    },
    'ohg': {
        'full_name': 'Offene Handelsgesellschaft',
        'abbreviation': 'OHG',
        'description': 'Personengesellschaft mit unbeschränkter Haftung'
    },
    'kg': {
        'full_name': 'Kommanditgesellschaft',
        'abbreviation': 'KG',
        'description': 'Personengesellschaft mit Komplementären und Kommanditisten'
    },
    'ug': {
        'full_name': 'Unternehmergesellschaft',
        'abbreviation': 'UG',
        'description': 'Mini-GmbH mit geringerem Stammkapital'
    },
    'eg': {
        'full_name': 'eingetragene Genossenschaft',
        'abbreviation': 'eG',
        'description': 'Genossenschaftsunternehmen'
    },
    'einzelunternehmen': {
        'full_name': 'Einzelunternehmen',
        'abbreviation': 'e.K.',
        'description': 'Unternehmen einer natürlichen Person'
    },
    'freiberufler': {
        'full_name': 'Freiberufler',
        'abbreviation': '',
        'description': 'Selbstständige Tätigkeit in freien Berufen'
    }
}

# ========================================
# Industries (Extended)
# ========================================
industries = {
    'automotive': 'Automobilindustrie',
    'construction': 'Bauwesen',
    'chemicals': 'Chemie und Pharmazie',
    'electronics': 'Elektronik und Elektrotechnik',
    'energy': 'Energie und Umwelt',
    'food': 'Lebensmittel und Getränke',
    'healthcare': 'Gesundheitswesen',
    'it': 'Informationstechnologie',
    'logistics': 'Logistik und Transport',
    'manufacturing': 'Fertigung und Produktion',
    'retail': 'Einzelhandel',
    'services': 'Dienstleistungen',
    'textiles': 'Textil und Bekleidung',
    'finance': 'Finanz- und Versicherungswesen',
    'education': 'Bildung und Ausbildung',
    'tourism': 'Tourismus und Gastgewerbe',
    'media': 'Medien und Kommunikation',
    'real_estate': 'Immobilien',
    'agriculture': 'Land- und Forstwirtschaft',
    'consulting': 'Beratung',
    'other': 'Sonstige'
}