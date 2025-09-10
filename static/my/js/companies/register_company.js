// static/my/js/companies/register_company.js - MODAL VERSION

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

    // Add modal-specific enhancements
    const modal = document.getElementById('companyRegistrationModal');
    const modalBody = modal?.querySelector('.modal-body');

    // Smooth scrolling in modal for validation errors
    function scrollToError(element) {
        if (modalBody && element) {
            const elementRect = element.getBoundingClientRect();
            const modalRect = modalBody.getBoundingClientRect();
            const scrollTop = modalBody.scrollTop;
            const targetScroll = scrollTop + (elementRect.top - modalRect.top) - 20;

            modalBody.scrollTo({
                top: targetScroll,
                behavior: 'smooth'
            });
        }
    }

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
            // Scroll to first error in modal
            const firstError = form.querySelector('.is-invalid');
            if (firstError) {
                scrollToError(firstError);
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

            const contentType = response.headers.get('Content-Type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            } else {
                // Если не JSON, возможно это HTML редирект
                return response.text().then(text => {
                    // Проверяем заголовки для редиректа
                    const redirectHeader = response.headers.get('HX-Redirect');
                    if (redirectHeader) {
                        return { redirect: redirectHeader };
                    }
                    throw new Error('Unexpected response format');
                });
            }
        })
        .then(data => {
            hideProgress();

            // Обрабатываем JSON ответ с сообщениями
            if (data.messages && Array.isArray(data.messages)) {
                data.messages.forEach(message => {
                    showToast(message.text, message.tags, message.delay || 5000);
                });

                // Если есть успешное сообщение, перенаправляем через короткое время
                const hasSuccess = data.messages.some(msg => msg.tags === 'success');
                if (hasSuccess) {
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                }
            }

            // Обрабатываем редирект
            if (data.redirect) {
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1500);
            }
        })
        .catch(error => {
            console.error('Fehler bei der Firmenregistrierung:', error);
            hideProgress();

            if (error.message.includes('Unexpected response format')) {
                showToast('Firma wurde möglicherweise erfolgreich registriert. Seite wird aktualisiert...', 'info');
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                showToast('Fehler beim Registrieren der Firma: ' + error.message, 'error');
            }
        });
    }

    // ==================== PROGRESS FUNCTIONS ====================

    function showProgress() {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird registriert...';
        }

        if (progressContainer) {
            progressContainer.style.display = 'block';
        }

        if (progressLabel && progressBar) {
            let progress = 0;
            currentStep = 0;

            progressInterval = setInterval(() => {
                progress += Math.random() * 10;
                if (progress > 90) progress = 90;

                progressBar.style.width = progress + '%';

                // Update step label
                if (currentStep < progressSteps.length - 1) {
                    if (progress > (currentStep + 1) * 18) {
                        currentStep++;
                        progressLabel.textContent = progressSteps[currentStep];
                    }
                }
            }, 300);
        }
    }

    function hideProgress() {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }

        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-building-add me-1"></i>Firma registrieren';
        }

        // Complete progress bar
        if (progressBar) {
            progressBar.style.width = '100%';
        }

        if (progressLabel) {
            progressLabel.textContent = 'Registrierung abgeschlossen!';
        }

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

    // ==================== RESET FORM ====================

    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            if (confirm('Möchten Sie wirklich alle Eingaben zurücksetzen?')) {
                form.reset();

                // Clear all validation states
                formFields.forEach(field => {
                    clearFieldValidation(field);
                });

                // Scroll to top of modal
                if (modalBody) {
                    modalBody.scrollTo({
                        top: 0,
                        behavior: 'smooth'
                    });
                }

                showToast('Formular wurde zurückgesetzt', 'info');
            }
        });
    }

    // ==================== GLOBAL TOAST FALLBACK ====================

    // Global toast function fallback if not already defined
    if (typeof window.showToast === 'undefined') {
        window.showToast = function(message, type = 'info', delay = 5000) {
            // Create simple toast if no global system exists
            const toast = document.createElement('div');
            toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
            toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            toast.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;

            document.body.appendChild(toast);

            // Auto remove after delay
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, delay);
        };
    }

    console.log('✅ Company Registration Form (Modal Version) initialized');
});