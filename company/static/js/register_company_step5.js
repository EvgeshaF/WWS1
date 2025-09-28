document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('company-step5-form');
    if (!form) return;

    const completeRegistrationBtn = document.getElementById('complete-registration-btn');
    const saveBankingAndCloseBtn = document.getElementById('save-banking-and-close-btn');
    const progressContainer = document.getElementById('create-company-progress-container');
    const progressLabel = document.getElementById('company-progress-label');
    const progressBar = document.getElementById('company-progress');
    const creationDetails = document.getElementById('company-creation-details');
    const currentStep = document.getElementById('current-step');

    let progressInterval = null;
    let creationSteps = [
        'Validierung der Eingaben...',
        'Firmendaten werden gespeichert...',
        'Kontakte werden verarbeitet...',
        'Bankdaten werden verarbeitet...',
        'Adresse wird validiert...',
        'Firma wird aktiviert...'
    ];
    let currentStepIndex = 0;

    // Получаем реальные ID полей из data-attributes
    const ibanField = document.getElementById(form.dataset.ibanId);
    const secondaryIbanField = document.getElementById(form.dataset.secondaryIbanId);

    // IBAN валидация
    [ibanField, secondaryIbanField].forEach(field => {
        if (!field) return;
        field.addEventListener('input', () => validateIBAN(field));
        field.addEventListener('blur', () => validateIBAN(field));
    });

    // Кнопка сохранить & закрыть
    if (saveBankingAndCloseBtn) {
        saveBankingAndCloseBtn.addEventListener('click', () => submitForm('save_and_close'));
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        submitForm('complete');
    });

    function validateIBAN(field) {
        const iban = field.value.replace(/\s/g, '').toUpperCase();
        const feedback = field.closest('.mb-3').querySelector('.invalid-feedback') ||
                         field.closest('.mb-3').querySelector('.iban-feedback');
        field.classList.remove('is-valid', 'is-invalid');
        if (feedback) feedback.remove();

        if (!iban) return;

        const regex = /^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$/;
        if (!regex.test(iban)) {
            field.classList.add('is-invalid');
            showFieldError(field, 'Ungültiges IBAN-Format');
            return;
        }

        if (validateIBANChecksum(iban)) {
            field.classList.add('is-valid');
            showFieldSuccess(field, 'IBAN ist gültig');
        } else {
            field.classList.add('is-invalid');
            showFieldError(field, 'IBAN-Prüfsumme ist ungültig');
        }
    }

    function validateIBANChecksum(iban) {
        try {
            const rearranged = iban.slice(4) + iban.slice(0,4);
            let numeric = '';
            for (let c of rearranged) {
                numeric += c >= '0' && c <= '9' ? c : (c.charCodeAt(0) - 55);
            }
            return mod97(numeric) === 1;
        } catch {
            return false;
        }
    }

    function mod97(str) {
        let rem = 0;
        for (let c of str) rem = (rem*10 + parseInt(c)) % 97;
        return rem;
    }

    function showFieldError(field, msg) {
        const div = document.createElement('div');
        div.className = 'invalid-feedback iban-feedback d-block';
        div.textContent = msg;
        field.closest('.mb-3').appendChild(div);
    }

    function showFieldSuccess(field, msg) {
        const div = document.createElement('div');
        div.className = 'valid-feedback iban-feedback d-block';
        div.textContent = msg;
        div.style.color = '#198754';
        field.closest('.mb-3').appendChild(div);
    }

    // --- Отправка формы ---
    function submitForm(action) {
        const activeBtn = action === 'save_and_close' ? saveBankingAndCloseBtn : completeRegistrationBtn;

        if (action === 'complete') showProgress();
        else if (activeBtn) {
            activeBtn.disabled = true;
            activeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Wird gesichert...';
        }

        const formData = new FormData(form);
        formData.append('action', action);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {'X-Requested-With':'XMLHttpRequest','HX-Request':'true'}
        })
        .then(r => r.json())
        .then(data => {
            if (action === 'complete') hideProgress();
            else if (activeBtn) {
                activeBtn.disabled = false;
                activeBtn.innerHTML = '<i class="bi bi-bank me-1"></i>Bankdaten sichern & Schließen';
            }

            if (data.success && data.action === 'save_and_close') {
                if (data.messages) data.messages.forEach(m=>showToast(m.text,m.tags,m.delay));
                setTimeout(()=>window.location.href=data.redirect_url || '/',1500);
                return;
            }

            if (data.messages) {
                data.messages.forEach(m=>showToast(m.text,m.tags,m.delay));
                if (data.messages.some(m=>m.tags==='success') && action==='complete') {
                    if (currentStep) currentStep.textContent='Firma erfolgreich registriert!';
                    setTimeout(()=>window.location.href='/',2000);
                }
            }
        })
        .catch(e=>{
            console.error('Fehler:', e);
            if (action==='complete') hideProgress();
            if (activeBtn) {
                activeBtn.disabled=false;
                activeBtn.innerHTML='<i class="bi bi-bank me-1"></i>Bankdaten sichern & Schließen';
            }
            showToast('Kritischer Fehler beim Registrieren der Firma','error');
        });
    }

    function showProgress() {
        if (!completeRegistrationBtn) return;
        completeRegistrationBtn.disabled=true;
        completeRegistrationBtn.innerHTML='<span class="spinner-border spinner-border-sm me-2"></span>Wird registriert...';
        if (progressContainer) progressContainer.style.display='block';

        let progress=0; currentStepIndex=0;
        progressInterval=setInterval(()=>{
            progress+=Math.random()*10; if(progress>90) progress=90;
            if(progressBar) progressBar.style.width=progress+'%';
            if(currentStep && currentStepIndex<creationSteps.length-1 && progress>(currentStepIndex+1)*15){
                currentStepIndex++; currentStep.textContent=creationSteps[currentStepIndex];
            }
        },400);
    }

    function hideProgress() {
        if(progressInterval) {clearInterval(progressInterval); progressInterval=null;}
        if(completeRegistrationBtn) {completeRegistrationBtn.disabled=false; completeRegistrationBtn.innerHTML='<i class="bi bi-building me-1"></i>{{ text.btn }}';}
        if(progressBar) progressBar.style.width='100%';
        setTimeout(()=>{
            if(progressContainer) progressContainer.style.display='none';
            if(progressBar) progressBar.style.width='0%';
        },2000);
    }

    if(typeof window.showToast==='undefined') {
        window.showToast=(msg,type='info',delay=5000)=>{
            const toast=document.createElement('div');
            toast.className=`alert alert-${type==='error'?'danger':type} alert-dismissible fade show position-fixed`;
            toast.style.cssText='top:20px;right:20px;z-index:9999;min-width:300px;';
            toast.innerHTML=`${msg}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
            document.body.appendChild(toast);
            setTimeout(()=>{if(toast.parentNode) toast.remove();},delay);
        };
    }
});

// Закрытие модального окна
function closeModal() {
    if(confirm('Möchten Sie das Fenster schließen? Ungesicherte Änderungen gehen verloren.')) window.location.href='/';
}
