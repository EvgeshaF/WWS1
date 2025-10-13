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

    // ✅ ОТКЛЮЧЕНО: HTMX обрабатывает отправку формы
    // Оставляем только валидацию перед отправкой через HTMX
    if (saveAndCloseBtn) {
        // HTMX сам обработает клик через hx-post
    }
    form.addEventListener('submit', e => {
        // Проверяем валидацию, но не отправляем через fetch
        const email = form.querySelector('input[name="email"]');
        const phone = form.querySelector('input[name="phone"]');

        const valid =
            validateRequired(email, 'Haupt-E-Mail ist erforderlich') &&
            validateEmail(email) &&
            validateRequired(phone, 'Haupttelefon ist erforderlich') &&
            validatePhone(phone);

        if (!valid) {
            e.preventDefault();
            showToast('Bitte korrigieren Sie die Fehler im Formular', 'error');
            return false;
        }

        // Добавляем дополнительные контакты в hidden поле перед отправкой HTMX
        const contacts = companyAdditionalContactManager.getAdditionalContactsData();
        const hiddenInput = form.querySelector('input[name="additional_contacts_data"]');
        if (hiddenInput) {
            hiddenInput.value = JSON.stringify(contacts);
        }

        // Валидация прошла - позволяем HTMX отправить форму
    });

    // ✅ УДАЛЕНО: submitForm() больше не используется, HTMX обрабатывает отправку
    // Функция оставлена для совместимости, но не вызывается

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
