// company/static/js/company_contacts_manager.js - Менеджер дополнительных контактов компании

class CompanyAdditionalContactManager {
    constructor() {
        this.additionalContacts = [];
        this.editingIndex = -1;
        this.deletingIndex = -1;

        // Используем типы контактов и конфигурацию с сервера (из MongoDB) или fallback
        this.contactTypeLabels = window.companyContactTypeChoices ?
            this.buildContactTypeLabelsFromServer() :
            this.getDefaultContactTypeLabels();

        // Загружаем конфигурацию из MongoDB или используем fallback
        this.communicationConfig = window.companyCommunicationConfig ?
            window.companyCommunicationConfig :
            this.getDefaultCommunicationConfig();

        // Строим hints из конфигурации MongoDB
        this.contactHints = this.buildContactHintsFromConfig();

        // Строим иконки из конфигурации MongoDB
        this.contactTypeIcons = this.buildContactTypeIconsFromConfig();
    }

    buildContactTypeLabelsFromServer() {
        const labels = {};
        if (window.companyContactTypeChoices && Array.isArray(window.companyContactTypeChoices)) {
            window.companyContactTypeChoices.forEach(choice => {
                if (choice.value) {
                    // Убираем эмодзи из текста
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
                placeholder: 'info@firma.de',
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
                placeholder: 'https://www.firma.de',
                hint: 'Geben Sie eine Website-URL ein',
                pattern: '^https?:\\/\\/.+\\..+$|^www\\..+\\..+$'
            },
            'linkedin': {
                placeholder: 'linkedin.com/company/firma',
                hint: 'Geben Sie Ihr LinkedIn-Profil ein',
                pattern: '^(https?:\\/\\/)?(www\\.)?linkedin\\.com\\/(company|in)\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$'
            },
            'xing': {
                placeholder: 'xing.com/companies/firma',
                hint: 'Geben Sie Ihr XING-Profil ein',
                pattern: '^(https?:\\/\\/)?(www\\.)?xing\\.com\\/(companies|profile)\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$'
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
                'placeholder': 'info@firma.de',
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
                'placeholder': 'https://www.firma.de',
                'hint': 'Geben Sie eine Website-URL ein'
            },
            'linkedin': {
                'label': 'LinkedIn',
                'icon_class': 'bi-linkedin',
                'validation_pattern': '^(https?:\\/\\/)?(www\\.)?linkedin\\.com\\/(company|in)\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$',
                'placeholder': 'linkedin.com/company/firma',
                'hint': 'Geben Sie Ihr LinkedIn-Profil ein'
            },
            'xing': {
                'label': 'XING',
                'icon_class': 'bi-person-badge',
                'validation_pattern': '^(https?:\\/\\/)?(www\\.)?xing\\.com\\/(companies|profile)\\/[a-zA-Z0-9\\-_]+\\/?$|^[a-zA-Z0-9\\-_]+$',
                'placeholder': 'xing.com/companies/firma',
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
        const addBtn = document.getElementById('addCompanyContactBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => {
                this.openContactModal();
            });
        }

        // Кнопка сохранения в модальном окне
        const saveBtn = document.getElementById('saveCompanyContactBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveContact();
            });
        }

        // Кнопка подтверждения удаления
        const confirmBtn = document.getElementById('confirmDeleteCompanyContactBtn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                this.deleteContact();
            });
        }

        // Изменение типа контакта для динамических подсказок
        const typeSelect = document.getElementById('companyContactType');
        if (typeSelect) {
            typeSelect.addEventListener('change', (e) => {
                this.updateContactHints(e.target.value);
            });
        }

        // Валидация в реальном времени
        const valueInput = document.getElementById('companyContactValue');
        if (valueInput) {
            valueInput.addEventListener('input', () => {
                this.validateContactValue();
            });
        }

        // Сброс формы при закрытии модального окна
        const modal = document.getElementById('companyContactModal');
        if (modal) {
            modal.addEventListener('hidden.bs.modal', () => {
                this.resetContactForm();
            });
        }
    }

    setupValidation() {
        const form = document.getElementById('companyContactForm');
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
            case 'companyContactType':
                if (!value) {
                    isValid = false;
                    errorMessage = 'Kontakttyp ist erforderlich';
                }
                break;

            case 'companyContactValue':
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
        const typeField = document.getElementById('companyContactType');
        if (!typeField) return 'Ungültiges Format';

        const type = typeField.value;

        if (this.communicationConfig && this.communicationConfig[type]) {
            return this.getValidationErrorFromConfig(type);
        }

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

        if (type === 'email') {
            return `Ungültiges ${label}-Format`;
        } else if (type === 'mobile' || type === 'fax') {
            return `Ungültiges ${label}nummer-Format`;
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

    openAdditionalContactsModal() {
        const modalElement = document.getElementById('companyAdditionalContactsModal');
        if (!modalElement) return;

        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    }

    openContactModal(index = -1) {
        this.editingIndex = index;
        const modalElement = document.getElementById('companyContactModal');
        if (!modalElement) return;

        const modal = new bootstrap.Modal(modalElement);
        const modalTitle = document.getElementById('companyContactModalLabel');
        const saveBtn = document.getElementById('saveCompanyContactBtn');

        if (index >= 0) {
            // Режим редактирования
            const contact = this.additionalContacts[index];
            modalTitle.innerHTML = '<i class="bi bi-pencil me-2"></i>Kontakt bearbeiten';
            saveBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Aktualisieren';

            this.setFieldValue('companyContactType', contact.type);
            this.setFieldValue('companyContactValue', contact.value);
            this.setFieldValue('companyContactLabel', contact.label || '');

            this.updateContactHints(contact.type);
        } else {
            // Режим добавления
            modalTitle.innerHTML = '<i class="bi bi-building-add me-2"></i>Kontakt hinzufügen';
            saveBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Speichern';
            this.resetContactForm();
        }

        modal.show();
    }

    setFieldValue(fieldId, value) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = value;
            if (field.tagName.toLowerCase() === 'select' && $(field).data('select2')) {
                $(field).val(value).trigger('change');
            }
        }
    }

    resetContactForm() {
        const form = document.getElementById('companyContactForm');
        if (!form) return;

        form.reset();

        form.querySelectorAll('.is-invalid, .is-valid').forEach(el => {
            el.classList.remove('is-invalid', 'is-valid');
        });

        const typeSelect = document.getElementById('companyContactType');
        if (typeSelect && $(typeSelect).data('select2')) {
            $(typeSelect).val('').trigger('change');
        }

        this.updateContactHints('');
    }

    updateContactHints(type) {
        const valueInput = document.getElementById('companyContactValue');
        const hintElement = document.getElementById('companyContactHint');

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
        const typeField = document.getElementById('companyContactType');
        const valueField = document.getElementById('companyContactValue');

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

    saveContact() {
        const form = document.getElementById('companyContactForm');
        if (!form) return;

        const typeField = document.getElementById('companyContactType');
        const valueField = document.getElementById('companyContactValue');
        const labelField = document.getElementById('companyContactLabel');

        const isTypeValid = this.validateContactField(typeField);
        const isValueValid = this.validateContactField(valueField);

        if (!isTypeValid || !isValueValid) {
            showToast('Bitte korrigieren Sie die Fehler im Formular', 'error');
            return;
        }

        const contactData = {
            type: typeField.value,
            value: valueField.value.trim(),
            label: labelField ? labelField.value.trim() : ''
        };

        if (this.editingIndex >= 0) {
            this.additionalContacts[this.editingIndex] = contactData;
            showToast('Kontakt erfolgreich aktualisiert', 'success');
        } else {
            this.additionalContacts.push(contactData);
            showToast('Kontakt erfolgreich hinzugefügt', 'success');
        }

        this.updateTable();
        this.updateAdditionalContactsDataInput();

        const modalElement = document.getElementById('companyContactModal');
        if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
        }
    }

    confirmDelete(index) {
        this.deletingIndex = index;
        const modalElement = document.getElementById('deleteCompanyContactModal');
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
            showToast('Kontakt erfolgreich gelöscht', 'info');

            const modalElement = document.getElementById('deleteCompanyContactModal');
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
            }
        }
    }

    updateTable() {
        const tableBody = document.getElementById('companyContactsTableBody');
        const placeholder = document.getElementById('emptyCompanyContactsPlaceholder');
        const table = document.getElementById('companyContactsTable');
        const counter = document.getElementById('additionalContactsCount');

        if (!tableBody || !placeholder || !table || !counter) return;

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
                    <div class="d-inline-flex justify-content-end gap-1">
                        <button type="button" class="btn btn-sm btn-outline-primary" 
                                onclick="companyAdditionalContactManager.openContactModal(${index})" 
                                title="Bearbeiten">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger" 
                                onclick="companyAdditionalContactManager.confirmDelete(${index})" 
                                title="Löschen">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    updateAdditionalContactsDataInput() {
        const input = document.getElementById('additionalContactsDataInput');
        if (input) {
            input.value = JSON.stringify(this.additionalContacts);
            console.log('Обновлены данные дополнительных контактов компании:', this.additionalContacts.length);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getAdditionalContactsData() {
        return this.additionalContacts;
    }

    loadAdditionalContacts(contactsData) {
        if (Array.isArray(contactsData)) {
            this.additionalContacts = contactsData;
            this.updateTable();
            this.updateAdditionalContactsDataInput();
            console.log('Загружено дополнительных контактов компании:', contactsData.length);
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('company-step4-form')) {
        window.companyAdditionalContactManager = new CompanyAdditionalContactManager();
        companyAdditionalContactManager.init();

        // Загружаем существующие контакты если есть
        const existingContacts = window.initialCompanyAdditionalContactsData || [];
        if (existingContacts.length > 0) {
            companyAdditionalContactManager.loadAdditionalContacts(existingContacts);
        }

        console.log('Company Additional Contact Manager успешно инициализирован');
        console.log('Доступные типы контактов:', window.companyContactTypeChoices);
        console.log('Конфигурация коммуникации:', window.companyCommunicationConfig);
    }
});