// Закрытие модалки
function closeModal() {
    if (confirm('Möchten Sie das Fenster schließen? Ungesicherte Änderungen gehen verloren.')) {
        window.location.href = '/';
    }
}

// Select2 инициализируется в template (register_company_step3.html)

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('company-step3-form');
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
                console.error('Ошибка отправки формы:', err);
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