# users/language.py - Немецкие тексты для форм создания администратора

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
# Create Admin Step 2 (Profil)
# ========================================
text_create_admin_step2 = {
    'title': "Administrator Profil",
    'header': "Profildaten eingeben",
    'desc': "Vervollständigen Sie das Profil des Administrators:",
    'salutation': "Anrede:",
    'title_field': "Titel:",
    'first_name': "Vorname:",
    'last_name': "Nachname:",
    'email': "E-Mail:",
    'phone': "Telefon:",
    'btn': "Weiter zu Schritt 3",
    'btn_back': "Zurück zu Schritt 1",
    'notification': "* Diese Informationen werden für die Kontaktaufnahme und Identifikation verwendet."
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
# General Messages
# ========================================
mess_form_invalid = "Das Formular wurde ungültig ausgefüllt. Bitte überprüfen Sie die eingegebenen Daten."
mess_mongodb_not_configured = "MongoDB muss zuerst konfiguriert werden, bevor Benutzer erstellt werden können."
mess_user_exists = "Ein Benutzer mit diesem Namen existiert bereits."
mess_user_created_success = "Administrator erfolgreich erstellt."
mess_user_creation_error = "Fehler beim Erstellen des Administrators."
mess_session_expired = "Die Sitzung ist abgelaufen. Bitte beginnen Sie erneut."
mess_step_incomplete = "Bitte vollenden Sie die vorherigen Schritte."

# ========================================
# Form Help Texts
# ========================================
help_text_username = "3-50 Zeichen, beginnt mit Buchstaben, nur Buchstaben, Zahlen und Unterstriche"
help_text_password = "Mindestens 8 Zeichen mit Groß-/Kleinbuchstaben, Zahlen und Sonderzeichen"
help_text_email = "Wird für wichtige Systembenachrichtigungen verwendet"
help_text_phone = "Optional - für Notfallkontakt oder 2FA"
help_text_super_admin = "Hat vollständigen Zugriff auf alle Systemfunktionen"
help_text_password_expires = "Passwort muss regelmäßig geändert werden (empfohlen: 90 Tage)"
help_text_two_factor = "Erhöht die Sicherheit erheblich (empfohlen für alle Administratoren)"