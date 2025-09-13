// static/my/js/users/create_admin_step2.js - ENHANCED MODAL VERSION

// ==================== ГЛАВНЫЙ КОНТАКТ МЕНЕДЖЕР ====================
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
        this.contactTypeSelect = document.getElementById('id_primary_contact_type');
        this.contactValueInput = document.getElementById('id_primary_contact_value');
        this.contactHintElement = document.getElementById('primaryContactHint');

        if (!this.contactTypeSelect || !this.contactValueInput || !this.contactHintElement) {
            console.warn('PrimaryContactManager: Не все элементы найдены на странице');
            return;
        }

        this.bindEvents();
        this.updateContactHints();
        console.log('PrimaryContactManager инициализирован');
    }

    bindEvents() {
        this.contactTypeSelect.addEventListener('change', () => {
            this.updateContactHints();
            this.validateContactValue();
        });

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
            this.contactValueInput.placeholder = config.placeholder;
            this.contactHintElement.innerHTML = `
                <i class="bi bi-lightbulb me-1"></i>
                ${config.hint}
            `;

            if (config.pattern) {
                this.contactValueInput.setAttribute('pattern', config.pattern);
            } else {
                this.contactValueInput.removeAttribute('pattern');
            }
        } else {
            this.contactValueInput.placeholder = 'Kontaktdaten eingeben...';
            this.contactHintElement.innerHTML = `
                <i class="bi bi-lightbulb me-1"></i>
                Wählen Sie zuerst den Kontakttyp aus
            `;
            this.contactValueInput.removeAttribute('pattern');
        }

        this.clearFieldValidation();
    }

    validateContactValue() {
        const selectedType = this.contactTypeSelect.value.toLowerCase();
        const value = this.contactValueInput.value.trim();

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

        if (config.pattern) {
            const regex = new RegExp(config.pattern);
            if (!regex.test(value)) {
                isValid = false;
                errorMessage = this.getValidationErrorMessage(selectedType);
            }
        }

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

        const existingError = this.contactValueInput.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        this.contactValueInput.closest('.mb-3').appendChild(errorDiv);
    }

    setFieldSuccess() {
        this.contactValueInput.classList.remove('is-invalid');
        this.contactValueInput.classList.add('is-valid');

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

    isValid() {
        return this.validateContactValue();
    }
}

// ==================== ДОПОЛНИТЕЛЬНЫЕ КОНТАКТЫ МЕНЕДЖЕР - ENHANCED VERSION ====================
class AdditionalContactManager {
    constructor() {
        this.additionalContacts = [];
        this.editingIndex = -1;
        this.deletingIndex = -1;

        this.contactTypeLabels = {
            'email': 'E-Mail',
            'mobile': 'Mobil',
            'fax': 'Fax',
            'website': 'Website',
            'linkedin': 'LinkedIn',
            'xing': 'XING',
            'other': 'Sonstige'
        };

        this.contactTypeIcons = {
            'email': 'bi-envelope',
            'mobile': 'bi-phone',
            'fax': 'bi-printer',
            'website': 'bi-globe',
            'linkedin': 'bi-linkedin',
            'xing': 'bi-person-badge',
            'other': 'bi-question-circle'
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
            modalTitle.innerHTML = '<i class="bi bi-pencil me-2"></i>Kontakt bearbeiten';
            saveBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Aktualisieren';

            this.setFieldValue('contactType', contact.type);
            this.setFieldValue('contactValue', contact.value);
            this.setFieldValue('contactLabel', contact.label || '');
            this.setCheckboxValue('contactPrimary', contact.primary || false);

            this.updateContactHints(contact.type);
        } else {
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
            'email': 'Geben Sie eine zusätzliche E-Mail-Adresse ein (z.B. privat@example.com)',
            'mobile': 'Geben Sie eine Mobilnummer ein (z.B. +49 170 1234567)',
            'fax': 'Geben Sie eine Faxnummer ein (z.B. +49 123 456789)',
            'website': 'Geben Sie eine Website-URL ein (z.B. https://www.example.com)',
            'linkedin': 'Geben Sie Ihr LinkedIn-Profil ein (z.B. linkedin.com/in/username)',
            'xing': 'Geben Sie Ihr XING-Profil ein (z.B. xing.com/profile/username)',
            'other': 'Geben Sie die entsprechenden Kontaktdaten ein'
        };

        const placeholders = {
            'email': 'privat@domain.com',
            'mobile': '+49 170 1234567',
            'fax': '+49 123 456789',
            'website': 'https://www.example.com',
            'linkedin': 'linkedin.com/in/username',
            'xing': 'xing.com/profile/username',
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
            case 'mobile':
            case 'fax':
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
        const primaryField = document.getElementById('contactPrimary');

        const isTypeValid = this.validateField(typeField);
        const isValueValid = this.validateField(valueField);

        if (!isTypeValid || !isValueValid) {
            this.showAlert('Bitte korrigieren Sie die Fehler im Formular', 'error');
            return;
        }

        const contactData = {
            type: typeField.value,
            value: valueField.value.trim(),
            label: labelField ? labelField.value.trim() : '',
            primary: primaryField ? primaryField.checked : false
        };

        if (contactData.primary) {
            this.additionalContacts.forEach(contact => contact.primary = false);
        }

        if (this.editingIndex >= 0) {
            this.additionalContacts[this.editingIndex] = contactData;
            this.showAlert('Kontakt erfolgreich aktualisiert', 'success');
        } else {
            this.additionalContacts.push(contactData);
            this.showAlert('Kontakt erfolgreich hinzugefügt', 'success');
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
            'mobile': 'Ungültiges Mobilnummer-Format',
            'fax': 'Ungültiges Faxnummer-Format',
            'website': 'Ungültiges Website-Format (muss mit http:// oder https:// beginnen)',
            'linkedin': 'Ungültiges LinkedIn-Profil-Format',
            'xing': 'Ungültiges XING-Profil-Format',
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

    // НОВАЯ ФУНКЦИЯ: Обновление summary на главной странице
    updateSummary() {
        const counter = document.getElementById('additionalContactsCount');
        const summaryText = document.getElementById('contactsSummaryText');

        if (counter) {
            counter.textContent = this.additionalContacts.length;
        }

        if (summaryText) {
            const count = this.additionalContacts.length;
            if (count === 0) {
                summaryText.textContent = 'Keine zusätzlichen Kontakte hinzugefügt';
            } else if (count === 1) {
                summaryText.textContent = '1 zusätzlicher Kontakt hinzugefügt';
            } else {
                summaryText.textContent = `${count} zusätzliche Kontakte hinzugefügt`;
            }
        }
    }

    createContactRow(contact, index) {
        const typeIcon = this.contactTypeIcons[contact.type] || 'bi-question-circle';
        const typeLabel = this.contactTypeLabels[contact.type] || contact.type;
        const primaryStar = contact.primary ? '<i class="bi bi-star-fill primary-contact-star me-1" title="Wichtig"></i>' : '';
        const labelText = contact.label ? `<div class="contact-label small text-muted">${this.escapeHtml(contact.label)}</div>` : '';

        return `
            <tr>
                <td>
                    <span class="contact-type-badge contact-type-${contact.type}">
                        <i class="bi ${typeIcon} me-1"></i>
                        ${typeLabel}
                    </span>
                    ${labelText}
                </td>
                <td>
                    ${primaryStar}
                    <code class="contact-value">${this.escapeHtml(contact.value)}</code>
                </td>
                <td>
                    ${contact.primary ? '<span class="badge bg-warning text-dark">Wichtig</span>' : '<span class="badge bg-secondary">Standard</span>'}
                </td>
                <td class="text-center">
                    <div class="btn-group btn-group-sm" role="group">
                        <button type="button" class="btn btn-outline-primary" 
                                onclick="additionalContactManager.openContactModal(${index})" 
                                title="Bearbeiten">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button type="button" class="btn btn-outline-danger" 
                                onclick="additionalContactManager.confirmDelete(${index})" 
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
            console.log('Обновлены данные дополнительных контактов:', this.additionalContacts.length);
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
        const form = document.getElementById('admin-step2-form');
        if (!form) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();

            const firstNameInput = form.querySelector('input[name="first_name"]');
            const lastNameInput = form.querySelector('input[name="last_name"]');
            const salutationSelect = form.querySelector('select[name="salutation"]');
            const emailInput = form.querySelector('input[name="email"]');
            const phoneInput = form.querySelector('input[name="phone"]');

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

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird gespeichert...';
            }

            const formData = new FormData(form);

            const additionalContactsData = this.getAdditionalContactsData();
            formData.append('additional_contacts_data', JSON.stringify(additionalContactsData));

            const primaryContactData = {
                type: primaryContactTypeSelect.value,
                value: primaryContactValueInput.value.trim(),
                label: 'Hauptkontakt',
                primary: true
            };
            formData.append('primary_contact_data', JSON.stringify(primaryContactData));

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

                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i>Weiter zu Schritt 3';
                }

                if (data.messages && Array.isArray(data.messages)) {
                    data.messages.forEach(message => {
                        this.showAlert(message.text, message.tags);
                    });

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

                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i>Weiter zu Schritt 3';
                }

                if (error.message.includes('non-JSON')) {
                    this.showAlert('Server hat eine ungültige Antwort gesendet. Bitte versuchen Sie es erneut.', 'error');
                } else {
                    this.showAlert('Fehler beim Speichern des Profils: ' + error.message, 'error');
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

        const email = emailInput.value.trim();
        this.clearFieldError(emailInput);

        if (!email) {
            this.setFieldError(emailInput, 'System E-Mail ist erforderlich');
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
            this.setFieldError(phoneInput, 'Telefon ist erforderlich');
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

    validatePrimaryContact(typeSelect, valueInput) {
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

        if (window.primaryContactManager && !window.primaryContactManager.isValid()) {
            return false;
        }

        this.setFieldSuccess(typeSelect);
        this.setFieldSuccess(valueInput);
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
    const form = document.getElementById('admin-step2-form');
    if (!form) return;

    // Инициализируем менеджер главного контакта
    window.primaryContactManager = new PrimaryContactManager();
    primaryContactManager.init();

    // Инициализируем менеджер дополнительных контактов
    window.additionalContactManager = new AdditionalContactManager();
    additionalContactManager.init();

    // Если есть существующие данные дополнительных контактов, загружаем их
    const existingAdditionalContacts = window.initialAdditionalContactsData || [];
    if (existingAdditionalContacts.length > 0) {
        additionalContactManager.loadAdditionalContacts(existingAdditionalContacts);
    }

    console.log('Create Admin Step 2 (Enhanced Modal Version) полностью инициализирован');
    console.log('- PrimaryContactManager: готов');
    console.log('- AdditionalContactManager: готов');
    console.log('- Загружено дополнительных контактов:', existingAdditionalContacts.length);
});