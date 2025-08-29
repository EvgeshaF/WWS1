// static/my_toasts/toasts.js - Исправленная версия

document.addEventListener('DOMContentLoaded', function() {
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
    document.body.addEventListener('htmx:afterRequest', function(event) {
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
    toast.className = `toast show align-items-center text-white bg-${getBootstrapClass(type)} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    const toastId = 'toast-' + Date.now();
    toast.id = toastId;

    // HTML структура toast
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="${getIcon(type)}"></i> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    // Добавляем в контейнер
    container.appendChild(toast);

    // Инициализируем Bootstrap Toast
    const bsToast = new bootstrap.Toast(toast, {
        delay: delay,
        autohide: true
    });

    // Показываем toast
    bsToast.show();

    // Удаляем элемент после скрытия
    toast.addEventListener('hidden.bs.toast', function() {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    });
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
        'warning': 'bi bi-exclamation-triangle-fill',
        'info': 'bi bi-info-circle-fill',
        'debug': 'bi bi-gear-fill'
    };
    return iconMap[type] || 'bi bi-info-circle-fill';
}