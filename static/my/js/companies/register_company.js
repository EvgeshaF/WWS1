// static/my/js/companies/register_company_modal.js - Modal Company Registration with Tabs

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
    const postalCodeField = document.getElementById('{{ form.postal_code.id_for_label }}');
    if (postalCodeField) {
        postalCodeField.addEventListener('input', function() {
            const value = this.value.replace(/\D/g, ''); // Nur Zahlen
            this.value = value.substring(0, 5); // Max 5 Stellen
        });
    }

    // VAT ID formatting
    const vatIdField = document.getElementById('{{ form.vat_id.id_for_label }}');
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
        const fieldId = field.id;

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
                setFieldError(field,