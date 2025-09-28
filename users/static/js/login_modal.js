// users/static/js/login_modal.js - JavaScript для модального окна аутентификации

(function() {
    'use strict';

    console.log('🔐 Login Modal System загружен');

    class LoginModal {
        constructor() {
            this.modal = null;
            this.form = null;
            this.submitBtn = null;
            this.loader = null;
            this.isSubmitting = false;
            this.maxAttempts = 5;
            this.currentAttempts = 0;
            this.lockoutTime = 15 * 60 * 1000; // 15 минут в миллисекундах

            this.init();
        }

        init() {
            // Ждем полной загрузки DOM
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setup());
            } else {
                this.setup();
            }
        }

        setup() {
            console.log('🔧 Инициализация Login Modal');

            // Ищем модальное окно
            this.modal = document.getElementById('loginModal');
            if (!this.modal) {
                console.warn('⚠️ Модальное окно #loginModal не найдено');
                return;
            }

            this.form = this.modal.querySelector('#loginForm');
            this.submitBtn = this.modal.querySelector('#loginSubmitBtn');
            this.loader = this.modal.querySelector('.login-loader');

            if (!this.form || !this.submitBtn) {
                console.error('❌ Форма или кнопка входа не найдены');
                return;
            }

            this.bindEvents();
            this.checkAuthStatus();
            this.restoreFormData();
            this.setupKeyboardShortcuts();

            console.log('✅ Login Modal инициализирован');
        }

        bindEvents() {
            // Обработка отправки формы
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));

            // Валидация в реальном времени
            const usernameInput = this.form.querySelector('input[name="username"]');
            const passwordInput = this.form.querySelector('input[name="password"]');

            if (usernameInput) {
                usernameInput.addEventListener('input', () => this.validateField(usernameInput));
                usernameInput.addEventListener('blur', () => this.validateField(usernameInput));
            }

            if (passwordInput) {
                passwordInput.addEventListener('input', () => this.validateField(passwordInput));
                passwordInput.addEventListener('blur', () => this.validateField(passwordInput));
            }

            // Автофокус на поле имени пользователя при открытии модального окна
            this.modal.addEventListener('shown.bs.modal', () => {
                if (usernameInput) {
                    usernameInput.focus();
                }
                this.currentAttempts = this.getStoredAttempts();
                this.updateAttemptsDisplay();
            });

            // Сохранение данных при закрытии (если разрешено)
            this.modal.addEventListener('hidden.bs.modal', () => {
                this.saveFormData();
            });

            // Обработка нажатия Escape
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.modal.classList.contains('show')) {
                    this.hideModal();
                }
            });

            // Предотвращение закрытия модального окна по клику вне его
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) {
                    e.stopPropagation();
                    this.showSecurityMessage();
                }
            });
        }

        setupKeyboardShortcuts() {
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

            // Проверяем блокировку
            if (this.isLockedOut()) {
                this.showLockoutMessage();
                return;
            }

            console.log('📤 Отправка формы входа');

            // Валидируем форму
            if (!this.validateForm()) {
                console.warn('⚠️ Форма не прошла валидацию');
                return;
            }

            this.showLoader();
            this.isSubmitting = true;

            try {
                const formData = new FormData(this.form);

                const response = await fetch('/users/login/', {
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

            // Очищаем счетчик попыток
            this.clearAttempts();
            this.clearFormData();

            // Показываем успешное сообщение
            if (typeof window.showToast === 'function') {
                window.showToast(data.message || 'Erfolgreich angemeldet', 'success');
            }

            // Скрываем модальное окно с анимацией
            this.hideModalWithSuccess();

            // Перенаправляем или перезагружаем страницу
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

            // Показываем ошибку
            const message = data.message || 'Ungültiger Benutzername oder Passwort';
            this.showFieldError('password', message);

            if (typeof window.showToast === 'function') {
                window.showToast(message, 'error');
            }

            // Проверяем блокировку
            if (this.currentAttempts >= this.maxAttempts) {
                this.setLockout();
                this.showLockoutMessage();
            } else {
                const remainingAttempts = this.maxAttempts - this.currentAttempts;
                this.showRemainingAttempts(remainingAttempts);
            }

            // Очищаем пароль
            const passwordInput = this.form.querySelector('input[name="password"]');
            if (passwordInput) {
                passwordInput.value = '';
                passwordInput.focus();
            }
        }

        handleNetworkError(error) {
            console.error('🌐 Сетевая ошибка:', error);

            const message = 'Verbindungsfehler. Bitte versuchen Sie es später erneut.';
            this.showFieldError('password', message);

            if (typeof window.showToast === 'function') {
                window.showToast(message, 'error');
            }
        }

        validateForm() {
            const usernameInput = this.form.querySelector('input[name="username"]');
            const passwordInput = this.form.querySelector('input[name="password"]');

            let isValid = true;

            // Валидируем имя пользователя
            if (!this.validateField(usernameInput)) {
                isValid = false;
            }

            // Валидируем пароль
            if (!this.validateField(passwordInput)) {
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

            if (field.name === 'username') {
                if (!value) {
                    isValid = false;
                    message = 'Benutzername ist erforderlich';
                } else if (value.length < 3) {
                    isValid = false;
                    message = 'Benutzername muss mindestens 3 Zeichen lang sein';
                }
            } else if (field.name === 'password') {
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

            // Удаляем старые сообщения
            const existingFeedback = field.parentNode.querySelector('.invalid-feedback');
            if (existingFeedback) {
                existingFeedback.remove();
            }

            // Добавляем новое сообщение
            const feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.textContent = message;
            field.parentNode.appendChild(feedback);
        }

        setFieldSuccess(field) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');

            const existingFeedback = field.parentNode.querySelector('.invalid-feedback');
            if (existingFeedback) {
                existingFeedback.remove();
            }
        }

        clearFieldError(field) {
            field.classList.remove('is-invalid', 'is-valid');

            const existingFeedback = field.parentNode.querySelector('.invalid-feedback');
            if (existingFeedback) {
                existingFeedback.remove();
            }
        }

        showFieldError(fieldName, message) {
            const field = this.form.querySelector(`input[name="${fieldName}"]`);
            if (field) {
                this.setFieldError(field, message);
            }
        }

        showLoader() {
            if (this.loader) {
                this.loader.classList.add('active');
            }

            if (this.submitBtn) {
                this.submitBtn.disabled = true;
                this.submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Anmeldung...';
            }
        }

        hideLoader() {
            if (this.loader) {
                this.loader.classList.remove('active');
            }

            if (this.submitBtn) {
                this.submitBtn.disabled = false;
                this.submitBtn.innerHTML = '<i class="bi bi-box-arrow-in-right me-2"></i>Anmelden';
            }
        }

        showModal() {
            if (this.modal && window.bootstrap) {
                const modal = new bootstrap.Modal(this.modal, {
                    backdrop: 'static',
                    keyboard: false
                });
                modal.show();
            }
        }

        hideModal() {
            if (this.modal && window.bootstrap) {
                const modal = bootstrap.Modal.getInstance(this.modal);
                if (modal) {
                    modal.hide();
                }
            }
        }

        hideModalWithSuccess() {
            // Добавляем класс успеха для анимации
            this.modal.classList.add('login-success');

            setTimeout(() => {
                this.hideModal();
            }, 500);
        }

        // ==================== СИСТЕМА ПОПЫТОК И БЛОКИРОВКИ ====================

        getStoredAttempts() {
            const stored = localStorage.getItem('login_attempts');
            const data = stored ? JSON.parse(stored) : { count: 0, timestamp: 0 };

            // Сбрасываем попытки если прошло достаточно времени
            if (Date.now() - data.timestamp > this.lockoutTime) {
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
            localStorage.setItem('login_attempts', JSON.stringify(data));
        }

        clearAttempts() {
            this.currentAttempts = 0;
            localStorage.removeItem('login_attempts');
            localStorage.removeItem('login_lockout');
        }

        isLockedOut() {
            const lockout = localStorage.getItem('login_lockout');
            if (!lockout) return false;

            const lockoutTime = parseInt(lockout);
            if (Date.now() < lockoutTime) {
                return true;
            }

            // Блокировка истекла
            localStorage.removeItem('login_lockout');
            this.clearAttempts();
            return false;
        }

        setLockout() {
            const lockoutUntil = Date.now() + this.lockoutTime;
            localStorage.setItem('login_lockout', lockoutUntil.toString());
        }

        updateAttemptsDisplay() {
            const attemptsInfo = this.modal.querySelector('.attempts-info');
            if (!attemptsInfo) return;

            if (this.currentAttempts > 0) {
                const remaining = this.maxAttempts - this.currentAttempts;
                attemptsInfo.innerHTML = `<i class="bi bi-exclamation-triangle text-warning"></i> ${remaining} Versuche verbleibend`;
                attemptsInfo.style.display = 'block';
            } else {
                attemptsInfo.style.display = 'none';
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

            // Блокируем форму
            this.form.style.pointerEvents = 'none';
            this.form.style.opacity = '0.5';

            // Показываем таймер разблокировки
            this.showLockoutTimer();
        }

        showLockoutTimer() {
            const lockout = localStorage.getItem('login_lockout');
            if (!lockout) return;

            const lockoutUntil = parseInt(lockout);
            const timerElement = document.createElement('div');
            timerElement.className = 'lockout-timer alert alert-danger text-center';
            timerElement.innerHTML = '<i class="bi bi-clock"></i> <span class="timer-text"></span>';

            const formContainer = this.form.parentNode;
            formContainer.insertBefore(timerElement, this.form);

            const updateTimer = () => {
                const remaining = lockoutUntil - Date.now();
                if (remaining <= 0) {
                    // Разблокировка
                    timerElement.remove();
                    this.form.style.pointerEvents = '';
                    this.form.style.opacity = '';
                    this.clearAttempts();
                    return;
                }

                const minutes = Math.floor(remaining / 60000);
                const seconds = Math.floor((remaining % 60000) / 1000);
                timerElement.querySelector('.timer-text').textContent =
                    `Entsperrt in ${minutes}:${seconds.toString().padStart(2, '0')}`;

                setTimeout(updateTimer, 1000);
            };

            updateTimer();
        }

        showSecurityMessage() {
            if (typeof window.showToast === 'function') {
                window.showToast('Aus Sicherheitsgründen müssen Sie sich anmelden', 'info');
            }
        }

        // ==================== СОХРАНЕНИЕ ДАННЫХ ФОРМЫ ====================

        saveFormData() {
            const rememberMe = this.form.querySelector('input[name="remember_me"]');
            if (!rememberMe || !rememberMe.checked) return;

            const username = this.form.querySelector('input[name="username"]').value;
            if (username) {
                localStorage.setItem('login_username', username);
            }
        }

        restoreFormData() {
            const savedUsername = localStorage.getItem('login_username');
            if (savedUsername) {
                const usernameInput = this.form.querySelector('input[name="username"]');
                const rememberInput = this.form.querySelector('input[name="remember_me"]');

                if (usernameInput) {
                    usernameInput.value = savedUsername;
                }
                if (rememberInput) {
                    rememberInput.checked = true;
                }
            }
        }

        clearFormData() {
            localStorage.removeItem('login_username');
        }

        // ==================== УТИЛИТЫ ====================

        getCSRFToken() {
            const token = document.querySelector('[name=csrfmiddlewaretoken]');
            return token ? token.value : '';
        }

        checkAuthStatus() {
            // Проверяем, нужно ли показывать модальное окно
            const showLogin = document.body.dataset.showLogin === 'true';
            if (showLogin) {
                // Показываем с небольшой задержкой для лучшего UX
                setTimeout(() => {
                    this.showModal();
                }, 500);
            }
        }
    }

    // ==================== АВТОИНИЦИАЛИЗАЦИЯ ====================

    // Создаем глобальный экземпляр
    window.loginModal = new LoginModal();

    // Экспортируем функции для внешнего использования
    window.showLoginModal = function() {
        if (window.loginModal) {
            window.loginModal.showModal();
        }
    };

    window.hideLoginModal = function() {
        if (window.loginModal) {
            window.loginModal.hideModal();
        }
    };

    console.log('✅ Login Modal System готов к работе');

})();