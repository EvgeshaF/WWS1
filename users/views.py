# users/views.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from loguru import logger
import datetime

from .forms import CreateAdminUserForm, AdminProfileForm, AdminPermissionsForm
from mongodb.mongodb_config import MongoConfig
from mongodb.mongodb_utils import MongoConnection
from .user_utils import UserManager
from . import language

from django_ratelimit.decorators import ratelimit


def render_toast_response(request):
    """JSON ответ с сообщениями для HTMX"""
    storage = messages.get_messages(request)
    messages_list = []
    for message in storage:
        messages_list.append({
            'tags': message.tags,
            'text': str(message),
            'delay': 5000
        })

    response = JsonResponse({'messages': messages_list})
    response['Content-Type'] = 'application/json'
    logger.debug(f"Отправляем toast ответ: {messages_list}")
    return response


@ratelimit(key='ip', rate='3/m', method='POST')
def create_admin_step1(request):
    """Шаг 1: Создание учетных данных администратора"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    # Проверяем, что MongoDB настроена
    config = MongoConfig.read_config()
    if not config.get('setup_completed'):
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    if request.method == 'POST':
        logger.info("Обработка POST запроса для шага 1")

        form = CreateAdminUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            logger.info(f"Валидация формы прошла для: {username}")

            # Используем UserManager для проверки
            user_manager = UserManager()

            # Проверяем, что пользователь с таким именем не существует
            existing_user = user_manager.find_user_by_username(username)
            if existing_user:
                logger.warning(f"Пользователь {username} уже существует")
                messages.error(request, f"Benutzer '{username}' existiert bereits")
                if is_htmx:
                    return render_toast_response(request)
            else:
                # Сохраняем данные в сессии для следующих шагов
                request.session['admin_creation'] = {
                    'username': username,
                    'password': password,
                    'step': 1
                }

                logger.success(f"Данные сохранены в сессии: {username}")
                messages.success(request, f"Benutzerdaten für '{username}' erfolgreich validiert")

                if is_htmx:
                    return render_toast_response(request)
                else:
                    return redirect('create_admin_step2')
        else:
            logger.error(f"Форма невалидна: {form.errors}")
            messages.error(request, "Formular ist ungültig. Bitte überprüfen Sie die Eingaben.")
            if is_htmx:
                return render_toast_response(request)

    else:  # GET-запрос
        form = CreateAdminUserForm()

    return render(request, 'users/create_admin_step1.html', {
        'form': form,
        'text': language.text_create_admin_step1,
        'step': 1
    })


@ratelimit(key='ip', rate='3/m', method='POST')
def create_admin_step2(request):
    """Шаг 2: Профиль администратора"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    # Проверяем, что первый шаг завершен
    admin_creation = request.session.get('admin_creation')
    if not admin_creation or admin_creation.get('step') != 1:
        messages.error(request, "Bitte vollenden Sie zuerst Schritt 1")
        return redirect('create_admin_step1')

    if request.method == 'POST':
        logger.info("Обработка POST запроса для шага 2")

        form = AdminProfileForm(request.POST)
        if form.is_valid():
            # Обновляем данные в сессии
            admin_creation.update({
                'salutation': form.cleaned_data['salutation'],
                'title': form.cleaned_data['title'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone'],
                'step': 2
            })
            request.session['admin_creation'] = admin_creation

            logger.success("Данные профиля сохранены в сессии")
            messages.success(request, "Profildaten erfolgreich erfasst")

            if is_htmx:
                return render_toast_response(request)
            else:
                return redirect('create_admin_step3')
        else:
            logger.error(f"Форма шага 2 невалидна: {form.errors}")
            messages.error(request, "Formular ist ungültig. Bitte überprüfen Sie die Eingaben.")
            if is_htmx:
                return render_toast_response(request)

    else:  # GET-запрос
        form = AdminProfileForm()

    return render(request, 'users/create_admin_step2.html', {
        'form': form,
        'text': language.text_create_admin_step2,
        'step': 2,
        'username': admin_creation['username']
    })


@ratelimit(key='ip', rate='2/m', method='POST')
def create_admin_step3(request):
    """Шаг 3: Разрешения и создание администратора"""
    is_htmx = request.headers.get('HX-Request') == 'true'

    # Проверяем сессию
    admin_creation = request.session.get('admin_creation')
    if not admin_creation or admin_creation.get('step') != 2:
        messages.error(request, "Bitte vollenden Sie die vorherigen Schritte")
        return redirect('create_admin_step1')

    if request.method == 'POST':
        logger.info(f"НАЧАЛО создания администратора: {admin_creation['username']}")

        form = AdminPermissionsForm(request.POST)
        if form.is_valid():
            try:
                # ====== ПРОВЕРЯЕМ ДОСТУПНОСТЬ MONGODB ======
                user_manager = UserManager()
                collection = user_manager.get_collection()

                if collection is None:  # ИСПРАВЛЕНО: используем 'is None'
                    logger.error("❌ Коллекция пользователей недоступна")
                    messages.error(request, "Datenbankfehler: Benutzersammlung nicht verfügbar")
                    if is_htmx:
                        return render_toast_response(request)
                    return render(request, 'users/create_admin_step3.html', {
                        'form': form,
                        'text': language.text_create_admin_step3,
                        'step': 3,
                        'username': admin_creation.get('username', ''),
                        'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}"
                    })

                # ====== ПОДГОТОВКА ДАННЫХ ПОЛЬЗОВАТЕЛЯ ======
                now = datetime.datetime.now()
                user_data = {
                    'username': admin_creation['username'],
                    'password': make_password(admin_creation['password']),
                    'profile': {
                        'salutation': admin_creation.get('salutation', ''),
                        'title': admin_creation.get('title', ''),
                        'first_name': admin_creation.get('first_name', ''),
                        'last_name': admin_creation.get('last_name', ''),
                        'email': admin_creation.get('email', ''),
                        'phone': admin_creation.get('phone', ''),
                    },
                    'permissions': {
                        'is_super_admin': form.cleaned_data.get('is_super_admin', False),
                        'can_manage_users': form.cleaned_data.get('can_manage_users', False),
                        'can_manage_database': form.cleaned_data.get('can_manage_database', False),
                        'can_view_logs': form.cleaned_data.get('can_view_logs', False),
                        'can_manage_settings': form.cleaned_data.get('can_manage_settings', False),
                        'password_expires': form.cleaned_data.get('password_expires', True),
                        'two_factor_required': form.cleaned_data.get('two_factor_required', False),
                    },
                    # Системные поля
                    'is_admin': True,
                    'is_active': True,
                    'created_at': now,
                    'modified_at': now,
                    'deleted': False,
                    'last_login': None,
                    'failed_login_attempts': 0,
                    'locked_until': None,
                    'password_changed_at': now
                }

                logger.info(f"✅ Данные пользователя подготовлены для: {user_data['username']}")

                # ====== ПРОВЕРКА ДУБЛИРОВАНИЯ ======
                existing_user = collection.find_one({
                    'username': user_data['username'],
                    'deleted': {'$ne': True}
                })

                if existing_user:
                    logger.error(f"❌ Пользователь {user_data['username']} уже существует")
                    messages.error(request, f"Benutzer '{user_data['username']}' existiert bereits")
                    if is_htmx:
                        return render_toast_response(request)
                    return render(request, 'users/create_admin_step3.html', {
                        'form': form,
                        'text': language.text_create_admin_step3,
                        'step': 3,
                        'username': admin_creation.get('username', ''),
                        'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}"
                    })

                # ====== СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ ======
                logger.info(f"🚀 ВСТАВЛЯЕМ пользователя в коллекцию: {collection.name}")

                # Логируем данные без пароля
                log_data = {k: v for k, v in user_data.items() if k != 'password'}
                logger.info(f"📝 Данные для вставки: {log_data}")

                # ВСТАВЛЯЕМ
                result = collection.insert_one(user_data.copy())

                logger.info(f"📋 Результат вставки: inserted_id={result.inserted_id}")

                if result.inserted_id:
                    # ====== НЕМЕДЛЕННАЯ ПРОВЕРКА ======
                    logger.info(f"🔍 Проверяем сохранение по ID: {result.inserted_id}")

                    verification_by_id = collection.find_one({'_id': result.inserted_id})
                    if verification_by_id:
                        logger.success(f"✅ НАЙДЕН по ID: {verification_by_id.get('username')}")

                        # Дополнительная проверка по имени
                        verification_by_name = collection.find_one({
                            'username': user_data['username'],
                            'deleted': {'$ne': True}
                        })

                        if verification_by_name:
                            logger.success(f"✅ НАЙДЕН по имени: {verification_by_name.get('username')}")

                            # Проверяем количество администраторов
                            admin_count = collection.count_documents({
                                'is_admin': True,
                                'deleted': {'$ne': True},
                                'is_active': True
                            })
                            logger.info(f"📊 Общее количество активных администраторов: {admin_count}")

                            # ====== УСПЕХ! ОЧИЩАЕМ СЕССИЮ ======
                            if 'admin_creation' in request.session:
                                del request.session['admin_creation']
                                logger.info("🧹 Сессия очищена")

                            success_msg = f"Administrator '{user_data['username']}' wurde erfolgreich erstellt!"
                            logger.success(f"🎉 {success_msg}")
                            messages.success(request, success_msg)

                            if is_htmx:
                                # Для HTMX возвращаем JSON с перенаправлением
                                logger.info("🔄 Возвращаем HTMX ответ с сообщением об успехе")
                                return render_toast_response(request)
                            else:
                                # Прямое перенаправление
                                logger.info("🔄 Прямое перенаправление на главную")
                                return redirect('home')

                        else:
                            logger.error("❌ НЕ НАЙДЕН по имени после создания!")
                    else:
                        logger.error("❌ НЕ НАЙДЕН по ID после создания!")

                # ====== ОШИБКА СОЗДАНИЯ ======
                logger.error("❌ Не удалось создать пользователя")
                messages.error(request, "Fehler beim Erstellen des Administrators")

            except Exception as e:
                logger.exception(f"💥 КРИТИЧЕСКАЯ ОШИБКА при создании администратора: {e}")
                messages.error(request, f"Kritischer Fehler: {str(e)}")

            # В случае ошибки возвращаем форму с ошибкой
            if is_htmx:
                return render_toast_response(request)

        else:
            logger.error(f"❌ Форма невалидна: {form.errors}")
            messages.error(request, "Bitte korrigieren Sie die Formularfehler")
            if is_htmx:
                return render_toast_response(request)

    else:  # GET
        form = AdminPermissionsForm()

    return render(request, 'users/create_admin_step3.html', {
        'form': form,
        'text': language.text_create_admin_step3,
        'step': 3,
        'username': admin_creation.get('username', ''),
        'full_name': f"{admin_creation.get('first_name', '')} {admin_creation.get('last_name', '')}"
    })
