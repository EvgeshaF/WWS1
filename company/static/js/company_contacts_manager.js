// ==================== ГЛАВНЫЙ КОНТАКТ МЕНЕДЖЕР ДЛЯ КОМПАНИИ ====================
class CompanyContactManager {
    constructor() {
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
            'email': 'E-Mail',
            'phone': 'Telefon',
            'mobile': 'Mobil',
            'fax': 'Fax',
            'website': 'Website',
            'linkedin': 'LinkedIn',
            'xing': 'XING',
            'emergency': 'Notfall',
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

        // Fallback если конфигурация не загружена
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
            'email': 'bi-envelope',
            'phone': 'bi-telephone',
            'mobile': 'bi-phone',
            'fax': 'bi-printer',
            'website': 'bi-globe',
            'linkedin': 'bi-linkedin',
            'xing': 'bi-person-badge',
            'emergency': 'bi-exclamation-triangle',
            'other': 'bi-question-circle'
        };
    }

    getDefaultContactHints() {
        return {
            'email': {
                placeholder: 'abteilung@firma.de',
                hint: 'Geben Sie eine E-Mail-Adresse ein (z.B. vertrieb@firma.de)',
                pattern: '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$'
            },
            'phone': {
                placeholder: '+49 123 456789',
                hint: 'Geben Sie eine Telefonnummer ein (z.B. +49 123 456789)',
                pattern: '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$'
            },
            'mobile': {
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
                placeholder: 'https://www.firma.de',
                hint: 'Geben Sie eine Website-URL ein (z.B. https://www.firma.de)',
                pattern: '^https?:\\/\\/.+\\..+$|^www\\..+\\..+$'
            },
            'linkedin': {
                placeholder: 'linkedin.com/company/firmenname',
                hint: 'Geben Sie das LinkedIn-Unternehmensprofil ein',
                pattern: '^(https?:\\/\\/)?(www\\.)?linkedin\\.com\\/company\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$'
            },
            'xing': {
                placeholder: 'xing.com/companies/firmenname',
                hint: 'Geben Sie das XING-Unternehmensprofil ein',
                pattern: '^(https?:\\/\\/)?(www\\.)?xing\\.com\\/companies\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$'
            },
            'emergency': {
                placeholder: '+49 170 1234567',
                hint: 'Geben Sie einen Notfallkontakt ein',
                pattern: '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$'
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
                'icon_class': 'bi-envelope',
                'validation_pattern': '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$',
                'placeholder': 'abteilung@firma.de',
                'hint': 'Geben Sie eine E-Mail-Adresse ein'
            },
            'phone': {
                'label': 'Telefon',
                'icon_class': 'bi-telephone',
                'validation_pattern': '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$',
                'placeholder': '+49 123 456789',
                'hint': 'Geben Sie eine Telefonnummer ein'
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
                'placeholder': 'https://www.firma.de',
                'hint': 'Geben Sie eine Website-URL ein'
            },
            'linkedin': {
                'label': 'LinkedIn',
                'icon_class': 'bi-linkedin',
                'validation_pattern': '^(https?:\\/\\/)?(www\\.)?linkedin\\.com\\/company\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$',
                'placeholder': 'linkedin.com/company/firmenname',
                'hint': 'Geben Sie das LinkedIn-Unternehmensprofil ein'
            },
            'xing': {
                'label': 'XING',
                'icon_class': 'bi-person-badge',
                'validation_pattern': '^(https?:\\/\\/)?(www\\.)?xing\\.com\\/companies\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$',
                'placeholder': 'xing.com/companies/firmenname',
                'hint': 'Geben Sie das XING-Unternehmensprofil ein'
            },
            'emergency': {
                'label': 'Notfall',
                'icon_class': 'bi-exclamation-triangle',
                'validation_pattern': '^[\\+]?[0-9\\s\\-\\(\\)]{7,20}$',
                'placeholder': '+49 170 1234567',
                'hint': 'Geben Sie einen Notfallkontakt ein'
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
}

// ==================== ДОПОЛНИТЕЛЬНЫЕ КОНТАКТЫ КОМПАНИИ МЕНЕДЖЕР ====================
class CompanyAdditionalContactManager {
    constructor() {
        this.additionalContacts = [];
        this.editingIndex = -1;
        this.deletingIndex = -1;

        // ИЗМЕНЕНО: Используем те же названия переменных что и у users
        this.contactTypeLabels = window.contactTypeChoices ?
            this.buildContactTypeLabelsFromServer() :
            this.getDefaultContactTypeLabels();

        // ИЗМЕНЕНО: Используем communicationConfig вместо companyCommunicationConfig
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
        // ИЗМЕНЕНО: Используем contactTypeChoices вместо companyContactTypeChoices
        if (window.contactTypeChoices && Array.isArray(window.contactTypeChoices)) {
            window.contactTypeChoices.forEach(choice => {
                if (choice.value) {
                    labels[choice.value] = choice.text;
                }
            });
        }
        return labels;
    }

    init() {
        this.bindEvents();
        this.updateTable();
        this.updateSummary();
        this.setupFormSubmission();
        this.setupValidation();
        console.log('CompanyAdditionalContactManager инициализирован');
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

        // Сброс формы при закрытии модального окна
        const modal = document.getElementById('contactModal');
        if (modal) {
            // Setup Select2 for contact modal
            modal.addEventListener('shown.bs.modal', () => {
                console.log('Открыта модалка добавления контакта компании');

                const typeSelect = document.getElementById('contactType');
                if (typeSelect) {
                    // Destroy existing Select2 if present
                    if ($(typeSelect).data('select2')) {
                        $(typeSelect).select2('destroy');
                    }

                    // Initialize Select2 with company-specific options
                    $(typeSelect).select2({
                        theme: 'bootstrap-5',
                        placeholder: 'Kontakttyp auswählen...',
                        allowClear: false,
                        width: '100%',
                        dropdownParent: $('#contactModal'),
                        minimumResultsForSearch: Infinity,
                        language: {
                            noResults: () => 'Keine Ergebnisse gefunden'
                        }
                    }).on('select2:select', (e) => {
                        console.log('Выбран тип контакта:', e.params.data.id, '-', e.params.data.text);
                        $(typeSelect).closest('.mb-3').find('.invalid-feedback').hide();
                        this.updateContactHints(e.params.data.id);

                        // Автофокус на поле контактных данных
                        setTimeout(() => {
                            $('#contactValue').trigger('focus');
                        }, 100);
                    });
                }
            });

            modal.addEventListener('hidden.bs.modal', () => {
                this.resetContactForm();
            });
        }

        // Валидация в реальном времени
        const valueInput = document.getElementById('contactValue');
        if (valueInput) {
            valueInput.addEventListener('input', () => {
                this.validateContactValue();
            });
        }
    }

    openAdditionalContactsModal() {
        const modalElement = document.getElementById('additionalContactsModal');
        if (!modalElement) return;

        const modal = new bootstrap.Modal(modalElement);
        this.updateTable();
        this.updateModalCounter();
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
            modalTitle.innerHTML = '<i class="bi bi-pencil me-2"></i>Firmenkontakt bearbeiten';
            saveBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Aktualisieren';

            // Заполняем форму данными
            this.setFieldValue('contactType', contact.type);
            this.setFieldValue('contactValue', contact.value);
            this.setFieldValue('contactLabel', contact.department || '');
            this.setCheckboxValue('contactImportant', contact.important || false);
            this.setCheckboxValue('contactPublic', contact.public || false);

            this.updateContactHints(contact.type);
        } else {
            // Режим добавления
            modalTitle.innerHTML = '<i class="bi bi-person-vcard me-2"></i>Firmenkontakt hinzufügen';
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

    setCheckboxValue(fieldId, checked) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.checked = checked;
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
            'phone': 'Ungültiges Telefonformat',
            'mobile': 'Ungültiges Mobilnummer-Format',
            'fax': 'Ungültiges Faxnummer-Format',
            'website': 'Ungültiges Website-Format (muss mit http:// oder https:// beginnen)',
            'linkedin': 'Ungültiges LinkedIn-Profil-Format',
            'xing': 'Ungültiges XING-Profil-Format',
            'emergency': 'Ungültiges Notfallkontakt-Format',
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
        } else if (type === 'phone' || type === 'mobile' || type === 'fax') {
            return `Ungültiges ${label}format`;
        } else if (type === 'website') {
            return `Ungültiges ${label}-Format (muss mit http:// oder https:// beginnen)`;
        } else if (type === 'linkedin' || type === 'xing') {
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
        const importantField = document.getElementById('contactImportant');
        const publicField = document.getElementById('contactPublic');

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
            department: labelField ? labelField.value.trim() : '',
            label: labelField ? (this.departmentLabels[labelField.value] || labelField.value) : '',
            important: importantField ? importantField.checked : false,
            public: publicField ? publicField.checked : false
        };

        // Если отмечен как важный, снимаем флаг с других контактов
        if (contactData.important) {
            this.additionalContacts.forEach(contact => contact.important = false);
        }

        if (this.editingIndex >= 0) {
            // Обновляем существующий контакт
            this.additionalContacts[this.editingIndex] = contactData;
            this.showAlert('Firmenkontakt erfolgreich aktualisiert', 'success');
        } else {
            // Добавляем новый контакт
            this.additionalContacts.push(contactData);
            this.showAlert('Firmenkontakt erfolgreich hinzugefügt', 'success');
        }

        this.updateTable();
        this.updateModalCounter();
        this.updateSummary();
        this.updateContactsDataInput();

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
            this.updateModalCounter();
            this.updateSummary();
            this.updateContactsDataInput();
            this.showAlert('Firmenkontakt erfolgreich gelöscht', 'info');

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
        const modalTableContainer = document.querySelector('#additionalContactsModal .table-responsive');
        const modalPlaceholder = document.querySelector('#additionalContactsModal #emptyAdditionalContactsPlaceholder');

        if (!tableBody) return;

        if (this.additionalContacts.length === 0) {
            if (modalTableContainer) modalTableContainer.style.display = 'none';
            if (modalPlaceholder) modalPlaceholder.style.display = 'block';
            tableBody.innerHTML = '';
            return;
        }

        if (modalTableContainer) modalTableContainer.style.display = 'block';
        if (modalPlaceholder) modalPlaceholder.style.display = 'none';

        tableBody.innerHTML = this.additionalContacts.map((contact, index) => {
            return this.createContactRow(contact, index);
        }).join('');
    }

    updateModalCounter() {
        const modalCounter = document.getElementById('modalContactsCount');
        if (modalCounter) {
            modalCounter.textContent = this.additionalContacts.length;
        }
    }

    updateSummary() {
        const counter = document.getElementById('additionalContactsCount');
        const summaryText = document.getElementById('contactsSummaryText');

        if (counter) {
            counter.textContent = this.additionalContacts.length;
        }

        if (summaryText) {
            const count = this.additionalContacts.length;
            if (count === 0) {
                summaryText.textContent = 'Keine zusätzlichen Firmenkontakte hinzugefügt';
            } else if (count === 1) {
                summaryText.textContent = '1 zusätzlicher Firmenkontakt hinzugefügt';
            } else {
                summaryText.textContent = `${count} zusätzliche Firmenkontakte hinzugefügt`;
            }
        }
    }

    createContactRow(contact, index) {
        const typeIcon = this.contactTypeIcons[contact.type] || 'bi-question-circle';
        const typeLabel = this.contactTypeLabels[contact.type] || contact.type;
        const importantStar = contact.important ? '<i class="bi bi-star-fill text-warning me-1" title="Wichtig"></i>' : '';
        const publicIcon = contact.public ? '<i class="bi bi-eye-fill text-success me-1" title="Öffentlich"></i>' : '';
        const departmentText = contact.label ? `<div class="contact-department small text-muted">${this.escapeHtml(contact.label)}</div>` : '';

        return `
            <tr>
                <td>
                    <span class="contact-type-badge contact-type-${contact.type}">
                        <i class="bi ${typeIcon} me-1"></i>
                        ${typeLabel}
                    </span>
                    ${departmentText}
                </td>
                <td>
                    ${importantStar}${publicIcon}
                    <code class="contact-value">${this.escapeHtml(contact.value)}</code>
                </td>
                <td>
                    ${contact.department ? this.departmentLabels[contact.department] || contact.department : '<em class="text-muted">-</em>'}
                </td>
                <td class="text-center">
                    <div class="btn-group btn-group-sm" role="group">
                        <button type="button" class="btn btn-outline-primary" 
                                onclick="companyAdditionalContactManager.openContactModal(${index})" 
                                title="Bearbeiten">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button type="button" class="btn btn-outline-danger" 
                                onclick="companyAdditionalContactManager.confirmDelete(${index})" 
                                title="Löschen">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    updateContactsDataInput() {
        const input = document.getElementById('additionalContactsDataInput');
        if (input) {
            input.value = JSON.stringify(this.additionalContacts);
            console.log('Обновлены данные дополнительных контактов компании:', this.additionalContacts.length);
        }
    }

    setupFormSubmission() {
        const form = document.getElementById('company-step4-form');
        if (!form) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();

            const emailInput = form.querySelector('input[name="email"]');
            const phoneInput = form.querySelector('input[name="phone"]');

            const isValid = this.validateRequired(emailInput, 'Haupt-E-Mail ist erforderlich') &&
                            this.validateEmail(emailInput) &&
                            this.validateRequired(phoneInput, 'Haupttelefon ist erforderlich') &&
                            this.validatePhone(phoneInput);

            if (!isValid) {
                this.showAlert('Bitte korrigieren Sie die Fehler im Formular', 'error');
                return;
            }

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird gespeichert...';
            }

            const formData = new FormData(form);

            const additionalContactsData = this.getAdditionalContactsData();
            formData.append('additional_contacts_data', JSON.stringify(additionalContactsData));

            fetch(form.action, {
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

                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i>Weiter zu Schritt 5';
                }

                if (data.messages && Array.isArray(data.messages)) {
                    data.messages.forEach(message => {
                        this.showAlert(message.text, message.tags);
                    });

                    const hasSuccess = data.messages.some(msg => msg.tags === 'success');
                    if (hasSuccess) {
                        setTimeout(() => {
                            window.location.href = '/company/register/step5/';
                        }, 1500);
                    }
                } else {
                    console.warn('No messages in response:', data);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);

                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i>Weiter zu Schritt 5';
                }

                if (error.message.includes('non-JSON')) {
                    this.showAlert('Server hat eine ungültige Antwort gesendet. Bitte versuchen Sie es erneut.', 'error');
                } else {
                    this.showAlert('Fehler beim Speichern der Kontaktdaten: ' + error.message, 'error');
                }
            });
        });
    }

    validateRequired(field, errorMessage) {
        if (!field) return false;

        const value = field.value.trim();
        this.clearFieldError(field);

        if (value === '') {
            this.setFieldError(field, errorMessage);
            return false;
        }

        this.setFieldSuccess(field);
        return true;
    }

    validateEmail(emailInput) {
        if (!emailInput) return false;

        const email = emailInput.value.trim();
        this.clearFieldError(emailInput);

        if (!email) {
            this.setFieldError(emailInput, 'Haupt-E-Mail ist erforderlich');
            return false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            this.setFieldError(emailInput, 'Ungültiges E-Mail-Format');
            return false;
        }

        this.setFieldSuccess(emailInput);
        return true;
    }

    validatePhone(phoneInput) {
        if (!phoneInput) return false;

        const phone = phoneInput.value.trim();
        this.clearFieldError(phoneInput);

        if (!phone) {
            this.setFieldError(phoneInput, 'Haupttelefon ist erforderlich');
            return false;
        }

        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{7,20}$/;
        if (!phoneRegex.test(phone)) {
            this.setFieldError(phoneInput, 'Ungültiges Telefonformat');
            return false;
        }

        this.setFieldSuccess(phoneInput);
        return true;
    }

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
        if (typeof window.showToast === 'function') {
            window.showToast(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }

    getAdditionalContactsData() {
        return this.additionalContacts;
    }

    loadAdditionalContacts(contactsData) {
        if (Array.isArray(contactsData)) {
            this.additionalContacts = contactsData;
            this.updateTable();
            this.updateSummary();
            this.updateContactsDataInput();
        }
    }
}

// ==================== ИНИЦИАЛИЗАЦИЯ ====================
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('company-step4-form')) {
        window.companyAdditionalContactManager = new CompanyAdditionalContactManager();
        companyAdditionalContactManager.init();

        // Загружаем существующие контакты если есть
        const existingContacts = window.initialAdditionalContactsData || [];
        if (existingContacts.length > 0) {
            companyAdditionalContactManager.loadAdditionalContacts(existingContacts);
        }

        console.log('Company Additional Contact Manager успешно инициализирован');
        console.log('Доступные типы контактов:', window.contactTypeChoices);
        console.log('Конфигурация коммуникации:', window.communicationConfig);
    }
});

// Глобальная функция для показа тостов (если не определена)
if (typeof window.showToast === 'undefined') {
    window.showToast = function(message, type = 'info', delay = 5000) {
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
        }, delay);
    };
}

