// register_company.js - ПОЛНАЯ ВЕРСИЯ В СТИЛЕ АДМИНИСТРАТОРА

// ==================== КОНФИГУРАЦИЯ ====================
const CONFIG = {
    VALIDATION_PATTERNS: {
        EMAIL: /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/,
        GERMAN_PHONE: /^[\+]?[0-9\s\-\(\)]{7,20}$/,
        GERMAN_POSTAL: /^[0-9]{5}$/,
        VAT_ID: /^DE[0-9]{9}$/,
        COMMERCIAL_REGISTER: /^HR[AB][0-9]+$/,
        WEBSITE: /^https?:\/\/([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/,
        LINKEDIN: /(https?:\/\/)?(www\.)?linkedin\.com\/(company|in)\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$/,
        XING: /(https?:\/\/)?(www\.)?xing\.com\/(companies|profile)\/[a-zA-Z0-9\-_]+\/?$|^[a-zA-Z0-9\-_]+$/
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
            CONTACT_SAVED: 'Kontakt erfolgreich hinzugefügt',
            CONTACT_UPDATED: 'Kontakt erfolgreich aktualisiert',
            CONTACT_DELETED: 'Kontakt erfolgreich gelöscht',
            FORM_SUCCESS: 'Firma erfolgreich registriert!',
            FILL_REQUIRED_FIELDS: 'Bitte füllen Sie alle erforderlichen Felder aus',
            CORRECT_ERRORS: 'Bitte korrigieren Sie alle Fehler im Formular'
        }
    }
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

    static getCachedElement(id, cache = new Map()) {
        if (!cache.has(id)) {
            cache.set(id, document.getElementById(id));
        }
        return cache.get(id);
    }
}

// ==================== ВАЛИДАТОР ====================
class FormValidator {
    constructor() {
        this.patterns = CONFIG.VALIDATION_PATTERNS;
        this.messages = CONFIG.MESSAGES.de;
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;
        this.clearFieldValidation(field);

        if (field.hasAttribute('required') && !value) {
            this.setFieldError(field, this.messages.FIELD_REQUIRED);
            return false;
        }

        if (!value && !field.hasAttribute('required')) {
            return true;
        }

        const validationRules = {
            email: () => this.patterns.EMAIL.test(value) || this.messages.INVALID_EMAIL,
            phone: () => this.patterns.GERMAN_PHONE.test(value) || this.messages.INVALID_PHONE,
            fax: () => this.patterns.GERMAN_PHONE.test(value) || this.messages.INVALID_PHONE,
            postal_code: () => this.patterns.GERMAN_POSTAL.test(value) || this.messages.INVALID_POSTAL,
            website: () => this.patterns.WEBSITE.test(value) || this.messages.INVALID_WEBSITE,
            vat_id: () => this.patterns.VAT_ID.test(value) || this.messages.INVALID_VAT,
            commercial_register: () => this.patterns.COMMERCIAL_REGISTER.test(value) || this.messages.INVALID_REGISTER
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
            linkedin: () => this.patterns.LINKEDIN.test(value) || 'Ungültiges LinkedIn-Format',
            xing: () => this.patterns.XING.test(value) || 'Ungültiges XING-Format',
            other: () => value.length >= 3 || 'Mindestens 3 Zeichen erforderlich'
        };

        const rule = contactValidation[type];
        return rule ? rule() : true;
    }

    setFieldError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        this.removeExistingFeedback(field);

        const errorDiv = Utils.createElement('div', {
            className: 'invalid-feedback d-block'
        }, message);
        field.parentNode.appendChild(errorDiv);
    }

    setFieldSuccess(field) {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');
        this.removeExistingFeedback(field);
    }

    clearFieldValidation(field) {
        field.classList.remove('is-invalid', 'is-valid');
        this.removeExistingFeedback(field);
    }

    removeExistingFeedback(field) {
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }
}

// ==================== МЕНЕДЖЕР ДОПОЛНИТЕЛЬНЫХ КОНТАКТОВ ====================
class CompanyAdditionalContactManager {
    constructor() {
        this.additionalContacts = [];
        this.editingIndex = -1;
        this.deletingIndex = -1;
        this.validator = new FormValidator();
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
    }

    init() {
        this.bindEvents();
        this.loadExistingData();
        this.updateDisplay();
        console.log('CompanyAdditionalContactManager инициализирован');
    }

    bindEvents() {
        this.addEventListenerSafe('manage-additional-contacts', 'click', () => this.openAdditionalContactsModal());
        this.addEventListenerSafe('add-contact-btn', 'click', () => this.openContactModal());
        this.addEventListenerSafe('saveContactBtn', 'click', () => this.saveContact());
        this.addEventListenerSafe('confirmDeleteBtn', 'click', () => this.deleteContact());
        this.addEventListenerSafe('contactType', 'change', (e) => this.updateContactHints(e.target.value));
        this.addEventListenerSafe('contactValue', 'input', () => this.validateContactValue());
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
        if (typeof window.initialAdditionalContactsData !== 'undefined') {
            try {
                this.additionalContacts = window.initialAdditionalContactsData || [];
                console.log('Загружены существующие дополнительные контакты:', this.additionalContacts.length);
            } catch (e) {
                console.error('Ошибка загрузки существующих контактов:', e);
                this.additionalContacts = [];
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
            const contact = this.additionalContacts[index];
            this.setModalTitle(modalTitle, 'bi-pencil', 'Kontakt bearbeiten');
            this.setButtonContent(saveBtn, 'bi-check', 'Aktualisieren');
            this.setFieldValue('contactType', contact.type);
            this.setFieldValue('contactValue', contact.value);
            this.setFieldValue('contactLabel', contact.label || '');
            this.setCheckboxValue('contactImportant', contact.important || false);
            this.updateContactHints(contact.type);
        } else {
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
        });
        form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
        this.updateContactHints('');
    }

    updateContactHints(type) {
        const valueInput = Utils.getCachedElement('contactValue', this.elementCache);
        const hintElement = Utils.getCachedElement('contactHint', this.elementCache);

        if (!valueInput || !hintElement) return;

        const hints = {
            email: {
                placeholder: 'marketing@firma.de',
                hint: 'Geben Sie eine zusätzliche E-Mail-Adresse ein'
            },
            mobile: {
                placeholder: '+49 170 1234567',
                hint: 'Geben Sie eine Mobilnummer ein'
            },
            fax: {
                placeholder: '+49 123 456789',
                hint: 'Geben Sie eine Faxnummer ein'
            },
            website: {
                placeholder: 'https://shop.firma.de',
                hint: 'Geben Sie eine Website-URL ein'
            },
            linkedin: {
                placeholder: 'linkedin.com/company/firma',
                hint: 'Geben Sie das LinkedIn-Profil ein'
            },
            xing: {
                placeholder: 'xing.com/companies/firma',
                hint: 'Geben Sie das XING-Profil ein'
            },
            other: {
                placeholder: 'Kontaktdaten eingeben...',
                hint: 'Geben Sie die entsprechenden Kontaktdaten ein'
            }
        };

        const config = hints[type];
        if (config) {
            valueInput.placeholder = config.placeholder;
            hintElement.innerHTML = `<i class="bi bi-lightbulb me-1"></i>${config.hint}`;
        } else {
            valueInput.placeholder = 'Kontaktdaten eingeben...';
            hintElement.innerHTML = '<i class="bi bi-lightbulb me-1"></i>Wählen Sie zuerst den Kontakttyp aus';
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

        if (!type) {
            this.showToast('Kontakttyp ist erforderlich', 'error');
            return;
        }

        if (!value) {
            this.showToast('Kontaktdaten sind erforderlich', 'error');
            return;
        }

        if (!this.validateContactValue()) {
            return;
        }

        const contactData = { type, value, label, important };

        if (this.editingIndex >= 0) {
            this.additionalContacts[this.editingIndex] = contactData;
            this.showToast(CONFIG.MESSAGES.de.CONTACT_UPDATED, 'success');
        } else {
            this.additionalContacts.push(contactData);
            this.showToast(CONFIG.MESSAGES.de.CONTACT_SAVED, 'success');
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
            this.showToast(CONFIG.MESSAGES.de.CONTACT_DELETED, 'info');

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

        tableBody.innerHTML = '';
        this.additionalContacts.forEach((contact, index) => {
            const row = this.createContactRow(contact, index);
            tableBody.appendChild(row);
        });
    }

    createContactRow(contact, index) {
        const row = Utils.createElement('tr');

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

        const valueCell = Utils.createElement('td');
        const valueCode = Utils.createElement('code', {
            className: 'contact-value'
        }, contact.value);
        valueCell.appendChild(valueCode);

        const labelCell = Utils.createElement('td');
        if (contact.label) {
            labelCell.textContent = contact.label;
        } else {
            const emptyLabel = Utils.createElement('em', {
                className: 'text-muted'
            }, 'Keine Beschreibung');
            labelCell.appendChild(emptyLabel);
        }

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
            className: `btn btn-sm ${buttonClass}`,
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

    showToast(message, type = 'info') {
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
        this.elementCache = new Map();

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
        this.nextTabBtn.addEventListener('click', () => this.nextTab());
        this.prevTabBtn.addEventListener('click', () => this.prevTab());
        this.submitBtn.addEventListener('click', () => this.submitForm());

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
                    this.showToast('Bitte füllen Sie zuerst die vorherigen Tabs aus', 'warning');
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
            field.addEventListener('input', Utils.debounce(() => {
                this.validator.clearFieldValidation(field);
                this.validateField(field);
            }, 300));
        });
    }

    nextTab() {
        if (this.validateCurrentTab()) {
            if (this.currentTabIndex < this.tabs.length - 1) {
                this.currentTabIndex++;
                this.switchToTab(this.currentTabIndex);
                this.updateProgress();
                this.updateNavigationButtons();
            }
        } else {
            this.showToast(CONFIG.MESSAGES.de.FILL_REQUIRED_FIELDS, 'warning');
        }
    }

    prevTab() {
        if (this.currentTabIndex > 0) {
            this.currentTabIndex--;
            this.switchToTab(this.currentTabIndex);
            this.updateProgress();
            this.updateNavigationButtons();
        }
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
        this.prevTabBtn.style.display = this.currentTabIndex === 0 ? 'none' : 'inline-flex';

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
            this.showToast(CONFIG.MESSAGES.de.CORRECT_ERRORS, 'error');
            return;
        }

        this.setSubmitButtonLoading(true);

        const formData = new FormData(this.form);

        if (window.companyContactManager) {
            const contactsData = JSON.stringify(window.companyContactManager.getAdditionalContactsData());
            formData.append('additional_contacts_data', contactsData);
        }

        this.sendFormData(formData)
            .then(this.handleSubmitSuccess.bind(this))
            .catch(this.handleSubmitError.bind(this));
    }

    async sendFormData(formData) {
        const response = await fetch(window.location.pathname, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'HX-Request': 'true'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    }

    handleSubmitSuccess(data) {
        this.setSubmitButtonLoading(false);

        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(message => {
                this.showToast(message.text, message.tags);
            });

            const hasSuccess = data.messages.some(msg => msg.tags === 'success');
            if (hasSuccess) {
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            }
        } else {
            this.showToast(CONFIG.MESSAGES.de.FORM_SUCCESS, 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        }
    }

    handleSubmitError(error) {
        console.error('Ошибка отправки формы:', error);
        this.setSubmitButtonLoading(false);
        this.showToast('Ein unerwarteter Fehler ist aufgetreten', 'error');
    }

    setSubmitButtonLoading(isLoading) {
        if (isLoading) {
            this.submitBtn.disabled = true;
            this.submitBtn.innerHTML = '';

            const spinner = Utils.createElement('span', {
                className: 'spinner-border spinner-border-sm me-2'
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

    showToast(message, type = 'info') {
        if (typeof window.showToast === 'function') {
            window.showToast(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }
}

// ==================== ДОПОЛНИТЕЛЬНЫЕ УТИЛИТЫ ====================

function calculateFormCompleteness() {
    const form = document.getElementById('company-form');
    if (!form) return 0;

    const allFields = form.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], select, textarea');
    const filledFields = Array.from(allFields).filter(field => {
        const value = field.value ? field.value.trim() : '';
        return value.length > 0;
    });

    const completeness = Math.round((filledFields.length / allFields.length) * 100);
    console.log(`Форма заполнена на ${completeness}% (${filledFields.length}/${allFields.length})`);

    return completeness;
}

function initializeSelect2() {
    if (typeof $ !== 'undefined' && $.fn.select2) {
        console.log('Инициализация Select2 в стиле администратора...');

        $.fn.select2.defaults.set('language', 'de');

        const defaultSelect2Config = {
            theme: 'bootstrap-5',
            width: '100%',
            language: {
                noResults: function() {
                    return 'Keine Ergebnisse gefunden';
                },
                searching: function() {
                    return 'Suche läuft...';
                },
                inputTooShort: function() {
                    return 'Bitte geben Sie mindestens 1 Zeichen ein';
                },
                removeAllItems: function() {
                    return 'Alle Elemente entfernen';
                }
            }
        };

        $('.form-select:not(.select2-hidden-accessible)').each(function() {
            const $this = $(this);
            const config = Object.assign({}, defaultSelect2Config);

            if ($this.data('placeholder')) {
                config.placeholder = $this.data('placeholder');
                config.allowClear = true;
            }

            if ($this.data('allow-clear')) {
                config.allowClear = true;
            }

            if ($this.data('search') === false) {
                config.minimumResultsForSearch = Infinity;
            }

            if ($this.attr('name') === 'legal_form') {
                config.placeholder = 'Rechtsform auswählen...';
                config.minimumResultsForSearch = Infinity;
            } else if ($this.attr('name') === 'country') {
                config.placeholder = 'Land auswählen...';
                config.minimumResultsForSearch = Infinity;
            }

            $this.select2(config);
        });

        $('.form-select').on('select2:select', function (e) {
            const $this = $(this);
            console.log('Select2 выбор:', e.params.data.id, '-', e.params.data.text);

            $this.closest('.mb-3').find('.invalid-feedback').hide();
            $this.removeClass('is-invalid').addClass('is-valid');
        });

        $('.form-select').on('select2:clear', function (e) {
            const $this = $(this);
            console.log('Select2 очистка для:', $this.attr('name'));
            $this.removeClass('is-valid is-invalid');
        });

        console.log('Select2 успешно инициализирован в стиле администратора');
    } else {
        console.warn('jQuery или Select2 не загружены');
    }
}

function initializeInteractiveElements() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    console.log('Интерактивные элементы инициализированы');
}

function animateElementsIn() {
    const animatedElements = document.querySelectorAll('.card, .alert, .tab-pane.active');

    animatedElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';

        setTimeout(() => {
            element.style.transition = 'all 0.4s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function enhanceUserExperience() {
    const activePane = document.querySelector('.tab-pane.active');
    if (activePane) {
        const firstInput = activePane.querySelector('input[type="text"]:not([readonly]), select:not([disabled])');
        if (firstInput && !firstInput.value) {
            setTimeout(() => {
                firstInput.focus();
            }, 300);
        }
    }

    const firstError = document.querySelector('.is-invalid');
    if (firstError) {
        firstError.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }

    document.querySelectorAll('input, select, textarea').forEach(field => {
        field.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        field.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
}

function enableAutosave() {
    const form = document.getElementById('company-form');
    if (!form) return;

    let autosaveTimeout;
    const AUTOSAVE_DELAY = 30000; // 30 секунд

    function saveFormDraft() {
        const formData = new FormData(form);
        const draftData = {};

        for (let [key, value] of formData.entries()) {
            draftData[key] = value;
        }

        try {
            localStorage.setItem('company_form_draft', JSON.stringify({
                data: draftData,
                timestamp: new Date().toISOString(),
                completeness: calculateFormCompleteness()
            }));
            console.log('Черновик формы сохранен');
        } catch (e) {
            console.warn('Не удалось сохранить черновик:', e);
        }
    }

    function scheduleAutosave() {
        clearTimeout(autosaveTimeout);
        autosaveTimeout = setTimeout(saveFormDraft, AUTOSAVE_DELAY);
    }

    form.addEventListener('input', scheduleAutosave);
    form.addEventListener('change', scheduleAutosave);

    console.log('Автосохранение активировано (каждые 30 секунд)');
}

function loadFormDraft() {
    try {
        const draftJson = localStorage.getItem('company_form_draft');
        if (!draftJson) return false;

        const draft = JSON.parse(draftJson);
        const draftAge = Date.now() - new Date(draft.timestamp).getTime();
        const MAX_DRAFT_AGE = 24 * 60 * 60 * 1000; // 24 часа

        if (draftAge > MAX_DRAFT_AGE) {
            localStorage.removeItem('company_form_draft');
            return false;
        }

        const restore = confirm(`Найден сохраненный черновик от ${new Date(draft.timestamp).toLocaleString()}.\nВосстановить данные?`);

        if (restore && draft.data) {
            Object.entries(draft.data).forEach(([key, value]) => {
                const field = document.querySelector(`[name="${key}"]`);
                if (field && !field.value) {
                    field.value = value;

                    if ($(field).hasClass('select2-hidden-accessible')) {
                        $(field).val(value).trigger('change');
                    }
                }
            });

            console.log('Черновик восстановлен');
            window.showToast('Черновик формы восстановлен', 'info');
            return true;
        }
    } catch (e) {
        console.warn('Ошибка при загрузке черновика:', e);
    }

    return false;
}

// ==================== ГЛОБАЛЬНЫЕ ФУНКЦИИ ====================

window.exportFormData = function() {
    const form = document.getElementById('company-form');
    if (!form) return null;

    const formData = new FormData(form);
    const exportData = {
        metadata: {
            exportDate: new Date().toISOString(),
            formVersion: '2.0',
            completeness: calculateFormCompleteness()
        },
        basicData: {},
        registrationData: {},
        addressData: {},
        contactsData: {},
        additionalContacts: window.companyContactManager ?
                          window.companyContactManager.getAdditionalContactsData() : []
    };

    for (let [key, value] of formData.entries()) {
        if (['company_name', 'legal_form', 'industry', 'description'].includes(key)) {
            exportData.basicData[key] = value;
        } else if (['commercial_register', 'tax_number', 'vat_id'].includes(key)) {
            exportData.registrationData[key] = value;
        } else if (['street', 'postal_code', 'city', 'country'].includes(key)) {
            exportData.addressData[key] = value;
        } else if (['email', 'phone', 'fax', 'website', 'ceo_name', 'contact_person'].includes(key)) {
            exportData.contactsData[key] = value;
        }
    }

    return exportData;
};

window.importFormData = function(jsonData) {
    if (!jsonData || typeof jsonData !== 'object') return false;

    try {
        const form = document.getElementById('company-form');
        if (!form) return false;

        Object.entries({
            ...jsonData.basicData,
            ...jsonData.registrationData,
            ...jsonData.addressData,
            ...jsonData.contactsData
        }).forEach(([key, value]) => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field && value) {
                field.value = value;

                if ($(field).hasClass('select2-hidden-accessible')) {
                    $(field).val(value).trigger('change');
                }

                if (window.companyFormManager) {
                    window.companyFormManager.validateField(field);
                }
            }
        });

        if (jsonData.additionalContacts && window.companyContactManager) {
            window.companyContactManager.loadAdditionalContacts(jsonData.additionalContacts);
        }

        console.log('Данные формы успешно импортированы');
        window.showToast('Данные импортированы', 'success');
        return true;

    } catch (e) {
        console.error('Ошибка импорта данных:', e);
        window.showToast('Ошибка импорта данных', 'error');
        return false;
    }
};

window.resetCompanyForm = function() {
    const completeness = calculateFormCompleteness();

    if (completeness > 10) {
        const confirm = window.confirm('Вы уверены, что хотите очистить все данные формы? Это действие нельзя отменить.');
        if (!confirm) return false;
    }

    const form = document.getElementById('company-form');
    if (form) {
        form.reset();

        $('.select2-hidden-accessible').val(null).trigger('change');

        form.querySelectorAll('.is-valid, .is-invalid').forEach(el => {
            el.classList.remove('is-valid', 'is-invalid');
        });
        form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());

        if (window.companyContactManager) {
            window.companyContactManager.additionalContacts = [];
            window.companyContactManager.updateDisplay();
        }

        try {
            localStorage.removeItem('company_form_draft');
        } catch (e) {
            console.warn('Не удалось очистить черновик:', e);
        }

        if (window.companyFormManager) {
            window.companyFormManager.currentTabIndex = 0;
            window.companyFormManager.switchToTab(0);
            window.companyFormManager.updateProgress();
            window.companyFormManager.updateNavigationButtons();
        }

        console.log('Форма полностью сброшена');
        window.showToast('Форма очищена', 'info');
        return true;
    }

    return false;
};

window.getFormStatistics = function() {
    const form = document.getElementById('company-form');
    if (!form) return null;

    const allFields = form.querySelectorAll('input, select, textarea');
    const requiredFields = form.querySelectorAll('[required]');
    const filledFields = Array.from(allFields).filter(f => f.value && f.value.trim());
    const validFields = form.querySelectorAll('.is-valid');
    const invalidFields = form.querySelectorAll('.is-invalid');

    const additionalContacts = window.companyContactManager ?
                              window.companyContactManager.getAdditionalContactsData() : [];

    return {
        totalFields: allFields.length,
        requiredFields: requiredFields.length,
        filledFields: filledFields.length,
        validFields: validFields.length,
        invalidFields: invalidFields.length,
        completeness: calculateFormCompleteness(),
        additionalContactsCount: additionalContacts.length,
        currentTab: window.companyFormManager ? window.companyFormManager.currentTabIndex + 1 : 1,
        lastModified: document.lastModified
    };
};

// ==================== ГЛОБАЛЬНАЯ ФУНКЦИЯ TOAST ====================
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

// ==================== ИНИЦИАЛИЗАЦИЯ ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Инициализация регистрации компании в стиле администратора...');

    try {
        window.companyContactManager = new CompanyAdditionalContactManager();
        companyContactManager.init();

        window.companyFormManager = new CompanyFormManager();
        companyFormManager.init();

        console.log('✅ Базовая инициализация завершена');
    } catch (error) {
        console.error('❌ Ошибка базовой инициализации:', error);
    }

    setTimeout(() => {
        try {
            initializeSelect2();
            initializeInteractiveElements();
            animateElementsIn();
            enhanceUserExperience();
            enableAutosave();
            loadFormDraft();

            console.log('✅ Расширенная инициализация завершена успешно');
        } catch (error) {
            console.error('❌ Ошибка расширенной инициализации:', error);
        }
    }, 500);

    window.addEventListener('beforeunload', function(e) {
        const completeness = calculateFormCompleteness();
        if (completeness > 20 && completeness < 100) {
            e.preventDefault();
            e.returnValue = 'У вас есть несохраненные изменения. Действительно покинуть страницу?';
            return e.returnValue;
        }
    });

    document.getElementById('company-form').addEventListener('submit', function() {
        setTimeout(() => {
            try {
                localStorage.removeItem('company_form_draft');
                console.log('Черновик очищен после отправки');
            } catch (e) {
                console.warn('Не удалось очистить черновик:', e);
            }
        }, 1000);
    });
});

// ==================== КЛАВИАТУРНЫЕ СОКРАЩЕНИЯ ====================
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (window.companyFormManager) {
            const completeness = calculateFormCompleteness();
            if (completeness > 0) {
                const form = document.getElementById('company-form');
                if (form) {
                    const formData = new FormData(form);
                    const draftData = {};

                    for (let [key, value] of formData.entries()) {
                        draftData[key] = value;
                    }

                    try {
                        localStorage.setItem('company_form_draft', JSON.stringify({
                            data: draftData,
                            timestamp: new Date().toISOString(),
                            completeness: completeness
                        }));
                        window.showToast('Черновик сохранен (Ctrl+S)', 'success', 2000);
                        console.log('Черновик сохранен по Ctrl+S');
                    } catch (err) {
                        console.warn('Ошибка сохранения черновика:', err);
                    }
                }
            }
        }
    }

    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }

    if (e.ctrlKey && ['1', '2', '3', '4'].includes(e.key)) {
        e.preventDefault();
        const tabIndex = parseInt(e.key) - 1;
        if (window.companyFormManager && tabIndex < window.companyFormManager.tabs.length) {
            const canSwitch = tabIndex <= window.companyFormManager.currentTabIndex ||
                             window.companyFormManager.validateTabsUpTo(tabIndex - 1);

            if (canSwitch) {
                window.companyFormManager.currentTabIndex = tabIndex;
                window.companyFormManager.switchToTab(tabIndex);
                window.companyFormManager.updateProgress();
                window.companyFormManager.updateNavigationButtons();
                console.log(`Переключение на таб ${tabIndex + 1} по клавиатуре`);
            } else {
                window.showToast('Заполните предыдущие разделы', 'warning', 2000);
            }
        }
    }
});

// Делаем функции доступными глобально для onclick handlers
window.openContactModal = (index) => {
    if (window.companyContactManager) {
        window.companyContactManager.openContactModal(index);
    }
};

window.confirmDeleteContact = (index) => {
    if (window.companyContactManager) {
        window.companyContactManager.confirmDeleteContact(index);
    }
};

// Экспорт утилит
window.CompanyFormUtils = {
    calculateFormCompleteness,
    initializeSelect2,
    enhanceUserExperience
};

window.CompanyFormAdvanced = {
    exportFormData: window.exportFormData,
    importFormData: window.importFormData,
    resetForm: window.resetCompanyForm,
    getStatistics: window.getFormStatistics
};

console.log('🎯 JavaScript для формы компании полностью готов!');
console.log('🚀 Форма компании стилизована под администратора!');