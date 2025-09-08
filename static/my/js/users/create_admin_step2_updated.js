// Добавить в конец файла static/my/js/users/create_admin_step2_updated.js

// Управление главным контактом с динамическими подсказками
class PrimaryContactManager {
    constructor() {
        this.contactTypeSelect = null;
        this.contactValueInput = null;
        this.contactHintElement = null;

        this.contactHints = {
            'email': {
                placeholder: 'beispiel@domain.com',
                hint: 'Geben Sie eine gültige E-Mail-Adresse ein',
                pattern: '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$'
            },
            'telefon': {
                placeholder: '+49 123 456789',
                hint: 'Geben Sie eine Telefonnummer ein (z.B. +49 123 456789)',
                pattern: '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$'
            },
            'mobil': {
                placeholder: '+49 170 1234567',
                hint: 'Geben Sie eine Mobilnummer ein (z.B. +49 170 1234567)',
                pattern: '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$'
            },
            'fax': {
                placeholder: '+49 123 456789',
                hint: 'Geben Sie eine Faxnummer ein (z.B. +49 123 456789)',
                pattern: '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$'
            },
            'website': {
                placeholder: 'https://www.example.com',
                hint: 'Geben Sie eine Website-URL ein (z.B. https://www.example.com)',
                pattern: '^https?:\\/\\/.+\\..+$|^www\\..+\\..+$'
            },
            'linkedin': {
                placeholder: 'linkedin.com/in/username',
                hint: 'Geben Sie Ihr LinkedIn-Profil ein (z.B. linkedin.com/in/username)',
                pattern: '^(https?:\\/\\/)?(www\\.)?linkedin\\.com\\/in\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$'
            },
            'xing': {
                placeholder: 'xing.com/profile/username',
                hint: 'Geben Sie Ihr XING-Profil ein (z.B. xing.com/profile/username)',
                pattern: '^(https?:\\/\\/)?(www\\.)?xing\\.com\\/profile\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$'
            },
            'sonstige': {
                placeholder: 'Kontaktdaten eingeben...',
                hint: 'Geben Sie die entsprechenden Kontaktdaten ein',
                pattern: '.{3,}'
            }
        };
    }

    init() {
        // Находим элементы на странице
        this.contactTypeSelect = document.getElementById('id_primary_contact_type');
        this.contactValueInput = document.getElementById('id_primary_contact_value');
        this.contactHintElement = document.getElementById('primaryContactHint');

        if (!this.contactTypeSelect || !this.contactValueInput || !this.contactHintElement) {
            console.warn('PrimaryContactManager: Не все элементы найдены на странице');
            return;
        }

        // Привязываем события
        this.bindEvents();

        // Устанавливаем начальное состояние
        this.updateContactHints();

        console.log('PrimaryContactManager инициализирован');
    }

    bindEvents() {
        // Изменение типа контакта
        this.contactTypeSelect.addEventListener('change', () => {
            this.updateContactHints();
            this.validateContactValue();
        });

        // Валидация при вводе
        this.contactValueInput.addEventListener('input', () => {
            this.validateContactValue();
        });

        this.contactValueInput.addEventListener('blur', () => {
            this.validateContactValue();
        });
    }

    updateContactHints() {
        const selectedType = this.contactTypeSelect.value.toLowerCase();
        const config = this.contactHints[selectedType];

        if (config) {
            // Обновляем placeholder
            this.contactValueInput.placeholder = config.placeholder;

            // Обновляем подсказку
            this.contactHintElement.innerHTML = `
                <i class="bi bi-lightbulb me-1"></i>
                ${config.hint}
            `;

            // Устанавливаем паттерн для HTML5 валидации
            if (config.pattern) {
                this.contactValueInput.setAttribute('pattern', config.pattern);
            } else {
                this.contactValueInput.removeAttribute('pattern');
            }
        } else {
            // Сброс к дефолтным значениям
            this.contactValueInput.placeholder = 'Kontaktdaten eingeben...';
            this.contactHintElement.innerHTML = `
                <i class="bi bi-lightbulb me-1"></i>
                Wählen Sie zuerst den Kontakttyp aus
            `;
            this.contactValueInput.removeAttribute('pattern');
        }

        // Очищаем предыдущую валидацию
        this.clearFieldValidation();
    }

    validateContactValue() {
        const selectedType = this.contactTypeSelect.value.toLowerCase();
        const value = this.contactValueInput.value.trim();

        // Если тип не выбран или значение пустое
        if (!selectedType || !value) {
            this.clearFieldValidation();
            return true;
        }

        const config = this.contactHints[selectedType];
        if (!config) {
            this.clearFieldValidation();
            return true;
        }

        let isValid = true;
        let errorMessage = '';

        // Проверяем по паттерну
        if (config.pattern) {
            const regex = new RegExp(config.pattern);
            if (!regex.test(value)) {
                isValid = false;
                errorMessage = this.getValidationErrorMessage(selectedType);
            }
        }

        // Устанавливаем состояние валидации
        if (isValid) {
            this.setFieldSuccess();
        } else {
            this.setFieldError(errorMessage);
        }

        return isValid;
    }

    getValidationErrorMessage(contactType) {
        const errorMessages = {
            'email': 'Ungültiges E-Mail-Format',
            'telefon': 'Ungültiges Telefonformat',
            'mobil': 'Ungültiges Mobilnummer-Format',
            'fax': 'Ungültiges Faxnummer-Format',
            'website': 'Ungültiges Website-Format (muss mit http:// oder https:// beginnen)',
            'linkedin': 'Ungültiges LinkedIn-Profil-Format',
            'xing': 'Ungültiges XING-Profil-Format',
            'sonstige': 'Kontaktdaten müssen mindestens 3 Zeichen lang sein'
        };

        return errorMessages[contactType] || 'Ungültiges Format';
    }

    setFieldError(message) {
        this.contactValueInput.classList.remove('is-valid');
        this.contactValueInput.classList.add('is-invalid');

        // Удаляем старые сообщения об ошибках
        const existingError = this.contactValueInput.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        // Добавляем новое сообщение об ошибке
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        this.contactValueInput.closest('.mb-3').appendChild(errorDiv);
    }

    setFieldSuccess() {
        this.contactValueInput.classList.remove('is-invalid');
        this.contactValueInput.classList.add('is-valid');

        // Удаляем сообщения об ошибках
        const existingError = this.contactValueInput.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    clearFieldValidation() {
        this.contactValueInput.classList.remove('is-invalid', 'is-valid');

        const existingError = this.contactValueInput.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    // Публичный метод для получения валидации (используется при отправке формы)
    isValid() {
        return this.validateContactValue();
    }
}

// Обновляем основной код инициализации
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admin-step2-form');
    if (!form) return;

    // Инициализируем менеджер дополнительных контактов
    window.additionalContactManager = new AdditionalContactManager();
    additionalContactManager.init();

    // НОВОЕ: Инициализируем менеджер главного контакта
    window.primaryContactManager = new PrimaryContactManager();
    primaryContactManager.init();

    // Select2 инициализация для типа главного контакта
    $(document).ready(function() {
        // Инициализация для Contact Type (простой выбор с иконками)
        $('#id_primary_contact_type').select2({
            theme: 'bootstrap-5',
            placeholder: 'Kontakttyp auswählen...',
            allowClear: false,
            minimumResultsForSearch: Infinity, // Отключаем поиск для простого списка
            width: '100%',
            escapeMarkup: function (markup) {
                return markup; // Позволяем HTML (эмодзи)
            }
        });

        // Событие изменения Select2 для главного контакта
        $('#id_primary_contact_type').on('select2:select', function (e) {
            console.log('Выбран тип главного контакта:', e.params.data.id, '-', e.params.data.text);
            // Trigger change event для PrimaryContactManager
            primaryContactManager.updateContactHints();
        });
    });

    // Обновляем валидацию формы для включения главного контакта
    const originalSetupFormSubmission = AdditionalContactManager.prototype.setupFormSubmission;
    AdditionalContactManager.prototype.setupFormSubmission = function() {
        // Вызываем оригинальный метод
        originalSetupFormSubmission.call(this);

        // Переопределяем обработчик отправки формы
        const form = document.getElementById('admin-step2-form');
        if (!form) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();

            // Валидируем основные поля
            const firstNameInput = form.querySelector('input[name="first_name"]');
            const lastNameInput = form.querySelector('input[name="last_name"]');
            const salutationSelect = form.querySelector('select[name="salutation"]');
            const emailInput = form.querySelector('input[name="email"]');
            const phoneInput = form.querySelector('input[name="phone"]');

            // НОВОЕ: Валидируем главный контакт
            const primaryContactTypeSelect = form.querySelector('select[name="primary_contact_type"]');
            const primaryContactValueInput = form.querySelector('input[name="primary_contact_value"]');

            const isValid = this.validateRequired(firstNameInput, 'Vorname ist erforderlich') &&
                            this.validateRequired(lastNameInput, 'Nachname ist erforderlich') &&
                            this.validateSalutation(salutationSelect) &&
                            this.validateEmail(emailInput) &&
                            this.validatePhone(phoneInput) &&
                            this.validatePrimaryContact(primaryContactTypeSelect, primaryContactValueInput);

            if (!isValid) {
                this.showAlert('Bitte korrigieren Sie die Fehler im Formular', 'error');
                return;
            }

            // Показываем прогресс
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird gespeichert...';
            }

            // Создаем FormData для отправки
            const formData = new FormData(form);

            // Добавляем данные дополнительных контактов
            const additionalContactsData = this.getAdditionalContactsData();
            formData.append('additional_contacts_data', JSON.dumps(additionalContactsData));

            // НОВОЕ: Добавляем данные главного контакта
            const primaryContactData = {
                type: primaryContactTypeSelect.value,
                value: primaryContactValueInput.value.trim(),
                label: 'Hauptkontakt',
                primary: true
            };
            formData.append('primary_contact_data', JSON.stringify(primaryContactData));

            // Отправляем запрос
            fetch('/users/create-admin/step2/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'HX-Request': 'true'
                }
            })
            .then(response => {
                console.log('Response status:', response.status);

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const contentType = response.headers.get('Content-Type');
                if (!contentType || !contentType.includes('application/json')) {
                    return response.text().then(text => {
                        console.error('Non-JSON response:', text);
                        throw new Error('Server returned non-JSON response');
                    });
                }

                return response.json();
            })
            .then(data => {
                console.log('JSON response:', data);

                // Скрываем прогресс
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i>Weiter zu Schritt 3';
                }

                // Обрабатываем сообщения
                if (data.messages && Array.isArray(data.messages)) {
                    data.messages.forEach(message => {
                        this.showAlert(message.text, message.tags);
                    });

                    // Если есть успешное сообщение, перенаправляем через короткое время
                    const hasSuccess = data.messages.some(msg => msg.tags === 'success');
                    if (hasSuccess) {
                        setTimeout(() => {
                            window.location.href = '/users/create-admin/step3/';
                        }, 1500);
                    }
                } else {
                    console.warn('No messages in response:', data);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);

                // Скрываем прогресс
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i>Weiter zu Schritt 3';
                }

                // Показываем ошибку пользователю
                if (error.message.includes('non-JSON')) {
                    this.showAlert('Server hat eine ungültige Antwort gesendet. Bitte versuchen Sie es erneut.', 'error');
                } else {
                    this.showAlert('Fehler beim Speichern des Profils: ' + error.message, 'error');
                }
            });
        });
    };

    // Добавляем новый метод валидации главного контакта
    AdditionalContactManager.prototype.validatePrimaryContact = function(typeSelect, valueInput) {
        if (!typeSelect || !valueInput) return false;

        const type = typeSelect.value;
        const value = valueInput.value.trim();

        this.clearFieldError(typeSelect);
        this.clearFieldError(valueInput);

        if (!type) {
            this.setFieldError(typeSelect, 'Hauptkontakt Typ ist erforderlich');
            return false;
        }

        if (!value) {
            this.setFieldError(valueInput, 'Hauptkontakt ist erforderlich');
            return false;
        }

        // Используем валидацию из PrimaryContactManager
        if (window.primaryContactManager && !window.primaryContactManager.isValid()) {
            return false; // Ошибка уже установлена в PrimaryContactManager
        }

        this.setFieldSuccess(typeSelect);
        this.setFieldSuccess(valueInput);
        return true;
    };

    // Если есть существующие данные дополнительных контактов, загружаем их
    const existingAdditionalContacts = window.initialAdditionalContactsData || [];
    if (existingAdditionalContacts.length > 0) {
        additionalContactManager.loadAdditionalContacts(existingAdditionalContacts);
    }

    console.log('Create Admin Step 2 (обновленный) с PrimaryContactManager и AdditionalContactManager инициализирован');
    console.log('Загружено дополнительных контактов:', existingAdditionalContacts.length);
});