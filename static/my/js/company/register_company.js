document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('company-form');
    const nextTabBtn = document.getElementById('next-tab-btn');
    const prevTabBtn = document.getElementById('prev-tab-btn');
    const submitBtn = document.getElementById('submit-btn');
    const nextBtnText = document.getElementById('next-btn-text');

    const tabs = ['basic', 'registration', 'address', 'details'];
    let currentTabIndex = 0;
    let additionalContacts = [];
    let editingContactIndex = -1;
    let deletingContactIndex = -1;

    const contactTypeLabels = {
        'email': 'E-Mail (zusätzlich)',
        'mobile': 'Mobil',
        'fax': 'Fax (zusätzlich)',
        'website': 'Website (zusätzlich)',
        'linkedin': 'LinkedIn',
        'xing': 'XING',
        'other': 'Sonstige'
    };

    const contactTypeIcons = {
        'email': 'bi-envelope-plus',
        'mobile': 'bi-phone',
        'fax': 'bi-printer',
        'website': 'bi-globe',
        'linkedin': 'bi-linkedin',
        'xing': 'bi-person-badge',
        'other': 'bi-question-circle'
    };

    if (!form || !nextTabBtn || !prevTabBtn || !submitBtn) {
        console.error('Required elements not found');
        return;
    }

    // Initialize
    console.log('Initializing company registration modal...');
    initialize();

    function initialize() {
        // Setup all functionality
        bindEvents();
        setupFormValidation();
        setupSpecialFieldValidation();
        setupModalResetHandlers();
        setupBrowserNavigation();
        setupKeyboardShortcuts();
        setupAutoSave();
        setupErrorHandling();
        
        // Load existing data
        loadExistingAdditionalContacts();
        
        // Try to restore from session storage (only if no existing data)
        if (additionalContacts.length === 0) {
            loadFormDataFromSessionStorage();
        }
        
        // Initialize form validation
        initializeFormValidation();
        
        // Update UI
        updateProgress();
        updateNavigationButtons();
        updateContactsSummary();
        
        console.log('Company registration modal fully initialized');
        console.log('- Current tab:', currentTabIndex);
        console.log('- Additional contacts:', additionalContacts.length);
    }

    function bindEvents() {
        // Navigation buttons
        nextTabBtn.addEventListener('click', nextTab);
        prevTabBtn.addEventListener('click', prevTab);
        submitBtn.addEventListener('click', submitForm);

        // Tab click handlers
        const tabButtons = document.querySelectorAll('#companyTabs button[data-bs-toggle="tab"]');
        tabButtons.forEach((button, index) => {
            button.addEventListener('click', function(e) {
                if (index <= currentTabIndex || validateTabsUpTo(index - 1)) {
                    currentTabIndex = index;
                    updateProgress();
                    updateNavigationButtons();
                } else {
                    e.preventDefault();
                    e.stopPropagation();
                    showToast('Bitte füllen Sie zuerst die vorherigen Tabs aus', 'warning');
                }
            });
        });

        // Additional contacts management
        const manageContactsBtn = document.getElementById('manage-additional-contacts');
        if (manageContactsBtn) {
            manageContactsBtn.addEventListener('click', openAdditionalContactsModal);
        }

        const addContactBtn = document.getElementById('add-contact-btn');
        if (addContactBtn) {
            addContactBtn.addEventListener('click', () => openContactModal());
        }

        const saveContactBtn = document.getElementById('saveContactBtn');
        if (saveContactBtn) {
            saveContactBtn.addEventListener('click', saveContact);
        }

        const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        if (confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener('click', deleteContact);
        }

        // Contact type change
        const contactTypeSelect = document.getElementById('contactType');
        if (contactTypeSelect) {
            contactTypeSelect.addEventListener('change', (e) => {
                updateContactHints(e.target.value);
            });
        }

        // Tab switching with Bootstrap events
        document.querySelectorAll('#companyTabs button[data-bs-toggle="tab"]').forEach((tabButton, index) => {
            tabButton.addEventListener('shown.bs.tab', function () {
                currentTabIndex = index;
                updateProgress();
                updateNavigationButtons();
            });
        });
    }

    function setupFormValidation() {
        const requiredFields = form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            field.addEventListener('blur', function() {
                validateField(this);
            });

            field.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    }

    function setupSpecialFieldValidation() {
        // PLZ validation
        const postalCodeField = form.querySelector('input[name="postal_code"]');
        if (postalCodeField) {
            postalCodeField.addEventListener('input', function() {
                const value = this.value.replace(/\D/g, '');
                this.value = value.substring(0, 5);
            });
        }

        // VAT ID formatting
        const vatIdField = form.querySelector('input[name="vat_id"]');
        if (vatIdField) {
            vatIdField.addEventListener('input', function() {
                let value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
                if (value.length > 0 && !value.startsWith('DE')) {
                    value = 'DE' + value;
                }
                if (value.length > 11) {
                    value = value.substring(0, 11);
                }
                this.value = value;
            });
        }

        // Commercial register formatting
        const hrField = form.querySelector('input[name="commercial_register"]');
        if (hrField) {
            hrField.addEventListener('input', function() {
                let value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
                this.value = value;
            });
        }
    }

    function nextTab() {
        if (validateCurrentTab()) {
            if (currentTabIndex < tabs.length - 1) {
                currentTabIndex++;
                switchToTab(currentTabIndex);
                updateProgress();
                updateNavigationButtons();
            }
        } else {
            showToast('Bitte füllen Sie alle erforderlichen Felder aus', 'warning');
        }
    }

    function prevTab() {
        if (currentTabIndex > 0) {
            currentTabIndex--;
            switchToTab(currentTabIndex);
            updateProgress();
            updateNavigationButtons();
        }
    }

    function switchToTab(index) {
        const targetTab = tabs[index];
        const tabButton = document.querySelector(`#${targetTab}-tab`);
        if (tabButton) {
            const tab = new bootstrap.Tab(tabButton);
            tab.show();
        }
    }

    function updateProgress() {
        const progress = ((currentTabIndex + 1) / tabs.length) * 100;
        const progressBar = document.getElementById('progress-bar');
        const currentStep = document.getElementById('current-step');
        
        if (progressBar) {
            progressBar.style.width = progress + '%';
        }
        if (currentStep) {
            currentStep.textContent = currentTabIndex + 1;
        }
    }

    function updateNavigationButtons() {
        // Update previous button
        if (currentTabIndex === 0) {
            prevTabBtn.style.display = 'none';
        } else {
            prevTabBtn.style.display = 'inline-flex';
        }

        // Update next/submit button
        if (currentTabIndex === tabs.length - 1) {
            nextTabBtn.style.display = 'none';
            submitBtn.style.display = 'inline-flex';
        } else {
            nextTabBtn.style.display = 'inline-flex';
            submitBtn.style.display = 'none';

            // Update next button text
            const isLastBeforeSubmit = currentTabIndex === tabs.length - 2;
            nextBtnText.innerHTML = isLastBeforeSubmit
                ? '<i class="bi bi-check-circle me-1"></i>Zur Übersicht'
                : '<i class="bi bi-arrow-right me-1"></i>Weiter';
        }

        // Update tab indicators
        updateTabIndicators();
    }

    function updateTabIndicators() {
        const tabButtons = document.querySelectorAll('#companyTabs button[data-bs-toggle="tab"]');
        tabButtons.forEach((button, index) => {
            const isCompleted = index < currentTabIndex;
            const isCurrent = index === currentTabIndex;

            button.classList.remove('completed', 'current');

            if (isCompleted) {
                button.classList.add('completed');
                const icon = button.querySelector('i');
                if (icon && !icon.classList.contains('bi-check-circle-fill')) {
                    icon.className = 'bi bi-check-circle-fill me-1';
                }
            } else if (isCurrent) {
                button.classList.add('current');
            }
        });
    }

    function validateCurrentTab() {
        const currentTab = tabs[currentTabIndex];
        const currentPane = document.getElementById(currentTab);
        const fieldsInTab = currentPane.querySelectorAll('input[required], select[required], textarea[required]');

        let isValid = true;
        fieldsInTab.forEach(field => {
            if (!validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    function validateTabsUpTo(index) {
        for (let i = 0; i <= index; i++) {
            const tab = tabs[i];
            const pane = document.getElementById(tab);
            const fieldsInTab = pane.querySelectorAll('input[required], select[required], textarea[required]');

            for (let field of fieldsInTab) {
                if (!validateField(field)) {
                    return false;
                }
            }
        }
        return true;
    }

    function validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;

        clearFieldError(field);

        // Check required fields
        if (field.hasAttribute('required') && !value) {
            setFieldError(field, 'Dieses Feld ist erforderlich');
            return false;
        }

        // Skip validation for empty optional fields
        if (!value && !field.hasAttribute('required')) {
            return true;
        }

        // Field-specific validation
        switch (fieldName) {
            case 'email':
                if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                    setFieldError(field, 'Ungültiges E-Mail-Format');
                    return false;
                }
                break;
            
            case 'phone':
            case 'fax':
                if (!/^[\+]?[0-9\s\-\(\)]{7,20}$/.test(value)) {
                    setFieldError(field, 'Ungültiges Telefonformat');
                    return false;
                }
                break;
            
            case 'postal_code':
                if (!/^[0-9]{5}$/.test(value)) {
                    setFieldError(field, 'PLZ muss aus 5 Ziffern bestehen');
                    return false;
                }
                break;
            
            case 'website':
                if (value && !/^https?:\/\/.+/.test(value)) {
                    setFieldError(field, 'Website muss mit http:// oder https:// beginnen');
                    return false;
                }
                break;
            
            case 'vat_id':
                if (value && !/^DE[0-9]{9}$/.test(value)) {
                    setFieldError(field, 'USt-IdNr. muss im Format DE123456789 sein');
                    return false;
                }
                break;
            
            case 'commercial_register':
                if (value && !/^HR[AB][0-9]+$/.test(value)) {
                    setFieldError(field, 'Handelsregister muss im Format HRA12345 oder HRB12345 sein');
                    return false;
                }
                break;

            case 'company_name':
                if (value.length < 2) {
                    setFieldError(field, 'Firmenname muss mindestens 2 Zeichen haben');
                    return false;
                }
                if (value.length > 100) {
                    setFieldError(field, 'Firmenname darf maximal 100 Zeichen haben');
                    return false;
                }
                break;
        }

        setFieldSuccess(field);
        return true;
    }

    function setFieldError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');

        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    function setFieldSuccess(field) {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');

        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    function clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');

        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    // Additional Contacts Management
    function openAdditionalContactsModal() {
        const modalElement = document.getElementById('additionalContactsModal');
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            updateContactsTable();
            updateModalCounter();
            modal.show();
        }
    }

    function openContactModal(index = -1) {
        editingContactIndex = index;
        const modalElement = document.getElementById('contactModal');
        if (!modalElement) return;

        const modal = new bootstrap.Modal(modalElement);
        const modalTitle = document.getElementById('contactModalLabel');
        const saveBtn = document.getElementById('saveContactBtn');

        if (index >= 0) {
            const contact = additionalContacts[index];
            modalTitle.innerHTML = '<i class="bi bi-pencil me-2"></i>Kontakt bearbeiten';
            saveBtn.innerHTML = '<i class="bi bi-check me-1"></i>Aktualisieren';

            document.getElementById('contactType').value = contact.type;
            document.getElementById('contactValue').value = contact.value;
            document.getElementById('contactLabel').value = contact.label || '';
            document.getElementById('contactImportant').checked = contact.important || false;

            updateContactHints(contact.type);
        } else {
            modalTitle.innerHTML = '<i class="bi bi-person-plus me-2"></i>Kontakt hinzufügen';
            saveBtn.innerHTML = '<i class="bi bi-check me-1"></i>Speichern';
            resetContactForm();
        }

        modal.show();
    }

    function resetContactForm() {
        const contactForm = document.getElementById('contactForm');
        if (!contactForm) return;

        contactForm.reset();

        contactForm.querySelectorAll('.is-invalid, .is-valid').forEach(el => {
            el.classList.remove('is-invalid', 'is-valid');
        });

        updateContactHints('');
    }

    function updateContactHints(type) {
        const valueInput = document.getElementById('contactValue');
        const hintElement = document.getElementById('contactHint');

        if (!valueInput || !hintElement) return;

        const hints = {
            'email': 'Geben Sie eine zusätzliche E-Mail-Adresse ein (z.B. marketing@firma.de)',
            'mobile': 'Geben Sie eine Mobilnummer ein (z.B. +49 170 1234567)',
            'fax': 'Geben Sie eine zusätzliche Faxnummer ein (z.B. +49 123 456789)',
            'website': 'Geben Sie eine zusätzliche Website ein (z.B. https://shop.firma.de)',
            'linkedin': 'Geben Sie das LinkedIn-Profil ein (z.B. linkedin.com/company/firma)',
            'xing': 'Geben Sie das XING-Profil ein (z.B. xing.com/companies/firma)',
            'other': 'Geben Sie die entsprechenden Kontaktdaten ein'
        };

        const placeholders = {
            'email': 'marketing@firma.de',
            'mobile': '+49 170 1234567',
            'fax': '+49 123 456789',
            'website': 'https://shop.firma.de',
            'linkedin': 'linkedin.com/company/firma',
            'xing': 'xing.com/companies/firma',
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

    function saveContact() {
        const typeField = document.getElementById('contactType');
        const valueField = document.getElementById('contactValue');
        const labelField = document.getElementById('contactLabel');
        const importantField = document.getElementById('contactImportant');

        if (!typeField || !valueField) return;

        const type = typeField.value;
        const value = valueField.value.trim();
        const label = labelField ? labelField.value.trim() : '';
        const important = importantField ? importantField.checked : false;

        // Validation
        if (!type) {
            showToast('Kontakttyp ist erforderlich', 'error');
            return;
        }

        if (!value) {
            showToast('Kontaktdaten sind erforderlich', 'error');
            return;
        }

        if (!validateContactValue(type, value)) {
            return;
        }

        const contactData = { type, value, label, important };

        if (editingContactIndex >= 0) {
            additionalContacts[editingContactIndex] = contactData;
            showToast('Kontakt erfolgreich aktualisiert', 'success');
        } else {
            additionalContacts.push(contactData);
            showToast('Kontakt erfolgreich hinzugefügt', 'success');
        }

        updateContactsTable();
        updateModalCounter();
        updateContactsSummary();
        updateAdditionalContactsDataInput();

        const modalElement = document.getElementById('contactModal');
        if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
        }
    }

    function validateContactValue(type, value) {
        let isValid = true;
        let message = '';

        switch (type) {
            case 'email':
                isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
                message = 'Ungültiges E-Mail-Format';
                break;
            case 'mobile':
            case 'fax':
                isValid = /^[\+]?[0-9\s\-\(\)]{7,20}$/.test(value);
                message = 'Ungültiges Telefonformat';
                break;
            case 'website':
                isValid = /^https?:\/\/.+/.test(value);
                message = 'Website muss mit http:// oder https:// beginnen';
                break;
            case 'linkedin':
                isValid = value.includes('linkedin.com') || /^[a-zA-Z0-9\-_]+$/.test(value);
                message = 'Ungültiges LinkedIn-Format';
                break;
            case 'xing':
                isValid = value.includes('xing.com') || /^[a-zA-Z0-9\-_]+$/.test(value);
                message = 'Ungültiges XING-Format';
                break;
            default:
                isValid = value.length >= 3;
                message = 'Kontaktdaten müssen mindestens 3 Zeichen lang sein';
        }

        if (!isValid) {
            showToast(message, 'error');
        }

        return isValid;
    }

    function confirmDeleteContact(index) {
        deletingContactIndex = index;
        const modalElement = document.getElementById('deleteContactModal');
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    }

    function deleteContact() {
        if (deletingContactIndex >= 0) {
            additionalContacts.splice(deletingContactIndex, 1);
            updateContactsTable();
            updateModalCounter();
            updateContactsSummary();
            updateAdditionalContactsDataInput();
            showToast('Kontakt erfolgreich gelöscht', 'info');

            const modalElement = document.getElementById('deleteContactModal');
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
            }
        }
    }

    function updateContactsTable() {
        const tableBody = document.getElementById('contacts-table-body');
        const tableContainer = document.getElementById('contacts-table-container');
        const placeholder = document.getElementById('empty-contacts-placeholder');

        if (!tableBody || !tableContainer || !placeholder) return;

        if (additionalContacts.length === 0) {
            tableContainer.style.display = 'none';
            placeholder.style.display = 'block';
            return;
        }

        tableContainer.style.display = 'block';
        placeholder.style.display = 'none';

        tableBody.innerHTML = additionalContacts.map((contact, index) => {
            return createContactRow(contact, index);
        }).join('');
    }

    function createContactRow(contact, index) {
        const typeIcon = contactTypeIcons[contact.type] || 'bi-question-circle';
        const typeLabel = contactTypeLabels[contact.type] || contact.type;
        const importantBadge = contact.important ? '<span class="badge bg-warning text-dark ms-1">Wichtig</span>' : '';
        const labelText = contact.label || '<em class="text-muted">Keine Beschreibung</em>';

        return `
            <tr>
                <td>
                    <i class="bi ${typeIcon} me-2 text-primary"></i>
                    ${typeLabel}
                    ${importantBadge}
                </td>
                <td>
                    <code class="company-contact-value">${escapeHtml(contact.value)}</code>
                </td>
                <td>${labelText}</td>
                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-outline-primary company-action-btn me-1" 
                            onclick="openContactModal(${index})" title="Bearbeiten">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-danger company-action-btn" 
                            onclick="confirmDeleteContact(${index})" title="Löschen">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    function updateModalCounter() {
        const modalCounter = document.getElementById('modal-contacts-count');
        if (modalCounter) {
            modalCounter.textContent = additionalContacts.length;
        }
    }

    function updateContactsSummary() {
        const counter = document.getElementById('additional-contacts-count');
        const summary = document.getElementById('contacts-summary');
        const summaryText = document.getElementById('contacts-summary-text');

        if (counter) {
            counter.textContent = additionalContacts.length;
        }

        if (summary && summaryText) {
            if (additionalContacts.length === 0) {
                summary.classList.add('d-none');
                summaryText.textContent = 'Keine zusätzlichen Kontakte hinzugefügt';
            } else {
                summary.classList.remove('d-none');
                const count = additionalContacts.length;
                if (count === 1) {
                    summaryText.textContent = '1 zusätzlicher Kontakt hinzugefügt';
                } else {
                    summaryText.textContent = `${count} zusätzliche Kontakte hinzugefügt`;
                }
            }
        }
    }

    function updateAdditionalContactsDataInput() {
        const input = document.getElementById('additionalContactsDataInput');
        if (input) {
            input.value = JSON.stringify(additionalContacts);
            console.log('Updated additional contacts data:', additionalContacts.length);
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function submitForm() {
        if (!validateAllTabs()) {
            showToast('Bitte korrigieren Sie alle Fehler im Formular', 'error');
            return;
        }

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird registriert...';

        // Prepare form data
        const formData = new FormData(form);
        
        // Add additional contacts data
        formData.append('additional_contacts_data', JSON.stringify(additionalContacts));

        // Submit form
        fetch(form.action || window.location.pathname, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'HX-Request': 'true'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Hide loading state
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-building-add me-1"></i>Firma registrieren';

            // Handle messages
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(message => {
                    showToast(message.text, message.tags, message.delay);
                });

                // If success, redirect to home
                const hasSuccess = data.messages.some(msg => msg.tags === 'success');
                if (hasSuccess) {
                    handleFormSubmissionSuccess();
                }
            }
        })
        .catch(error => {
            console.error('Error submitting form:', error);

            // Hide loading state
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-building-add me-1"></i>Firma registrieren';

            showToast('Fehler beim Registrieren der Firma', 'error');
        });
    }

    function validateAllTabs() {
        let isValid = true;

        tabs.forEach(tabId => {
            const pane = document.getElementById(tabId);
            const fieldsInTab = pane.querySelectorAll('input, select, textarea');

            fieldsInTab.forEach(field => {
                if (!validateField(field)) {
                    isValid = false;
                }
            });
        });

        return isValid;
    }

    function showToast(message, type = 'info', delay = 5000) {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('#toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        // Create toast element
        const toastId = 'toast_' + Date.now();
        const typeConfig = {
            'success': { bg: 'bg-success', icon: 'bi-check-circle-fill', title: 'Erfolg' },
            'error': { bg: 'bg-danger', icon: 'bi-x-circle-fill', title: 'Fehler' },
            'warning': { bg: 'bg-warning', icon: 'bi-exclamation-triangle-fill', title: 'Warnung' },
            'info': { bg: 'bg-info', icon: 'bi-info-circle-fill', title: 'Info' }
        };

        const config = typeConfig[type] || typeConfig['info'];

        const toastHTML = `
            <div id="${toastId}" class="toast ${config.bg} text-white" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header ${config.bg} text-white border-0">
                    <i class="bi ${config.icon} me-2"></i>
                    <strong class="me-auto">${config.title}</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);

        // Initialize and show toast
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: delay });
        toast.show();

        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    }

    // Initialize form validation on page load
    function initializeFormValidation() {
        form.querySelectorAll('input, select, textarea').forEach(field => {
            // Set initial state
            if (field.value.trim()) {
                validateField(field);
            }
        });
    }

    // Load existing additional contacts data
    function loadExistingAdditionalContacts() {
        const input = document.getElementById('additionalContactsDataInput');
        if (input && input.value) {
            try {
                const existingData = JSON.parse(input.value);
                if (Array.isArray(existingData)) {
                    additionalContacts = existingData;
                    updateContactsTable();
                    updateModalCounter();
                    updateContactsSummary();
                    updateAdditionalContactsDataInput();
                    console.log('Loaded existing additional contacts:', additionalContacts.length);
                }
            } catch (e) {
                console.error('Error parsing existing additional contacts data:', e);
            }
        }
    }

    // Handle modal reset when closing
    function setupModalResetHandlers() {
        const contactModal = document.getElementById('contactModal');
        if (contactModal) {
            contactModal.addEventListener('hidden.bs.modal', () => {
                resetContactForm();
                editingContactIndex = -1;
            });
        }

        const deleteModal = document.getElementById('deleteContactModal');
        if (deleteModal) {
            deleteModal.addEventListener('hidden.bs.modal', () => {
                deletingContactIndex = -1;
            });
        }
    }

    // Handle browser back/forward buttons
    function setupBrowserNavigation() {
        window.addEventListener('beforeunload', function(e) {
            // Check if form has unsaved changes
            if (formHasChanges()) {
                const confirmationMessage = 'Sie haben ungespeicherte Änderungen. Möchten Sie die Seite wirklich verlassen?';
                e.returnValue = confirmationMessage;
                return confirmationMessage;
            }
        });
    }

    function formHasChanges() {
        // Check if any form field has been modified
        const formFields = form.querySelectorAll('input, select, textarea');
        for (let field of formFields) {
            if (field.defaultValue !== field.value) {
                return true;
            }
        }
        // Check if additional contacts have been added
        return additionalContacts.length > 0;
    }

    // Handle keyboard shortcuts
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + Enter to submit form (only on last tab)
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                if (currentTabIndex === tabs.length - 1) {
                    e.preventDefault();
                    submitForm();
                }
            }

            // Escape to go back (if not on first tab)
            if (e.key === 'Escape' && currentTabIndex > 0) {
                e.preventDefault();
                prevTab();
            }

            // Ctrl/Cmd + Right Arrow to go forward
            if ((e.ctrlKey || e.metaKey) && e.key === 'ArrowRight') {
                if (currentTabIndex < tabs.length - 1) {
                    e.preventDefault();
                    nextTab();
                }
            }

            // Ctrl/Cmd + Left Arrow to go back
            if ((e.ctrlKey || e.metaKey) && e.key === 'ArrowLeft') {
                if (currentTabIndex > 0) {
                    e.preventDefault();
                    prevTab();
                }
            }
        });
    }

    // Auto-save functionality (optional)
    function setupAutoSave() {
        let autoSaveTimeout;
        
        form.addEventListener('input', function() {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                saveFormDataToSessionStorage();
            }, 2000); // Auto-save after 2 seconds of no input
        });
    }

    function saveFormDataToSessionStorage() {
        try {
            const formData = new FormData(form);
            const formObject = {};
            
            for (let [key, value] of formData.entries()) {
                formObject[key] = value;
            }
            
            formObject.additional_contacts = additionalContacts;
            formObject.current_tab = currentTabIndex;
            
            sessionStorage.setItem('companyFormData', JSON.stringify(formObject));
            console.log('Form data auto-saved to session storage');
        } catch (e) {
            console.error('Error saving form data to session storage:', e);
        }
    }

    function loadFormDataFromSessionStorage() {
        try {
            const savedData = sessionStorage.getItem('companyFormData');
            if (savedData) {
                const formObject = JSON.parse(savedData);
                
                // Restore form fields
                for (let [key, value] of Object.entries(formObject)) {
                    if (key !== 'additional_contacts' && key !== 'current_tab') {
                        const field = form.querySelector(`[name="${key}"]`);
                        if (field) {
                            field.value = value;
                        }
                    }
                }
                
                // Restore additional contacts
                if (formObject.additional_contacts) {
                    additionalContacts = formObject.additional_contacts;
                    updateContactsTable();
                    updateModalCounter();
                    updateContactsSummary();
                    updateAdditionalContactsDataInput();
                }
                
                // Restore current tab
                if (formObject.current_tab && formObject.current_tab > 0) {
                    currentTabIndex = formObject.current_tab;
                    switchToTab(currentTabIndex);
                    updateProgress();
                    updateNavigationButtons();
                }
                
                console.log('Form data restored from session storage');
                showToast('Formular aus vorheriger Sitzung wiederhergestellt', 'info', 3000);
            }
        } catch (e) {
            console.error('Error loading form data from session storage:', e);
        }
    }

    function clearFormDataFromSessionStorage() {
        try {
            sessionStorage.removeItem('companyFormData');
            console.log('Form data cleared from session storage');
        } catch (e) {
            console.error('Error clearing form data from session storage:', e);
        }
    }

    // Enhanced error handling
    function setupErrorHandling() {
        window.addEventListener('error', function(e) {
            console.error('JavaScript error:', e.error);
            showToast('Ein unerwarteter Fehler ist aufgetreten', 'error');
        });

        window.addEventListener('unhandledrejection', function(e) {
            console.error('Unhandled promise rejection:', e.reason);
            showToast('Ein unerwarteter Fehler ist aufgetreten', 'error');
        });
    }

    // Add success handler for AJAX form submission
    function handleFormSubmissionSuccess() {
        form.dataset.submitted = 'true';
        clearFormDataFromSessionStorage();
        showToast('Firma erfolgreich registriert!', 'success');
        
        // Optional: Close modal and redirect after delay
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);
    }

    // Utility function to get current form data as object
    function getCurrentFormData() {
        const formData = new FormData(form);
        const formObject = {};
        
        for (let [key, value] of formData.entries()) {
            formObject[key] = value;
        }
        
        formObject.additional_contacts = additionalContacts;
        return formObject;
    }

    // Make functions globally available for onclick handlers
    window.openContactModal = openContactModal;
    window.confirmDeleteContact = confirmDeleteContact;

    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        // Only clear auto-saved data if form was successfully submitted
        if (form.dataset.submitted === 'true') {
            clearFormDataFromSessionStorage();
        }
    });

    // Mark form as submitted when successfully submitted
    form.addEventListener('submit', function() {
        form.dataset.submitted = 'true';
        clearFormDataFromSessionStorage();
    });

    // Debug function (can be removed in production)
    window.debugCompanyForm = function() {
        console.log('=== Company Form Debug Info ===');
        console.log('Current tab index:', currentTabIndex);
        console.log('Additional contacts:', additionalContacts);
        console.log('Form data:', getCurrentFormData());
        console.log('Form validation state:', {
            tab0: validateTabsUpTo(0),
            tab1: validateTabsUpTo(1), 
            tab2: validateTabsUpTo(2),
            tab3: validateTabsUpTo(3)
        });
        console.log('Session storage data:', sessionStorage.getItem('companyFormData'));
    };

    // Helper function for form reset (useful for testing)
    window.resetCompanyForm = function() {
        if (confirm('Möchten Sie wirklich das gesamte Formular zurücksetzen?')) {
            form.reset();
            additionalContacts = [];
            currentTabIndex = 0;
            
            updateContactsTable();
            updateModalCounter();
            updateContactsSummary();
            updateAdditionalContactsDataInput();
            switchToTab(0);
            updateProgress();
            updateNavigationButtons();
            
            clearFormDataFromSessionStorage();
            showToast('Formular wurde zurückgesetzt', 'info');
        }
    };

    // Helper function to validate entire form (useful for testing)
    window.validateCompanyForm = function() {
        const isValid = validateAllTabs();
        console.log('Form validation result:', isValid);
        
        if (!isValid) {
            showToast('Formular enthält Fehler', 'warning');
        } else {
            showToast('Formular ist vollständig und gültig', 'success');
        }
        
        return isValid;
    };

    console.log('Company registration modal script loaded successfully');
    console.log('Available debug functions: debugCompanyForm(), resetCompanyForm(), validateCompanyForm()');
});