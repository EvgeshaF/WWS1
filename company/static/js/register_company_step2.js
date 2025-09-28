document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('company-step2-form');
    if (!form) return;

    const continueBtn = document.getElementById('continue-btn');
    const saveAndCloseBtn = document.getElementById('save-and-close-btn');
    const validationStatus = document.getElementById('validationStatus');
    const validationSuccess = document.getElementById('validationSuccess');
    const validationErrors = document.getElementById('validationErrors');
    const validationErrorText = document.getElementById('validationErrorText');

    const postUrl = form.dataset.url;
    const nextUrl = form.dataset.nextUrl;

    // Поля для валидации
    const requiredFields = [
        'id_commercial_register',
        'id_tax_number',
        'id_vat_id',
        'id_tax_id'
    ];

    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('input', () => {
                validateField(field);
                updateValidationStatus();
            });
            field.addEventListener('blur', () => {
                validateField(field);
                updateValidationStatus();
            });
        }
    });

    if (saveAndCloseBtn) {
        saveAndCloseBtn.addEventListener('click', () => submitForm('save_and_close'));
    }

    form.addEventListener('submit', e => {
        e.preventDefault();
        submitForm('continue');
    });

    function validateField(field) {
        const value = field.value.trim();
        const name = field.name;
        let isValid = true;
        let errorMessage = '';

        field.classList.remove('is-valid', 'is-invalid');
        const existingError = field.closest('.mb-3').querySelector('.field-error');
        if (existingError) existingError.remove();

        if (!value) {
            isValid = false;
            errorMessage = 'Dieses Feld ist erforderlich';
        } else {
            switch (name) {
                case 'commercial_register':
                    if (!/^(HR[AB]\s*\d+|HRA\s*\d+|HRB\s*\d+)$/i.test(value)) {
                        isValid = false;
                        errorMessage = 'Format: HRA12345 oder HRB12345';
                    }
                    break;
                case 'tax_number':
                    if (!/^\d{1,3}\/\d{3}\/\d{4,5}$/.test(value)) {
                        isValid = false;
                        errorMessage = 'Format: 12/345/67890';
                    }
                    break;
                case 'vat_id':
                    if (!/^DE\d{9}$/.test(value)) {
                        isValid = false;
                        errorMessage = 'Format: DE123456789';
                    }
                    break;
                case 'tax_id':
                    if (!/^\d{11}$/.test(value)) {
                        isValid = false;
                        errorMessage = '11-stellige Nummer erforderlich';
                    }
                    break;
            }
        }

        if (isValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'field-error text-danger small mt-1';
            errorDiv.textContent = errorMessage;
            field.closest('.mb-3').appendChild(errorDiv);
        }
        return isValid;
    }

    function updateValidationStatus() {
        let allValid = true;
        let errorCount = 0;

        requiredFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field && (field.classList.contains('is-invalid') || !field.value.trim())) {
                allValid = false;
                errorCount++;
            }
        });

        if (validationStatus) {
            if (allValid) {
                validationStatus.style.display = 'block';
                validationSuccess.style.display = 'block';
                validationErrors.style.display = 'none';
            } else if (errorCount > 0) {
                validationStatus.style.display = 'block';
                validationSuccess.style.display = 'none';
                validationErrors.style.display = 'block';
                validationErrorText.textContent = `${errorCount} Feld(er) müssen korrigiert werden`;
            } else {
                validationStatus.style.display = 'none';
            }
        }

        if (continueBtn) continueBtn.disabled = !allValid;
        if (saveAndCloseBtn) saveAndCloseBtn.disabled = !allValid;
    }

    setTimeout(updateValidationStatus, 100);

    function submitForm(action) {
        let allValid = true;
        requiredFields.forEach(fid => {
            const field = document.getElementById(fid);
            if (field && !validateField(field)) allValid = false;
        });
        if (!allValid) {
            showToast('Bitte füllen Sie alle Pflichtfelder korrekt aus', 'error');
            return;
        }

        const activeBtn = action === 'save_and_close' ? saveAndCloseBtn : continueBtn;
        if (activeBtn) {
            activeBtn.disabled = true;
            activeBtn.innerHTML = action === 'save_and_close'
                ? '<span class="spinner-border spinner-border-sm me-2"></span>Wird gesichert...'
                : '<span class="spinner-border spinner-border-sm me-2"></span>Wird validiert...';
        }

        const formData = new FormData(form);
        formData.append('action', action);

        fetch(postUrl, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'HX-Request': 'true' }
        })
            .then(r => {
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                return r.json();
            })
            .then(data => {
                if (activeBtn) {
                    activeBtn.disabled = false;
                    activeBtn.innerHTML = action === 'save_and_close'
                        ? '<i class="bi bi-check-circle me-1"></i>Sichern & Schließen'
                        : '<i class="bi bi-arrow-right me-1"></i>Weiter';
                }

                if (data.success !== undefined && data.action === 'save_and_close') {
                    if (data.messages) data.messages.forEach(m => showToast(m.text, m.tags, m.delay));
                    if (data.success) {
                        setTimeout(() => window.location.href = data.redirect_url || '/', 1500);
                    }
                    return;
                }

                if (data.messages) {
                    data.messages.forEach(m => showToast(m.text, m.tags, m.delay));
                    const hasSuccess = data.messages.some(m => m.tags === 'success');
                    if (hasSuccess && action === 'continue') {
                        setTimeout(() => window.location.href = nextUrl, 1500);
                    }
                }
            })
            .catch(err => {
                console.error('Form error:', err);
                if (activeBtn) {
                    activeBtn.disabled = false;
                    activeBtn.innerHTML = action === 'save_and_close'
                        ? '<i class="bi bi-check-circle me-1"></i>Sichern & Schließen'
                        : '<i class="bi bi-arrow-right me-1"></i>Weiter';
                }
                showToast('Fehler beim Senden des Formulars', 'error');
            });
    }
});

// Закрытие модалки
function closeModal() {
    if (confirm('Möchten Sie das Fenster schließen? Ungesicherte Änderungen gehen verloren.')) {
        window.location.href = '/';
    }
}

// Тосты
if (typeof window.showToast === 'undefined') {
    window.showToast = function (message, type = 'info', delay = 5000) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top:20px;right:20px;z-index:9999;min-width:300px;';
        toast.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
        document.body.appendChild(toast);
        setTimeout(() => { if (toast.parentNode) toast.remove(); }, delay);
    };
}
