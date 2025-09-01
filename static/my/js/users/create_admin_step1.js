document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admin-step1-form');
    if (!form) return;

    const submitBtn = document.getElementById('submit-btn');
    const usernameInput = form.querySelector('input[name="username"]');
    const passwordInput = form.querySelector('input[name="password"]');
    const confirmPasswordInput = form.querySelector('input[name="password_confirm"]');

    // Валидация в реальном времени
    if (usernameInput) {
        usernameInput.addEventListener('input', validateUsername);
        usernameInput.addEventListener('blur', validateUsername);
    }

    if (passwordInput) {
        passwordInput.addEventListener('input', validatePassword);
        passwordInput.addEventListener('blur', validatePassword);
    }

    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', validatePasswordConfirm);
        confirmPasswordInput.addEventListener('blur', validatePasswordConfirm);
    }

    // Обработчик отправки формы
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Проводим финальную валидацию
        const isValid = validateUsername() && validatePassword() && validatePasswordConfirm();

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
                        window.location.href = '/users/create-admin/step2/';
                    }, 1500);
                }
            }
        })
        .catch(error => {
            console.error('Ошибка создания пользователя:', error);
            hideProgress();
            showToast('Fehler beim Erstellen des Benutzers', 'error');
        });
    });

    function validateUsername() {
        if (!usernameInput) return false;

        const username = usernameInput.value.trim();
        const regex = /^[a-zA-Z][a-zA-Z0-9_]*$/;

        clearFieldError(usernameInput);

        if (username.length < 3) {
            setFieldError(usernameInput, 'Benutzername muss mindestens 3 Zeichen lang sein');
            return false;
        }

        if (username.length > 50) {
            setFieldError(usernameInput, 'Benutzername darf maximal 50 Zeichen lang sein');
            return false;
        }

        if (!regex.test(username)) {
            setFieldError(usernameInput, 'Benutzername muss mit einem Buchstaben beginnen und darf nur Buchstaben, Zahlen und Unterstriche enthalten');
            return false;
        }

        setFieldSuccess(usernameInput);
        return true;
    }

    function validatePassword() {
        if (!passwordInput) return false;

        const password = passwordInput.value;
        clearFieldError(passwordInput);

        if (password.length < 8) {
            setFieldError(passwordInput, 'Passwort muss mindestens 8 Zeichen lang sein');
            return false;
        }

        if (!/[A-Z]/.test(password)) {
            setFieldError(passwordInput, 'Passwort muss mindestens einen Großbuchstaben enthalten');
            return false;
        }

        if (!/[a-z]/.test(password)) {
            setFieldError(passwordInput, 'Passwort muss mindestens einen Kleinbuchstaben enthalten');
            return false;
        }

        if (!/\d/.test(password)) {
            setFieldError(passwordInput, 'Passwort muss mindestens eine Ziffer enthalten');
            return false;
        }

        setFieldSuccess(passwordInput);

        // Повторно проверяем подтверждение пароля, если оно уже введено
        if (confirmPasswordInput && confirmPasswordInput.value) {
            validatePasswordConfirm();
        }

        return true;
    }

    function validatePasswordConfirm() {
        if (!confirmPasswordInput || !passwordInput) return false;

        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        clearFieldError(confirmPasswordInput);

        if (confirmPassword !== password) {
            setFieldError(confirmPasswordInput, 'Passwörter stimmen nicht überein');
            return false;
        }

        if (confirmPassword.length > 0) {
            setFieldSuccess(confirmPasswordInput);
        }

        return true;
    }

    function setFieldError(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');

        // Удаляем старые сообщения об ошибках
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        // Добавляем новое сообщение об ошибке
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    function setFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');

        // Удаляем сообщения об ошибках
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    function clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');

        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    function showProgress() {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird validiert...';
        }
    }

    function hideProgress() {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i>Weiter zu Schritt 2';
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