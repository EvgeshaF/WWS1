// user_auth/static/js/login_modal_htmx.js - HTMX версия для модального окна авторизации

(function() {
    'use strict';

    // КРИТИЧЕСКАЯ ПРОВЕРКА: НЕ инициализируем на страницах создания админа
    var currentPath = window.location.pathname;
    var isAdminCreationPage = currentPath.includes('/users/create-admin/') ||
                               currentPath.includes('create-admin') ||
                               (window.isAdminCreationPage === true);

    if (isAdminCreationPage) {
        console.log('🚫 Auth Login Modal HTMX System ОТКЛЮЧЕН на странице:', currentPath);
        return;
    }

    console.log('🔐 Auth Login Modal HTMX System загружен на странице:', currentPath);

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

    class AuthLoginModalHTMX {
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
            this.currentAttempts = 0;
            this.lockoutInterval = null;

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
            console.log('🔧 Инициализация Auth Login Modal HTMX');

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

            console.log('✅ Auth Login Modal HTMX инициализирован');
        }

        checkAuthStatus() {
            if (window.isAuthenticated === false && window.requiresAuth === true) {
                setTimeout(() => {
                    this.showModal();

                    // Проверяем блокировку при открытии модального окна
                    if (this.isLockedOut()) {
                        this.showLockoutMessage();
                        this.startLockoutTimer();
                    }
                }, 1000);
            }
        }

        bindEvents() {
            // HTMX события для формы
            this.form.addEventListener('htmx:beforeRequest', (e) => {
                console.log('📤 HTMX: Отправка формы логина');
                if (this.isLockedOut()) {
                    e.preventDefault();
                    this.showLockoutMessage();
                    return;
                }
                this.showLoader();
            });

            this.form.addEventListener('htmx:afterRequest', (e) => {
                console.log('📥 HTMX: Ответ получен');

                // Помечаем событие как обработанное
                e.detail.loginHandled = true;
                e.stopImmediatePropagation();

                this.hideLoader();

                try {
                    const response = JSON.parse(e.detail.xhr.response);
                    console.log('📦 Parsed login response:', response);

                    if (response.success) {
                        this.handleLoginSuccess(response);
                    } else {
                        this.handleLoginError(response);
                    }
                } catch (error) {
                    console.error('❌ Ошибка парсинга ответа:', error);
                }
            });

            this.form.addEventListener('htmx:responseError', (e) => {
                console.error('❌ HTMX Response Error:', e.detail);

                // Помечаем событие как обработанное и останавливаем распространение
                e.detail.loginHandled = true;
                e.stopImmediatePropagation();

                this.hideLoader();
                if (window.showToast) {
                    window.showToast('Serverfehler aufgetreten', 'error');
                }
            });

            this.form.addEventListener('htmx:sendError', (e) => {
                console.error('❌ HTMX Send Error:', e.detail);

                // Помечаем событие как обработанное и останавливаем распространение
                e.detail.loginHandled = true;
                e.stopImmediatePropagation();

                this.hideLoader();
                if (window.showToast) {
                    window.showToast('Verbindungsfehler', 'error');
                }
            });

            // Toggle password visibility
            if (this.togglePasswordBtn) {
                this.togglePasswordBtn.addEventListener('click', () => this.togglePasswordVisibility());
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

                // Очищаем таймер блокировки при закрытии модального окна
                if (this.lockoutInterval) {
                    clearInterval(this.lockoutInterval);
                    this.lockoutInterval = null;
                }
            });
        }

        handleLoginSuccess(data) {
            console.log('✅ Успешный вход');
            console.log('📊 Login success data:', data);
            console.log('🔗 Redirect URL:', data.redirect_url);

            this.clearAttempts();
            this.clearFormData();

            // Показываем toast вручную, так как используем stopImmediatePropagation()
            // и глобальный обработчик не сработает
            if (data.messages && Array.isArray(data.messages)) {
                console.log('📬 Showing messages from array:', data.messages);
                data.messages.forEach(msg => {
                    if (typeof window.showToast === 'function') {
                        window.showToast(msg.text, msg.tags, msg.delay || 5000);
                    }
                });
            } else if (data.message) {
                // Fallback: показываем message напрямую
                console.log('📬 Showing message:', data.message);
                if (typeof window.showToast === 'function') {
                    window.showToast(data.message, 'success', 5000);
                }
            }

            this.hideModalWithSuccess();

            console.log('⏰ Установлен таймер редиректа на 1500ms');
            setTimeout(() => {
                console.log('🚀 Выполняем редирект...');
                if (data.redirect_url) {
                    console.log('➡️ Редирект на:', data.redirect_url);
                    window.location.href = data.redirect_url;
                } else {
                    console.log('🔄 Перезагрузка страницы');
                    window.location.reload();
                }
            }, 1500);
        }

        handleLoginError(data) {
            console.warn('⚠️ Ошибка входа:', data.message);

            this.currentAttempts++;
            this.storeAttempts();
            this.updateAttemptsDisplay();

            // Показываем toast вручную, так как используем stopImmediatePropagation()
            // и глобальный обработчик не сработает
            if (data.messages && Array.isArray(data.messages)) {
                data.messages.forEach(msg => {
                    if (typeof window.showToast === 'function') {
                        window.showToast(msg.text, msg.tags, msg.delay || 5000);
                    }
                });
            } else if (data.message) {
                // Fallback: показываем message напрямую
                if (typeof window.showToast === 'function') {
                    window.showToast(data.message, 'error', 5000);
                }
            }

            if (this.currentAttempts >= CONFIG.maxAttempts) {
                this.setLockout();
                this.showLockoutMessage();
                this.startLockoutTimer();
            }

            if (this.passwordInput) {
                this.passwordInput.value = '';
                this.passwordInput.focus();
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

        showLockoutMessage() {
            const lockout = localStorage.getItem(CONFIG.storageKeys.lockout);
            if (!lockout) return;

            const lockoutTime = parseInt(lockout);
            const remainingMs = lockoutTime - Date.now();
            const remainingMinutes = Math.ceil(remainingMs / 60000);

            // НЕ показываем toast - информация отображается на самой форме
            // const message = `Zu viele fehlgeschlagene Anmeldeversuche. Konto für ${remainingMinutes} Minuten gesperrt.`;

            this.form.style.pointerEvents = 'none';
            this.form.style.opacity = '0.5';

            // Показываем сообщение на форме с таймером
            if (this.attemptsAlert) {
                const attemptsText = document.getElementById('authAttemptsText');
                if (attemptsText) {
                    attemptsText.innerHTML = `<strong>Konto gesperrt.</strong> Versuchen Sie es erneut in: <span id="lockoutTimer"></span>`;
                }
                this.attemptsAlert.classList.remove('alert-warning');
                this.attemptsAlert.classList.add('alert-danger');
                this.attemptsAlert.style.display = 'block';
            }
        }

        startLockoutTimer() {
            const timerElement = document.getElementById('lockoutTimer');
            if (!timerElement) return;

            // Очищаем предыдущий интервал, если есть
            if (this.lockoutInterval) {
                clearInterval(this.lockoutInterval);
            }

            const updateTimer = () => {
                const lockout = localStorage.getItem(CONFIG.storageKeys.lockout);
                if (!lockout) {
                    // Блокировка снята
                    this.clearLockoutDisplay();
                    return;
                }

                const lockoutTime = parseInt(lockout);
                const remainingMs = lockoutTime - Date.now();

                if (remainingMs <= 0) {
                    // Время истекло
                    this.clearLockoutDisplay();
                    this.clearAttempts();
                    return;
                }

                const minutes = Math.floor(remainingMs / 60000);
                const seconds = Math.floor((remainingMs % 60000) / 1000);
                timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            };

            // Обновляем сразу
            updateTimer();

            // Обновляем каждую секунду
            this.lockoutInterval = setInterval(updateTimer, 1000);
        }

        clearLockoutDisplay() {
            if (this.lockoutInterval) {
                clearInterval(this.lockoutInterval);
                this.lockoutInterval = null;
            }

            if (this.attemptsAlert) {
                this.attemptsAlert.classList.remove('alert-danger');
                this.attemptsAlert.classList.add('alert-warning');
                this.attemptsAlert.style.display = 'none';
            }

            this.form.style.pointerEvents = '';
            this.form.style.opacity = '';

            // НЕ показываем toast - разблокировка происходит автоматически
            // Пользователь увидит это по исчезновению сообщения на форме

            // Обновляем отображение попыток
            this.currentAttempts = 0;
            this.updateAttemptsDisplay();
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
    }

    // Создаем глобальный экземпляр
    if (!isAdminCreationPage) {
        window.authLoginModal = new AuthLoginModalHTMX();

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

        console.log('✅ Auth Login Modal HTMX System готов к работе');
    }

})();
