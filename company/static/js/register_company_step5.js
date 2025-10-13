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

    // НОВОЕ: Получаем поля для валидации
    const requiredFields = {
        'bank_name': 'Name der Bank',
        'iban': 'IBAN',
        'bic': 'BIC/SWIFT',
        'account_holder': 'Kontoinhaber'
    };

    // Получаем реальные ID полей из data-attributes
    const ibanField = document.getElementById(form.dataset.ibanId);
    const secondaryIbanField = document.getElementById(form.dataset.secondaryIbanId);

    // НОВОЕ: Валидация обязательных полей
    Object.keys(requiredFields).forEach(fieldName => {
        const field = document.getElementById(`id_${fieldName}`);
        if (field) {
            field.addEventListener('input', () => validateRequiredField(field, requiredFields[fieldName]));
            field.addEventListener('blur', () => validateRequiredField(field, requiredFields[fieldName]));
        }
    });

    // IBAN валидация (существующая логика расширена)
    [ibanField, secondaryIbanField].forEach(field => {
        if (!field) return;
        field.addEventListener('input', () => validateIBAN(field));
        field.addEventListener('blur', () => validateIBAN(field));
    });

    // ✅ ОТКЛЮЧЕНО: HTMX обрабатывает отправку формы
    // Оставляем только валидацию перед отправкой через HTMX
    if (saveBankingAndCloseBtn) {
        // HTMX сам обработает клик через hx-post
    }

    form.addEventListener('submit', function (e) {
        // Проверяем валидацию перед отправкой через HTMX
        const validation = validateAllRequiredFields();

        if (!validation.allValid) {
            e.preventDefault();
            showToast('Bitte füllen Sie alle Pflichtfelder korrekt aus', 'error');

            // Показываем первое поле с ошибкой
            const firstErrorField = form.querySelector('.is-invalid');
            if (firstErrorField) {
                firstErrorField.focus();
                firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return false;
        }

        // Валидация прошла - позволяем HTMX отправить форму
        // HTMX обработчик покажет прогресс и перенаправит
    });

    // НОВАЯ ФУНКЦИЯ: Валидация обязательных полей
    function validateRequiredField(field, fieldLabel) {
        const value = field.value.trim();
        clearFieldValidation(field);

        if (!value) {
            setFieldError(field, `${fieldLabel} ist erforderlich`);
            return false;
        }

        setFieldSuccess(field);
        return true;
    }

    // НОВАЯ ФУНКЦИЯ: Валидация всех обязательных полей
    function validateAllRequiredFields() {
        let allValid = true;
        const errors = [];

        Object.entries(requiredFields).forEach(([fieldName, fieldLabel]) => {
            const field = document.getElementById(`id_${fieldName}`);
            if (field) {
                const isValid = validateRequiredField(field, fieldLabel);
                if (!isValid) {
                    allValid = false;
                    errors.push(`${fieldLabel} ist erforderlich`);
                }
            }
        });

        // Дополнительная валидация IBAN и BIC форматов
        const ibanField = document.getElementById('id_iban');
        if (ibanField && ibanField.value.trim()) {
            const isValidIban = validateIBAN(ibanField);
            if (!isValidIban) {
                allValid = false;
                errors.push('IBAN-Format ist ungültig');
            }
        }

        const bicField = document.getElementById('id_bic');
        if (bicField && bicField.value.trim()) {
            const bicValue = bicField.value.trim().toUpperCase();
            if (!/^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$/.test(bicValue)) {
                setFieldError(bicField, 'Ungültiges BIC-Format (z.B. DEUTDEFF)');
                allValid = false;
                errors.push('BIC-Format ist ungültig');
            } else {
                setFieldSuccess(bicField);
            }
        }

        return { allValid, errors };
    }

    function validateIBAN(field) {
        const iban = field.value.replace(/\s/g, '').toUpperCase();
        const feedback = field.closest('.mb-3').querySelector('.invalid-feedback') ||
                         field.closest('.mb-3').querySelector('.iban-feedback');
        clearFieldValidation(field);

        if (!iban) {
            // Для основного IBAN проверяем обязательность
            if (field.id === 'id_iban') {
                setFieldError(field, 'IBAN ist erforderlich');
                return false;
            }
            return true; // Для вторичного IBAN пустое значение допустимо
        }

        const regex = /^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$/;
        if (!regex.test(iban)) {
            setFieldError(field, 'Ungültiges IBAN-Format');
            return false;
        }

        if (validateIBANChecksum(iban)) {
            setFieldSuccess(field, 'IBAN ist gültig');
            return true;
        } else {
            setFieldError(field, 'IBAN-Prüfsumme ist ungültig');
            return false;
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

    function setFieldError(field, msg) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');

        clearFieldFeedback(field);

        const div = document.createElement('div');
        div.className = 'invalid-feedback iban-feedback d-block';
        div.textContent = msg;
        field.closest('.mb-3').appendChild(div);
    }

    function setFieldSuccess(field, msg = '') {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');

        clearFieldFeedback(field);

        if (msg) {
            const div = document.createElement('div');
            div.className = 'valid-feedback iban-feedback d-block';
            div.textContent = msg;
            div.style.color = '#198754';
            field.closest('.mb-3').appendChild(div);
        }
    }

    function clearFieldValidation(field) {
        field.classList.remove('is-invalid', 'is-valid');
        clearFieldFeedback(field);
    }

    function clearFieldFeedback(field) {
        const feedback = field.closest('.mb-3').querySelector('.iban-feedback');
        if (feedback) feedback.remove();
    }

    // ✅ УДАЛЕНО: submitForm() больше не используется, HTMX обрабатывает отправку
    // Прогресс-бар и редирект обрабатываются через HTMX events

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
        if(completeRegistrationBtn) {
            completeRegistrationBtn.disabled=false;
            completeRegistrationBtn.innerHTML='<i class="bi bi-building me-1"></i>Firma registrieren';
        }
        if(progressBar) progressBar.style.width='100%';
        setTimeout(()=>{
            if(progressContainer) progressContainer.style.display='none';
            if(progressBar) progressBar.style.width='0%';
        },2000);
    }

    // НОВОЕ: Автоматическая валидация при загрузке страницы
    setTimeout(() => {
        validateAllRequiredFields();
    }, 500);

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