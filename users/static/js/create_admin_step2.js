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

        // === Select2 для Hauptkontakt Typ ===
        $(this.contactTypeSelect).select2({
            theme: 'bootstrap-5',
            placeholder: 'Kontakttyp auswählen...',
            allowClear: false,
            width: '100%'
        }).on('select2:select', () => {
            this.updateContactHints();
            this.validateContactValue();
        });

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
            this.contactHintElement.innerHTML = `<i class="bi bi-lightbulb me-1"></i>${config.hint}`;
            if (config.pattern) {
                this.contactValueInput.setAttribute('pattern', config.pattern);
            } else {
                this.contactValueInput.removeAttribute('pattern');
            }
        } else {
            this.contactValueInput.placeholder = 'Kontaktdaten eingeben...';
            this.contactHintElement.innerHTML = `<i class="bi bi-lightbulb me-1"></i>Wählen Sie zuerst den Kontakttyp aus`;
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
        if (existingError) existingError.remove();
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        this.contactValueInput.closest('.mb-3').appendChild(errorDiv);
    }

    setFieldSuccess() {
        this.contactValueInput.classList.remove('is-invalid');
        this.contactValueInput.classList.add('is-valid');
        const existingError = this.contactValueInput.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) existingError.remove();
    }

    clearFieldValidation() {
        this.contactValueInput.classList.remove('is-invalid', 'is-valid');
        const existingError = this.contactValueInput.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) existingError.remove();
    }

    isValid() {
        return this.validateContactValue();
    }
}

// ==================== ДОПОЛНИТЕЛЬНЫЕ КОНТАКТЫ МЕНЕДЖЕР ====================
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
        if (openBtn) openBtn.addEventListener('click', () => this.openAdditionalContactsModal());

        const addBtn = document.getElementById('addAdditionalContactBtn');
        if (addBtn) addBtn.addEventListener('click', () => this.openContactModal());

        const saveBtn = document.getElementById('saveContactBtn');
        if (saveBtn) saveBtn.addEventListener('click', () => this.saveContact());

        const confirmBtn = document.getElementById('confirmDeleteBtn');
        if (confirmBtn) confirmBtn.addEventListener('click', () => this.deleteContact());

        const modal = document.getElementById('contactModal');
        if (modal) {
            modal.addEventListener('shown.bs.modal', () => {
                if ($('#contactType').data('select2')) {
                    $('#contactType').select2('destroy');
                }
                $('#contactType').select2({
                    theme: 'bootstrap-5',
                    placeholder: 'Kontakttyp auswählen...',
                    dropdownParent: $('#contactModal'),
                    allowClear: false,
                    width: '100%'
                }).on('select2:select', (e) => {
                    this.updateContactHints(e.params.data.id);
                });
            });

            modal.addEventListener('hidden.bs.modal', () => {
                $('#contactType').val('').trigger('change');
                this.resetContactForm();
            });
        }
    }

    // ... остальной код AdditionalContactManager без изменений ...
    // (таблица, валидация, сохранение, удаление и т.д.)
}

// ==================== ИНИЦИАЛИЗАЦИЯ ====================
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admin-step2-form');
    if (!form) return;

    window.primaryContactManager = new PrimaryContactManager();
    primaryContactManager.init();

    window.additionalContactManager = new AdditionalContactManager();
    additionalContactManager.init();

    const existingAdditionalContacts = window.initialAdditionalContactsData || [];
    if (existingAdditionalContacts.length > 0) {
        additionalContactManager.loadAdditionalContacts(existingAdditionalContacts);
    }

    console.log('Create Admin Step 2 (Enhanced + Select2) полностью инициализирован');
});
