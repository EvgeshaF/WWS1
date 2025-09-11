// static/my/js/company/register_company_modal.js - Modal Company Registration with Tabs

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('company-form');
    const nextTabBtn = document.getElementById('next-tab-btn');
    const prevTabBtn = document.getElementById('prev-tab-btn');
    const submitBtn = document.getElementById('submit-btn');
    const nextBtnText = document.getElementById('next-btn-text');

    const tabs = ['basic', 'address', 'contact', 'details'];
    let currentTabIndex = 0;

    // Tab navigation
    const tabButtons = document.querySelectorAll('#companyTabs button[data-bs-toggle="tab"]');
    const tabPanes = document.querySelectorAll('.tab-pane');

    if (!form || !nextTabBtn || !prevTabBtn || !submitBtn) {
        console.error('Required elements not found');
        return;
    }

    // Initialize tab navigation
    updateNavigationButtons();

    // Next tab button click
    nextTabBtn.addEventListener('click', function() {
        if (validateCurrentTab()) {
            if (currentTabIndex < tabs.length - 1) {
                currentTabIndex++;
                switchToTab(currentTabIndex);
                updateNavigationButtons();
            }
        }
    });

    // Previous tab button click
    prevTabBtn.addEventListener('click', function() {
        if (currentTabIndex > 0) {
            currentTabIndex--;
            switchToTab(currentTabIndex);
            updateNavigationButtons();
        }
    });

    // Tab click handlers
    tabButtons.forEach((button, index) => {
        button.addEventListener('click', function(e) {
            // Allow going to previous tabs or current tab
            if (index <= currentTabIndex || validateTabsUpTo(index - 1)) {
                currentTabIndex = index;
                updateNavigationButtons();
            } else {
                e.preventDefault();
                e.stopPropagation();
                showToast('Bitte füllen Sie zuerst die vorherigen Tabs aus', 'warning');
            }
        });
    });

    // Form field validation
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(this);
        });

        field.addEventListener('input', function() {
            clearFieldError(this);
        });
    });

    // PLZ validation
    const postalCodeField = form.querySelector('input[name="postal_code"]');
    if (postalCodeField) {
        postalCodeField.addEventListener('input', function() {
            const value = this.value.replace(/\D/g, ''); // Nur Zahlen
            this.value = value.substring(0, 5); // Max 5 Stellen
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

    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        if (!validateAllTabs()) {
            showToast('Bitte korrigieren Sie alle Fehler im Formular', 'error');
            return;
        }

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird registriert...';

        // Submit form
        const formData = new FormData(form);

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
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1500);
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
    });

    // Helper functions
    function switchToTab(index) {
        const targetTab = tabs[index];
        const tabButton = document.querySelector(`#${targetTab}-tab`);
        if (tabButton) {
            const tab = new bootstrap.Tab(tabButton);
            tab.show();
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
        tabButtons.forEach((button, index) => {
            const isCompleted = index < currentTabIndex;
            const isCurrent = index === currentTabIndex;

            // Remove all state classes
            button.classList.remove('completed', 'current');

            if (isCompleted) {
                button.classList.add('completed');
                // Add checkmark to completed tabs
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

        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                setFieldError(field, 'Ungültiges E-Mail-Format');
                return false;
            }
        }

        // URL validation
        if (field.type === 'url' && value) {
            try {
                new URL(value);
            } catch {
                setFieldError(field, 'Ungültiges URL-Format (z.B. https://www.firma.de)');
                return false;
            }
        }

        // Phone/Fax validation
        if ((fieldName === 'phone' || fieldName === 'fax') && value) {
            const phoneRegex = /^[\+]?[0-9\s\-\(\)]{7,20}$/;
            if (!phoneRegex.test(value)) {
                setFieldError(field, 'Ungültiges Telefonformat');
                return false;
            }
        }

        // Postal code validation
        if (fieldName === 'postal_code' && value) {
            const plzRegex = /^[0-9]{5}$/;
            if (!plzRegex.test(value)) {
                setFieldError(field, 'PLZ muss aus 5 Ziffern bestehen');
                return false;
            }
        }

        // VAT ID validation
        if (fieldName === 'vat_id' && value) {
            const vatRegex = /^DE[0-9]{9}$/;
            if (!vatRegex.test(value)) {
                setFieldError(field, 'Ungültiges Format (DE + 9 Ziffern)');
                return false;
            }
        }

        // Commercial register validation
        if (fieldName === 'commercial_register' && value) {
            const hrRegex = /^HR[AB][0-9]+$/;
            if (!hrRegex.test(value)) {
                setFieldError(field, 'Ungültiges Format (z.B. HRB12345)');
                return false;
            }
        }

        // Company name validation
        if (fieldName === 'company_name' && value) {
            if (value.length < 2) {
                setFieldError(field, 'Firmenname muss mindestens 2 Zeichen haben');
                return false;
            }
            if (value.length > 100) {
                setFieldError(field, 'Firmenname darf maximal 100 Zeichen haben');
                return false;
            }
        }

        // String length validation for all text fields
        if ((field.type === 'text' || field.type === 'textarea') && value) {
            const maxLength = field.maxLength || 500;
            if (value.length > maxLength) {
                setFieldError(field, `Maximal ${maxLength} Zeichen erlaubt`);
                return false;
            }
        }

        return true;
    }

    function setFieldError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');

        // Remove existing error message
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        // Create new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    function clearFieldError(field) {
        field.classList.remove('is-invalid');

        // Remove error message
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }

        // Add valid class if field has value
        if (field.value.trim()) {
            field.classList.add('is-valid');
        } else {
            field.classList.remove('is-valid');
        }
    }

    // Toast notification function
    function showToast(message, type = 'info', delay = 5000) {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        // Create toast element
        const toastId = 'toast_' + Date.now();
        const toastBg = type === 'success' ? 'bg-success' :
                       type === 'error' ? 'bg-danger' :
                       type === 'warning' ? 'bg-warning' : 'bg-primary';

        const toastHTML = `
            <div id="${toastId}" class="toast ${toastBg} text-white" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header ${toastBg} text-white border-0">
                    <i class="bi bi-${getToastIcon(type)} me-2"></i>
                    <strong class="me-auto">System</strong>
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

    function getToastIcon(type) {
        switch (type) {
            case 'success': return 'check-circle-fill';
            case 'error': return 'exclamation-triangle-fill';
            case 'warning': return 'exclamation-triangle-fill';
            default: return 'info-circle-fill';
        }
    }

    // Initialize form validation on page load
    form.querySelectorAll('input, select, textarea').forEach(field => {
        // Set initial state
        if (field.value.trim()) {
            validateField(field);
        }
    });

    // Handle tab switching with Bootstrap events
    document.querySelectorAll('#companyTabs button[data-bs-toggle="tab"]').forEach((tabButton, index) => {
        tabButton.addEventListener('shown.bs.tab', function () {
            currentTabIndex = index;
            updateNavigationButtons();
        });
    });

    console.log('Company registration form initialized');
});