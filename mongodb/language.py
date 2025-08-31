# language.py

# ========================================
# Connection Form (Serverkonfiguration)
# ========================================
text_server_conf = {
    'title': "Serverkonfiguration",
    'header': "Konfigurieren der Verbindung mit dem Server",
    'desc': "Geben Sie Host und Port ein:",
    'host': "Host:",
    'port': "Port:",
    'btn': "Überprüfen Sie die Verbindung",
    'notification': "* Nach einer erfolgreichen Überprüfung der Verbindung werden die Daten zur weiteren Verwendung gespeichert."
}

mess_server_configuration_warning = "Parameter zum Pingen des Datenbankservers fehlen oder sind falsch."
mess_server_configuration_info = "Geben Sie die Anforderungen der Parameter ein."
mess_server_ping_success = "Ping des MongoDB-Servers war erfolgreich"
mess_server_ping_error = "Ping des MongoDB-Server fehlgeschlagen"
mess_server_auth_success = "Authentifizierung des MongoDB-Serveradministrators war erfolgreich"
mess_server_auth_error = "Authentifizierung des MongoDB-Serveradministrators fehlgeschlagen"
mess_server_connect_success = "Die Verbindung zum Server war erfolgreich"
mess_db_name_admin_warning = "In der Konfigurationsdatei der Datenbankverbindung wird die Hauptdatenbank als 'admin' angegeben"
mess_datei_conf_update_succeed = "Konfigurationsdatei für die Datenbankverbindung aktualisiert"

# ========================================
# Login Form (Serveradministrator)
# ========================================
text_login_form = {
    'title': "Serververbindungsparameter",
    'header': "Autorisierung des Serveradministrators MongoDB",
    'desc': "Geben Sie die Daten des Serveradministrators ein:",
    'username': "Serveradministrator:",
    'password': "Administrator Passwort:",
    'db_name': "Standarddatenbank:",
    'btn': "Anmelden",
    'notification': "* Nach einer erfolgreichen Verbindung können Sie eine neue Datenbank erstellen."
}

mess_login_success1 = "Der Benutzer "
mess_login_success2 = " hat sich erfolgreich angemeldet."
mess_user_login_error = "Falscher Benutzername oder falsches Passwort."
mess_login_parameter_info = mess_server_configuration_info
mess_login_admin_error = "Falsche Administratoranmeldeinformationen."
mess_admin_auth_in_progress = "Authentifizierung läuft..."
mess_admin_rights_verified = "Administratorrechte verifiziert"

# ========================================
# Create Database Form (Neue Datenbank)
# ========================================
text_create_db_form = {
    'title': "Neue Datenbank erstellen",
    'header': "Erstellen einer neuen Datenbank",
    'desc': "Geben Sie einen Namen für eine neue Datenbank ein:",
    'db_name': "Neuer Datenbankname:",
    'btn': "Datenbank erstellen",
    'btn_warten': "Wird erstellt...",
    'notification': "* Nach dem Erstellen einer Datenbank ist die Konfiguration abgeschlossen."
}

mess_server_create_db = "Die Datenbank '"
mess_server_create_db_warning2 = "' existiert bereits"
mess_server_create_db_success2 = "' erfolgreich erstellt"
mess_server_create_db_error2 = "' konnte nicht erstellt werden"
mess_default_data_elemente = " Elemente hinzugefügt in der "
mess_default_data_element = " Element hinzugefügt in der "
mess_default_data_loaded_success = "Standarddaten erfolgreich geladen"
mess_default_data_loaded_error = " Hinzufügen der Standarddaten ist fehlgeschlagen"
mess_default_data_reading_error = " Fehler beim Lesen der Datei"
mess_form_invalid = "Das Formular wurde ungültig ausgefüllt. Bitte überprüfen Sie die eingegebenen Daten."

# ========================================
# General Messages
# ========================================
mess_connection_setup_required = "Zuerst müssen Sie die Serververbindung konfigurieren"
mess_unexpected_error = "Ein unerwarteter Fehler ist aufgetreten"
mess_operation_cancelled = "Vorgang abgebrochen"
