document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admin-step2-form');
    if (!form) return;

    const submitBtn = form.querySelector('button[type="submit"]');
    const emailInput = form.querySelector('input[name="email"]');
    const phoneInput = form.querySelector('input[name="phone"]');
    const firstNameInput = form.querySelector('input[name="first_name"]');
    const lastNameInput = form.querySelector('input[name="last_name"]');
    const salutationSelect = form.querySelector('select[name="salutation"]');

    // Валидация в реальном времени
    if (emailInput) {
        emailInput.addEventListener('input', validateEmail);
        emailInput.addEventListener('blur', validateEmail);
    }

    if (phoneInput) {
        phoneInput.addEventListener('input', validatePhone);
        phoneInput.addEventListener('blur', validatePhone);
    }

    if (firstNameInput) {
        firstNameInput.addEventListener('blur', validateRequired.bind(null, firstNameInput, 'Vorname ist erforderlich'));
    }

    if (lastNameInput) {
        lastNameInput.addEventListener('blur', validateRequired.bind(null, lastNameInput, 'Nachname ist erforderlich'));
    }

    // Обработчик отправки формы
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Проводим финальную валидацию
        const isValid = validateEmail() &&
                        validatePhone() &&
                        validateRequired(firstNameInput, 'Vorname ist erforderlich') &&
                        validateRequired(lastNameInput, 'Nachname ist erforderlich') &&
                        validateSalutation();

        if (!isValid) {
            showToast('Bitte korrigieren Sie die Fehler im Formular', 'error');
            return;
        }

        showProgress();

        // Создаем FormData для отправки
        const formData = new FormData(form);

        // Отправляем запрос через fetch
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

            // Обрабатываем сообщения
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(message => {
                    showToast(message.text, message.tags, message.delay);
                });

                // Если есть успешное сообщение, перенаправляем через короткое время
                const hasSuccess = data.messages.some(msg => msg.tags === 'success');
                if (hasSuccess) {
                    setTimeout(() => {
                        window.location.href = '/users/create-admin/step3/';
                    }, 1500);
                }
            }
        })
        .catch(error => {
            console.error('Ошибка сохранения профиля:', error);
            hideProgress();
            showToast('Fehler beim Speichern des Profils', 'error');
        });
    });

    function validateSalutation() {
        if (!salutationSelect) return true;

        const value = salutationSelect.value;
        clearFieldError(salutationSelect);

        if (!value) {
            setFieldError(salutationSelect, 'Anrede ist erforderlich');
            return false;
        }

        setFieldSuccess(salutationSelect);
        return true;
    }

    function validateEmail() {
        if (!emailInput) return true;

        const email = emailInput.value.trim();
        clearFieldError(emailInput);

        if (email === '') {
            return true; // Пустой email допустим
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) {
            setFieldError(emailInput, 'Ungültiges E-Mail-Format');
            return false;
        }

        setFieldSuccess(emailInput);
        return true;
    }

    function validatePhone() {
        if (!phoneInput) return true;

        const phone = phoneInput.value.trim();
        clearFieldError(phoneInput);

        if (phone === '') {
            return true; // Пустой телефон допустим
        }

        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{7,20}$/;

        if (!phoneRegex.test(phone)) {
            setFieldError(phoneInput, 'Ungültiges Telefonformat');
            return false;
        }

        setFieldSuccess(phoneInput);
        return true;
    }

    function validateRequired(field, errorMessage) {
        if (!field) return false;

        const value = field.value.trim();
        clearFieldError(field);

        if (value === '') {
            setFieldError(field, errorMessage);
            return false;
        }

        if (value.length > 50) {
            setFieldError(field, 'Maximal 50 Zeichen erlaubt');
            return false;
        }

        setFieldSuccess(field);
        return true;
    }

    function setFieldError(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');

        // Удаляем старые сообщения об ошибках
        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        // Добавляем новое сообщение об ошибке
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        field.closest('.mb-3').appendChild(errorDiv);
    }

    function setFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');

        // Удаляем сообщения об ошибках
        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    function clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');

        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    function showProgress() {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird gespeichert...';
        }
    }

    function hideProgress() {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i>Weiter zu Schritt 3';
        }
    }

    // Глобальная функция для показа тостов (если не определена)
    if (typeof window.showToast === 'undefined') {
        window.showToast = function(message, type = 'info', delay = 5000) {
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
        };
    }
});