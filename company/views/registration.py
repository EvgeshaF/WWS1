import json
import re

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from loguru import logger

from ..company_manager import CompanyManager
from .session import CompanySessionManager
from ..company_utils import check_mongodb_availability, render_with_messages
from ..forms import CompanyBasicDataForm, CompanyRegistrationForm, CompanyAddressForm, CompanyContactForm, CompanyBankingForm
from ..language import company_success_messages, company_error_messages, text_company_step1, text_company_step2, text_company_step3, text_company_step4, text_company_step5


def register_company(request):
    """Стартовая страница регистрации - перенаправляет на шаг 1"""
    # Очищаем предыдущие данные сессии
    CompanySessionManager.clear_session_data(request)
    logger.info("Начало процесса регистрации компании")
    return redirect('company:register_company_step1')


def register_company_step1(request):
    """Шаг 1: Основные данные компании - ОБНОВЛЕНО с возможностью сохранения"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    # Получаем данные из сессии для предзаполнения
    session_data = CompanySessionManager.get_session_data(request)

    if request.method == 'POST':
        form = CompanyBasicDataForm(request.POST)

        # НОВОЕ: Определяем действие пользователя
        action = request.POST.get('action', 'continue')  # 'continue' или 'save_and_close'

        if form.is_valid():
            # Сохраняем данные шага в сессию
            step_data = form.cleaned_data.copy()
            CompanySessionManager.update_session_data(request, step_data)

            company_name = step_data.get('company_name', '')

            # НОВОЕ: Если действие "сохранить и закрыть"
            if action == 'save_and_close':
                success = save_partial_company_data(request, step_data, step=1)
                if success:
                    return JsonResponse({
                        'success': True,
                        'action': 'save_and_close',
                        'messages': [{
                            'text': f"Grunddaten für '{company_name}' erfolgreich gespeichert",
                            'tags': 'success',
                            'delay': 3000
                        }],
                        'redirect_url': reverse('company:company_info')
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'messages': [{
                            'text': "Fehler beim Speichern der Grunddaten",
                            'tags': 'error',
                            'delay': 5000
                        }]
                    })

            # Обычное продолжение к следующему шагу
            messages.success(
                request,
                company_success_messages['step1_completed'].format(company_name=company_name)
            )

            return render_with_messages(
                request,
                'register_company_step1.html',
                {'form': form, 'step': 1, 'text': text_company_step1},
                reverse('company:register_company_step2')
            )
        else:
            messages.error(request, company_error_messages['form_submission_error'])
    else:
        # GET запрос - предзаполняем форму данными из сессии
        form = CompanyBasicDataForm(initial=session_data)

    context = {
        'form': form,
        'step': 1,
        'text': text_company_step1
    }
    return render(request, 'register_company_step1.html', context)


def register_company_step2(request):
    """Шаг 2: Регистрационные данные - ОБНОВЛЕНО с возможностью сохранения"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    # Проверяем, завершен ли предыдущий шаг
    completion = CompanySessionManager.get_completion_status(request)
    if not completion['step1_complete']:
        messages.warning(request, "Bitte vollenden Sie zuerst Schritt 1")
        return redirect('company:register_company_step1')

    session_data = CompanySessionManager.get_session_data(request)
    company_name = session_data.get('company_name', '')
    legal_form = session_data.get('legal_form', '')

    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)

        # НОВОЕ: Определяем действие пользователя
        action = request.POST.get('action', 'continue')

        # Дополнительная валидация для обязательных полей
        additional_errors = []
        required_fields = {
            'commercial_register': 'Handelsregister',
            'tax_number': 'Steuernummer',
            'vat_id': 'USt-IdNr.',
            'tax_id': 'Steuer-ID'
        }

        for field_name, field_label in required_fields.items():
            field_value = request.POST.get(field_name, '').strip()
            if not field_value:
                additional_errors.append(f"{field_label} ist erforderlich")

        # Проверяем форматы полей
        commercial_register = request.POST.get('commercial_register', '').strip()
        if commercial_register and not re.match(r'^(HR[AB]\s*\d+|HRA\s*\d+|HRB\s*\d+)$', commercial_register):
            additional_errors.append("Handelsregister: Format HRA12345 oder HRB12345 erforderlich")

        tax_number = request.POST.get('tax_number', '').strip()
        if tax_number and not re.match(r'^\d{1,3}/\d{3}/\d{4,5}$', tax_number):
            additional_errors.append("Steuernummer: Format 12/345/67890 erforderlich")

        vat_id = request.POST.get('vat_id', '').strip()
        if vat_id and not re.match(r'^DE\d{9}$', vat_id):
            additional_errors.append("USt-IdNr.: Format DE123456789 erforderlich")

        tax_id = request.POST.get('tax_id', '').strip()
        if tax_id and not re.match(r'^\d{11}$', tax_id):
            additional_errors.append("Steuer-ID: 11-stellige Nummer erforderlich")

        if additional_errors:
            for error in additional_errors:
                messages.error(request, error)
            logger.warning(f"Валидационные ошибки шага 2: {additional_errors}")

        if form.is_valid() and not additional_errors:
            # Сохраняем данные шага в сессию
            step_data = form.cleaned_data.copy()
            step_data['registration_data_processed'] = True
            step_data['all_registration_fields_complete'] = True
            CompanySessionManager.update_session_data(request, step_data)

            # НОВОЕ: Если действие "сохранить и закрыть"
            if action == 'save_and_close':
                # Получаем полные данные из сессии для сохранения
                full_data = CompanySessionManager.get_session_data(request)
                success = save_partial_company_data(request, full_data, step=2)
                if success:
                    return JsonResponse({
                        'success': True,
                        'action': 'save_and_close',
                        'messages': [{
                            'text': f"Registrierungsdaten für '{company_name}' erfolgreich gespeichert",
                            'tags': 'success',
                            'delay': 3000
                        }],
                        'redirect_url': reverse('company:company_info')
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'messages': [{
                            'text': "Fehler beim Speichern der Registrierungsdaten",
                            'tags': 'error',
                            'delay': 5000
                        }]
                    })

            logger.success(f"Шаг 2 завершен для компании '{company_name}': все регистрационные данные валидны")
            messages.success(request, company_success_messages['step2_completed'])

            return render_with_messages(
                request,
                'register_company_step2.html',
                {
                    'form': form, 'step': 2, 'text': text_company_step2,
                    'company_name': company_name, 'legal_form': legal_form
                },
                reverse('company:register_company_step3')
            )
        else:
            # Логируем конкретные ошибки формы
            if form.errors:
                for field, errors in form.errors.items():
                    logger.error(f"Ошибка поля {field}: {errors}")
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

            if additional_errors:
                messages.error(request, "Alle Registrierungsfelder müssen korrekt ausgefüllt werden")
            else:
                messages.error(request, company_error_messages['form_submission_error'])
    else:
        # GET запрос - предзаполняем форму данными из сессии
        form = CompanyRegistrationForm(initial=session_data)

    context = {
        'form': form,
        'step': 2,
        'text': text_company_step2,
        'company_name': company_name,
        'legal_form': legal_form
    }
    return render(request, 'register_company_step2.html', context)


def register_company_step3(request):
    """Шаг 3: Адресные данные - ОБНОВЛЕНО с возможностью сохранения"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    # Проверяем предыдущие шаги
    completion = CompanySessionManager.get_completion_status(request)
    if not completion['step1_complete']:
        messages.warning(request, "Bitte vollenden Sie zuerst Schritt 1")
        return redirect('company:register_company_step1')

    session_data = CompanySessionManager.get_session_data(request)
    company_name = session_data.get('company_name', '')
    legal_form = session_data.get('legal_form', '')

    if request.method == 'POST':
        form = CompanyAddressForm(request.POST)

        # НОВОЕ: Определяем действие пользователя
        action = request.POST.get('action', 'continue')

        if form.is_valid():
            step_data = form.cleaned_data.copy()
            CompanySessionManager.update_session_data(request, step_data)

            # НОВОЕ: Если действие "сохранить и закрыть"
            if action == 'save_and_close':
                full_data = CompanySessionManager.get_session_data(request)
                success = save_partial_company_data(request, full_data, step=3)
                if success:
                    return JsonResponse({
                        'success': True,
                        'action': 'save_and_close',
                        'messages': [{
                            'text': f"Adressdaten für '{company_name}' erfolgreich gespeichert",
                            'tags': 'success',
                            'delay': 3000
                        }],
                        'redirect_url': reverse('company:company_info')
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'messages': [{
                            'text': "Fehler beim Speichern der Adressdaten",
                            'tags': 'error',
                            'delay': 5000
                        }]
                    })

            messages.success(request, company_success_messages['step3_completed'])

            return render_with_messages(
                request,
                'register_company_step3.html',
                {
                    'form': form, 'step': 3, 'text': text_company_step3,
                    'company_name': company_name, 'legal_form': legal_form
                },
                reverse('company:register_company_step4')
            )
        else:
            messages.error(request, company_error_messages['form_submission_error'])
    else:
        form = CompanyAddressForm(initial=session_data)

    context = {
        'form': form,
        'step': 3,
        'text': text_company_step3,
        'company_name': company_name,
        'legal_form': legal_form
    }
    return render(request, 'register_company_step3.html', context)


def register_company_step4(request):
    """Шаг 4: Контактные данные - ОБНОВЛЕНО с возможностью сохранения"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    # Проверяем предыдущие шаги
    completion = CompanySessionManager.get_completion_status(request)
    if not completion['step1_complete'] or not completion['step3_complete']:
        messages.warning(request, "Bitte vollenden Sie die vorherigen Schritte")
        return redirect('company:register_company_step1')

    session_data = CompanySessionManager.get_session_data(request)
    company_name = session_data.get('company_name', '')
    legal_form = session_data.get('legal_form', '')

    # Получаем существующие дополнительные контакты из сессии
    existing_additional_contacts = session_data.get('additional_contacts_data', '[]')
    if isinstance(existing_additional_contacts, str):
        try:
            existing_additional_contacts = json.loads(existing_additional_contacts)
        except:
            existing_additional_contacts = []

    if request.method == 'POST':
        form = CompanyContactForm(request.POST)

        # НОВОЕ: Определяем действие пользователя
        action = request.POST.get('action', 'continue')

        if form.is_valid():
            step_data = form.cleaned_data.copy()

            # Обрабатываем дополнительные контакты
            additional_contacts_data = request.POST.get('additional_contacts_data', '[]')
            try:
                contacts = json.loads(additional_contacts_data) if additional_contacts_data else []
                if isinstance(contacts, list):
                    step_data['additional_contacts_data'] = additional_contacts_data
                    logger.info(f"Обработано {len(contacts)} дополнительных контактов")
                else:
                    step_data['additional_contacts_data'] = '[]'
            except json.JSONDecodeError:
                logger.warning("Некорректные данные дополнительных контактов")
                step_data['additional_contacts_data'] = '[]'

            CompanySessionManager.update_session_data(request, step_data)

            # НОВОЕ: Если действие "сохранить и закрыть"
            if action == 'save_and_close':
                full_data = CompanySessionManager.get_session_data(request)
                success = save_partial_company_data(request, full_data, step=4)
                if success:
                    additional_count = len(contacts) if contacts else 0
                    return JsonResponse({
                        'success': True,
                        'action': 'save_and_close',
                        'messages': [{
                            'text': f"Kontaktdaten für '{company_name}' erfolgreich gespeichert ({additional_count} zusätzliche Kontakte)",
                            'tags': 'success',
                            'delay': 3000
                        }],
                        'redirect_url': reverse('company:company_info')
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'messages': [{
                            'text': "Fehler beim Speichern der Kontaktdaten",
                            'tags': 'error',
                            'delay': 5000
                        }]
                    })

            # Формируем информацию о контактах для сообщения
            main_contacts = f"{step_data.get('email', '')}, {step_data.get('phone', '')}"
            additional_count = len(contacts) if contacts else 0

            if additional_count > 0:
                contact_info = f"{main_contacts} + {additional_count} zusätzliche"
            else:
                contact_info = main_contacts

            messages.success(
                request,
                company_success_messages['step4_completed'].format(contact_info=contact_info)
            )

            return render_with_messages(
                request,
                'register_company_step4.html',
                {
                    'form': form, 'step': 4, 'text': text_company_step4,
                    'company_name': company_name, 'legal_form': legal_form,
                    'existing_additional_contacts': json.dumps(contacts) if contacts else '[]'
                },
                reverse('company:register_company_step5')
            )
        else:
            messages.error(request, company_error_messages['form_submission_error'])
    else:
        form = CompanyContactForm(initial=session_data)

    context = {
        'form': form,
        'step': 4,
        'text': text_company_step4,
        'company_name': company_name,
        'legal_form': legal_form,
        'existing_additional_contacts': json.dumps(existing_additional_contacts)
    }
    return render(request, 'register_company_step4.html', context)


def register_company_step5(request):
    """ОБНОВЛЕНО: Шаг 5 - Банковские данные и создание компании с обязательными основными полями"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    # Проверяем предыдущие шаги
    completion = CompanySessionManager.get_completion_status(request)
    if not completion['step4_complete']:
        messages.warning(request, "Bitte vollenden Sie die vorherigen Schritte")
        return redirect('company:register_company_step4')

    session_data = CompanySessionManager.get_session_data(request)
    company_name = session_data.get('company_name', '')
    legal_form = session_data.get('legal_form', '')
    primary_email = session_data.get('email', '')

    # Подсчитываем контакты
    additional_contacts = session_data.get('additional_contacts_data', '[]')
    if isinstance(additional_contacts, str):
        try:
            additional_contacts = json.loads(additional_contacts)
        except:
            additional_contacts = []

    contact_count = 2  # email + phone
    if session_data.get('fax'):
        contact_count += 1
    if session_data.get('website'):
        contact_count += 1
    contact_count += len(additional_contacts)

    if request.method == 'POST':
        form = CompanyBankingForm(request.POST)

        # НОВОЕ: Определяем действие пользователя
        action = request.POST.get('action', 'complete')  # 'complete' или 'save_and_close'

        # НОВОЕ: Дополнительная валидация обязательных банковских полей
        additional_errors = []
        required_banking_fields = {
            'bank_name': 'Name der Bank',
            'iban': 'IBAN',
            'bic': 'BIC/SWIFT',
            'account_holder': 'Kontoinhaber'
        }

        for field_name, field_label in required_banking_fields.items():
            field_value = request.POST.get(field_name, '').strip()
            if not field_value:
                additional_errors.append(f"{field_label} ist erforderlich")

        # Дополнительная валидация IBAN и BIC форматов
        iban = request.POST.get('iban', '').strip().upper().replace(' ', '')
        if iban and not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$', iban):
            additional_errors.append("IBAN: Ungültiges Format (z.B. DE89370400440532013000)")

        bic = request.POST.get('bic', '').strip().upper()
        if bic and not re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', bic):
            additional_errors.append("BIC/SWIFT: Ungültiges Format (z.B. DEUTDEFF)")

        # Валидация вторичной IBAN, если она указана
        secondary_iban = request.POST.get('secondary_iban', '').strip().upper().replace(' ', '')
        if secondary_iban and not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$', secondary_iban):
            additional_errors.append("IBAN (Zweitbank): Ungültiges Format")

        secondary_bic = request.POST.get('secondary_bic', '').strip().upper()
        if secondary_bic and not re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', secondary_bic):
            additional_errors.append("BIC/SWIFT (Zweitbank): Ungültiges Format")

        if additional_errors:
            for error in additional_errors:
                messages.error(request, error)
            logger.warning(f"Валидационные ошибки банковских данных шага 5: {additional_errors}")

        if form.is_valid() and not additional_errors:
            # Сохраняем банковские данные в сессию
            banking_data = form.cleaned_data.copy()
            CompanySessionManager.update_session_data(request, banking_data)

            # Объединяем все данные из всех шагов
            final_data = CompanySessionManager.get_session_data(request)

            # Добавляем стандартные настройки компании
            final_data.update({
                'is_primary': True,
                'enable_notifications': True,
                'enable_marketing': False,
                'data_protection_consent': True
            })

            # НОВОЕ: Если действие "сохранить и закрыть" - только сохраняем банковские данные
            if action == 'save_and_close':
                success = save_partial_company_data(request, final_data, step=5)
                if success:
                    return JsonResponse({
                        'success': True,
                        'action': 'save_and_close',
                        'messages': [{
                            'text': f"Bankdaten für '{company_name}' erfolgreich gespeichert",
                            'tags': 'success',
                            'delay': 3000
                        }],
                        'redirect_url': reverse('company:company_info')
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'messages': [{
                            'text': "Fehler beim Speichern der Bankdaten",
                            'tags': 'error',
                            'delay': 5000
                        }]
                    })

            # Обычное завершение - создаем компанию в базе данных
            company_manager = CompanyManager()
            if company_manager.create_or_update_company(final_data):
                # Очищаем сессию после успешного создания
                CompanySessionManager.clear_session_data(request)

                # Формируем сообщение о банковских данных
                banking_info = "mit vollständiger Bankverbindung"
                if banking_data.get('secondary_iban'):
                    banking_info = "mit Haupt- und Zweitbankverbindung"

                success_message = f"Firma '{company_name}' wurde erfolgreich registriert ({banking_info})! Kontakte: {contact_count}"
                messages.success(request, success_message)

                return render_with_messages(
                    request,
                    'register_company_step5.html',
                    {
                        'form': form, 'step': 5, 'text': text_company_step5,
                        'company_name': company_name, 'legal_form': legal_form,
                        'primary_email': primary_email, 'contact_count': contact_count
                    },
                    reverse('home')
                )
            else:
                messages.error(request, company_error_messages['company_creation_error'])
        else:
            # Логируем конкретные ошибки формы
            if form.errors:
                for field, errors in form.errors.items():
                    logger.error(f"Ошибка поля {field}: {errors}")
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

            if additional_errors:
                messages.error(request, "Alle Hauptbankverbindungsfelder müssen korrekt ausgefüllt werden")
            else:
                messages.error(request, company_error_messages['validation_failed'])
    else:
        form = CompanyBankingForm(initial=session_data)

    context = {
        'form': form,
        'step': 5,
        'text': text_company_step5,
        'company_name': company_name,
        'legal_form': legal_form,
        'primary_email': primary_email,
        'contact_count': contact_count
    }
    return render(request, 'register_company_step5.html', context)


def save_partial_company_data(request, data, step):

    try:
        company_manager = CompanyManager()

        # Проверяем, существует ли уже компания
        existing_company = company_manager.get_company()

        if existing_company:
            # Обновляем существующую компанию, объединяя данные
            updated_data = existing_company.copy()
            updated_data.update(data)

            # Добавляем информацию о частичном сохранении
            updated_data['partial_save'] = True
            updated_data['last_saved_step'] = step

            # Убираем служебные поля MongoDB
            if '_id' in updated_data:
                del updated_data['_id']

            success = company_manager.create_or_update_company(updated_data)
        else:
            # Создаем новую частичную запись
            partial_data = data.copy()
            partial_data.update({
                'partial_save': True,
                'last_saved_step': step,
                'is_primary': True,
                'enable_notifications': True,
                'enable_marketing': False,
                'data_protection_consent': True
            })
            success = company_manager.create_or_update_company(partial_data)

        if success:
            logger.success(f"Частичные данные компании сохранены (шаг {step})")
            return True
        else:
            logger.error(f"Ошибка сохранения частичных данных компании (шаг {step})")
            return False

    except Exception as e:
        logger.error(f"Критическая ошибка сохранения частичных данных: {e}")
        return False


@require_http_methods(["GET"])
def company_validation_check(request):
    """ОБНОВЛЕНО: Улучшенная проверка валидности данных компании с обязательными банковскими полями"""
    if not check_mongodb_availability():
        return JsonResponse({'error': 'MongoDB not available'}, status=500)

    company_manager = CompanyManager()
    company = company_manager.get_company()

    if not company:
        return JsonResponse({'error': 'No company found'}, status=404)

    # Валидируем данные компании
    validation_results = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'completeness': 0,
        'step_status': {
            'step1': {'complete': False, 'errors': []},
            'step2': {'complete': False, 'errors': []},
            'step3': {'complete': False, 'errors': []},
            'step4': {'complete': False, 'errors': []},
            'step5': {'complete': False, 'errors': []}  # ИЗМЕНЕНО: теперь может быть incomplete
        }
    }

    # Проверяем обязательные поля по шагам
    step1_fields = {
        'company_name': 'Firmenname',
        'legal_form': 'Rechtsform'
    }

    # Все поля шага 2 теперь обязательны
    step2_fields = {
        'commercial_register': 'Handelsregister',
        'tax_number': 'Steuernummer',
        'vat_id': 'USt-IdNr.',
        'tax_id': 'Steuer-ID'
    }

    step3_fields = {
        'street': 'Straße',
        'postal_code': 'PLZ',
        'city': 'Stadt',
        'country': 'Land'
    }

    step4_fields = {
        'email': 'E-Mail',
        'phone': 'Telefon'
    }

    # ОБНОВЛЕНО: Банковские поля теперь обязательны (основные)
    step5_required_fields = {
        'bank_name': 'Name der Bank',
        'iban': 'IBAN',
        'bic': 'BIC/SWIFT',
        'account_holder': 'Kontoinhaber'
    }

    # Опциональные банковские поля
    step5_optional_fields = {
        'bank_address': 'Adresse der Bank',
        'account_type': 'Kontotyp',
        'secondary_bank_name': 'Zweitbank',
        'secondary_iban': 'IBAN (Zweitbank)',
        'secondary_bic': 'BIC/SWIFT (Zweitbank)',
        'banking_notes': 'Notizen'
    }

    # ОБНОВЛЕНО: Включаем обязательные банковские поля в общий список
    all_required_fields = {**step1_fields, **step2_fields, **step3_fields, **step4_fields, **step5_required_fields}

    filled_count = 0
    total_count = len(all_required_fields)

    # Валидируем каждый шаг отдельно (включая шаг 5)
    for step, fields in [('step1', step1_fields), ('step2', step2_fields),
                         ('step3', step3_fields), ('step4', step4_fields),
                         ('step5', step5_required_fields)]:  # ДОБАВЛЕНО: step5
        step_complete = True
        step_errors = []

        for field, label in fields.items():
            if not company.get(field) or not str(company.get(field)).strip():
                step_complete = False
                step_errors.append(f'{label} fehlt')
                validation_results['errors'].append(f'{label} fehlt')
                validation_results['is_valid'] = False
            else:
                filled_count += 1

                # Дополнительная валидация форматов для шага 2
                if step == 'step2':
                    field_value = str(company.get(field, '')).strip()
                    if field == 'commercial_register' and not re.match(r'^(HR[AB]\s*\d+|HRA\s*\d+|HRB\s*\d+)$', field_value):
                        step_errors.append(f'{label}: Format HRA12345 oder HRB12345 erforderlich')
                        validation_results['warnings'].append(f'{label}: Ungültiges Format')
                    elif field == 'tax_number' and not re.match(r'^\d{1,3}/\d{3}/\d{4,5}$', field_value):
                        step_errors.append(f'{label}: Format 12/345/67890 erforderlich')
                        validation_results['warnings'].append(f'{label}: Ungültiges Format')
                    elif field == 'vat_id' and not re.match(r'^DE\d{9}$', field_value):
                        step_errors.append(f'{label}: Format DE123456789 erforderlich')
                        validation_results['warnings'].append(f'{label}: Ungültiges Format')
                    elif field == 'tax_id' and not re.match(r'^\d{11}$', field_value):
                        step_errors.append(f'{label}: 11-stellige Nummer erforderlich')
                        validation_results['warnings'].append(f'{label}: Ungültiges Format')

                # НОВОЕ: Дополнительная валидация банковских форматов для шага 5
                elif step == 'step5':
                    field_value = str(company.get(field, '')).strip()
                    if field == 'iban':
                        iban_clean = field_value.replace(' ', '').upper()
                        if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$', iban_clean):
                            step_errors.append(f'{label}: Ungültiges Format')
                            validation_results['warnings'].append(f'{label}: Ungültiges Format')
                    elif field == 'bic':
                        bic_clean = field_value.upper()
                        if not re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', bic_clean):
                            step_errors.append(f'{label}: Ungültiges Format')
                            validation_results['warnings'].append(f'{label}: Ungültiges Format')

        validation_results['step_status'][step]['complete'] = step_complete
        validation_results['step_status'][step]['errors'] = step_errors

    # ОБНОВЛЕНО: Проверяем опциональные банковские данные (вторичные)
    secondary_banking_data_present = False
    secondary_banking_errors = []

    for field, label in step5_optional_fields.items():
        field_value = company.get(field, '')
        if field_value and str(field_value).strip():
            secondary_banking_data_present = True

            # Валидация вторичных банковских данных
            if field == 'secondary_iban':
                iban_clean = str(field_value).replace(' ', '').upper()
                if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$', iban_clean):
                    secondary_banking_errors.append(f'{label}: Ungültiges Format')
                    validation_results['warnings'].append(f'{label}: Ungültiges Format')
            elif field == 'secondary_bic':
                bic_clean = str(field_value).upper()
                if not re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', bic_clean):
                    secondary_banking_errors.append(f'{label}: Ungültiges Format')
                    validation_results['warnings'].append(f'{label}: Ungültiges Format')

    # Добавляем информацию о вторичных банковских данных
    validation_results['secondary_banking_data_present'] = secondary_banking_data_present
    validation_results['secondary_banking_errors'] = secondary_banking_errors

    # Подсчитываем полноту заполнения
    validation_results['completeness'] = round((filled_count / total_count) * 100, 1) if total_count > 0 else 0

    # Дополнительные проверки форматов
    if company.get('email'):
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, company.get('email', '')):
            validation_results['warnings'].append('E-Mail-Format möglicherweise ungültig')

    if company.get('postal_code'):
        if not re.match(r'^[0-9]{5}$', company.get('postal_code', '')):
            validation_results['warnings'].append('PLZ-Format möglicherweise ungültig')

    # НОВОЕ: Общая информация о статусе банковских данных
    main_banking_complete = validation_results['step_status']['step5']['complete']
    validation_results['main_banking_complete'] = main_banking_complete
    validation_results['banking_status'] = {
        'main_required_complete': main_banking_complete,
        'secondary_optional_present': secondary_banking_data_present,
        'overall_banking_status': 'complete' if main_banking_complete else 'incomplete'
    }

    return JsonResponse(validation_results)


def validate_registration_data(data):
    """ОБНОВЛЕНО: Валидирует регистрационные данные компании включая банковские поля"""
    errors = []

    # Проверяем обязательные поля шага 2
    step2_required_fields = {
        'commercial_register': 'Handelsregister',
        'tax_number': 'Steuernummer',
        'vat_id': 'USt-IdNr.',
        'tax_id': 'Steuer-ID'
    }

    for field, label in step2_required_fields.items():
        if not data.get(field) or not str(data[field]).strip():
            errors.append(f"{label} ist erforderlich")

    # НОВОЕ: Проверяем обязательные банковские поля
    banking_required_fields = {
        'bank_name': 'Name der Bank',
        'iban': 'IBAN',
        'bic': 'BIC/SWIFT',
        'account_holder': 'Kontoinhaber'
    }

    for field, label in banking_required_fields.items():
        if not data.get(field) or not str(data[field]).strip():
            errors.append(f"{label} ist erforderlich")

    # Проверяем форматы шага 2
    if data.get('commercial_register'):
        if not re.match(r'^(HR[AB]\s*\d+|HRA\s*\d+|HRB\s*\d+)$', data['commercial_register']):
            errors.append("Handelsregister: Format HRA12345 oder HRB12345 erforderlich")

    if data.get('tax_number'):
        if not re.match(r'^\d{1,3}/\d{3}/\d{4,5}$', data['tax_number']):
            errors.append("Steuernummer: Format 12/345/67890 erforderlich")

    if data.get('vat_id'):
        if not re.match(r'^DE\d{9}$', data['vat_id']):
            errors.append("USt-IdNr.: Format DE123456789 erforderlich")

    if data.get('tax_id'):
        if not re.match(r'^\d{11}$', data['tax_id']):
            errors.append("Steuer-ID: 11-stellige Nummer erforderlich")

    # НОВОЕ: Проверяем форматы банковских данных
    if data.get('iban'):
        iban_clean = data['iban'].replace(' ', '').upper()
        if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$', iban_clean):
            errors.append("IBAN: Ungültiges Format (z.B. DE89370400440532013000)")

    if data.get('bic'):
        bic_clean = data['bic'].upper()
        if not re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', bic_clean):
            errors.append("BIC/SWIFT: Ungültiges Format (z.B. DEUTDEFF)")

    # Проверяем опциональные вторичные банковские данные, если они указаны
    if data.get('secondary_iban'):
        iban_clean = data['secondary_iban'].replace(' ', '').upper()
        if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$', iban_clean):
            errors.append("IBAN (Zweitbank): Ungültiges Format")

    if data.get('secondary_bic'):
        bic_clean = data['secondary_bic'].upper()
        if not re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', bic_clean):
            errors.append("BIC/SWIFT (Zweitbank): Ungültiges Format")

    return errors
