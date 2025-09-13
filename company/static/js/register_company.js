// register_company.js - УЛУЧШЕННАЯ ВЕРСИЯ

// ==================== КОНСТАНТЫ И КОНФИГУРАЦИЯ ====================
const CONFIG = {
    VALIDATION_PATTERNS: {
        EMAIL: /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/,
        GERMAN_PHONE: /^[\+]?[0-9\s\-\(\)]{7,20}$/,
        GERMAN_POSTAL: /^[0-9]{5}$/,
        VAT_ID: /^DE[0-9]{9}$/,
        COMMERCIAL_REGISTER: /^HR[AB][0-9]+$/,
        WEBSITE: /^https?:\/\/([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/,
        LINKEDIN: /(https?:\/\/)?(www\.)?linkedin\.com\/company\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$/,
        XING: /(https?:\/\/)?(www\.)?xing\.com\/companies\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$/
    },

    MESSAGES: {
        de: {
            FIELD_REQUIRED: 'Dieses Feld ist erforderlich',
            INVALID_EMAIL: 'Ungültiges E-Mail-Format',
            INVALID_PHONE: 'Ungültiges Telefonformat',
            INVALID_POSTAL: 'PLZ muss aus 5 Ziffern bestehen',
            INVALID_WEBSITE: 'Website muss mit http:// oder https:// beginnen',
            INVALID_VAT: 'USt-IdNr. muss im Format DE123456789 sein',
            INVALID_REGISTER: 'Handelsregister muss im Format HRA12345 oder HRB12345 sein',
            INVALID_LINKEDIN: 'Ungültiges LinkedIn-Profil-Format',
            INVALID_XING: 'Ungültiges XING-Profil-Format',
            MIN_LENGTH: 'Mindestens {min} Zeichen erforderlich',
            MAX_LENGTH: 'Maximal {max} Zeichen erlaubt',
            CONTACT_SAVED: 'Kontakt erfolgreich hinzugefügt',
            CONTACT_UPDATED: 'Kontakt erfolgreich aktualisiert',
            CONTACT_DELETED: 'Kontakt erfolgreich gelöscht',
            FORM_SUCCESS: 'Firma erfolgreich registriert!',
            NETWORK_ERROR: 'Netzwerkfehler. Bitte überprüfen Sie Ihre Internetverbindung.',
            SERVER_ERROR: 'Serverfehler. Bitte versuchen Sie es später erneut.',
            VALIDATION_ERROR: 'Ungültige Daten. Bitte überprüfen Sie Ihre Eingaben.',
            FILL_PREVIOUS_TABS: 'Bitte füllen Sie zuerst die vorherigen Tabs aus',
            FILL_REQUIRED_FIELDS: 'Bitte füllen Sie alle erforderlichen Felder aus',
            CORRECT_ERRORS: 'Bitte korrigieren Sie alle Fehler im Formular',
            UNSAVED_CHANGES: 'Sie haben ungespeicherte Änderungen. Möchten Sie die Seite wirklich verlassen?'
        }
    },

    DEBOUNCE_DELAY: 300,
    AUTOSAVE_DELAY: 2000,
    TOAST_DELAY: 5000
};

// ==================== УТИЛИТЫ ====================
class Utils {
    static debounce(func, delay) {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    static throttle(func, delay) {
        let inThrottle;
        return (...args) => {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, delay);
            }
        };
    }

    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    static createElement(tag, attributes = {}, textContent = '') {
        const element = document.createElement(tag);

        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'className') {
                element.className = value;
            } else {
                element.setAttribute(key, value);
            }
        });

        if (textContent) {
            element.textContent = textContent;
        }

        return element;
    }

    static formatMessage(template, params = {}) {
        return template.replace(/\{(\w+)\}/g, (match, key) => params[key] || match);
    }

    static getCachedElement(id, cache = new Map()) {
        if (!cache.has(id)) {
            cache.set(id, document.getElementById(id));
        }
        return cache.get(id);
    }
}

// ==================== ВАЛИДАТОР ====================
class FormValidator {
    constructor(messages = CONFIG.MESSAGES.de) {
        this.messages = messages;
        this.patterns = CONFIG.VALIDATION_PATTERNS;
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;

        this.clearFieldValidation(field);

        // Проверка обязательных полей
        if (field.hasAttribute('required') && !value) {
            this.setFieldError(field, this.messages.FIELD_REQUIRED);
            return false;
        }

        // Пропускаем валидацию пустых необязательных полей
        if (!value && !field.hasAttribute('required')) {
            return true;
        }

        // Специфическая валидация
        const validationRules = {
            email: () => this.patterns.EMAIL.test(value) || this.messages.INVALID_EMAIL,
            phone: () => this.patterns.GERMAN_PHONE.test(value) || this.messages.INVALID_PHONE,
            fax: () => this.patterns.GERMAN_PHONE.test(value) || this.messages.INVALID_PHONE,
            postal_code: () => this.patterns.GERMAN_POSTAL.test(value) || this.messages.INVALID_POSTAL,
            website: () => this.patterns.WEBSITE.test(value) || this.messages.INVALID_WEBSITE,
            vat_id: () => this.patterns.VAT_ID.test(value) || this.messages.INVALID_VAT,
            commercial_register: () => this.patterns.COMMERCIAL_REGISTER.test(value) || this.messages.INVALID_REGISTER,
            company_name: () => {
                if (value.length < 2) return Utils.formatMessage(this.messages.MIN_LENGTH, { min: 2 });
                if (value.length > 100) return Utils.formatMessage(this.messages.MAX_LENGTH, { max: 100 });
                return true;
            }
        };

        const rule = validationRules[fieldName];
        if (rule) {
            const result = rule();
            if (result !== true) {
                this.setFieldError(field, result);
                return false;
            }
        }

        this.setFieldSuccess(field);
        return true;
    }

    validateContactValue(type, value) {
        if (!type || !value) return true;

        const contactValidation = {
            email: () => this.patterns.EMAIL.test(value) || this.messages.INVALID_EMAIL,
            mobile: () => this.patterns.GERMAN_PHONE.test(value) || this.messages.INVALID_PHONE,
            fax: () => this.patterns.GERMAN_PHONE.test(value) || this.messages.INVALID_PHONE,
            website: () => this.patterns.WEBSITE.test(value) || this.messages.INVALID_WEBSITE,
            linkedin: () => this.patterns.LINKEDIN.test(value) || this.messages.INVALID_LINKEDIN,
            xing: () => this.patterns.XING.test(value) || this.messages.INVALID_XING,
            other: () => value.length >= 3 || Utils.formatMessage(this.messages.MIN_LENGTH, { min: 3 })
        };

        const rule = contactValidation[type];
        return rule ? rule() : true;
    }

    setFieldError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        field.setAttribute('aria-invalid', 'true');

        this.removeExistingFeedback(field);

        const errorDiv = Utils.createElement('div', {
            className: 'invalid-feedback d-block',
            role: 'alert',
            'aria-live': 'polite'
        }, message);

        const errorId = `${field.id || field.name}_error`;
        errorDiv.id = errorId;
        field.setAttribute('aria-describedby', errorId);

        field.parentNode.appendChild(errorDiv);
    }

    setFieldSuccess(field) {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');
        field.setAttribute('aria-invalid', 'false');
        field.removeAttribute('aria-describedby');

        this.removeExistingFeedback(field);
    }

    clearFieldValidation(field) {
        field.classList.remove('is-invalid', 'is-valid');
        field.removeAttribute('aria-invalid');
        field.removeAttribute('aria-describedby');

        this.removeExistingFeedback(field);
    }

    removeExistingFeedback(field) {
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }
}

// ==================== СИСТЕМА УВЕДОМЛЕНИЙ ====================
class ToastManager {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        let container = document.querySelector('#toast-container');
        if (!container) {
            container = Utils.createElement('div', {
                id: 'toast-container',
                className: 'position-fixed top-0 end-0 p-3',
                style: 'z-index: 9999;'
            });
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', delay = CONFIG.TOAST_DELAY) {
        const toastId = `toast_${Date.now()}`;
        const config = this.getTypeConfig(type);

        const toast = this.createToast(toastId, message, config);
        this.container.appendChild(toast);

        const bootstrapToast = new bootstrap.Toast(toast, { delay });
        bootstrapToast.show();

        toast.addEventListener('hidden.bs.toast', () => toast.remove());

        return bootstrapToast;
    }

    getTypeConfig(type) {
        const configs = {
            success: { bg: 'bg-success', icon: 'bi-check-circle-fill', title: 'Erfolg' },
            error: { bg: 'bg-danger', icon: 'bi-x-circle-fill', title: 'Fehler' },
            warning: { bg: 'bg-warning', icon: 'bi-exclamation-triangle-fill', title: 'Warnung' },
            info: { bg: 'bg-info', icon: 'bi-info-circle-fill', title: 'Info' }
        };
        return configs[type] || configs.info;
    }

    createToast(id, message, config) {
        const toast = Utils.createElement('div', {
            id,
            className: `toast ${config.bg} text-white`,
            role: 'alert',
            'aria-live': 'assertive',
            'aria-atomic': 'true'
        });

        const header = Utils.createElement('div', {
            className: `toast-header ${config.bg} text-white border-0`
        });

        const icon = Utils.createElement('i', { className: `bi ${config.icon} me-2` });
        const title = Utils.createElement('strong', { className: 'me-auto' }, config.title);
        const closeBtn = Utils.createElement('button', {
            type: 'button',
            className: 'btn-close btn-close-white',
            'data-bs-dismiss': 'toast',
            'aria-label': 'Close'
        });

        header.appendChild(icon);
        header.appendChild(title);
        header.appendChild(closeBtn);

        const body = Utils.createElement('div', { className: 'toast-body' }, message);

        toast.appendChild(header);
        toast.appendChild(body);

        return toast;
    }
}

// ==================== МЕНЕДЖЕР ДОПОЛНИТЕЛЬНЫХ КОНТАКТОВ ====================
class CompanyAdditionalContactManager {
    constructor() {
        this.additionalContacts = [];
        this.editingIndex = -1;
        this.deletingIndex = -1;
        this.validator = new FormValidator();
        this.toastManager = new ToastManager();
        this.elementCache = new Map();

        this.contactTypeLabels = {
            email: 'E-Mail (zusätzlich)',
            mobile: 'Mobil',
            fax: 'Fax (zusätzlich)',
            website: 'Website (zusätzlich)',
            linkedin: 'LinkedIn',
            xing: 'XING',
            other: 'Sonstige'
        };

        this.contactTypeIcons = {
            email: 'bi-envelope-plus',
            mobile: 'bi-phone',
            fax: 'bi-printer',
            website: 'bi-globe',
            linkedin: 'bi-linkedin',
            xing: 'bi-person-badge',
            other: 'bi-question-circle'
        };

        this.contactHints = {
            email: {
                placeholder: 'marketing@firma.de',
                hint: 'Geben Sie eine zusätzliche E-Mail-Adresse ein (z.B. marketing@firma.de)'
            },
            mobile: {
                placeholder: '+49 170 1234567',
                hint: 'Geben Sie eine Mobilnummer ein (z.B. +49 170 1234567)'
            },
            fax: {
                placeholder: '+49 123 456789',
                hint: 'Geben Sie eine zusätzliche Faxnummer ein (z.B. +49 123 456789)'
            },
            website: {
                placeholder: 'https://shop.firma.de',
                hint: 'Geben Sie eine zusätzliche Website ein (z.B. https://shop.firma.de)'
            },
            linkedin: {
                placeholder: 'linkedin.com/company/firma',
                hint: 'Geben Sie das LinkedIn-Profil ein (z.B. linkedin.com/company/firma)'
            },
            xing: {
                placeholder: 'xing.com/companies/firma',
                hint: 'Geben Sie das XING-Profil ein (z.B. xing.com/companies/firma)'
            },
            other: {
                placeholder: 'Kontaktdaten eingeben...',
                hint: 'Geben Sie die entsprechenden Kontaktdaten ein'
            }
        };
    }

    init() {
        this.bindEvents();
        this.loadExistingData();
        this.updateDisplay();
        console.log('CompanyAdditionalContactManager инициализирован');
    }

    bindEvents() {
        const debouncedValidation = Utils.debounce(() => this.validateContactValue(), CONFIG.DEBOUNCE_DELAY);

        // Основные кнопки управления
        this.addEventListenerSafe('manage-additional-contacts', 'click', () => this.openAdditionalContactsModal());
        this.addEventListenerSafe('add-contact-btn', 'click', () => this.openContactModal());
        this.addEventListenerSafe('saveContactBtn', 'click', () => this.saveContact());
        this.addEventListenerSafe('confirmDeleteBtn', 'click', () => this.deleteContact());

        // Обработчики формы
        this.addEventListenerSafe('contactType', 'change', (e) => this.updateContactHints(e.target.value));
        this.addEventListenerSafe('contactValue', 'input', debouncedValidation);
        this.addEventListenerSafe('contactValue', 'blur', () => this.validateContactValue());

        // Обработчики модальных окон
        this.addModalEventListener('contactModal', 'hidden.bs.modal', () => this.resetContactForm());
        this.addModalEventListener('deleteContactModal', 'hidden.bs.modal', () => {
            this.deletingIndex = -1;
        });
    }

    addEventListenerSafe(elementId, event, handler) {
        const element = Utils.getCachedElement(elementId, this.elementCache);
        if (element) {
            element.addEventListener(event, handler);
        }
    }

    addModalEventListener(modalId, event, handler) {
        const modal = Utils.getCachedElement(modalId, this.elementCache);
        if (modal) {
            modal.addEventListener(event, handler);
        }
    }

    loadExistingData() {
        const input = Utils.getCachedElement('additionalContactsDataInput', this.elementCache);
        if (input && input.value) {
            try {
                const existingData = JSON.parse(input.value);
                if (Array.isArray(existingData)) {
                    this.additionalContacts = existingData;
                    console.log('Загружены существующие дополнительные контакты:', this.additionalContacts.length);
                }
            } catch (e) {
                console.error('Ошибка загрузки существующих контактов:', e);
            }
        }
    }

    updateDisplay() {
        this.updateContactsTable();
        this.updateModalCounter();
        this.updateContactsSummary();
        this.updateAdditionalContactsDataInput();
    }

    openAdditionalContactsModal() {
        const modalElement = Utils.getCachedElement('additionalContactsModal', this.elementCache);
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            this.updateContactsTable();
            this.updateModalCounter();
            modal.show();
        }
    }

    openContactModal(index = -1) {
        this.editingIndex = index;
        const modalElement = Utils.getCachedElement('contactModal', this.elementCache);
        if (!modalElement) return;

        const modal = new bootstrap.Modal(modalElement);
        const modalTitle = Utils.getCachedElement('contactModalLabel', this.elementCache);
        const saveBtn = Utils.getCachedElement('saveContactBtn', this.elementCache);

        if (index >= 0) {
            // Режим редактирования
            const contact = this.additionalContacts[index];
            this.setModalTitle(modalTitle, 'bi-pencil', 'Kontakt bearbeiten');
            this.setButtonContent(saveBtn, 'bi-check', 'Aktualisieren');

            this.setFieldValue('contactType', contact.type);
            this.setFieldValue('contactValue', contact.value);
            this.setFieldValue('contactLabel', contact.label || '');
            this.setCheckboxValue('contactImportant', contact.important || false);

            this.updateContactHints(contact.type);
        } else {
            // Режим добавления
            this.setModalTitle(modalTitle, 'bi-person-plus', 'Kontakt hinzufügen');
            this.setButtonContent(saveBtn, 'bi-check', 'Speichern');
            this.resetContactForm();
        }

        modal.show();
    }

    setModalTitle(titleElement, iconClass, text) {
        if (!titleElement) return;

        titleElement.innerHTML = '';
        const icon = Utils.createElement('i', { className: `bi ${iconClass} me-2` });
        titleElement.appendChild(icon);
        titleElement.appendChild(document.createTextNode(text));
    }

    setButtonContent(button, iconClass, text) {
        if (!button) return;

        button.innerHTML = '';
        const icon = Utils.createElement('i', { className: `bi ${iconClass} me-1` });
        button.appendChild(icon);
        button.appendChild(document.createTextNode(text));
    }

    setFieldValue(fieldId, value) {
        const field = Utils.getCachedElement(fieldId, this.elementCache);
        if (field) {
            field.value = value;
        }
    }

    setCheckboxValue(fieldId, checked) {
        const field = Utils.getCachedElement(fieldId, this.elementCache);
        if (field) {
            field.checked = checked;
        }
    }

    resetContactForm() {
        const form = Utils.getCachedElement('contactForm', this.elementCache);
        if (!form) return;

        form.reset();
        form.querySelectorAll('.is-invalid, .is-valid').forEach(el => {
            el.classList.remove('is-invalid', 'is-valid');
            el.removeAttribute('aria-invalid');
            el.removeAttribute('aria-describedby');
        });

        // Очистка feedback элементов
        form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());

        this.updateContactHints('');
    }

    updateContactHints(type) {
        const valueInput = Utils.getCachedElement('contactValue', this.elementCache);
        const hintElement = Utils.getCachedElement('contactHint', this.elementCache);

        if (!valueInput || !hintElement) return;

        const config = this.contactHints[type];

        if (config) {
            valueInput.placeholder = config.placeholder;

            hintElement.innerHTML = '';
            const icon = Utils.createElement('i', { className: 'bi bi-lightbulb me-1' });
            hintElement.appendChild(icon);
            hintElement.appendChild(document.createTextNode(config.hint));
        } else {
            valueInput.placeholder = 'Kontaktdaten eingeben...';

            hintElement.innerHTML = '';
            const icon = Utils.createElement('i', { className: 'bi bi-lightbulb me-1' });
            hintElement.appendChild(icon);
            hintElement.appendChild(document.createTextNode('Wählen Sie zuerst den Kontakttyp aus'));
        }

        this.validator.clearFieldValidation(valueInput);
    }

    validateContactValue() {
        const typeField = Utils.getCachedElement('contactType', this.elementCache);
        const valueField = Utils.getCachedElement('contactValue', this.elementCache);

        if (!typeField || !valueField) return true;

        const type = typeField.value;
        const value = valueField.value.trim();

        if (!type || !value) {
            this.validator.clearFieldValidation(valueField);
            return true;
        }

        const result = this.validator.validateContactValue(type, value);
        if (result === true) {
            this.validator.setFieldSuccess(valueField);
            return true;
        } else {
            this.validator.setFieldError(valueField, result);
            return false;
        }
    }

    saveContact() {
        const typeField = Utils.getCachedElement('contactType', this.elementCache);
        const valueField = Utils.getCachedElement('contactValue', this.elementCache);
        const labelField = Utils.getCachedElement('contactLabel', this.elementCache);
        const importantField = Utils.getCachedElement('contactImportant', this.elementCache);

        if (!typeField || !valueField) return;

        const type = typeField.value;
        const value = valueField.value.trim();
        const label = labelField ? labelField.value.trim() : '';
        const important = importantField ? importantField.checked : false;

        // Валидация
        if (!type) {
            this.toastManager.show('Kontakttyp ist erforderlich', 'error');
            return;
        }

        if (!value) {
            this.toastManager.show('Kontaktdaten sind erforderlich', 'error');
            return;
        }

        if (!this.validateContactValue()) {
            return;
        }

        const contactData = { type, value, label, important };

        if (this.editingIndex >= 0) {
            this.additionalContacts[this.editingIndex] = contactData;
            this.toastManager.show(CONFIG.MESSAGES.de.CONTACT_UPDATED, 'success');
        } else {
            this.additionalContacts.push(contactData);
            this.toastManager.show(CONFIG.MESSAGES.de.CONTACT_SAVED, 'success');
        }

        this.updateDisplay();

        const modalElement = Utils.getCachedElement('contactModal', this.elementCache);
        if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
        }
    }

    confirmDeleteContact(index) {
        this.deletingIndex = index;
        const modalElement = Utils.getCachedElement('deleteContactModal', this.elementCache);
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    }

    deleteContact() {
        if (this.deletingIndex >= 0) {
            this.additionalContacts.splice(this.deletingIndex, 1);
            this.updateDisplay();
            this.toastManager.show(CONFIG.MESSAGES.de.CONTACT_DELETED, 'info');

            const modalElement = Utils.getCachedElement('deleteContactModal', this.elementCache);
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
            }
        }
    }

    updateContactsTable() {
        const tableBody = Utils.getCachedElement('contacts-table-body', this.elementCache);
        const tableContainer = Utils.getCachedElement('contacts-table-container', this.elementCache);
        const placeholder = Utils.getCachedElement('empty-contacts-placeholder', this.elementCache);

        if (!tableBody || !tableContainer || !placeholder) return;

        if (this.additionalContacts.length === 0) {
            tableContainer.style.display = 'none';
            placeholder.style.display = 'block';
            return;
        }

        tableContainer.style.display = 'block';
        placeholder.style.display = 'none';

        // Очищаем таблицу
        tableBody.innerHTML = '';

        // Добавляем строки
        this.additionalContacts.forEach((contact, index) => {
            const row = this.createContactRow(contact, index);
            tableBody.appendChild(row);
        });
    }

    createContactRow(contact, index) {
        const row = Utils.createElement('tr');

        // Колонка типа
        const typeCell = Utils.createElement('td');
        const typeIcon = Utils.createElement('i', {
            className: `bi ${this.contactTypeIcons[contact.type] || 'bi-question-circle'} me-2 text-primary`
        });
        typeCell.appendChild(typeIcon);
        typeCell.appendChild(document.createTextNode(this.contactTypeLabels[contact.type] || contact.type));

        if (contact.important) {
            const badge = Utils.createElement('span', {
                className: 'badge bg-warning text-dark ms-1'
            }, 'Wichtig');
            typeCell.appendChild(badge);
        }

        // Колонка значения
        const valueCell = Utils.createElement('td');
        const valueCode = Utils.createElement('code', {
            className: 'company-contact-value'
        }, contact.value);
        valueCell.appendChild(valueCode);

        // Колонка описания
        const labelCell = Utils.createElement('td');
        if (contact.label) {
            labelCell.textContent = contact.label;
        } else {
            const emptyLabel = Utils.createElement('em', {
                className: 'text-muted'
            }, 'Keine Beschreibung');
            labelCell.appendChild(emptyLabel);
        }

        // Колонка действий
        const actionsCell = Utils.createElement('td', { className: 'text-center' });

        const editBtn = this.createActionButton('bi-pencil', 'Bearbeiten', 'btn-outline-primary', () => this.openContactModal(index));
        const deleteBtn = this.createActionButton('bi-trash', 'Löschen', 'btn-outline-danger', () => this.confirmDeleteContact(index));

        actionsCell.appendChild(editBtn);
        actionsCell.appendChild(document.createTextNode(' '));
        actionsCell.appendChild(deleteBtn);

        row.appendChild(typeCell);
        row.appendChild(valueCell);
        row.appendChild(labelCell);
        row.appendChild(actionsCell);

        return row;
    }

    createActionButton(iconClass, title, buttonClass, onClick) {
        const button = Utils.createElement('button', {
            type: 'button',
            className: `btn btn-sm ${buttonClass} company-action-btn`,
            title
        });

        const icon = Utils.createElement('i', { className: `bi ${iconClass}` });
        button.appendChild(icon);
        button.addEventListener('click', onClick);

        return button;
    }

    updateModalCounter() {
        const modalCounter = Utils.getCachedElement('modal-contacts-count', this.elementCache);
        if (modalCounter) {
            modalCounter.textContent = this.additionalContacts.length;
        }
    }

    updateContactsSummary() {
        const counter = Utils.getCachedElement('additional-contacts-count', this.elementCache);
        const summary = Utils.getCachedElement('contacts-summary', this.elementCache);
        const summaryText = Utils.getCachedElement('contacts-summary-text', this.elementCache);

        if (counter) {
            counter.textContent = this.additionalContacts.length;
        }

        if (summary && summaryText) {
            const count = this.additionalContacts.length;

            if (count === 0) {
                summary.classList.add('d-none');
                summaryText.textContent = 'Keine zusätzlichen Kontakte hinzugefügt';
            } else {
                summary.classList.remove('d-none');
                if (count === 1) {
                    summaryText.textContent = '1 zusätzlicher Kontakt hinzugefügt';
                } else {
                    summaryText.textContent = `${count} zusätzliche Kontakte hinzugefügt`;
                }
            }
        }
    }

    updateAdditionalContactsDataInput() {
        const input = Utils.getCachedElement('additionalContactsDataInput', this.elementCache);
        if (input) {
            input.value = JSON.stringify(this.additionalContacts);
            console.log('Обновлены данные дополнительных контактов:', this.additionalContacts.length);
        }
    }

    getAdditionalContactsData() {
        return this.additionalContacts;
    }

    loadAdditionalContacts(contactsData) {
        if (Array.isArray(contactsData)) {
            this.additionalContacts = contactsData;
            this.updateDisplay();
        }
    }
}

// ==================== ОСНОВНОЙ МЕНЕДЖЕР ФОРМЫ ====================
class CompanyFormManager {
    constructor() {
        this.form = null;
        this.currentTabIndex = 0;
        this.tabs = ['basic', 'registration', 'address', 'details'];
        this.validator = new FormValidator();
        this.toastManager = new ToastManager();
        this.elementCache = new Map();

        // Дебаунсированные функции
        this.debouncedValidation = Utils.debounce((field) => this.validateField(field), CONFIG.DEBOUNCE_DELAY);
        this.debouncedAutosave = Utils.debounce(() => this.saveFormDataToSessionStorage(), CONFIG.AUTOSAVE_DELAY);

        this.nextTabBtn = null;
        this.prevTabBtn = null;
        this.submitBtn = null;
        this.nextBtnText = null;
    }

    init() {
        this.cacheElements();

        if (!this.form || !this.nextTabBtn || !this.prevTabBtn || !this.submitBtn) {
            console.error('Не найдены необходимые элементы формы');
            return;
        }

        this.bindEvents();
        this.setupFormValidation();
        this.setupSpecialFieldValidation();
        this.setupKeyboardShortcuts();
        this.setupAutoSave();
        this.setupErrorHandling();
        this.setupBeforeUnloadProtection();

        this.initializeFormValidation();
        this.loadFormDataFromSessionStorage();
        this.updateProgress();
        this.updateNavigationButtons();

        console.log('CompanyFormManager инициализирован');
    }

    cacheElements() {
        const elementIds = [
            'company-form', 'next-tab-btn', 'prev-tab-btn', 'submit-btn', 'next-btn-text',
            'progress-bar', 'current-step', 'companyTabs'
        ];

        elementIds.forEach(id => {
            Utils.getCachedElement(id, this.elementCache);
        });

        this.form = Utils.getCachedElement('company-form', this.elementCache);
        this.nextTabBtn = Utils.getCachedElement('next-tab-btn', this.elementCache);
        this.prevTabBtn = Utils.getCachedElement('prev-tab-btn', this.elementCache);
        this.submitBtn = Utils.getCachedElement('submit-btn', this.elementCache);
        this.nextBtnText = Utils.getCachedElement('next-btn-text', this.elementCache);
    }

    bindEvents() {
        // Кнопки навигации
        this.nextTabBtn.addEventListener('click', () => this.nextTab());
        this.prevTabBtn.addEventListener('click', () => this.prevTab());
        this.submitBtn.addEventListener('click', () => this.submitForm());

        // Обработчики табов
        const tabButtons = document.querySelectorAll('#companyTabs button[data-bs-toggle="tab"]');
        tabButtons.forEach((button, index) => {
            button.addEventListener('click', (e) => {
                if (index <= this.currentTabIndex || this.validateTabsUpTo(index - 1)) {
                    this.currentTabIndex = index;
                    this.updateProgress();
                    this.updateNavigationButtons();
                } else {
                    e.preventDefault();
                    e.stopPropagation();
                    this.toastManager.show(CONFIG.MESSAGES.de.FILL_PREVIOUS_TABS, 'warning');
                }
            });

            button.addEventListener('shown.bs.tab', () => {
                this.currentTabIndex = index;
                this.updateProgress();
                this.updateNavigationButtons();
            });
        });
    }

    setupFormValidation() {
        const requiredFields = this.form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => {
                this.validator.clearFieldValidation(field);
                this.debouncedValidation(field);
            });
        });
    }

    setupSpecialFieldValidation() {
        // PLZ валидация с форматированием
        const postalCodeField = this.form.querySelector('input[name="postal_code"]');
        if (postalCodeField) {
            postalCodeField.addEventListener('input', Utils.throttle(function() {
                const value = this.value.replace(/\D/g, '');
                this.value = value.substring(0, 5);
            }, 100));
        }

        // VAT ID форматирование
        const vatIdField = this.form.querySelector('input[name="vat_id"]');
        if (vatIdField) {
            vatIdField.addEventListener('input', Utils.throttle(function() {
                let value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
                if (value.length > 0 && !value.startsWith('DE')) {
                    value = 'DE' + value;
                }
                if (value.length > 11) {
                    value = value.substring(0, 11);
                }
                this.value = value;
            }, 100));
        }

        // Handelsregister форматирование
        const hrField = this.form.querySelector('input[name="commercial_register"]');
        if (hrField) {
            hrField.addEventListener('input', Utils.throttle(function() {
                let value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
                this.value = value;
            }, 100));
        }

        // Телефонные номера - улучшенное форматирование
        const phoneFields = this.form.querySelectorAll('input[name="phone"], input[name="fax"]');
        phoneFields.forEach(field => {
            field.addEventListener('input', Utils.throttle(this.formatPhoneNumber.bind(this), 150));
        });
    }

    formatPhoneNumber(e) {
        const input = e.target;
        let value = input.value.replace(/\D/g, '');

        // Форматируем как немецкий номер
        if (value.startsWith('49')) {
            value = '+49 ' + this.formatGermanNumber(value.substring(2));
        } else if (value.startsWith('0')) {
            value = '+49 ' + this.formatGermanNumber(value.substring(1));
        } else if (value.length > 0 && !value.startsWith('+')) {
            value = '+49 ' + this.formatGermanNumber(value);
        }

        input.value = value.substring(0, 20); // Ограничиваем длину
    }

    formatGermanNumber(number) {
        if (number.length <= 3) return number;
        if (number.length <= 7) return number.substring(0, 3) + ' ' + number.substring(3);
        return number.substring(0, 3) + ' ' + number.substring(3, 7) + ' ' + number.substring(7);
    }

    nextTab() {
        if (this.validateCurrentTab()) {
            if (this.currentTabIndex < this.tabs.length - 1) {
                this.currentTabIndex++;
                this.switchToTab(this.currentTabIndex);
                this.updateProgress();
                this.updateNavigationButtons();
                this.focusFirstField();
            }
        } else {
            this.toastManager.show(CONFIG.MESSAGES.de.FILL_REQUIRED_FIELDS, 'warning');
        }
    }

    prevTab() {
        if (this.currentTabIndex > 0) {
            this.currentTabIndex--;
            this.switchToTab(this.currentTabIndex);
            this.updateProgress();
            this.updateNavigationButtons();
            this.focusFirstField();
        }
    }

    focusFirstField() {
        setTimeout(() => {
            const currentPane = document.getElementById(this.tabs[this.currentTabIndex]);
            const firstInput = currentPane.querySelector('input, select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        }, 100);
    }

    switchToTab(index) {
        const targetTab = this.tabs[index];
        const tabButton = document.querySelector(`#${targetTab}-tab`);
        if (tabButton) {
            const tab = new bootstrap.Tab(tabButton);
            tab.show();
        }
    }

    updateProgress() {
        const progress = ((this.currentTabIndex + 1) / this.tabs.length) * 100;
        const progressBar = Utils.getCachedElement('progress-bar', this.elementCache);
        const currentStep = Utils.getCachedElement('current-step', this.elementCache);

        if (progressBar) {
            progressBar.style.width = progress + '%';
            progressBar.setAttribute('aria-valuenow', progress);
        }
        if (currentStep) {
            currentStep.textContent = this.currentTabIndex + 1;
        }
    }

    updateNavigationButtons() {
        // Обновляем кнопку "Назад"
        this.prevTabBtn.style.display = this.currentTabIndex === 0 ? 'none' : 'inline-flex';

        // Обновляем кнопку "Далее/Отправить"
        if (this.currentTabIndex === this.tabs.length - 1) {
            this.nextTabBtn.style.display = 'none';
            this.submitBtn.style.display = 'inline-flex';
        } else {
            this.nextTabBtn.style.display = 'inline-flex';
            this.submitBtn.style.display = 'none';

            const isLastBeforeSubmit = this.currentTabIndex === this.tabs.length - 2;
            if (this.nextBtnText) {
                this.nextBtnText.innerHTML = '';
                const icon = Utils.createElement('i', {
                    className: isLastBeforeSubmit ? 'bi bi-check-circle me-1' : 'bi bi-arrow-right me-1'
                });
                const text = isLastBeforeSubmit ? 'Zur Übersicht' : 'Weiter';

                this.nextBtnText.appendChild(icon);
                this.nextBtnText.appendChild(document.createTextNode(text));
            }
        }

        this.updateTabIndicators();
    }

    updateTabIndicators() {
        const tabButtons = document.querySelectorAll('#companyTabs button[data-bs-toggle="tab"]');
        tabButtons.forEach((button, index) => {
            const isCompleted = index < this.currentTabIndex;
            const isCurrent = index === this.currentTabIndex;

            button.classList.remove('completed', 'current');
            button.removeAttribute('aria-current');

            if (isCompleted) {
                button.classList.add('completed');
                const icon = button.querySelector('i');
                if (icon && !icon.classList.contains('bi-check-circle-fill')) {
                    icon.className = 'bi bi-check-circle-fill me-1';
                }
            } else if (isCurrent) {
                button.classList.add('current');
                button.setAttribute('aria-current', 'step');
            }
        });
    }

    validateCurrentTab() {
        const currentTab = this.tabs[this.currentTabIndex];
        const currentPane = document.getElementById(currentTab);
        const fieldsInTab = currentPane.querySelectorAll('input[required], select[required], textarea[required]');

        let isValid = true;
        fieldsInTab.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateTabsUpTo(index) {
        for (let i = 0; i <= index; i++) {
            const tab = this.tabs[i];
            const pane = document.getElementById(tab);
            const fieldsInTab = pane.querySelectorAll('input[required], select[required], textarea[required]');

            for (let field of fieldsInTab) {
                if (!this.validateField(field)) {
                    return false;
                }
            }
        }
        return true;
    }

    validateField(field) {
        return this.validator.validateField(field);
    }

    submitForm() {
        if (!this.validateAllTabs()) {
            this.toastManager.show(CONFIG.MESSAGES.de.CORRECT_ERRORS, 'error');
            this.highlightErrorTabs();
            return;
        }

        this.setSubmitButtonLoading(true);

        // Подготавливаем данные формы
        const formData = new FormData(this.form);

        // Добавляем данные дополнительных контактов
        if (window.companyContactManager) {
            const contactsData = JSON.stringify(window.companyContactManager.getAdditionalContactsData());
            formData.append('additional_contacts_data', contactsData);
        }

        // Отправляем форму
        this.sendFormData(formData)
            .then(this.handleSubmitSuccess.bind(this))
            .catch(this.handleSubmitError.bind(this));
    }

    async sendFormData(formData) {
        const response = await fetch(this.form.action || window.location.pathname, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'HX-Request': 'true'
            }
        });

        if (!response.ok) {
            const errorDetails = {
                status: response.status,
                statusText: response.statusText,
                url: response.url
            };

            if (response.status >= 400 && response.status < 500) {
                throw new Error('CLIENT_ERROR', { cause: errorDetails });
            } else if (response.status >= 500) {
                throw new Error('SERVER_ERROR', { cause: errorDetails });
            } else {
                throw new Error('NETWORK_ERROR', { cause: errorDetails });
            }
        }

        return response.json();
    }

    handleSubmitSuccess(data) {
        this.setSubmitButtonLoading(false);

        // Обрабатываем сообщения
        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(message => {
                this.toastManager.show(message.text, message.tags, message.delay);
            });

            // Если успех, перенаправляем на главную
            const hasSuccess = data.messages.some(msg => msg.tags === 'success');
            if (hasSuccess) {
                this.handleFormSubmissionSuccess();
            }
        } else {
            // Если нет сообщений, показываем стандартное
            this.toastManager.show(CONFIG.MESSAGES.de.FORM_SUCCESS, 'success');
            this.handleFormSubmissionSuccess();
        }
    }

    handleSubmitError(error) {
        console.error('Ошибка отправки формы:', error);
        this.setSubmitButtonLoading(false);

        let message;
        if (error.message === 'CLIENT_ERROR') {
            message = CONFIG.MESSAGES.de.VALIDATION_ERROR;
        } else if (error.message === 'SERVER_ERROR') {
            message = CONFIG.MESSAGES.de.SERVER_ERROR;
        } else if (error.message === 'NETWORK_ERROR') {
            message = CONFIG.MESSAGES.de.NETWORK_ERROR;
        } else {
            message = 'Ein unerwarteter Fehler ist aufgetreten';
        }

        this.toastManager.show(message, 'error');
    }

    setSubmitButtonLoading(isLoading) {
        if (isLoading) {
            this.submitBtn.disabled = true;
            this.submitBtn.innerHTML = '';

            const spinner = Utils.createElement('span', {
                className: 'spinner-border spinner-border-sm me-2',
                role: 'status',
                'aria-hidden': 'true'
            });
            this.submitBtn.appendChild(spinner);
            this.submitBtn.appendChild(document.createTextNode('Wird registriert...'));
        } else {
            this.submitBtn.disabled = false;
            this.submitBtn.innerHTML = '';

            const icon = Utils.createElement('i', { className: 'bi bi-building-add me-1' });
            this.submitBtn.appendChild(icon);
            this.submitBtn.appendChild(document.createTextNode('Firma registrieren'));
        }
    }

    validateAllTabs() {
        let isValid = true;

        this.tabs.forEach(tabId => {
            const pane = document.getElementById(tabId);
            const fieldsInTab = pane.querySelectorAll('input, select, textarea');

            fieldsInTab.forEach(field => {
                if (!this.validateField(field)) {
                    isValid = false;
                }
            });
        });

        return isValid;
    }

    highlightErrorTabs() {
        const tabButtons = document.querySelectorAll('#companyTabs button[data-bs-toggle="tab"]');

        this.tabs.forEach((tabId, index) => {
            const pane = document.getElementById(tabId);
            const hasErrors = pane.querySelectorAll('.is-invalid').length > 0;
            const tabButton = tabButtons[index];

            if (hasErrors) {
                tabButton.classList.add('has-errors');
                setTimeout(() => tabButton.classList.remove('has-errors'), 3000);
            }
        });
    }

    handleFormSubmissionSuccess() {
        this.form.dataset.submitted = 'true';
        this.clearFormDataFromSessionStorage();

        // Перенаправляем на главную после задержки
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);
    }

    // Автосохранение и защита от потери данных
    setupAutoSave() {
        this.form.addEventListener('input', this.debouncedAutosave);
        this.form.addEventListener('change', this.debouncedAutosave);
    }

    saveFormDataToSessionStorage() {
        try {
            const formData = new FormData(this.form);
            const formObject = { current_tab: this.currentTabIndex };

            for (let [key, value] of formData.entries()) {
                formObject[key] = value;
            }

            if (window.companyContactManager) {
                formObject.additional_contacts = window.companyContactManager.getAdditionalContactsData();
            }

            sessionStorage.setItem('companyFormData', JSON.stringify(formObject));
        } catch (e) {
            console.error('Ошибка сохранения данных формы:', e);
        }
    }

    loadFormDataFromSessionStorage() {
        try {
            const savedData = sessionStorage.getItem('companyFormData');
            if (!savedData) return;

            const formObject = JSON.parse(savedData);

            // Восстанавливаем поля формы
            Object.entries(formObject).forEach(([key, value]) => {
                if (key === 'current_tab') {
                    this.currentTabIndex = Math.min(value, this.tabs.length - 1);
                } else if (key === 'additional_contacts') {
                    if (window.companyContactManager) {
                        window.companyContactManager.loadAdditionalContacts(value);
                    }
                } else {
                    const field = this.form.querySelector(`[name="${key}"]`);
                    if (field) {
                        if (field.type === 'checkbox') {
                            field.checked = value === 'on';
                        } else {
                            field.value = value;
                        }
                    }
                }
            });

            // Переключаемся на сохраненный таб
            this.switchToTab(this.currentTabIndex);
            this.updateProgress();
            this.updateNavigationButtons();

            console.log('Данные формы восстановлены из session storage');
        } catch (e) {
            console.error('Ошибка загрузки данных формы:', e);
        }
    }

    clearFormDataFromSessionStorage() {
        try {
            sessionStorage.removeItem('companyFormData');
        } catch (e) {
            console.error('Ошибка очистки данных формы:', e);
        }
    }

    setupBeforeUnloadProtection() {
        let formSubmitted = false;

        this.form.addEventListener('submit', () => {
            formSubmitted = true;
        });

        window.addEventListener('beforeunload', (e) => {
            if (formSubmitted || this.form.dataset.submitted === 'true') return;

            // Проверяем наличие несохраненных изменений
            const hasChanges = this.hasUnsavedChanges();
            if (hasChanges) {
                e.returnValue = CONFIG.MESSAGES.de.UNSAVED_CHANGES;
                return CONFIG.MESSAGES.de.UNSAVED_CHANGES;
            }
        });
    }

    hasUnsavedChanges() {
        const formFields = this.form.querySelectorAll('input, select, textarea');
        for (let field of formFields) {
            if (field.type === 'checkbox') {
                if (field.defaultChecked !== field.checked) return true;
            } else {
                if (field.defaultValue !== field.value) return true;
            }
        }

        if (window.companyContactManager && window.companyContactManager.additionalContacts.length > 0) {
            return true;
        }

        return false;
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter для отправки формы (только на последнем табе)
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                if (this.currentTabIndex === this.tabs.length - 1) {
                    e.preventDefault();
                    this.submitForm();
                }
                return;
            }

            // Escape для возврата назад
            if (e.key === 'Escape' && this.currentTabIndex > 0) {
                e.preventDefault();
                this.prevTab();
                return;
            }

            // Навигация стрелками (только с Ctrl/Cmd)
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'ArrowRight' && this.currentTabIndex < this.tabs.length - 1) {
                    e.preventDefault();
                    this.nextTab();
                } else if (e.key === 'ArrowLeft' && this.currentTabIndex > 0) {
                    e.preventDefault();
                    this.prevTab();
                }
            }
        });
    }

    setupErrorHandling() {
        // Глобальная обработка ошибок JavaScript
        window.addEventListener('error', (e) => {
            console.error('JavaScript error:', e.error);
            this.toastManager.show('Ein unerwarteter Fehler ist aufgetreten', 'error');
        });

        // Обработка неперехваченных Promise ошибок
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            this.toastManager.show('Ein unerwarteter Fehler ist aufgetreten', 'error');
        });
    }

    initializeFormValidation() {
        // Валидируем все поля, которые уже имеют значения
        this.form.querySelectorAll('input, select, textarea').forEach(field => {
            if (field.value.trim()) {
                this.validateField(field);
            }
        });
    }
}

// ==================== ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ====================

/**
 * Инициализация расширенных возможностей
 */
class FormEnhancements {
    static initializeSelect2() {
        if (typeof $ !== 'undefined' && $.fn.select2) {
            console.log('Инициализация Select2...');

            const selects = [
                { selector: 'select[name="legal_form"]', placeholder: 'Rechtsform auswählen...' },
                { selector: 'select[name="country"]', placeholder: 'Land auswählen...' },
                { selector: 'select[name="industry"]', placeholder: 'Branche auswählen...' }
            ];

            selects.forEach(({ selector, placeholder }) => {
                const element = document.querySelector(selector);
                if (element) {
                    $(element).select2({
                        theme: 'bootstrap-5',
                        placeholder,
                        allowClear: false,
                        minimumResultsForSearch: 10,
                        width: '100%'
                    });
                }
            });

            console.log('Select2 инициализирован');
        }
    }

    static initializeTooltips() {
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            const tooltipList = Array.from(tooltipTriggerList).map(tooltipTriggerEl => {
                return new bootstrap.Tooltip(tooltipTriggerEl, {
                    trigger: 'hover focus'
                });
            });
            console.log(`Инициализировано ${tooltipList.length} тултипов`);
        }
    }

    static initializeCharCounters() {
        const textareas = document.querySelectorAll('textarea[maxlength]');
        textareas.forEach(textarea => {
            const maxLength = parseInt(textarea.getAttribute('maxlength'));
            if (!maxLength) return;

            const counter = Utils.createElement('div', {
                className: 'char-counter text-muted small mt-1',
                style: 'text-align: right;'
            });

            const updateCounter = () => {
                const remaining = maxLength - textarea.value.length;
                counter.textContent = `${textarea.value.length}/${maxLength} Zeichen`;

                counter.className = 'char-counter small mt-1 ' +
                    (remaining < 20 ? 'text-danger' :
                     remaining < 50 ? 'text-warning' : 'text-muted');
            };

            textarea.parentNode.appendChild(counter);
            textarea.addEventListener('input', updateCounter);
            updateCounter();
        });
    }

    static initializeProgressiveFields() {
        const postalCodeField = document.querySelector('input[name="postal_code"]');
        const cityField = document.querySelector('input[name="city"]');

        if (postalCodeField && cityField) {
            const cityMap = new Map([
                ['10115', 'Berlin'], ['20095', 'Hamburg'], ['80331', 'München'],
                ['50667', 'Köln'], ['60311', 'Frankfurt am Main'], ['70173', 'Stuttgart'],
                ['40213', 'Düsseldorf'], ['44135', 'Dortmund'], ['45127', 'Essen'],
                ['28195', 'Bremen'], ['01067', 'Dresden'], ['30159', 'Hannover'],
                ['90402', 'Nürnberg'], ['86150', 'Augsburg']
            ]);

            postalCodeField.addEventListener('blur', function() {
                const postalCode = this.value.trim();
                const suggestedCity = cityMap.get(postalCode);

                if (suggestedCity && !cityField.value.trim()) {
                    cityField.value = suggestedCity;
                    cityField.dispatchEvent(new Event('input', { bubbles: true }));

                    if (window.companyFormManager) {
                        window.companyFormManager.toastManager.show(
                            `Stadt automatisch ergänzt: ${suggestedCity}`,
                            'info',
                            3000
                        );
                    }
                }
            });
        }
    }

    static initializeAll() {
        try {
            this.initializeSelect2();
            this.initializeTooltips();
            this.initializeCharCounters();
            this.initializeProgressiveFields();
            console.log('✅ Все дополнительные функции инициализированы');
        } catch (error) {
            console.error('❌ Ошибка инициализации дополнительных функций:', error);
        }
    }
}

// ==================== УТИЛИТЫ ОТЛАДКИ ====================
const DEBUG_UTILS = {
    validateForm: () => {
        if (!window.companyFormManager) return null;

        const results = {
            overall: true,
            tabs: {},
            errors: [],
            warnings: []
        };

        // Проверяем каждый таб
        window.companyFormManager.tabs.forEach((tabName, index) => {
            const isValid = window.companyFormManager.validateTabsUpTo(index);
            results.tabs[tabName] = isValid;

            if (!isValid) {
                results.overall = false;
                results.errors.push(`Tab "${tabName}" содержит ошибки`);
            }
        });

        console.group('🔍 Результаты валидации формы');
        console.log('📊 Общий результат:', results.overall ? '✅ Валидна' : '❌ Содержит ошибки');
        console.log('📋 Результаты по табам:', results.tabs);

        if (results.errors.length > 0) {
            console.error('❌ Ошибки:', results.errors);
        }

        if (results.warnings.length > 0) {
            console.warn('⚠️ Предупреждения:', results.warnings);
        }

        console.groupEnd();
        return results;
    },

    getFormSummary: () => {
        if (!window.companyFormManager || !window.companyFormManager.form) return null;

        const form = window.companyFormManager.form;
        const formData = new FormData(form);

        return {
            companyName: formData.get('company_name') || '',
            legalForm: formData.get('legal_form') || '',
            industry: formData.get('industry') || '',
            address: {
                street: formData.get('street') || '',
                postalCode: formData.get('postal_code') || '',
                city: formData.get('city') || '',
                country: formData.get('country') || ''
            },
            contacts: {
                email: formData.get('email') || '',
                phone: formData.get('phone') || '',
                fax: formData.get('fax') || '',
                website: formData.get('website') || ''
            },
            additionalContacts: window.companyContactManager ?
                window.companyContactManager.additionalContacts : [],
            registration: {
                commercialRegister: formData.get('commercial_register') || '',
                taxNumber: formData.get('tax_number') || '',
                vatId: formData.get('vat_id') || ''
            },
            people: {
                ceo: formData.get('ceo_name') || '',
                contact: formData.get('contact_person') || ''
            },
            isPrimary: formData.get('is_primary') === 'on'
        };
    },

    previewData: () => {
        const summary = DEBUG_UTILS.getFormSummary();
        if (!summary) {
            console.error('Не удалось получить данные формы');
            return null;
        }

        console.group('👀 Предварительный просмотр данных компании');
        console.log('🏢 Основная информация:');
        console.log(`  Название: ${summary.companyName}`);
        console.log(`  Правовая форма: ${summary.legalForm}`);
        console.log(`  Отрасль: ${summary.industry || 'Не указана'}`);

        console.log('📍 Адрес:');
        console.log(`  ${summary.address.street}`);
        console.log(`  ${summary.address.postalCode} ${summary.address.city}`);
        console.log(`  ${summary.address.country}`);

        console.log('📞 Контакты:');
        console.log(`  Email: ${summary.contacts.email}`);
        console.log(`  Телефон: ${summary.contacts.phone}`);
        if (summary.contacts.fax) console.log(`  Факс: ${summary.contacts.fax}`);
        if (summary.contacts.website) console.log(`  Сайт: ${summary.contacts.website}`);

        if (summary.additionalContacts.length > 0) {
            console.log('📱 Дополнительные контакты:');
            summary.additionalContacts.forEach((contact, index) => {
                console.log(`  ${index + 1}. ${contact.type}: ${contact.value}`);
            });
        }

        if (summary.registration.commercialRegister || summary.registration.taxNumber || summary.registration.vatId) {
            console.log('📋 Регистрационные данные:');
            if (summary.registration.commercialRegister) console.log(`  Торговый реестр: ${summary.registration.commercialRegister}`);
            if (summary.registration.taxNumber) console.log(`  Налоговый номер: ${summary.registration.taxNumber}`);
            if (summary.registration.vatId) console.log(`  НДС ID: ${summary.registration.vatId}`);
        }

        if (summary.people.ceo || summary.people.contact) {
            console.log('👥 Ответственные лица:');
            if (summary.people.ceo) console.log(`  Директор: ${summary.people.ceo}`);
            if (summary.people.contact) console.log(`  Контактное лицо: ${summary.people.contact}`);
        }

        console.log(`⭐ Основная компания: ${summary.isPrimary ? 'Да' : 'Нет'}`);
        console.groupEnd();

        return summary;
    },

    exportData: () => {
        const summary = DEBUG_UTILS.getFormSummary();
        if (summary) {
            const dataStr = JSON.stringify(summary, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'company_form_data.json';
            link.click();
            URL.revokeObjectURL(url);
            console.log('✅ Данные формы экспортированы');
        }
    },

    showStats: () => {
        console.group('📈 Статистика формы');

        if (window.companyFormManager) {
            const form = window.companyFormManager.form;
            const totalFields = form.querySelectorAll('input, select, textarea').length;
            const filledFields = Array.from(form.querySelectorAll('input, select, textarea')).filter(field => {
                if (field.type === 'checkbox') return field.checked;
                return field.value.trim() !== '';
            }).length;
            const validFields = form.querySelectorAll('.is-valid').length;
            const invalidFields = form.querySelectorAll('.is-invalid').length;

            console.log(`📝 Всего полей: ${totalFields}`);
            console.log(`✏️ Заполнено полей: ${filledFields} (${Math.round(filledFields/totalFields*100)}%)`);
            console.log(`✅ Валидных полей: ${validFields}`);
            console.log(`❌ Невалидных полей: ${invalidFields}`);
            console.log(`📄 Текущий таб: ${window.companyFormManager.currentTabIndex + 1}/${window.companyFormManager.tabs.length}`);
        }

        if (window.companyContactManager) {
            console.log(`📞 Дополнительных контактов: ${window.companyContactManager.additionalContacts.length}`);
        }

        console.groupEnd();
    }
};

// ==================== ИНИЦИАЛИЗАЦИЯ ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Инициализация регистрации компании...');

    try {
        // Инициализируем менеджер дополнительных контактов
        window.companyContactManager = new CompanyAdditionalContactManager();
        companyContactManager.init();

        // Инициализируем менеджер формы
        window.companyFormManager = new CompanyFormManager();
        companyFormManager.init();

        // Инициализируем дополнительные возможности
        setTimeout(() => {
            FormEnhancements.initializeAll();
        }, 500);

        // Делаем функции доступными глобально для onclick handlers
        window.openContactModal = (index) => companyContactManager.openContactModal(index);
        window.confirmDeleteContact = (index) => companyContactManager.confirmDeleteContact(index);

        // Отладочные функции
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            window.validateCompanyForm = DEBUG_UTILS.validateForm;
            window.getCompanyFormSummary = DEBUG_UTILS.getFormSummary;
            window.previewCompanyData = DEBUG_UTILS.previewData;
            window.exportCompanyData = DEBUG_UTILS.exportData;
            window.showCompanyFormStats = DEBUG_UTILS.showStats;

            // Горячие клавиши для отладки
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.shiftKey) {
                    switch(e.key) {
                        case 'D':
                            e.preventDefault();
                            DEBUG_UTILS.validateForm();
                            break;
                        case 'S':
                            e.preventDefault();
                            DEBUG_UTILS.showStats();
                            break;
                        case 'E':
                            e.preventDefault();
                            DEBUG_UTILS.exportData();
                            break;
                        case 'P':
                            e.preventDefault();
                            DEBUG_UTILS.previewData();
                            break;
                    }
                }
            });

            console.log('🎯 Debug режим активен. Доступные функции:');
            console.log('  - validateCompanyForm()');
            console.log('  - getCompanyFormSummary()');
            console.log('  - previewCompanyData()');
            console.log('  - exportCompanyData()');
            console.log('  - showCompanyFormStats()');
            console.log('🎹 Горячие клавиши:');
            console.log('  - Ctrl+Shift+D: Валидация');
            console.log('  - Ctrl+Shift+S: Статистика');
            console.log('  - Ctrl+Shift+E: Экспорт');
            console.log('  - Ctrl+Shift+P: Просмотр');
        }

        console.log('✅ Регистрация компании полностью инициализирована');

    } catch (error) {
        console.error('❌ Критическая ошибка инициализации:', error);

        // Показываем пользователю сообщение об ошибке
        const alertDiv = Utils.createElement('div', {
            className: 'alert alert-danger alert-dismissible fade show position-fixed',
            style: 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;',
            role: 'alert'
        });

        alertDiv.innerHTML = `
            <strong>Fehler!</strong> Die Formular-Initialisierung ist fehlgeschlagen.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        document.body.appendChild(alertDiv);

        // Автоматически скрываем через 10 секунд
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 10000);
    }
});

// ==================== ГЛОБАЛЬНЫЙ DEBUG ОБЪЕКТ ====================
window.COMPANY_FORM_DEBUG = {
    version: '3.0.0',
    initialized: true,
    timestamp: new Date().toISOString(),

    managers: {
        form: () => window.companyFormManager,
        contacts: () => window.companyContactManager
    },

    utils: DEBUG_UTILS,

    config: CONFIG,

    classes: {
        Utils,
        FormValidator,
        ToastManager,
        CompanyAdditionalContactManager,
        CompanyFormManager,
        FormEnhancements
    },

    reinit: () => {
        console.log('🔄 Переинициализация компонентов...');

        if (window.companyContactManager) {
            window.companyContactManager.init();
        }

        if (window.companyFormManager) {
            window.companyFormManager.init();
        }

        FormEnhancements.initializeAll();

        console.log('✅ Переинициализация завершена');
    }
};

// ==================== ИНФОРМАЦИЯ О МОДУЛЕ ====================
console.group('🏢 Company Registration Module v3.0');
console.log('📦 Version: 3.0.0 (Production Ready)');
console.log('🏗️ Architecture: Modular ES6+ Classes');
console.log('🚀 Performance: Optimized with caching and debouncing');
console.log('🔒 Security: XSS protection and input sanitization');
console.log('♿ Accessibility: ARIA labels and keyboard navigation');
console.log('📱 Responsive: Mobile-first design');
console.log('🌐 i18n Ready: Configurable messages');
console.log('🔧 Debug Tools:', window.location.hostname.includes('localhost') ? 'Enabled' : 'Disabled');

if (window.location.hostname.includes('localhost')) {
    console.log('🎮 Available in window.COMPANY_FORM_DEBUG');
    console.log('📋 Managers:', Object.keys(window.COMPANY_FORM_DEBUG.managers).length);
    console.log('🛠️ Utils:', Object.keys(window.COMPANY_FORM_DEBUG.utils).length);
    console.log('🏗️ Classes:', Object.keys(window.COMPANY_FORM_DEBUG.classes).length);
}

console.groupEnd();

// ==================== ЭКСПОРТ (для тестирования) ====================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CONFIG,
        Utils,
        FormValidator,
        ToastManager,
        CompanyAdditionalContactManager,
        CompanyFormManager,
        FormEnhancements,
        DEBUG_UTILS
    };
}

console.log('📄 register_company.js v3.0 - Ready for production! 🎉');