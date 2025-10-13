// Общий JS для обработки форм MongoDB с HTMX и toast-уведомлениями
(function() {
    'use strict';

    console.log('🔧 MongoDB Forms HTMX Module загружен');

    // Класс для управления прогресс-баром
    class ProgressManager {
        constructor(config) {
            this.submitBtn = config.submitBtn;
            this.progressLabel = config.progressLabel;
            this.progressBar = config.progressBar;
            this.progressBarContainer = config.progressBarContainer;
            this.originalBtnText = config.originalBtnText;
            this.processingBtnText = config.processingBtnText;
            this.progressInterval = null;
        }

        show() {
            if (!this.submitBtn || !this.progressLabel || !this.progressBarContainer || !this.progressBar) {
                console.warn('⚠️ Не все элементы прогресс-бара найдены');
                return;
            }

            this.submitBtn.disabled = true;
            this.submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>${this.processingBtnText}`;

            this.progressLabel.style.visibility = 'visible';
            this.progressBarContainer.style.visibility = 'visible';

            let progress = 0;
            this.progressInterval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                this.progressBar.style.width = progress + '%';
            }, 200);

            console.log('🔄 Прогресс-бар показан');
        }

        hide() {
            if (!this.submitBtn || !this.progressLabel || !this.progressBarContainer || !this.progressBar) {
                return;
            }

            if (this.progressInterval) {
                clearInterval(this.progressInterval);
                this.progressInterval = null;
            }

            this.submitBtn.disabled = false;
            this.submitBtn.innerHTML = this.originalBtnText;

            // Завершаем прогресс-бар
            this.progressBar.style.width = '100%';

            setTimeout(() => {
                this.progressLabel.style.visibility = 'hidden';
                this.progressBarContainer.style.visibility = 'hidden';
                this.progressBar.style.width = '0%';
            }, 500);

            console.log('✅ Прогресс-бар скрыт');
        }
    }

    // Инициализация форм MongoDB
    function initializeMongoDBForms() {
        console.log('🚀 Инициализация MongoDB форм...');

        // Шаг 1: Подключение к серверу
        const step1Form = document.getElementById('mongo-form');
        if (step1Form) {
            console.log('📝 Найдена форма Step 1');
            const progressManager = new ProgressManager({
                submitBtn: step1Form.querySelector('button[type="submit"]'),
                progressLabel: document.getElementById('progress-label'),
                progressBar: document.getElementById('connection-progress'),
                progressBarContainer: document.getElementById('progress-bar-container'),
                originalBtnText: '<i class="bi bi-wifi me-1"></i>Verbindung prüfen',
                processingBtnText: 'Wird geprüft...'
            });

            step1Form.addEventListener('htmx:beforeRequest', function() {
                console.log('📤 Step 1: Отправка запроса...');
                progressManager.show();
            });

            step1Form.addEventListener('htmx:afterRequest', function(event) {
                console.log('📥 Step 1: Ответ получен');
                progressManager.hide();
                // НЕ обрабатываем сообщения здесь - это делает глобальный обработчик
            });
        }

        // Шаг 2: Авторизация
        const step2Form = document.getElementById('mongo-login-form');
        if (step2Form) {
            console.log('📝 Найдена форма Step 2');
            const progressManager = new ProgressManager({
                submitBtn: step2Form.querySelector('button[type="submit"]'),
                progressLabel: document.getElementById('auth-progress-label'),
                progressBar: document.getElementById('auth-progress'),
                progressBarContainer: document.getElementById('auth-progress-bar-container'),
                originalBtnText: '<i class="bi bi-box-arrow-in-right me-1"></i>Anmelden',
                processingBtnText: 'Authentifizierung läuft...'
            });

            step2Form.addEventListener('htmx:beforeRequest', function() {
                console.log('📤 Step 2: Отправка запроса...');
                progressManager.show();
            });

            step2Form.addEventListener('htmx:afterRequest', function() {
                console.log('📥 Step 2: Ответ получен');
                progressManager.hide();
            });
        }

        // Шаг 3: Создание БД
        const step3Form = document.getElementById('create-db-form');
        if (step3Form) {
            console.log('📝 Найдена форма Step 3');
            const progressManager = new ProgressManager({
                submitBtn: step3Form.querySelector('button[type="submit"]'),
                progressLabel: document.getElementById('db-progress-label'),
                progressBar: document.getElementById('db-progress'),
                progressBarContainer: document.getElementById('db-progress-bar-container'),
                originalBtnText: '<i class="bi bi-database-add me-1"></i>Datenbank erstellen',
                processingBtnText: 'Datenbank wird erstellt...'
            });

            step3Form.addEventListener('htmx:beforeRequest', function() {
                console.log('📤 Step 3: Отправка запроса...');
                progressManager.show();
            });

            step3Form.addEventListener('htmx:afterRequest', function() {
                console.log('📥 Step 3: Ответ получен');
                progressManager.hide();
            });
        }
    }

    // Глобальный обработчик для HTMX событий с toast-сообщениями
    // ВАЖНО: используем capture phase, чтобы обработать событие ПЕРВЫМИ
    document.body.addEventListener('htmx:afterRequest', function(event) {
        console.log('🔔 MongoDB HTMX afterRequest event', event.detail);

        // Проверяем, что это форма MongoDB
        const formElement = event.detail.elt;
        if (!formElement || !formElement.id || (!formElement.id.includes('mongo') && !formElement.id.includes('create-db'))) {
            console.log('❌ Не MongoDB форма, пропускаем. ID:', formElement?.id);
            return; // Не наша форма
        }

        console.log('✅ MongoDB форма обнаружена, обрабатываем');

        // Помечаем событие как обработанное для MongoDB форм
        // Это предотвратит обработку в глобальном обработчике toasts.js
        event.detail.mongodbHandled = true;

        // Останавливаем всплытие события, чтобы другие обработчики не сработали
        event.stopImmediatePropagation();

        try {
            const response = JSON.parse(event.detail.xhr.response);
            console.log('📦 Parsed response:', response);

            // Обрабатываем сообщения
            if (response.messages && Array.isArray(response.messages)) {
                console.log(`💬 Показываем ${response.messages.length} сообщений`);

                // Обрабатываем редирект при успехе
                const hasSuccess = response.messages.some(msg => msg.tags === 'success');
                const redirectDelay = hasSuccess && response.redirect_url ? 2500 : 5000;

                // Если есть редирект, сохраняем сообщения и делаем немедленный редирект
                if (hasSuccess && response.redirect_url) {
                    console.log(`🔀 Немедленный редирект на: ${response.redirect_url}`);
                    console.log(`💾 Сохраняем ${response.messages.length} сообщений для показа на новой странице`);

                    // Сообщения уже в Django session, просто делаем редирект
                    // Django messages будут показаны на следующей странице через base.html
                    window.location.href = response.redirect_url;
                } else {
                    // Нет редиректа - показываем toast на текущей странице
                    response.messages.forEach(function(message) {
                        if (window.showToast) {
                            window.showToast(message.text, message.tags, message.delay || 5000);
                        } else {
                            console.error('❌ window.showToast не определена!');
                        }
                    });
                }
            }
        } catch (e) {
            // Не JSON ответ
            const contentType = event.detail.xhr.getResponseHeader('Content-Type');
            if (contentType && contentType.includes('application/json')) {
                console.error('❌ Ошибка парсинга JSON:', e);
                if (window.showToast) {
                    window.showToast('Fehler beim Verarbeiten der Serverantwort', 'error');
                }
            }
        }
    });

    // Обработчик ошибок HTMX
    document.body.addEventListener('htmx:responseError', function(event) {
        console.error('❌ HTMX Response Error:', event.detail);
        if (window.showToast) {
            window.showToast('Serverfehler aufgetreten', 'error');
        }
    });

    document.body.addEventListener('htmx:sendError', function(event) {
        console.error('❌ HTMX Send Error:', event.detail);
        if (window.showToast) {
            window.showToast('Verbindungsfehler', 'error');
        }
    });

    document.body.addEventListener('htmx:timeout', function(event) {
        console.error('⏱️ HTMX Timeout:', event.detail);
        if (window.showToast) {
            window.showToast('Anfrage-Zeitüberschreitung', 'warning');
        }
    });

    // Инициализация при загрузке
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeMongoDBForms);
    } else {
        initializeMongoDBForms();
    }

    console.log('✅ MongoDB Forms HTMX Module инициализирован');

})();