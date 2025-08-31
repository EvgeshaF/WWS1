// static/my_toasts/toasts.js - обновленная версия с цветной шапкой

document.addEventListener('DOMContentLoaded', function () {
    // Обрабатываем Django сообщения при загрузке страницы
    const djangoMessages = document.getElementById('django-messages');
    if (djangoMessages) {
        const messages = djangoMessages.querySelectorAll('div[data-tags]');
        messages.forEach(messageDiv => {
            const tags = messageDiv.getAttribute('data-tags');
            const text = messageDiv.getAttribute('data-text');
            const delay = parseInt(messageDiv.getAttribute('data-delay')) || 5000;
            showToast(text, tags, delay);
        });
    }

    // Обрабатываем HTMX ответы
    document.body.addEventListener('htmx:afterRequest', function (event) {
        const response = event.detail.xhr.responseText;

        // Проверяем, является ли ответ JSON с сообщениями
        try {
            const data = JSON.parse(response);
            if (data && data.messages && Array.isArray(data.messages)) {
                // Очищаем контейнер toast от JSON текста
                const container = document.getElementById('toast-container');
                if (container && container.textContent.includes('{"messages"')) {
                    container.innerHTML = '';
                }

                // Показываем каждое сообщение как toast
                data.messages.forEach(message => {
                    showToast(message.text, message.tags, message.delay || 5000);
                });
            }
        } catch (e) {
            // Если это не JSON, игнорируем
        }
    });
});

function showToast(message, type = 'info', delay = 5000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    // Создаем элемент toast
    const toast = document.createElement('div');
    const toastClass = getToastClass(type);

    toast.className = `toast show toast-${toastClass}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.style.setProperty('--toast-delay', delay + 'ms');

    const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    toast.id = toastId;

    // HTML структура с цветной шапкой и белым телом
    toast.innerHTML = `
        <div class="toast-header">
            <i class="${getIcon(type)}"></i>
            <strong>${getTitle(type)}</strong>
            <button type="button" class="toast-close-btn" onclick="closeToast('${toastId}')" aria-label="Close">
                <i class="bi bi-x"></i>
            </button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    // Добавляем в контейнер
    container.appendChild(toast);

    // Запускаем анимацию появления
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    // Автоматическое скрытие
    const autoHideTimeout = setTimeout(() => {
        closeToast(toastId);
    }, delay);

    // Останавливаем автоскрытие при hover
    toast.addEventListener('mouseenter', () => {
        clearTimeout(autoHideTimeout);
        toast.style.animationPlayState = 'paused';
    });

    // Возобновляем при mouse leave
    toast.addEventListener('mouseleave', () => {
        toast.style.animationPlayState = 'running';
        setTimeout(() => closeToast(toastId), 1000);
    });

    // Ограничиваем количество toast'ов
    limitToasts();
}

function closeToast(toastId) {
    const toast = document.getElementById(toastId);
    if (!toast) return;

    // Добавляем класс для анимации скрытия
    toast.classList.add('hiding');
    toast.classList.remove('show');

    // Удаляем элемент после анимации
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

function limitToasts() {
    const container = document.getElementById('toast-container');
    const toasts = container.querySelectorAll('.toast');

    // Оставляем только последние 4 toast'а
    if (toasts.length > 4) {
        for (let i = 0; i < toasts.length - 4; i++) {
            closeToast(toasts[i].id);
        }
    }
}

function getToastClass(type) {
    const typeMap = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning',
        'info': 'info',
        'debug': 'primary'
    };
    return typeMap[type] || 'info';
}

function getIcon(type) {
    const iconMap = {
        'success': 'bi bi-check-circle-fill',
        'error': 'bi bi-exclamation-triangle-fill',
        'warning': 'bi bi-exclamation-triangle',
        'info': 'bi bi-info-circle-fill',
        'debug': 'bi bi-gear-fill'
    };
    return iconMap[type] || 'bi bi-info-circle-fill';
}

function getTitle(type) {
    const titleMap = {
        'success': 'Erfolg',
        'error': 'Fehler',
        'warning': 'Warnung',
        'info': 'Information',
        'debug': 'Hinweis'
    };
    return titleMap[type] || 'Information';
}

// Глобальная функция для создания toast из любого места
window.showToast = showToast;// static/my_toasts/toasts.js - обновленная версия в едином стиле

document.addEventListener('DOMContentLoaded', function () {
    // Обрабатываем Django сообщения при загрузке страницы
    const djangoMessages = document.getElementById('django-messages');
    if (djangoMessages) {
        const messages = djangoMessages.querySelectorAll('div[data-tags]');
        messages.forEach(messageDiv => {
            const tags = messageDiv.getAttribute('data-tags');
            const text = messageDiv.getAttribute('data-text');
            const delay = parseInt(messageDiv.getAttribute('data-delay')) || 5000;
            showToast(text, tags, delay);
        });
    }

    // Обрабатываем HTMX ответы
    document.body.addEventListener('htmx:afterRequest', function (event) {
        const response = event.detail.xhr.responseText;

        // Проверяем, является ли ответ JSON с сообщениями
        try {
            const data = JSON.parse(response);
            if (data && data.messages && Array.isArray(data.messages)) {
                // Очищаем контейнер toast от JSON текста
                const container = document.getElementById('toast-container');
                if (container && container.textContent.includes('{"messages"')) {
                    container.innerHTML = '';
                }

                // Показываем каждое сообщение как toast
                data.messages.forEach(message => {
                    showToast(message.text, message.tags, message.delay || 5000);
                });
            }
        } catch (e) {
            // Если это не JSON, игнорируем
        }
    });
});

function showToast(message, type = 'info', delay = 5000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    // Создаем элемент toast
    const toast = document.createElement('div');
    const bootstrapClass = getBootstrapClass(type);

    toast.className = `toast show align-items-center text-white bg-${bootstrapClass} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.style.setProperty('--toast-delay', delay + 'ms');

    const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    toast.id = toastId;

    // HTML структура toast в новом стиле
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="${getIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    onclick="closeToast('${toastId}')" aria-label="Close">
            </button>
        </div>
    `;

    // Добавляем в контейнер
    container.appendChild(toast);

    // Запускаем анимацию появления
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    // Автоматическое скрытие
    const autoHideTimeout = setTimeout(() => {
        closeToast(toastId);
    }, delay);

    // Останавливаем автоскрытие при hover
    toast.addEventListener('mouseenter', () => {
        clearTimeout(autoHideTimeout);
        toast.style.animationPlayState = 'paused';
    });

    // Возобновляем при mouse leave
    toast.addEventListener('mouseleave', () => {
        toast.style.animationPlayState = 'running';
        setTimeout(() => closeToast(toastId), 1000);
    });

    // Ограничиваем количество toast'ов
    limitToasts();
}

function closeToast(toastId) {
    const toast = document.getElementById(toastId);
    if (!toast) return;

    // Добавляем класс для анимации скрытия
    toast.classList.add('hiding');
    toast.classList.remove('show');

    // Удаляем элемент после анимации
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

function limitToasts() {
    const container = document.getElementById('toast-container');
    const toasts = container.querySelectorAll('.toast');

    // Оставляем только последние 4 toast'а
    if (toasts.length > 4) {
        for (let i = 0; i < toasts.length - 4; i++) {
            closeToast(toasts[i].id);
        }
    }
}

function getBootstrapClass(type) {
    const typeMap = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning',
        'info': 'info',
        'debug': 'secondary'
    };
    return typeMap[type] || 'info';
}

function getIcon(type) {
    const iconMap = {
        'success': 'bi bi-check-circle-fill',
        'error': 'bi bi-exclamation-triangle-fill',
        'warning': 'bi bi-exclamation-triangle',
        'info': 'bi bi-info-circle-fill',
        'debug': 'bi bi-gear-fill'
    };
    return iconMap[type] || 'bi bi-info-circle-fill';
}

// Глобальная функция для создания toast из любого места
window.showToast = showToast;