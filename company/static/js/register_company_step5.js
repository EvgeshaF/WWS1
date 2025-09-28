// Закрытие модалки
function closeModal() {
    if (confirm('Möchten Sie das Fenster schließen? Ungesicherte Änderungen gehen verloren.')) {
        window.location.href = '/';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('company-step5-form');
    if (!form) return;

    const completeBtn = document.getElementById('complete-registration-btn');
    const saveCloseBtn = document.getElementById('save-banking-and-close-btn');
    const progressContainer = document.getElementById('create-company-progress-container');
    const progressBar = document.getElementById('company-progress');
    const currentStep = document.getElementById('current-step');

    const postUrl = form.dataset.url;
    const redirectUrl = form.dataset.redirectUrl;

    let progressInterval = null;
    const steps = [
        'Validierung der Eingaben...',
        'Firmendaten werden gespeichert...',
        'Kontakte werden verarbeitet...',
        'Bankdaten werden verarbeitet...',
        'Adresse wird validiert...',
        'Firma wird aktiviert...'
    ];
    let stepIndex = 0;

    // Валидация IBAN полей
    [form.querySelector('#id_iban'), form.querySelector('#id_secondary_iban')].forEach(field => {
        if (!field) return;
        field.addEventListener('input', () => validateIBAN(field));
        field.addEventListener('blur', () => validateIBAN(field));
    });

    if (saveCloseBtn) {
        saveCloseBtn.addEventListener('click', () => submitForm('save_and_close'));
    }
    form.addEventListener('submit', e => {
        e.preventDefault();
        submitForm('complete');
    });

    function submitForm(action) {
        const activeBtn = action === 'save_and_close' ? saveCloseBtn : completeBtn;

        if (action === 'complete') {
            showProgress();
        } else {
            activeBtn.disabled = true;
            activeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Wird gesichert...';
        }

        const data = new FormData(form);
        data.append('action', action);

        fetch(postUrl, {
            method: 'POST',
            body: data,
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'HX-Request': 'true' }
        })
            .then(r => r.json())
            .then(resp => {
                if (action === 'complete') {
                    hideProgress();
                } else {
                    activeBtn.disabled = false;
                    activeBtn.innerHTML = '<i class="bi bi-bank me-1"></i> Bankdaten sichern & Schließen';
                }

                if (resp.messages) {
                    resp.messages.forEach(m => showToast(m.text, m.tags, m.delay));
                }

                if (resp.success) {
                    setTimeout(() => {
                        window.location.href = resp.redirect_url || redirectUrl;
                    }, 2000);
                }
            })
            .catch(err => {
                console.error('Fehler:', err);
                if (action === 'complete') {
                    hideProgress();
                } else {
                    activeBtn.disabled = false;
                    activeBtn.innerHTML = '<i class="bi bi-bank me-1"></i> Bankdaten sichern & Schließen';
                }
                showToast('Fehler beim Speichern der Bankdaten', 'error');
            });
    }

    // IBAN проверка
    function validateIBAN(field) {
        const iban = field.value.replace(/\s/g, '').toUpperCase();
        field.classList.remove('is-valid', 'is-invalid');
        removeFeedback(field);

        if (!iban) return;

        if (!/^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$/.test(iban)) {
            field.classList.add('is-invalid');
            showFeedback(field, 'Ungültiges IBAN-Format', 'invalid');
            return;
        }
        if (ibanChecksum(iban)) {
            field.classList.add('is-valid');
            showFeedback(field, 'IBAN ist gültig', 'valid');
        } else {
            field.classList.add('is-invalid');
            showFeedback(field, 'IBAN-Prüfsumme ist ungültig', 'invalid');
        }
    }

    function ibanChecksum(iban) {
        const rearr = iban.slice(4) + iban.slice(0, 4);
        let num = '';
        for (let c of rearr) num += /\d/.test(c) ? c : (c.charCodeAt(0) - 55);
        return mod97(num) === 1;
    }

    function mod97(str) {
        let rem = 0;
        for (let d of str) rem = (rem * 10 + +d) % 97;
        return rem;
    }

    function showFeedback(field, msg, type) {
        const div = document.createElement('div');
        div.className = (type === 'valid' ? 'valid-feedback' : 'invalid-feedback') + ' d-block';
        div.textContent = msg;
        field.closest('.mb-3').appendChild(div);
    }
    function removeFeedback(field) {
        field.closest('.mb-3').querySelectorAll('.valid-feedback, .invalid-feedback').forEach(el => el.remove());
    }

    // Прогресс
    function showProgress() {
        completeBtn.disabled = true;
        completeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Wird registriert...';
        progressContainer.style.display = 'block';

        let prog = 0;
        stepIndex = 0;
        progressInterval = setInterval(() => {
            prog += Math.random() * 10;
            if (prog > 90) prog = 90;
            progressBar.style.width = prog + '%';
            if (currentStep && stepIndex < steps.length - 1 && prog > (stepIndex + 1) * 15) {
                currentStep.textContent = steps[++stepIndex];
            }
        }, 400);
    }
    function hideProgress() {
        clearInterval(progressInterval);
        completeBtn.disabled = false;
        completeBtn.innerHTML = '<i class="bi bi-building me-1"></i> Registrierung abschließen';
        progressBar.style.width = '100%';
        setTimeout(() => {
            progressContainer.style.display = 'none';
            progressBar.style.width = '0%';
        }, 1500);
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
