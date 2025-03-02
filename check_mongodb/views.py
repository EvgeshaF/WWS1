from django.http import JsonResponse
from django.shortcuts import render
from .forms import DBSettingsForm
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_SETTINGS_PATH = os.path.join(BASE_DIR, 'check_mongodb', 'db.cfg')

def create_db_settings(username, password, host, port, auth_source):
    """Создаёт файл db_settings.cfg с параметрами подключения к MongoDB"""
    settings_content = f"""DATABASES = {{
    'default': {{
        'ENGINE': 'djongo',
        'NAME': 'wws',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {{
            'host': 'mongodb://{username}:{password}@{host}:{port}/',
            'authSource': '{auth_source}',
        }}
    }}
}}"""
    print(f"📁 Начало создания файла {DB_SETTINGS_PATH}")

    try:
        with open(DB_SETTINGS_PATH, "w", encoding="utf-8") as f:
            f.write(settings_content)

        if os.path.exists(DB_SETTINGS_PATH):
            print(f"✅ Файл {DB_SETTINGS_PATH} успешно создан.")
            return True
        else:
            print(f"❌ Файл {DB_SETTINGS_PATH} НЕ был создан.")
            return False

    except Exception as e:
        print(f"❌ Ошибка при создании файла: {e}")
        return False


def check_mongodb(request):
    # Если файл не существует, показываем форму для ввода данных
    if not os.path.exists(DB_SETTINGS_PATH):
        if request.method == "POST":
            form = DBSettingsForm(request.POST)

            if form.is_valid():
                print("✅ Форма валидна!")

                created = create_db_settings(
                    form.cleaned_data["username"],
                    form.cleaned_data["password"],
                    form.cleaned_data["host"],
                    form.cleaned_data["port"],
                    form.cleaned_data["auth_source"],
                )


                if created:
                    print("🎯 Настройки сохранены")
                    return render(request, 'check_mongodb/status_update.html', {
                        'status': "✅ Файл настроек успешно создан! Перезагрузите страницу.",
                        'success': True
                    })
                else:
                    print("❌ Ошибка при сохранении файла")
                    return render(request, 'check_mongodb/status_update.html', {
                        'status': "❌ Ошибка при создании файла!",
                        'success': False
                    })

            else:
                print("❌ Форма НЕ валидна:", form.errors)
                # initial_data = {
                #     'username': 'evgenij',
                #     'password': '',
                #     'host': '192.168.178.100',
                #     'port': 27017,
                #     'auth_source': 'admin'
                # }
                # form = DBSettingsForm(initial=initial_data)
                # Если форма невалидна, отобразим ошибку
                form = DBSettingsForm()
                return render(request, "check_mongodb/setup_form.html", {"form": form})


    print("🔍 Файл уже существует")
    return JsonResponse({
        "status": "✅ Файл настроек уже существует!",
        "success": True
    })
