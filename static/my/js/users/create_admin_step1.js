// static/my/js/users/create_admin_step1.js - Updated with correct URLs
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

        // Отправляем запрос через fetch - FIXED URL
        fetch('/users/create-admin/step1/', {
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

// static/my/js/users/create_admin_step2.js - Updated with correct URLs
// (Note: Most of step2 JS is self-contained contact management, main fix is form submission URL)

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admin-step2-form');
    if (!form) return;

    // Инициализируем менеджер контактов
    window.contactManager = new ContactManager();
    contactManager.init();

    // Если есть существующие данные контактов, загружаем их
    const existingContacts = window.initialContactsData || [];
    if (existingContacts.length > 0) {
        contactManager.loadContacts(existingContacts);
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    const firstNameInput = form.querySelector('input[name="first_name"]');
    const lastNameInput = form.querySelector('input[name="last_name"]');
    const salutationSelect = form.querySelector('select[name="salutation"]');

    // Валидация в реальном времени для основных полей
    if (firstNameInput) {
        firstNameInput.addEventListener('blur', () => {
            validateRequired(firstNameInput, 'Vorname ist erforderlich');
        });
    }

    if (lastNameInput) {
        lastNameInput.addEventListener('blur', () => {
            validateRequired(lastNameInput, 'Nachname ist erforderlich');
        });
    }

    // Обработчик отправки формы
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Валидируем основные поля
        const isValid = validateRequired(firstNameInput, 'Vorname ist erforderlich') &&
                        validateRequired(lastNameInput, 'Nachname ist erforderlich') &&
                        validateSalutation();

        // Валидируем контакты
        const contactsValid = contactManager.validateAllContacts();

        if (!isValid || !contactsValid) {
            showToast('Bitte korrigieren Sie die Fehler im Formular', 'error');
            return;
        }

        showProgress();

        // Создаем FormData для отправки
        const formData = new FormData(form);

        // Добавляем данные контактов
        const contactsData = contactManager.getContactsData();
        formData.append('contacts_data', JSON.stringify(contactsData));

        // Отправляем запрос через fetch - FIXED URL
        fetch('/users/create-admin/step2/', {
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

    console.log('Create Admin Step 2 с Contact Manager инициализирован');
});

// static/my/js/users/create_admin_step3.js - Updated with correct URLs
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admin-step3-form');
    if (!form) return;

    const submitBtn = document.getElementById('create-admin-btn');
    const progressContainer = document.getElementById('create-admin-progress-container');
    const progressLabel = document.getElementById('admin-progress-label');
    const progressBar = document.getElementById('admin-progress');
    const creationDetails = document.getElementById('admin-creation-details');
    const currentStep = document.getElementById('current-step');

    let progressInterval = null;
    let creationSteps = [
        'Validierung der Eingaben...',
        'Benutzer wird erstellt...',
        'Berechtigungen werden gesetzt...',
        'Profildaten werden gespeichert...',
        'Sicherheitseinstellungen werden angewendet...',
        'Administrator wird aktiviert...'
    ];
    let currentStepIndex = 0;

    // Обработчик изменения чекбоксов для зависимостей
    const superAdminCheckbox = form.querySelector('input[name="is_super_admin"]');
    const otherPermissions = [
        'can_manage_users',
        'can_manage_database',
        'can_view_logs',
        'can_manage_settings'
    ];

    if (superAdminCheckbox) {
        superAdminCheckbox.addEventListener('change', function() {
            if (this.checked) {
                // При выборе Super Admin автоматически выбираем все остальные права
                otherPermissions.forEach(permName => {
                    const checkbox = form.querySelector(`input[name="${permName}"]`);
                    if (checkbox) {
                        checkbox.checked = true;
                        checkbox.disabled = true;
                    }
                });
            } else {
                // При снятии Super Admin разблокируем остальные права
                otherPermissions.forEach(permName => {
                    const checkbox = form.querySelector(`input[name="${permName}"]`);
                    if (checkbox) {
                        checkbox.disabled = false;
                    }
                });
            }
        });

        // Инициализируем состояние при загрузке
        if (superAdminCheckbox.checked) {
            superAdminCheckbox.dispatchEvent(new Event('change'));
        }
    }

    // Обработчик отправки формы
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Показываем прогресс и блокируем форму
        showProgress();

        // Создаем FormData для отправки
        const formData = new FormData(form);

        // Отправляем запрос через fetch - FIXED URL
        fetch('/users/create-admin/step3/', {
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

                // Если есть успешное сообщение, перенаправляем на главную
                const hasSuccess = data.messages.some(msg => msg.tags === 'success');
                if (hasSuccess) {
                    // Показываем финальный шаг
                    if (currentStep) {
                        currentStep.textContent = 'Administrator erfolgreich erstellt!';
                    }

                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                }
            }
        })
        .catch(error => {
            console.error('Ошибка создания администратора:', error);
            hideProgress();
            showToast('Kritischer Fehler beim Erstellen des Administrators', 'error');
        });
    });

    function showProgress() {
        if (!submitBtn) return;

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird erstellt...';

        if (progressContainer) {
            progressContainer.style.display = 'block';
        }

        if (progressLabel) {
            progressLabel.style.visibility = 'visible';
        }

        if (creationDetails) {
            creationDetails.style.visibility = 'visible';
        }

        let progress = 0;
        currentStepIndex = 0;

        progressInterval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 90) progress = 90;

            if (progressBar) {
                progressBar.style.width = progress + '%';
            }

            // Обновляем текущий шаг
            if (currentStep && currentStepIndex < creationSteps.length - 1) {
                if (progress > (currentStepIndex + 1) * 15) {
                    currentStepIndex++;
                    currentStep.textContent = creationSteps[currentStepIndex];
                }
            }
        }, 400);
    }

    function hideProgress() {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }

        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-person-plus me-1"></i>Administrator erstellen';
        }

        // Завершаем прогресс-бар
        if (progressBar) {
            progressBar.style.width = '100%';
        }

        setTimeout(() => {
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
            if (progressBar) {
                progressBar.style.width = '0%';
            }
        }, 2000);
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