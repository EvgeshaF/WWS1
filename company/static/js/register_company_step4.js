// Закрытие модалки
function closeModal() {
    if (confirm('Möchten Sie das Fenster schließen? Ungesicherte Änderungen gehen verloren.')) {
        window.location.href = '/';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('company-step4-form');
    if (!form) return;

    const continueBtn = document.getElementById('continue-btn');
    const saveAndCloseBtn = document.getElementById('save-and-close-btn');
    const postUrl = form.dataset.url;
    const nextUrl = form.dataset.nextUrl;

    if (saveAndCloseBtn) {
        saveAndCloseBtn.addEventListener('click', () => submitForm('save_and_close'));
    }
    form.addEventListener('submit', e => {
        e.preventDefault();
        submitForm('continue');
    });

    function submitForm(action) {
        const email = form.querySelector('input[name="email"]');
        const phone = form.querySelector('input[name="phone"]');

        const valid =
            validateRequired(email, 'Haupt-E-Mail ist erforderlich') &&
            validateEmail(email) &&
            validateRequired(phone, 'Haupttelefon ist erforderlich') &&
            validatePhone(phone);

        if (!valid) {
            showToast('Bitte korrigieren Sie die Fehler im Formular', 'error');
            return;
        }

        const activeBtn = action === 'save_and_close' ? saveAndCloseBtn : continueBtn;
        if (activeBtn) {
            activeBtn.disabled = true;
            activeBtn.innerHTML =
                action === 'save_and_close'
                    ? '<span class="spinner-border spinner-border-sm me-2"></span>Wird gesichert...'
                    : '<span class="spinner-border spinner-border-sm me-2"></span>Wird gespeichert...';
        }

        const formData = new FormData(form);
        const contacts = companyAdditionalContactManager.getAdditionalContactsData();
        formData.append('additional_contacts_data', JSON.stringify(contacts));
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
                    activeBtn.innerHTML =
                        action === 'save_and_close'
                            ? '<i class="bi bi-check-circle me-1"></i>Sichern & Schließen'
                            : '<i class="bi bi-arrow-right me-1"></i>Weiter';
                }

                if (data.success !== undefined && data.action === 'save_and_close') {
                    if (data.messages) data.messages.forEach(m => showToast(m.text, m.tags, m.delay));
                    if (data.success) {
                        setTimeout(() => (window.location.href = data.redirect_url || '/'), 1500);
                    }
                    return;
                }

                if (data.messages) {
                    data.messages.forEach(m => showToast(m.text, m.tags, m.delay));
                    const hasSuccess = data.messages.some(m => m.tags === 'success');
                    if (hasSuccess && action === 'continue') {
                        setTimeout(() => (window.location.href = nextUrl), 1500);
                    }
                }
            })
            .catch(err => {
                console.error('Fehler:', err);
                if (activeBtn) {
                    activeBtn.disabled = false;
                    activeBtn.innerHTML =
                        action === 'save_and_close'
                            ? '<i class="bi bi-check-circle me-1"></i>Sichern & Schließen'
                            : '<i class="bi bi-arrow-right me-1"></i>Weiter';
                }
                showToast('Fehler beim Speichern der Kontaktdaten', 'error');
            });
    }

    // Валидация
    function validateRequired(field, msg) {
        if (!field) return false;
        const val = field.value.trim();
        clearFieldError(field);
        if (!val) {
            setFieldError(field, msg);
            return false;
        }
        setFieldSuccess(field);
        return true;
    }

    function validateEmail(field) {
        if (!field) return false;
        const val = field.value.trim();
        clearFieldError(field);
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
            setFieldError(field, 'Ungültiges E-Mail-Format');
            return false;
        }
        setFieldSuccess(field);
        return true;
    }

    function validatePhone(field) {
        if (!field) return false;
        const val = field.value.trim();
        clearFieldError(field);
        if (!/^[\+]?[0-9\s\-\(\)]{7,20}$/.test(val)) {
            setFieldError(field, 'Ungültiges Telefonformat');
            return false;
        }
        setFieldSuccess(field);
        return true;
    }

    function setFieldError(field, msg) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        const err = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (err) err.remove();
        const div = document.createElement('div');
        div.className = 'invalid-feedback d-block';
        div.textContent = msg;
        field.closest('.mb-3').appendChild(div);
    }

    function setFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        const err = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (err) err.remove();
    }

    function clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');
        const err = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (err) err.remove();
    }
});

// Toast
if (typeof window.showToast === 'undefined') {
    window.showToast = function (msg, type = 'info', delay = 5000) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top:20px;right:20px;z-index:9999;min-width:300px;';
        toast.innerHTML = `${msg}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), delay);
    };
}
