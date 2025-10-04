// company/static/js/register_company_step1.js - ОБНОВЛЕНО с поддержкой Select2

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('company-step1-form');
    if (!form) return;

    const continueBtn = document.getElementById('continue-btn');
    const saveAndCloseBtn = document.getElementById('save-and-close-btn');

    const postUrl = form.dataset.url;
    const nextUrl = form.dataset.nextUrl;

    // Поля для валидации
    const requiredFields = [
        'id_company_name',
        'id_legal_form',
        'id_ceo_salutation',
        'id_ceo_first_name',
        'id_ceo_last_name'
    ];

    // Валидация полей при изменении
    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            // Обработка обычных полей
            field.addEventListener('input', () => {
                validateField(field);
            });
            field.addEventListener('blur', () => {
                validateField(field);
            });

            // Обработка Select2 полей
            if (field.tagName.toLowerCase() === 'select') {
                $(field).on('select2:select', () => {
                    validateField(field);
                });
                $(field).on('select2:clear', () => {
                    validateField(field);
                });
            }
        }
    });

    // Кнопка "Сохранить и закрыть"
    if (saveAndCloseBtn) {
        saveAndCloseBtn.addEventListener('click', () => submitForm('save_and_close'));
    }

    // Отправка формы
    form.addEventListener('submit', e => {
        e.preventDefault();
        submitForm('continue');
    });

    function validateField(field) {
        const value = field.value ? field.value.trim() : '';
        const name = field.name;
        let isValid = true;
        let errorMessage = '';

        field.classList.remove('is-valid', 'is-invalid');
        const existingError = field.closest('.mb-3').querySelector('.field-error');
        if (existingError) existingError.remove();

        if (!value) {
            isValid = false;
            
            // Специфичные сообщения об ошибках
            switch (name) {
                case 'company_name':
                    errorMessage = 'Firmenname ist erforderlich';
                    break;
                case 'legal_form':
                    errorMessage = 'Rechtsform ist erforderlich';
                    break;
                case 'ceo_salutation':
                    errorMessage = 'Anrede ist erforderlich';
                    break;
                case 'ceo_first_name':
                    errorMessage = 'Vorname ist erforderlich';
                    break;
                case 'ceo_last_name':
                    errorMessage = 'Nachname ist erforderlich';
                    break;
                default:
                    errorMessage = 'Dieses Feld ist erforderlich';
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

    function submitForm(action) {
        // Валидируем все обязательные поля
        let allValid = true;
        requiredFields.forEach(fid => {
            const field = document.getElementById(fid);
            if (field && !validateField(field)) allValid = false;
        });

        if (!allValid) {
            showToast('Bitte füllen Sie alle Pflichtfelder aus', 'error');
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

                // Обрабатываем ответ для "save_and_close"
                if (data.success !== undefined && data.action === 'save_and_close') {
                    if (data.messages) data.messages.forEach(m => showToast(m.text, m.tags, m.delay));
                    if (data.success) {
                        setTimeout(() => window.location.href = data.redirect_url || '/', 1500);
                    }
                    return;
                }

                // Обрабатываем обычный ответ
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

// Функция закрытия модального окна
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