# company/company_registration_views.py - ОБНОВЛЕНО: банковский шаг 5 вместо настроек

from django.shortcuts import redirect
from loguru import logger

from company.company_session_views import CompanySessionManager


def register_company(request):
    """Стартовая страница регистрации - перенаправляет на шаг 1"""
    # Очищаем предыдущие данные сессии
    CompanySessionManager.clear_session_data(request)
    logger.info("Начало процесса регистрации компании")
    return redirect('company:register_company_step1')


import json
import re

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from loguru import logger

from company.company_manager import CompanyManager
from company.company_session_views import CompanySessionManager
from company.company_utils import check_mongodb_availability, render_with_messages
from company.forms import CompanyBasicDataForm, CompanyRegistrationForm, CompanyAddressForm, CompanyContactForm, CompanyBankingForm
from company.language import company_success_messages, company_error_messages, text_company_step1, text_company_step2, text_company_step3, text_company_step4, text_company_step5


def register_company_step1(request):
    """Шаг 1: Основные данные компании"""
    if not check_mongodb_availability():
        messages.error(request, "MongoDB muss zuerst konfiguriert werden")
        return redirect('home')

    # Получаем данные из сессии для предзаполнения
    session_data = CompanySessionManager.get_session_data(request)

    if request.method == 'POST':
        form = CompanyBasicDataForm(request.POST)
        if form.is_valid():
            # Сохраняем данные шага в сессию
            step_data = form.cleaned_data.copy()
            CompanySessionManager.update_session_data(request, step_data)

            company_name = step_data.get('company_name', '')
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
    """Шаг 2: Регистрационные данные - ОБНОВЛЕНО: ВСЕ ПОЛЯ ОБЯЗАТЕЛЬНЫ с улучшенной валидацией"""
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

        # НОВАЯ: Дополнительная валидация для обязательных полей
        additional_errors = []

        # Проверяем, что все обязательные поля заполнены
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

        # Если есть дополнительные ошибки, добавляем их в форму
        if additional_errors:
            for error in additional_errors:
                messages.error(request, error)
            logger.warning(f"Валидационные ошибки шага 2: {additional_errors}")

        if form.is_valid() and not additional_errors:
            # Сохраняем данные шага в сессию
            step_data = form.cleaned_data.copy()
            step_data['registration_data_processed'] = True
            step_data['all_registration_fields_complete'] = True  # НОВОЕ: флаг полноты
            CompanySessionManager.update_session_data(request, step_data)

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
    """Шаг 3: Адресные данные"""
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
        if form.is_valid():
            step_data = form.cleaned_data.copy()
            CompanySessionManager.update_session_data(request, step_data)

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
    """Шаг 4: Контактные данные"""
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
    """НОВОЕ: Шаг 5 - Банковские данные и создание компании"""
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
        if form.is_valid():
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

            # Создаем компанию в базе данных
            company_manager = CompanyManager()
            if company_manager.create_or_update_company(final_data):
                # Очищаем сессию после успешного создания
                CompanySessionManager.clear_session_data(request)

                # Формируем сообщение о банковских данных
                banking_info = ""
                if banking_data.get('iban') or banking_data.get('bank_name'):
                    if banking_data.get('secondary_iban'):
                        banking_info = "mit Haupt- und Zweitbankverbindung"
                    else:
                        banking_info = "mit Bankverbindung"
                else:
                    banking_info = "ohne Bankverbindung"

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


@require_http_methods(["GET"])
def company_validation_check(request):
    """Улучшенная проверка валидности данных компании с учетом обязательных полей шага 2 и банковских данных"""
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
            'step5': {'complete': False, 'errors': []}  # НОВОЕ: проверка банковских данных
        }
    }

    # Проверяем обязательные поля по шагам
    step1_fields = {
        'company_name': 'Firmenname',
        'legal_form': 'Rechtsform'
    }

    # ОБНОВЛЕНО: Все поля шага 2 теперь обязательны
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

    # НОВОЕ: Банковские поля (все опциональны)
    step5_fields = {
        'bank_name': 'Bankname',
        'iban': 'IBAN',
        'bic': 'BIC'
    }

    all_required_fields = {**step1_fields, **step2_fields, **step3_fields, **step4_fields}

    filled_count = 0
    total_count = len(all_required_fields)

    # Валидируем каждый шаг отдельно
    for step, fields in [('step1', step1_fields), ('step2', step2_fields),
                         ('step3', step3_fields), ('step4', step4_fields)]:
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

                # НОВАЯ: Дополнительная валидация форматов для шага 2
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

        validation_results['step_status'][step]['complete'] = step_complete
        validation_results['step_status'][step]['errors'] = step_errors

    # НОВАЯ: Проверяем банковские данные (шаг 5) - ВСЕ ОПЦИОНАЛЬНЫ
    step5_complete = True
    step5_errors = []
    banking_data_present = False

    for field, label in step5_fields.items():
        field_value = company.get(field, '')
        if field_value and str(field_value).strip():
            banking_data_present = True
            # Валидация IBAN
            if field == 'iban':
                if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$', field_value):
                    step5_errors.append(f'{label}: Ungültiges Format')
                    validation_results['warnings'].append(f'{label}: Ungültiges Format')
            # Валидация BIC
            elif field == 'bic':
                if not re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', field_value):
                    step5_errors.append(f'{label}: Ungültiges Format')
                    validation_results['warnings'].append(f'{label}: Ungültiges Format')

    validation_results['step_status']['step5']['complete'] = step5_complete
    validation_results['step_status']['step5']['errors'] = step5_errors
    validation_results['banking_data_present'] = banking_data_present

    # Подсчитываем полноту заполнения
    validation_results['completeness'] = round((filled_count / total_count) * 100, 1) if total_count > 0 else 0

    # Дополнительные проверки форматов (существующий код)
    if company.get('email'):
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, company.get('email', '')):
            validation_results['warnings'].append('E-Mail-Format möglicherweise ungültig')

    if company.get('postal_code'):
        if not re.match(r'^[0-9]{5}$', company.get('postal_code', '')):
            validation_results['warnings'].append('PLZ-Format möglicherweise ungültig')

    return JsonResponse(validation_results)


def validate_registration_data(data):
    """Валидирует регистрационные данные компании"""
    errors = []

    # Проверяем обязательные поля шага 2
    required_fields = {
        'commercial_register': 'Handelsregister',
        'tax_number': 'Steuernummer',
        'vat_id': 'USt-IdNr.',
        'tax_id': 'Steuer-ID'
    }

    for field, label in required_fields.items():
        if not data.get(field) or not str(data[field]).strip():
            errors.append(f"{label} ist erforderlich")

    # Проверяем форматы
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

    return errors