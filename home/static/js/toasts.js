// Обновление home/static/js/toasts.js для интеграции с модальным окном

// Глобальная система тостов для приложения - ОБНОВЛЕНО
(function() {
    'use strict';

    console.log('🍞 Toast система загружена');

    // Создаем контейнер для тостов если его нет
    function ensureToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed';
            container.style.cssText = `
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    // Главная функция показа тостов
    window.showToast = function(message, type = 'info', delay = 5000) {
        const container = ensureToastContainer();

        // Определяем стили для разных типов
        const typeConfig = {
            'success': {
                bgClass: 'toast-success',
                icon: 'bi-check-circle-fill',
                title: 'Erfolg'
            },
            'error': {
                bgClass: 'toast-danger',
                icon: 'bi-x-circle-fill',
                title: 'Fehler'
            },
            'danger': {  // Алиас для error
                bgClass: 'toast-danger',
                icon: 'bi-x-circle-fill',
                title: 'Fehler'
            },
            'warning': {
                bgClass: 'toast-warning',
                icon: 'bi-exclamation-triangle-fill',
                title: 'Warnung'
            },
            'info': {
                bgClass: 'toast-info',
                icon: 'bi-info-circle-fill',
                title: 'Info'
            },
            'primary': {
                bgClass: 'toast-primary',
                icon: 'bi-info-circle-fill',
                title: 'Hinweis'
            }
        };

        const config = typeConfig[type] || typeConfig['info'];

        // Создаем уникальный ID для toast
        const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);

        // Создаем HTML для toast
        const toastHTML = `
            <div class="toast ${config.bgClass}" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true" style="--toast-delay: ${delay}ms;">
                <div class="toast-header">
                    <i class="bi ${config.icon} me-2"></i>
                    <strong class="me-auto">${config.title}</strong>
                    <button type="button" class="toast-close-btn" data-bs-dismiss="toast" aria-label="Schließen">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        // Добавляем toast в контейнер
        container.insertAdjacentHTML('beforeend', toastHTML);

        // Получаем элемент toast
        const toastElement = document.getElementById(toastId);

        if (toastElement) {
            // Показываем toast
            setTimeout(() => {
                toastElement.classList.add('show');
            }, 10);

            // Автоматически скрываем через delay
            setTimeout(() => {
                if (toastElement && toastElement.parentNode) {
                    toastElement.classList.add('hiding');
                    setTimeout(() => {
                        if (toastElement.parentNode) {
                            toastElement.remove();
                        }
                    }, 300);
                }
            }, delay);

            // Обработчик кнопки закрытия
            const closeBtn = toastElement.querySelector('.toast-close-btn');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    toastElement.classList.add('hiding');
                    setTimeout(() => {
                        if (toastElement.parentNode) {
                            toastElement.remove();
                        }
                    }, 300);
                });
            }

            // Автозакрытие при клике на toast
            toastElement.addEventListener('click', () => {
                toastElement.classList.add('hiding');
                setTimeout(() => {
                    if (toastElement.parentNode) {
                        toastElement.remove();
                    }
                }, 300);
            });

            console.log(`🍞 Toast показан: ${type} - ${message.substring(0, 50)}...`);
        }
    };

    // Функция для показа Django сообщений при загрузке страницы
    function showDjangoMessages() {
        const messagesContainer = document.getElementById('django-messages');
        if (!messagesContainer) return;

        const messages = messagesContainer.querySelectorAll('[data-tags]');
        messages.forEach(function(msgElement) {
            const tags = msgElement.getAttribute('data-tags');
            const text = msgElement.getAttribute('data-text');
            const delay = parseInt(msgElement.getAttribute('data-delay')) || 5000;

            if (text) {
                showToast(text, tags, delay);
            }
        });

        // Очищаем контейнер после обработки
        messagesContainer.innerHTML = '';
    }

    // Обработчик для HTMX событий
    document.body.addEventListener('htmx:afterRequest', function(event) {
        // Пропускаем события, которые уже обработаны специализированными модулями
        if (event.detail.mongodbHandled) {
            console.log('🔵 Toast system: событие уже обработано MongoDB модулем, пропускаем');
            return;
        }

        // Если ответ содержит JSON с сообщениями
        try {
            const response = JSON.parse(event.detail.xhr.response);
            if (response.messages && Array.isArray(response.messages)) {
                response.messages.forEach(function(message) {
                    showToast(message.text, message.tags, message.delay || 5000);
                });
            }
        } catch (e) {
            // Не JSON ответ или другая ошибка - проверяем заголовки
            const contentType = event.detail.xhr.getResponseHeader('Content-Type');
            if (contentType && contentType.includes('application/json')) {
                console.error('Ошибка парсинга JSON ответа:', e);
                console.log('Сырой ответ:', event.detail.xhr.response);
            }
            // Если это не JSON, игнорируем
        }
    });

    // Обработчик ошибок HTMX
    document.body.addEventListener('htmx:responseError', function(event) {
        console.error('HTMX Response Error:', event.detail);
        showToast('Serverfehler aufgetreten', 'error');
    });

    document.body.addEventListener('htmx:sendError', function(event) {
        console.error('HTMX Send Error:', event.detail);
        showToast('Verbindungsfehler', 'error');
    });

    document.body.addEventListener('htmx:timeout', function(event) {
        console.error('HTMX Timeout:', event.detail);
        showToast('Anfrage-Zeitüberschreitung', 'warning');
    });

    // Показываем Django сообщения при загрузке страницы
    document.addEventListener('DOMContentLoaded', function() {
        showDjangoMessages();
    });

    // Альтернативный вызов если DOMContentLoaded уже прошел
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', showDjangoMessages);
    } else {
        showDjangoMessages();
    }

    // Экспортируем функции для использования в других скриптах
    window.toastSystem = {
        show: window.showToast,
        showSuccess: function(message, delay) {
            window.showToast(message, 'success', delay);
        },
        showError: function(message, delay) {
            window.showToast(message, 'error', delay);
        },
        showWarning: function(message, delay) {
            window.showToast(message, 'warning', delay);
        },
        showInfo: function(message, delay) {
            window.showToast(message, 'info', delay);
        }
    };

    // Дополнительные полезные функции

    // Функция для массового показа сообщений
    window.showMultipleToasts = function(messages) {
        if (!Array.isArray(messages)) return;

        messages.forEach(function(msg, index) {
            // Задержка между показом тостов
            setTimeout(function() {
                showToast(msg.text || msg.message, msg.tags || msg.type, msg.delay);
            }, index * 300);
        });
    };

    // Функция для очистки всех тостов
    window.clearAllToasts = function() {
        const container = document.getElementById('toast-container');
        if (container) {
            const toasts = container.querySelectorAll('.toast');
            toasts.forEach(function(toast) {
                toast.classList.add('hiding');
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.remove();
                    }
                }, 300);
            });
        }
    };

    // Обработка для глобальных ошибок JavaScript
    window.addEventListener('error', function(event) {
        console.error('Global JavaScript Error:', event.error);
        if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
            // Показываем ошибку только в продакшене
            showToast('Ein unerwarteter Fehler ist aufgetreten', 'error');
        }
    });

    // Обработка для unhandled promise rejections
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled Promise Rejection:', event.reason);
        if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
            showToast('Ein unerwarteter Fehler ist aufgetreten', 'error');
        }
    });

    // Интеграция с модальным окном входа
    window.addEventListener('loginSuccess', function(event) {
        const data = event.detail;
        showToast(data.message || 'Erfolgreich angemeldet', 'success');

        // Закрываем модальное окно через короткое время
        setTimeout(() => {
            if (window.hideLoginModal) {
                window.hideLoginModal();
            }
            // Перенаправляем или перезагружаем страницу
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                window.location.reload();
            }
        }, 1500);
    });

    window.addEventListener('loginError', function(event) {
        const data = event.detail;
        showToast(data.message || 'Anmeldung fehlgeschlagen', 'error');
    });

    console.log('✅ Toast система инициализирована и готова к работе');

})();