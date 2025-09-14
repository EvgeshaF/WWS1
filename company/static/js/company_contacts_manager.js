// company/static/js/company_contacts_manager.js - Company Contacts Management

// ==================== COMPANY ADDITIONAL CONTACTS MANAGER ====================
class CompanyAdditionalContactManager {
    constructor() {
        this.additionalContacts = [];
        this.editingIndex = -1;
        this.deletingIndex = -1;

        this.contactTypeLabels = {
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

        this.contactTypeIcons = {
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

        this.departmentLabels = {
            'management': 'Geschäftsführung',
            'sales': 'Vertrieb',
            'support': 'Kundensupport',
            'accounting': 'Buchhaltung',
            'hr': 'Personalabteilung',
            'it': 'IT-Abteilung',
            'marketing': 'Marketing',
            'production': 'Produktion',
            'logistics': 'Logistik',
            'purchasing': 'Einkauf',
            'quality': 'Qualitätsmanagement',
            'legal': 'Rechtsabteilung',
            'reception': 'Empfang/Zentrale',
            'other': 'Sonstige'
        };
    }

    init() {
        this.bindEvents();
        this.updateTable();
        this.updateSummary();
        this.setupFormSubmission();
    }

    bindEvents() {
        const openBtn = document.getElementById('openAdditionalContactsBtn');
        if (openBtn) {
            openBtn.addEventListener('click', () => {
                this.openAdditionalContactsModal();
            });
        }

        const addBtn = document.getElementById('addAdditionalContactBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => {
                this.openContactModal();
            });
        }

        const saveBtn = document.getElementById('saveContactBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveContact();
            });
        }

        const confirmBtn = document.getElementById('confirmDeleteBtn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                this.deleteContact();
            });
        }

        const typeSelect = document.getElementById('contactType');
        if (typeSelect) {
            typeSelect.addEventListener('change', (e) => {
                this.updateContactHints(e.target.value);
            });
        }

        const valueInput = document.getElementById('contactValue');
        if (valueInput) {
            valueInput.addEventListener('input', () => {
                this.validateContactValue();
            });
        }

        const modal = document.getElementById('contactModal');
        if (modal) {
            modal.addEventListener('hidden.bs.modal', () => {
                this.resetContactForm();
            });
        }
    }

    openAdditionalContactsModal() {
        const modalElement = document.getElementById('additionalContactsModal');
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            this.updateTable();
            this.updateModalCounter();
            modal.show();
        }
    }

    openContactModal(index = -1) {
        this.editingIndex = index;
        const modalElement = document.getElementById('contactModal');
        if (!modalElement) return;

        const modal = new bootstrap.Modal(modalElement);
        const modalTitle = document.getElementById('contactModalLabel');
        const saveBtn = document.getElementById('saveContactBtn');

        if (index >= 0) {
            const contact = this.additionalContacts[index];
            modalTitle.innerHTML = '<i class="bi bi-pencil me-2"></i>Firmenkontakt bearbeiten';
            saveBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Aktualisieren';

            this.setFieldValue('contactType', contact.type);
            this.setFieldValue('contactValue', contact.value);
            this.setFieldValue('contactLabel', contact.department || '');
            this.setCheckboxValue('contactImportant', contact.important || false);
            this.setCheckboxValue('contactPublic', contact.public || false);

            this.updateContactHints(contact.type);
        } else {
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

        form.querySelectorAll('.is-invalid, .is-valid').forEach(el => {
            el.classList.remove('is-invalid', 'is-valid');
        });

        this.updateContactHints('');
    }

    updateContactHints(type) {
        const valueInput = document.getElementById('contactValue');
        const hintElement = document.getElementById('contactHint');

        if (!valueInput || !hintElement) return;

        const hints = {
            'email': 'Geben Sie eine E-Mail-Adresse ein (z.B. vertrieb@firma.de)',
            'phone': 'Geben Sie eine Telefonnummer ein (z.B. +49 123 456789)',
            'mobile': 'Geben Sie eine Mobilnummer ein (z.B. +49 170 1234567)',
            'fax': 'Geben Sie eine Faxnummer ein (z.B. +49 123 456789)',
            'website': 'Geben Sie eine Website-URL ein (z.B. https://www.firma.de)',
            'linkedin': 'Geben Sie das LinkedIn-Unternehmensprofil ein',
            'xing': 'Geben Sie das XING-Unternehmensprofil ein',
            'emergency': 'Geben Sie einen Notfallkontakt ein (z.B. +49 170 1234567)',
            'other': 'Geben Sie die entsprechenden Kontaktdaten ein'
        };

        const placeholders = {
            'email': 'abteilung@firma.de',
            'phone': '+49 123 456789',
            'mobile': '+49 170 1234567',
            'fax': '+49 123 456789',
            'website': 'https://www.firma.de',
            'linkedin': 'linkedin.com/company/firmenname',
            'xing': 'xing.com/companies/firmenname',
            'emergency': '+49 170 1234567',
            'other': 'Kontaktdaten eingeben...'
        };

        if (type && hints[type]) {
            hintElement.innerHTML = `<i class="bi bi-lightbulb me-1"></i>${hints[type]}`;
            valueInput.placeholder = placeholders[type];
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

        switch (type) {
            case 'email':
                return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
            case 'phone':
            case 'mobile':
            case 'fax':
            case 'emergency':
                return /^[\+]?[0-9\s\-\(\)]{7,20}$/.test(value);
            case 'website':
                return /^https?:\/\/.+\..+$/.test(value) || /^www\..+\..+$/.test(value);
            case 'linkedin':
                return value.includes('linkedin.com') || /^[a-zA-Z0-9\-_]+$/.test(value);
            case 'xing':
                return value.includes('xing.com') || /^[a-zA-Z0-9\-_]+$/.test(value);
            default:
                return value.length >= 3;
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

        const isTypeValid = this.validateField(typeField);
        const isValueValid = this.validateField(valueField);

        if (!isTypeValid || !isValueValid) {
            this.showAlert('Bitte korrigieren Sie die Fehler im Formular', 'error');
            return;
        }

        const contactData = {
            type: typeField.value,
            value: valueField.value.trim(),
            department: labelField ? labelField.value : '',
            label: labelField ? (this.departmentLabels[labelField.value] || labelField.value) : '',
            important: importantField ? importantField.checked : false,
            public: publicField ? publicField.checked : false
        };

        if (contactData.important) {
            this.additionalContacts.forEach(contact => contact.important = false);
        }

        if (this.editingIndex >= 0) {
            this.additionalContacts[this.editingIndex] = contactData;
            this.showAlert('Firmenkontakt erfolgreich aktualisiert', 'success');
        } else {
            this.additionalContacts.push(contactData);
            this.showAlert('Firmenkontakt erfolgreich hinzugefügt', 'success');
        }

        this.updateTable();
        this.updateModalCounter();
        this.updateSummary();
        this.updateContactsDataInput();

        const modalElement = document.getElementById('contactModal');
        if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
        }
    }

    validateField(field) {
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

        this.setFieldValidation(field, isValid, errorMessage);
        return isValid;
    }

    getValidationError() {
        const typeField = document.getElementById('contactType');
        if (!typeField) return 'Ungültiges Format';

        const type = typeField.value;

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

    setFieldValidation(field, isValid, errorMessage = '') {
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
}

// ==================== ИНИЦИАЛИЗАЦИЯ ====================
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('company-step4-form');
    if (!form) return;

    // Инициализируем менеджер дополнительных контактов компании
    window.companyAdditionalContactManager = new CompanyAdditionalContactManager();
    companyAdditionalContactManager.init();

    // Если есть существующие данные дополнительных контактов, загружаем их
    const existingAdditionalContacts = window.initialAdditionalContactsData || [];
    if (existingAdditionalContacts.length > 0) {
        companyAdditionalContactManager.loadAdditionalContacts(existingAdditionalContacts);
    }

    console.log('Company Contact Manager полностью инициализирован');
    console.log('- CompanyAdditionalContactManager: готов');
    console.log('- Загружено дополнительных контактов:', existingAdditionalContacts.length);
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