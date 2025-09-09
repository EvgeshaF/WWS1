// static/my/js/companies/register_company.js

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('companyRegistrationForm');
    if (!form) return;

    const submitBtn = document.getElementById('submitFormBtn');
    const resetBtn = document.getElementById('resetFormBtn');
    const progressContainer = document.getElementById('progressContainer');
    const progressLabel = document.getElementById('progressLabel');
    const progressBar = document.getElementById('progressBar');

    let progressInterval = null;
    let validationTimeout = null;

    const progressSteps = [
        'Daten werden validiert...',
        'Prüfe auf Duplikate...',
        'Firma wird erstellt...',
        'Bestätigungs-E-Mail wird vorbereitet...',
        'Registrierung wird abgeschlossen...'
    ];
    let currentStep = 0;

    // ==================== FORM VALIDATION ====================

    // Real-time validation for all form fields
    const formFields = form.querySelectorAll('input, select, textarea');
    formFields.forEach(field => {
        // Validate on blur for better UX
        field.addEventListener('blur', () => {
            validateField(field);
        });

        // Validate on input for immediate feedback (with debounce)
        field.addEventListener('input', () => {
            clearTimeout(validationTimeout);
            validationTimeout = setTimeout(() => {
                validateField(field);
            }, 500);
        });

        // Clear validation on focus
        field.addEventListener('focus', () => {
            clearFieldValidation(field);
        });
    });

    // ==================== FIELD VALIDATION FUNCTIONS ====================

    function validateField(field) {
        const fieldName = field.name;
        const value = field.value.trim();

        // Clear previous validation
        clearFieldValidation(field);

        // Skip validation for optional fields if empty
        if (!field.required && !value) {
            return true;
        }

        // Required field validation
        if (field.required && !value) {
            setFieldError(field, getFieldLabel(field) + ' ist erforderlich');
            return false;
        }

        // Specific field validations
        switch (fieldName) {
            case 'company_name':
                return validateCompanyName(field, value);
            case 'tax_number':
                return validateTaxNumber(field, value);
            case 'vat_number':
                return validateVatNumber(field, value);
            case 'postal_code':
                return validatePostalCode(field, value);
            case 'phone':
            case 'fax':
            case 'contact_phone':
                return validatePhone(field, value);
            case 'email':
            case 'contact_email':
                return validateEmail(field, value);
            case 'website':
                return validateWebsite(field, value);
            default:
                if (value && value.length < 2) {
                    setFieldError(field, 'Mindestens 2 Zeichen erforderlich');
                    return false;
                }
                break;
        }

        // If we get here, the field is valid
        setFieldSuccess(field);
        return true;
    }

    function validateCompanyName(field, value) {
        if (value.length < 2) {
            setFieldError(field, 'Firmenname muss mindestens 2 Zeichen lang sein');
            return false;
        }
        if (value.length > 200) {
            setFieldError(field, 'Firmenname darf maximal 200 Zeichen lang sein');
            return false;
        }
        setFieldSuccess(field);
        return true;
    }

    function validateTaxNumber(field, value) {
        if (!value) return true; // Required validation handled separately

        // Remove all non-numeric characters for validation
        const cleanNumber = value.replace(/[^0-9]/g, '');

        if (cleanNumber.length < 10) {
            setFieldError(field, 'Steuernummer muss mindestens 10 Ziffern enthalten');
            return false;
        }

        if (!/^[0-9\/\-\s]+$/.test(value)) {
            setFieldError(field, 'Ungültiges Format der Steuernummer');
            return false;
        }

        setFieldSuccess(field);
        return true;
    }

    function validateVatNumber(field, value) {
        if (!value) return true; // Optional field

        const vatPattern = /^[A-Z]{2}[0-9A-Z]+$/;
        const cleanValue = value.toUpperCase().replace(/\s/g, '');

        if (!vatPattern.test(cleanValue)) {
            setFieldError(field, 'Ungültiges Format der USt-IdNr. (z.B. DE123456789)');
            return false;
        }

        // German VAT number specific validation
        if (cleanValue.startsWith('DE') && cleanValue.length !== 11) {
            setFieldError(field, 'Deutsche USt-IdNr. muss 11 Zeichen lang sein');
            return false;
        }

        setFieldSuccess(field);
        return true;
    }

    function validatePostalCode(field, value) {
        if (!value) return true;

        if (!/^[0-9]{4,6}$/.test(value)) {
            setFieldError(field, 'PLZ muss 4-6 Ziffern enthalten');
            return false;
        }

        setFieldSuccess(field);
        return true;
    }

    function validatePhone(field, value) {
        if (!value) return field.required ? false : true;

        if (!/^[\+]?[0-9\s\-\(\)]{7,20}$/.test(value)) {
            setFieldError(field, 'Ungültiges Telefonformat');
            return false;
        }

        setFieldSuccess(field);
        return true;
    }

    function validateEmail(field, value) {
        if (!value) return field.required ? false : true;

        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(value)) {
            setFieldError(field, 'Ungültige E-Mail-Adresse');
            return false;
        }

        setFieldSuccess(field);
        return true;
    }

    function validateWebsite(field, value) {
        if (!value) return true; // Optional field

        const urlPattern = /^https?:\/\/.+\..+$/;
        if (!urlPattern.test(value)) {
            setFieldError(field, 'Website muss mit http:// oder https:// beginnen');
            return false;
        }

        setFieldSuccess(field);
        return true;
    }

    // ==================== VALIDATION UI FUNCTIONS ====================

    function setFieldError(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        field.setAttribute('aria-invalid', 'true');

        // Remove existing feedback
        const existingFeedback = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        errorDiv.setAttribute('role', 'alert');
        field.closest('.mb-3').appendChild(errorDiv);

        // Add shake animation
        field.style.animation = 'shake 0.5s ease-in-out';
        setTimeout(() => {
            field.style.animation = '';
        }, 500);
    }

    function setFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        field.setAttribute('aria-invalid', 'false');

        // Remove existing feedback
        const existingFeedback = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
    }

    function clearFieldValidation(field) {
        field.classList.remove('is-invalid', 'is-valid');
        field.removeAttribute('aria-invalid');

        const existingFeedback = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
    }

    function getFieldLabel(field) {
        const label = field.closest('.mb-3').querySelector('label');
        return label ? label.textContent.replace('*', '').trim() : field.name;
    }

    // ==================== FORM SUBMISSION ====================

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Validate all fields
        let isValid = true;
        const fields = form.querySelectorAll('input[required], select[required], textarea[required]');

        fields.forEach(field => {
            if (!validateField(field)) {
                isValid = false;
            }
        });

        // Check terms acceptance
        const termsCheckbox = form.querySelector('input[name="terms_accepted"]');
        if (termsCheckbox && !termsCheckbox.checked) {
            setFieldError(termsCheckbox, 'Sie müssen die Nutzungsbedingungen akzeptieren');
            isValid = false;
        }

        // Cross-field validation
        const emailField = form.querySelector('input[name="email"]');
        const contactEmailField = form.querySelector('input[name="contact_email"]');

        if (emailField && contactEmailField &&
            emailField.value && contactEmailField.value &&
            emailField.value === contactEmailField.value) {
            setFieldError(contactEmailField, 'Unternehmens-E-Mail und Kontakt-E-Mail dürfen nicht identisch sein');
            isValid = false;
        }

        if (!isValid) {
            // Scroll to first error
            const firstError = form.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }

            showToast('Bitte korrigieren Sie die Fehler im Formular', 'error');
            return;
        }

        // Show progress and submit form
        showProgress();
        submitForm();
    });

    function submitForm() {
        const formData = new FormData(form);

        fetch(form.action, {
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
            hideProgress();

            // Handle messages
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(message => {
                    showToast(message.text, message.tags, message.delay);
                });

                // Redirect on success
                const hasSuccess = data.messages.some(msg => msg.tags === 'success');
                if (hasSuccess) {
                    setTimeout(() => {
                        window.location.href = '/companies/registration-success/';
                    }, 2000);
                }
            }
        })
        .catch(error => {
            console.error('Form submission error:', error);
            hideProgress();
            showToast('Ein Fehler ist beim Senden aufgetreten. Bitte versuchen Sie es erneut.', 'error');
        });
    }

    // ==================== PROGRESS HANDLING ====================

    function showProgress() {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.classList.add('btn-loading');
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird registriert...';
        }

        if (progressContainer) {
            progressContainer.style.display = 'block';
        }

        // Add loading class to form
        form.classList.add('form-loading');

        let progress = 0;
        currentStep = 0;

        progressInterval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;

            if (progressBar) {
                progressBar.style.width = progress + '%';
            }

            // Update current step
            if (progressLabel && currentStep < progressSteps.length - 1) {
                if (progress > (currentStep + 1) * 18) {
                    currentStep++;
                    progressLabel.textContent = progressSteps[currentStep];
                }
            }
        }, 400);
    }

    function hideProgress() {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }

        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('btn-loading');
            submitBtn.innerHTML = '<i class="bi bi-building-add"></i>Firma registrieren';
        }

        // Remove loading class from form
        form.classList.remove('form-loading');

        // Complete progress bar
        if (progressBar) {
            progressBar.style.width = '100%';
        }

        if (progressLabel) {
            progressLabel.textContent = 'Registrierung erfolgreich!';
        }

        // Hide progress after delay
        setTimeout(() => {
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
            if (progressBar) {
                progressBar.style.width = '0%';
            }
            if (progressLabel) {
                progressLabel.textContent = 'Daten werden verarbeitet...';
            }
        }, 2000);
    }

    // ==================== FORM RESET ====================

    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            if (confirm('Möchten Sie wirklich alle Eingaben zurücksetzen?')) {
                form.reset();

                // Clear all validation
                formFields.forEach(field => {
                    clearFieldValidation(field);
                });

                // Scroll to top
                window.scrollTo({ top: 0, behavior: 'smooth' });

                showToast('Formular wurde zurückgesetzt', 'info');
            }
        });
    }

    // ==================== TOAST FUNCTION ====================

    function showToast(message, type = 'info', delay = 5000) {
        // Use global toast function if available
        if (typeof window.showToast === 'function') {
            window.showToast(message, type, delay);
        } else {
            // Fallback toast implementation
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
        }
    }

    // ==================== ACCESSIBILITY ENHANCEMENTS ====================

    // Announce validation errors to screen readers
    function announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;

        document.body.appendChild(announcement);

        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    // ==================== AUTO-SAVE (OPTIONAL) ====================

    // Save form data to localStorage for recovery
    function saveFormData() {
        const formData = {};
        formFields.forEach(field => {
            if (field.type === 'checkbox') {
                formData[field.name] = field.checked;
            } else {
                formData[field.name] = field.value;
            }
        });

        try {
            localStorage.setItem('companyRegistrationForm', JSON.stringify(formData));
        } catch (e) {
            console.warn('Could not save form data to localStorage:', e);
        }
    }

    // Restore form data from localStorage
    function restoreFormData() {
        try {
            const savedData = localStorage.getItem('companyRegistrationForm');
            if (savedData) {
                const formData = JSON.parse(savedData);

                formFields.forEach(field => {
                    if (formData.hasOwnProperty(field.name)) {
                        if (field.type === 'checkbox') {
                            field.checked = formData[field.name];
                        } else {
                            field.value = formData[field.name];
                        }
                    }
                });

                // Show notification
                showToast('Gespeicherte Formulardaten wurden wiederhergestellt', 'info');
            }
        } catch (e) {
            console.warn('Could not restore form data from localStorage:', e);
        }
    }

    // Auto-save on input (with debounce)
    let saveTimeout;
    formFields.forEach(field => {
        field.addEventListener('input', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(saveFormData, 2000);
        });
    });

    // Clear saved data on successful submission
    form.addEventListener('submit', () => {
        localStorage.removeItem('companyRegistrationForm');
    });

    // Ask user if they want to restore data on page load
    if (localStorage.getItem('companyRegistrationForm')) {
        setTimeout(() => {
            if (confirm('Es wurden unvollständige Formulardaten gefunden. Möchten Sie diese wiederherstellen?')) {
                restoreFormData();
            } else {
                localStorage.removeItem('companyRegistrationForm');
            }
        }, 1000);
    }

    // ==================== FORM ENHANCEMENT UTILITIES ====================

    // Add character counter to textarea
    const textarea = form.querySelector('textarea[name="description"]');
    if (textarea) {
        const maxLength = 1000;
        const counter = document.createElement('small');
        counter.className = 'form-text text-end';
        counter.textContent = `0 / ${maxLength} Zeichen`;

        textarea.parentNode.appendChild(counter);

        textarea.addEventListener('input', () => {
            const length = textarea.value.length;
            counter.textContent = `${length} / ${maxLength} Zeichen`;

            if (length > maxLength * 0.9) {
                counter.style.color = '#dc3545';
            } else if (length > maxLength * 0.7) {
                counter.style.color = '#ffc107';
            } else {
                counter.style.color = '#6c757d';
            }
        });
    }

    // Add visual feedback for required fields
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        const label = field.closest('.mb-3').querySelector('label');
        if (label && !label.querySelector('.required')) {
            label.innerHTML += '<span class="required">*</span>';
        }
    });

    console.log('Company registration form initialized successfully');
});