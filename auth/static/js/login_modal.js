// auth/static/js/auth_login_modal.js - JavaScript для модального окна авторизации

(function() {
    'use strict';

    // КРИТИЧЕСКАЯ ПРОВЕРКА: НЕ инициализируем на страницах создания админа
    var currentPath = window.location.pathname;
    var isAdminCreationPage = currentPath.includes('/users/create-admin/') ||
                               currentPath.includes('create-admin') ||
                               (window.isAdminCreationPage === true);

    if (isAdminCreationPage) {
        console.log('🚫 Auth Login Modal System ОТКЛЮЧЕН на странице:', currentPath);

        document.addEventListener('DOMContentLoaded', function() {
            var modal = document.getElementById('authLoginModal');
            var loader = document.getElementById('authModalLoader');

            if (modal) {
                modal.remove();
                console.log('🗑️ Auth login modal удален');
            }

            if (loader) {
                loader.remove();
                console.log('🗑️ Auth modal loader удален');
            }

            var allBackdrops = document.querySelectorAll('.modal-backdrop');
            allBackdrops.forEach(function(el) {
                el.remove();
            });
        });

        return;
    }

    console.log('🔐 Auth Login Modal System загружен на странице:', currentPath);

    // Конфигурация
    const CONFIG = {
        maxAttempts: 5,
        lockoutTime: 15 * 60 * 1000,
        storageKeys: {
            attempts: 'auth_login_attempts',
            lockout: 'auth_login_lockout',
            username: 'auth_login_username'
        }
    };

    class AuthLoginModal {
        constructor() {
            this.modal = null;
            this.modalInstance = null;
            this.form = null;
            this.usernameInput = null;
            this.passwordInput = null;
            this.togglePasswordBtn = null;
            this.submitBtn = null;
            this.loader = null;
            this.attemptsAlert = null;
            this.isSubmitting = false;
            this.currentAttempts = 0;

            this.init();
        }

        init() {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setup());
            } else {
                this.setup();
            }
        }

        setup() {
            console.log('🔧 Инициализация Auth Login Modal');

            this.modal = document.getElementById('authLoginModal');
            if (!this.modal) {
                console.warn('⚠️ Модальное окно #authLoginModal не найдено');
                return;
            }

            this.form = document.getElementById('authLoginForm');
            this.usernameInput = document.getElementById('authUsername');
            this.passwordInput = document.getElementById('authPassword');
            this.togglePasswordBtn = document.getElementById('authTogglePassword');
            this.submitBtn = document.getElementById('authSubmitBtn');
            this.loader = document.getElementById('authModalLoader');
            this.attemptsAlert = document.getElementById('authAttemptsAlert');

            if (!this.form || !this.submitBtn) {
                console.error('❌ Форма или кнопка входа не найдены');
                return;
            }

            this.bindEvents();
            this.checkAuthStatus();
            this.restoreFormData();

            console.log('✅ Auth Login Modal инициализирован');
        }

        checkAuthStatus() {
            if (window.isAuthenticated === false && window.requiresAuth === true) {
                setTimeout(() => {
                    this.showModal();
                }, 1000);
            }
        }

        bindEvents() {
            // Обработка отправки формы
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));

            // Toggle password visibility
            if (this.togglePasswordBtn) {
                this.togglePasswordBtn.addEventListener('click', () => this.togglePasswordVisibility());
            }

            // Валидация в реальном времени
            if (this.usernameInput) {
                this.usernameInput.addEventListener('input', () => this.validateField(this.usernameInput));
                this.usernameInput.addEventListener('blur', () => this.validateField(this.usernameInput));
            }

            if (this.passwordInput) {
                this.passwordInput.addEventListener('input', () => this.validateField(this.passwordInput));
                this.passwordInput.addEventListener('blur', () => this.validateField(this.passwordInput));
            }

            // События модального окна
            this.modal.addEventListener('shown.bs.modal', () => {
                if (this.usernameInput && !this.usernameInput.value.trim()) {
                    this.usernameInput.focus();
                } else if (this.passwordInput) {
                    this.passwordInput.focus();
                }
                this.currentAttempts = this.getStoredAttempts();
                this.updateAttemptsDisplay();
            });

            this.modal.addEventListener('hidden.bs.modal', () => {
                this.saveFormData();
            });

            // Ctrl+Enter для быстрой отправки
            this.form.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    e.preventDefault();
                    this.handleSubmit(e);
                }
            });
        }

        async handleSubmit(e) {
            e.preventDefault();

            if (this.isSubmitting) {
                console.log('⏳ Форма уже отправляется');
                return;
            }

            if (this.isLockedOut()) {
                this.showLockoutMessage();
                return;
            }

            console.log('📤 Отправка формы входа');

            if (!this.validateForm()) {
                console.warn('⚠️ Форма не прошла валидацию');
                return;
            }

            this.showLoader();
            this.isSubmitting = true;

            try {
                const formData = new FormData(this.form);

                const response = await fetch(this.form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });

                console.log('📨 Получен ответ:', response.status);

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    const text = await response.text();
                    console.error('Получен не-JSON ответ:', text);
                    throw new Error('Server returned non-JSON response');
                }

                const data = await response.json();
                console.log('📊 Данные ответа:', data);

                if (data.success) {
                    this.handleLoginSuccess(data);
                } else {
                    this.handleLoginError(data);
                }

            } catch (error) {
                console.error('❌ Ошибка входа:', error);
                this.handleNetworkError(error);
            } finally {
                this.hideLoader();
                this.isSubmitting = false;
            }
        }

        handleLoginSuccess(data) {
            console.log('✅ Успешный вход');

            this.clearAttempts();
            this.clearFormData();

            if (typeof window.showToast === 'function') {
                window.showToast(data.message || 'Erfolgreich angemeldet', 'success');
            }

            this.hideModalWithSuccess();

            setTimeout(() => {
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    window.location.reload();
                }
            }, 1000);
        }

        handleLoginError(data) {
            console.warn('⚠️ Ошибка входа:', data.message);

            this.currentAttempts++;
            this.storeAttempts();
            this.updateAttemptsDisplay();

            const message = data.message || 'Ungültiger Benutzername oder Passwort';
            this.showFieldError('password', message);

            if (typeof window.showToast === 'function') {
                window.showToast(message, 'error');
            }

            if (this.currentAttempts >= CONFIG.maxAttempts) {
                this.setLockout();
                this.showLockoutMessage();
            } else {
                const remainingAttempts = CONFIG.maxAttempts - this.currentAttempts;
                this.showRemainingAttempts(remainingAttempts);
            }

            if (this.passwordInput) {
                this.passwordInput.value = '';
                this.passwordInput.focus();
            }
        }

        handleNetworkError(error) {
            console.error('🌐 Сетевая ошибка:', error);

            let message = 'Verbindungsfehler. Bitte versuchen Sie es später erneut.';

            if (error.message.includes('non-JSON')) {
                message = 'Server hat eine ungültige Antwort gesendet. Bitte versuchen Sie es erneut.';
            } else if (error.message.includes('Network')) {
                message = 'Netzwerkfehler. Überprüfen Sie Ihre Internetverbindung.';
            }

            this.showFieldError('password', message);

            if (typeof window.showToast === 'function') {
                window.showToast(message, 'error');
            }
        }

        validateForm() {
            let isValid = true;

            if (!this.validateField(this.usernameInput)) {
                isValid = false;
            }

            if (!this.validateField(this.passwordInput)) {
                isValid = false;
            }

            return isValid;
        }

        validateField(field) {
            if (!field) return false;

            const value = field.value.trim();
            let isValid = true;
            let message = '';

            this.clearFieldError(field);

            if (field === this.usernameInput) {
                if (!value) {
                    isValid = false;
                    message = 'Benutzername ist erforderlich';
                } else if (value.length < 3) {
                    isValid = false;
                    message = 'Benutzername muss mindestens 3 Zeichen lang sein';
                }
            } else if (field === this.passwordInput) {
                if (!value) {
                    isValid = false;
                    message = 'Passwort ist erforderlich';
                } else if (value.length < 3) {
                    isValid = false;
                    message = 'Passwort ist zu kurz';
                }
            }

            if (isValid) {
                this.setFieldSuccess(field);
            } else {
                this.setFieldError(field, message);
            }

            return isValid;
        }

        setFieldError(field, message) {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');

            const wrapper = field.closest('.input-icon-wrapper');
            if (wrapper) {
                const existingFeedback = wrapper.parentNode.querySelector('.invalid-feedback');
                if (existingFeedback) {
                    existingFeedback.remove();
                }

                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = message;
                wrapper.parentNode.appendChild(feedback);
            }
        }

        setFieldSuccess(field) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');

            const wrapper = field.closest('.input-icon-wrapper');
            if (wrapper) {
                const existingFeedback = wrapper.parentNode.querySelector('.invalid-feedback');
                if (existingFeedback) {
                    existingFeedback.remove();
                }
            }
        }

        clearFieldError(field) {
            field.classList.remove('is-invalid', 'is-valid');

            const wrapper = field.closest('.input-icon-wrapper');
            if (wrapper) {
                const existingFeedback = wrapper.parentNode.querySelector('.invalid-feedback');
                if (existingFeedback) {
                    existingFeedback.remove();
                }
            }
        }

        showFieldError(fieldName, message) {
            const field = this.form.querySelector(`input[name="${fieldName}"]`);
            if (field) {
                this.setFieldError(field, message);
            }
        }

        togglePasswordVisibility() {
            if (!this.passwordInput || !this.togglePasswordBtn) return;

            const type = this.passwordInput.type === 'password' ? 'text' : 'password';
            this.passwordInput.type = type;

            const icon = document.getElementById('authPasswordIcon');
            if (icon) {
                icon.className = type === 'password' ? 'bi bi-eye' : 'bi bi-eye-slash';
            }
        }

        showLoader() {
            if (this.loader) {
                this.loader.classList.add('active');
            }

            if (this.submitBtn) {
                this.submitBtn.disabled = true;
                const buttonText = document.getElementById('authButtonText');
                if (buttonText) {
                    buttonText.textContent = 'Anmeldung...';
                }
            }
        }

        hideLoader() {
            if (this.loader) {
                this.loader.classList.remove('active');
            }

            if (this.submitBtn) {
                this.submitBtn.disabled = false;
                const buttonText = document.getElementById('authButtonText');
                if (buttonText) {
                    buttonText.textContent = 'Anmelden';
                }
            }
        }

        showModal() {
            if (this.modal && window.bootstrap) {
                if (!this.modalInstance) {
                    this.modalInstance = new bootstrap.Modal(this.modal, {
                        backdrop: 'static',
                        keyboard: false
                    });
                }
                this.modalInstance.show();
            }
        }

        hideModal() {
            if (this.modalInstance) {
                this.modalInstance.hide();
            }
        }

        hideModalWithSuccess() {
            this.modal.classList.add('login-success');
            setTimeout(() => {
                this.hideModal();
            }, 500);
        }

        // ==================== ATTEMPTS & LOCKOUT ====================

        getStoredAttempts() {
            const stored = localStorage.getItem(CONFIG.storageKeys.attempts);
            const data = stored ? JSON.parse(stored) : {count: 0, timestamp: 0};

            if (Date.now() - data.timestamp > CONFIG.lockoutTime) {
                this.clearAttempts();
                return 0;
            }

            return data.count;
        }

        storeAttempts() {
            const data = {
                count: this.currentAttempts,
                timestamp: Date.now()
            };
            localStorage.setItem(CONFIG.storageKeys.attempts, JSON.stringify(data));
        }

        clearAttempts() {
            this.currentAttempts = 0;
            localStorage.removeItem(CONFIG.storageKeys.attempts);
            localStorage.removeItem(CONFIG.storageKeys.lockout);
        }

        isLockedOut() {
            const lockout = localStorage.getItem(CONFIG.storageKeys.lockout);
            if (!lockout) return false;

            const lockoutTime = parseInt(lockout);
            if (Date.now() < lockoutTime) {
                return true;
            }

            localStorage.removeItem(CONFIG.storageKeys.lockout);
            this.clearAttempts();
            return false;
        }

        setLockout() {
            const lockoutUntil = Date.now() + CONFIG.lockoutTime;
            localStorage.setItem(CONFIG.storageKeys.lockout, lockoutUntil.toString());
        }

        updateAttemptsDisplay() {
            if (!this.attemptsAlert) return;

            if (this.currentAttempts > 0) {
                const remaining = CONFIG.maxAttempts - this.currentAttempts;
                const attemptsText = document.getElementById('authAttemptsText');
                if (attemptsText) {
                    attemptsText.textContent = `Noch ${remaining} Versuche verbleibend`;
                }
                this.attemptsAlert.style.display = 'block';
            } else {
                this.attemptsAlert.style.display = 'none';
            }
        }

        showRemainingAttempts(remaining) {
            const message = `Noch ${remaining} Versuche übrig`;
            if (typeof window.showToast === 'function') {
                window.showToast(message, 'warning');
            }
        }

        showLockoutMessage() {
            const message = `Zu viele fehlgeschlagene Anmeldeversuche. Konto für 15 Minuten gesperrt.`;
            if (typeof window.showToast === 'function') {
                window.showToast(message, 'error', 10000);
            }

            this.form.style.pointerEvents = 'none';
            this.form.style.opacity = '0.5';
        }

        // ==================== STORAGE ====================

        saveFormData() {
            const rememberMe = document.getElementById('authRememberMe');
            if (!rememberMe || !rememberMe.checked) return;

            const username = this.usernameInput.value;
            if (username) {
                localStorage.setItem(CONFIG.storageKeys.username, username);
            }
        }

        restoreFormData() {
            const savedUsername = localStorage.getItem(CONFIG.storageKeys.username);
            if (savedUsername && this.usernameInput) {
                this.usernameInput.value = savedUsername;
                const rememberCheckbox = document.getElementById('authRememberMe');
                if (rememberCheckbox) {
                    rememberCheckbox.checked = true;
                }
            }
        }

        clearFormData() {
            localStorage.removeItem(CONFIG.storageKeys.username);
        }

        getCSRFToken() {
            const token = document.querySelector('[name=csrfmiddlewaretoken]');
            return token ? token.value : '';
        }
    }

    // Создаем глобальный экземпляр
    if (!isAdminCreationPage) {
        window.authLoginModal = new AuthLoginModal();

        // Экспортируем функции
        window.showAuthLoginModal = function() {
            if (window.authLoginModal) {
                window.authLoginModal.showModal();
            }
        };

        window.hideAuthLoginModal = function() {
            if (window.authLoginModal) {
                window.authLoginModal.hideModal();
            }
        };

        console.log('✅ Auth Login Modal System готов к работе');
    } else {
        console.log('🚫 Auth Login Modal System НЕ инициализирован (admin creation page)');

        window.showAuthLoginModal = function() {
            console.log('🚫 showAuthLoginModal заблокирован на admin creation page');
        };

        window.hideAuthLoginModal = function() {
            console.log('🚫 hideAuthLoginModal заблокирован на admin creation page');
        };
    }

})();