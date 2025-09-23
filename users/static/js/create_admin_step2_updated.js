class AdditionalContactManager {
    constructor() {
        this.additionalContacts = [];
        this.editingIndex = -1;
        this.deletingIndex = -1;

        // Используем типы контактов и конфигурацию с сервера (из MongoDB) или fallback
        this.contactTypeLabels = window.contactTypeChoices ?
            this.buildContactTypeLabelsFromServer() :
            this.getDefaultContactTypeLabels();

        // Загружаем конфигурацию из MongoDB или используем fallback
        this.communicationConfig = window.communicationConfig ?
            window.communicationConfig :
            this.getDefaultCommunicationConfig();

        // Строим hints из конфигурации MongoDB
        this.contactHints = this.buildContactHintsFromConfig();

        // Строим иконки из конфигурации MongoDB
        this.contactTypeIcons = this.buildContactTypeIconsFromConfig();
    }

    buildContactTypeLabelsFromServer() {
        const labels = {};
        if (window.contactTypeChoices && Array.isArray(window.contactTypeChoices)) {
            window.contactTypeChoices.forEach(choice => {
                if (choice.value) {
                    // Убираем эмодзи из текста для использования в качестве лейбла
                    const cleanText = choice.text.replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '').trim();
                    labels[choice.value] = cleanText;
                }
            });
        }
        return labels;
    }

    getDefaultContactTypeLabels() {
        return {
            'email': 'E-Mail (zusätzlich)',
            'mobile': 'Mobil',
            'fax': 'Fax',
            'website': 'Website',
            'linkedin': 'LinkedIn',
            'xing': 'XING',
            'other': 'Sonstige'
        };
    }

    buildContactHintsFromConfig() {
        const hints = {};

        if (this.communicationConfig) {
            Object.keys(this.communicationConfig).forEach(key => {
                const config = this.communicationConfig[key];
                hints[key] = {
                    placeholder: config.placeholder || 'Kontaktdaten eingeben...',
                    hint: config.hint || 'Geben Sie die entsprechenden Kontaktdaten ein',
                    pattern: config.validation_pattern || '.{3,}'
                };
            });
        }

        // Fallback wenn konфигuration не загружена
        if (Object.keys(hints).length === 0) {
            return this.getDefaultContactHints();
        }

        return hints;
    }

    buildContactTypeIconsFromConfig() {
        const icons = {};

        if (this.communicationConfig) {
            Object.keys(this.communicationConfig).forEach(key => {
                const config = this.communicationConfig[key];
                icons[key] = config.icon_class || 'bi-question-circle';
            });
        }

        // Fallback если конфигурация не загружена
        if (Object.keys(icons).length === 0) {
            return this.getDefaultContactTypeIcons();
        }

        return icons;
    }

    getDefaultContactTypeIcons() {
        return {
            'email': 'bi-envelope-plus',
            'mobile': 'bi-phone',
            'fax': 'bi-printer',
            'website': 'bi-globe',
            'linkedin': 'bi-linkedin',
            'xing': 'bi-person-badge',
            'other': 'bi-question-circle'
        };
    }

    getDefaultContactHints() {
        return {
            'email': {
                placeholder: 'privat@domain.com',
                hint: 'Geben Sie eine zusätzliche E-Mail-Adresse ein',
                pattern: '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$'
            },
            'mobile': {
                placeholder: '+49 170 1234567',
                hint: 'Geben Sie eine Mobilnummer ein',
                pattern: '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$'
            },
            'fax': {
                placeholder: '+49 123 456789',
                hint: 'Geben Sie eine Faxnummer ein',
                pattern: '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$'
            },
            'website': {
                placeholder: 'https://www.example.com',
                hint: 'Geben Sie eine Website-URL ein',
                pattern: '^https?:\\/\\/.+\\..+$|^www\\..+\\..+$'
            },
            'linkedin': {
                placeholder: 'linkedin.com/in/username',
                hint: 'Geben Sie Ihr LinkedIn-Profil ein',
                pattern: '^(https?:\\/\\/)?(www\\.)?linkedin\\.com\\/in\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$'
            },
            'xing': {
                placeholder: 'xing.com/profile/username',
                hint: 'Geben Sie Ihr XING-Profil ein',
                pattern: '^(https?:\\/\\/)?(www\\.)?xing\\.com\\/profile\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$'
            },
            'other': {
                placeholder: 'Kontaktdaten eingeben...',
                hint: 'Geben Sie die entsprechenden Kontaktdaten ein',
                pattern: '.{3,}'
            }
        };
    }

    getDefaultCommunicationConfig() {
        return {
            'email': {
                'label': 'E-Mail',
                'icon_class': 'bi-envelope-plus',
                'validation_pattern': '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$',
                'placeholder': 'beispiel@domain.com',
                'hint': 'Geben Sie eine gültige E-Mail-Adresse ein'
            },
            'mobile': {
                'label': 'Mobil',
                'icon_class': 'bi-phone',
                'validation_pattern': '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$',
                'placeholder': '+49 170 1234567',
                'hint': 'Geben Sie eine Mobilnummer ein'
            },
            'fax': {
                'label': 'Fax',
                'icon_class': 'bi-printer',
                'validation_pattern': '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$',
                'placeholder': '+49 123 456789',
                'hint': 'Geben Sie eine Faxnummer ein'
            },
            'website': {
                'label': 'Website',
                'icon_class': 'bi-globe',
                'validation_pattern': '^https?:\\/\\/.+\\..+$',
                'placeholder': 'https://www.example.com',
                'hint': 'Geben Sie eine Website-URL ein'
            },
            'linkedin': {
                'label': 'LinkedIn',
                'icon_class': 'bi-linkedin',
                'validation_pattern': '^(https?:\\/\\/)?(www\\.)?linkedin\\.com\\/in\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$',
                'placeholder': 'linkedin.com/in/username',
                'hint': 'Geben Sie Ihr LinkedIn-Profil ein'
            },
            'xing': {
                'label': 'XING',
                'icon_class': 'bi-person-badge',
                'validation_pattern': '^(https?:\\/\\/)?(www\\.)?xing\\.com\\/profile\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$',
                'placeholder': 'xing.com/profile/username',
                'hint': 'Geben Sie Ihr XING-Profil ein'
            },
            'other': {
                'label': 'Sonstige',
                'icon_class': 'bi-question-circle',
                'validation_pattern': '.{3,}',
                'placeholder': 'Kontaktdaten eingeben...',
                'hint': 'Geben Sie die entsprechenden Kontaktdaten ein'
            }
        };
    }

    init() {
        this.bindEvents();
        this.updateTable();
        this.setupValidation();
        this.setupFormSubmission();
    }

    bindEvents() {
        // Кнопка открытия модального окна дополнительных контактов
        const openBtn = document.getElementById('openAdditionalContactsBtn');
        if (openBtn) {
            openBtn.addEventListener('click', () => {
                this.openAdditionalContactsModal();
            });
        }

        // Кнопка добавления дополнительного контакта
        const addBtn = document.getElementById('addAdditionalContactBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => {
                this.openContactModal();
            });
        }

        // Кнопка сохранения в модальном окне
        const saveBtn = document.getElementById('saveContactBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveContact();
            });
        }

        // Кнопка подтверждения удаления
        const confirmBtn = document.getElementById('confirmDeleteBtn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                this.deleteContact();
            });
        }

        // Изменение типа контакта для динамических подсказок
        const typeSelect = document.getElementById('contactType');
        if (typeSelect) {
            typeSelect.addEventListener('change', (e) => {
                this.updateContactHints(e.target.value);
            });
        }

        // Валидация в реальном времени
        const valueInput = document.getElementById('contactValue');
        if (valueInput) {
            valueInput.addEventListener('input', () => {
                this.validateContactValue();
            });
        }

        // Сброс формы при закрытии модального окна
        const modal = document.getElementById('contactModal');
        if (modal) {
            modal.addEventListener('hidden.bs.modal', () => {
                this.resetContactForm();
            });
        }
    }

    setupFormSubmission() {
        const form = document.getElementById('admin-step2-form');
        if (!form) return;

        // Обработчик отправки формы
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            // Валидируем основные поля
            const firstNameInput = form.querySelector('input[name="first_name"]');
            const lastNameInput = form.querySelector('input[name="last_name"]');
            const salutationSelect = form.querySelector('select[name="salutation"]');
            const emailInput = form.querySelector('input[name="email"]');
            const phoneInput = form.querySelector('input[name="phone"]');

            const isValid = this.validateRequired(firstNameInput, 'Vorname ist erforderlich') &&
                            this.validateRequired(lastNameInput, 'Nachname ist erforderlich') &&
                            this.validateSalutation(salutationSelect) &&
                            this.validateEmail(emailInput) &&
                            this.validatePhone(phoneInput);

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
            formData.append('additional_contacts_data', JSON.stringify(additionalContactsData));

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
    }

    // Методы валидации основных полей
    validateRequired(field, errorMessage) {
        if (!field) return false;

        const value = field.value.trim();
        this.clearFieldError(field);

        if (value === '') {
            this.setFieldError(field, errorMessage);
            return false;
        }

        if (value.length > 50) {
            this.setFieldError(field, 'Maximal 50 Zeichen erlaubt');
            return false;
        }

        this.setFieldSuccess(field);
        return true;
    }

    validateSalutation(salutationSelect) {
        if (!salutationSelect) return true;

        const value = salutationSelect.value;
        this.clearFieldError(salutationSelect);

        if (!value) {
            this.setFieldError(salutationSelect, 'Anrede ist erforderlich');
            return false;
        }

        this.setFieldSuccess(salutationSelect);
        return true;
    }

    validateEmail(emailInput) {
        if (!emailInput) return false;

        const value = emailInput.value.trim();
        this.clearFieldError(emailInput);

        if (!value) {
            this.setFieldError(emailInput, 'E-Mail ist erforderlich');
            return false;
        }

        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(value)) {
            this.setFieldError(emailInput, 'Ungültiges E-Mail-Format');
            return false;
        }

        this.setFieldSuccess(emailInput);
        return true;
    }

    validatePhone(phoneInput) {
        if (!phoneInput) return false;

        const value = phoneInput.value.trim();
        this.clearFieldError(phoneInput);

        if (!value) {
            this.setFieldError(phoneInput, 'Telefon ist erforderlich');
            return false;
        }

        const phonePattern = /^[\+]?[0-9\s\-\(\)]{7,20}$/;
        if (!phonePattern.test(value)) {
            this.setFieldError(phoneInput, 'Ungültiges Telefonformat');
            return false;
        }

        this.setFieldSuccess(phoneInput);
        return true;
    }

    // Методы работы с дополнительными контактами
    openAdditionalContactsModal() {
        const modalElement = document.getElementById('additionalContactsModal');
        if (!modalElement) return;

        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    }

    openContactModal(index = -1) {
        this.editingIndex = index;
        const modalElement = document.getElementById('contactModal');
        if (!modalElement) return;

        const modal = new bootstrap.Modal(modalElement);
        const modalTitle = document.getElementById('contactModalLabel');
        const saveBtn = document.getElementById('saveContactBtn');

        if (index >= 0) {
            // Режим редактирования
            const contact = this.additionalContacts[index];
            modalTitle.innerHTML = '<i class="bi bi-pencil me-2"></i>Kontakt bearbeiten';
            saveBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Aktualisieren';

            // Заполняем форму данными
            this.setFieldValue('contactType', contact.type);
            this.setFieldValue('contactValue', contact.value);
            this.setFieldValue('contactLabel', contact.label || '');

            this.updateContactHints(contact.type);
        } else {
            // Режим добавления
            modalTitle.innerHTML = '<i class="bi bi-person-vcard me-2"></i>Kontakt hinzufügen';
            saveBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Speichern';
            this.resetContactForm();
        }

        modal.show();
    }

    setFieldValue(fieldId, value) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = value;
            // Обновляем Select2 если это select элемент
            if (field.tagName.toLowerCase() === 'select' && $(field).data('select2')) {
                $(field).val(value).trigger('change');
            }
        }
    }

    resetContactForm() {
        const form = document.getElementById('contactForm');
        if (!form) return;

        form.reset();

        // Очищаем валидацию
        form.querySelectorAll('.is-invalid, .is-valid').forEach(el => {
            el.classList.remove('is-invalid', 'is-valid');
        });

        // Сбрасываем Select2
        const typeSelect = document.getElementById('contactType');
        if (typeSelect && $(typeSelect).data('select2')) {
            $(typeSelect).val('').trigger('change');
        }

        this.updateContactHints('');
    }

    updateContactHints(type) {
        const valueInput = document.getElementById('contactValue');
        const hintElement = document.getElementById('contactHint');

        if (!valueInput || !hintElement) return;

        const config = this.contactHints[type];

        if (config) {
            hintElement.innerHTML = `<i class="bi bi-lightbulb me-1"></i>${config.hint}`;
            valueInput.placeholder = config.placeholder;
        } else {
            hintElement.innerHTML = '<i class="bi bi-lightbulb me-1"></i>Geben Sie die entsprechenden Kontaktdaten ein';
            valueInput.placeholder = 'Kontaktdaten eingeben...';
        }
    }

    validateContactValue() {
        const typeField = document.getElementById('contactType');
        const valueField = document.getElementById('contactValue');

        if (!typeField || !valueField) return false;

        const type = typeField.value;
        const value = valueField.value.trim();

        if (!value) return false;

        const config = this.contactHints[type];
        if (config && config.pattern) {
            const regex = new RegExp(config.pattern);
            return regex.test(value);
        }

        return value.length >= 3;
    }

    setupValidation() {
        const form = document.getElementById('contactForm');
        if (!form) return;

        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateContactField(input);
            });
        });
    }

    validateContactField(field) {
        if (!field) return true;

        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        switch (field.id) {
            case 'contactType':
                if (!value) {
                    isValid = false;
                    errorMessage = 'Kontakttyp ist erforderlich';
                }
                break;

            case 'contactValue':
                if (!value) {
                    isValid = false;
                    errorMessage = 'Kontaktdaten sind erforderlich';
                } else {
                    isValid = this.validateContactValue();
                    if (!isValid) {
                        errorMessage = this.getValidationError();
                    }
                }
                break;
        }

        this.setContactFieldValidation(field, isValid, errorMessage);
        return isValid;
    }

    getValidationError() {
        const typeField = document.getElementById('contactType');
        if (!typeField) return 'Ungültiges Format';

        const type = typeField.value;

        // Используем конфигурацию из MongoDB или fallback
        if (this.communicationConfig && this.communicationConfig[type]) {
            return this.getValidationErrorFromConfig(type);
        }

        // Fallback ошибки
        const errors = {
            'email': 'Ungültiges E-Mail-Format',
            'mobile': 'Ungültiges Mobilnummer-Format',
            'fax': 'Ungültiges Faxnummer-Format',
            'website': 'Ungültiges Website-Format (muss mit http:// oder https:// beginnen)',
            'linkedin': 'Ungültiges LinkedIn-Profil-Format',
            'xing': 'Ungültiges XING-Profil-Format',
            'other': 'Kontaktdaten müssen mindestens 3 Zeichen lang sein'
        };

        return errors[type] || 'Ungültiges Format';
    }

    getValidationErrorFromConfig(type) {
        const config = this.communicationConfig[type];
        const label = config.label || type;

        // Создаем сообщение об ошибке на основе типа
        if (type === 'email') {
            return `Ungültiges ${label}-Format`;
        } else if (type === 'mobile' || type === 'fax') {
            return `Ungültiges ${label}nummer-Format`;
        } else if (type === 'website') {
            return `Ungültiges ${label}-Format (muss mit http:// oder https:// beginnen)`;
        } else if (type === 'linkedin') {
            return `Ungültiges ${label}-Profil-Format`;
        } else if (type === 'xing') {
            return `Ungültiges ${label}-Profil-Format`;
        } else {
            return `${label} müssen mindestens 3 Zeichen lang sein`;
        }
    }

    setContactFieldValidation(field, isValid, errorMessage = '') {
        if (!field) return;

        const feedback = field.parentElement.querySelector('.invalid-feedback');

        field.classList.remove('is-valid', 'is-invalid');

        if (isValid) {
            field.classList.add('is-valid');
            if (feedback) feedback.textContent = '';
        } else {
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = errorMessage;
        }
    }

    saveContact() {
        const form = document.getElementById('contactForm');
        if (!form) return;

        const typeField = document.getElementById('contactType');
        const valueField = document.getElementById('contactValue');
        const labelField = document.getElementById('contactLabel');

        // Валидируем все поля
        const isTypeValid = this.validateContactField(typeField);
        const isValueValid = this.validateContactField(valueField);

        if (!isTypeValid || !isValueValid) {
            this.showAlert('Bitte korrigieren Sie die Fehler im Formular', 'error');
            return;
        }

        const contactData = {
            type: typeField.value,
            value: valueField.value.trim(),
            label: labelField ? labelField.value.trim() : ''
        };

        if (this.editingIndex >= 0) {
            // Обновляем существующий контакт
            this.additionalContacts[this.editingIndex] = contactData;
            this.showAlert('Kontakt erfolgreich aktualisiert', 'success');
        } else {
            // Добавляем новый контакт
            this.additionalContacts.push(contactData);
            this.showAlert('Kontakt erfolgreich hinzugefügt', 'success');
        }

        this.updateTable();
        this.updateAdditionalContactsDataInput();

        // Закрываем модальное окно
        const modalElement = document.getElementById('contactModal');
        if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
        }
    }

    confirmDelete(index) {
        this.deletingIndex = index;
        const modalElement = document.getElementById('deleteContactModal');
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    }

    deleteContact() {
        if (this.deletingIndex >= 0) {
            this.additionalContacts.splice(this.deletingIndex, 1);
            this.updateTable();
            this.updateAdditionalContactsDataInput();
            this.showAlert('Kontakt erfolgreich gelöscht', 'info');

            const modalElement = document.getElementById('deleteContactModal');
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
            }
        }
    }

    updateTable() {
        const tableBody = document.getElementById('additionalContactsTableBody');
        const placeholder = document.getElementById('emptyAdditionalContactsPlaceholder');
        const table = document.getElementById('additionalContactsTable');
        const counter = document.getElementById('additionalContactsCount');

        if (!tableBody || !placeholder || !table || !counter) return;

        // Обновляем счетчик
        counter.textContent = this.additionalContacts.length;

        if (this.additionalContacts.length === 0) {
            table.style.display = 'none';
            placeholder.style.display = 'block';
            return;
        }

        table.style.display = 'table';
        placeholder.style.display = 'none';

        tableBody.innerHTML = this.additionalContacts.map((contact, index) => {
            return this.createContactRow(contact, index);
        }).join('');
    }

    createContactRow(contact, index) {
        const typeIcon = this.contactTypeIcons[contact.type] || 'bi-question-circle';
        const typeLabel = this.contactTypeLabels[contact.type] || contact.type;
        const labelText = contact.label ? contact.label : '<em class="text-muted">Keine Bezeichnung</em>';

        return `
            <tr>
                <td>
                    <span class="contact-type-badge contact-type-${contact.type}">
                        <i class="bi ${typeIcon} me-1"></i>
                        ${typeLabel}
                    </span>
                </td>
                <td>
                    <code class="contact-value">${this.escapeHtml(contact.value)}</code>
                </td>
                <td>
                    ${labelText}
                </td>
                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-outline-primary action-btn me-1" 
                            onclick="additionalContactManager.openContactModal(${index})" 
                            title="Bearbeiten">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-danger action-btn" 
                            onclick="additionalContactManager.confirmDelete(${index})" 
                            title="Löschen">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    updateAdditionalContactsDataInput() {
        const input = document.getElementById('additionalContactsDataInput');
        if (input) {
            input.value = JSON.stringify(this.additionalContacts);
            console.log('Обновлены данные дополнительных контактов:', this.additionalContacts.length);
        }
    }

    // Утилиты для валидации и отображения
    setFieldError(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');

        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        field.closest('.mb-3').appendChild(errorDiv);
    }

    setFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');

        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');

        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showAlert(message, type = 'info') {
        // Используем глобальную функцию showToast если есть, иначе простой alert
        if (typeof window.showToast === 'function') {
            window.showToast(message, type);
        } else {
            // Создаем простой toast если нет глобальной функции
            this.createSimpleToast(message, type);
        }
    }

    createSimpleToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }

    // Методы для получения и загрузки данных
    getAdditionalContactsData() {
        return this.additionalContacts;
    }

    loadAdditionalContacts(contactsData) {
        if (Array.isArray(contactsData)) {
            this.additionalContacts = contactsData;
            this.updateTable();
            this.updateAdditionalContactsDataInput();
        }
    }
}

// Основной код для формы Step 2
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admin-step2-form');
    if (!form) return;

    // Инициализируем менеджер дополнительных контактов
    window.additionalContactManager = new AdditionalContactManager();
    additionalContactManager.init();

    // Если есть существующие данные дополнительных контактов, загружаем их
    const existingAdditionalContacts = window.initialAdditionalContactsData || [];
    if (existingAdditionalContacts.length > 0) {
        additionalContactManager.loadAdditionalContacts(existingAdditionalContacts);
    }

    console.log('Create Admin Step 2 (обновленный) с AdditionalContactManager инициализирован');
    console.log('Загружено дополнительных контактов:', existingAdditionalContacts.length);
    console.log('Доступные типы контактов с сервера:', window.contactTypeChoices);
    console.log('Конфигурация коммуникации из MongoDB:', window.communicationConfig);
});