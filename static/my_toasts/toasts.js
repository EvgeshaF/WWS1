function showToast(toastEl) {
    if (toastEl.classList.contains('shown')) return;

    const container = document.getElementById('toast-container');
    const toastDelay = parseInt(toastEl.dataset.delay) || 5000;

    // Удаляем дублирующиеся тосты с тем же текстом
    container.querySelectorAll('.toast').forEach(el => {
        const existingBody = el.querySelector('.toast-body');
        const newBody = toastEl.querySelector('.toast-body');

        if (existingBody && newBody && existingBody.innerHTML === newBody.innerHTML) {
            const oldToast = bootstrap.Toast.getInstance(el);
            if (oldToast) oldToast.hide();
            el.remove();
        }
    });

    toastEl.classList.add('toast', 'border-0', 'toast-pop', 'shown');
    container.prepend(toastEl);

    const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: toastDelay });

    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });

    toast.show();
}

function createToast(message) {
    const toastEl = document.createElement('div');
    toastEl.className = 'toast mb-2 fade';
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.dataset.delay = message.delay || 5000;

    let bgClass = 'bg-info text-white';
    let iconClass = 'bi-info-circle-fill';
    let strongText = 'Info';

    if (message.tags === 'success') {
        bgClass = 'bg-success text-white';
        iconClass = 'bi-check-circle-fill';
        strongText = 'Erfolg';
    }
    else if (message.tags === 'error') {
        bgClass = 'bg-danger text-white';
        iconClass = 'bi-x-circle-fill';
        strongText = 'Fehler';
    }
    else if (message.tags === 'warning') {
        bgClass = 'bg-warning text-dark';
        iconClass = 'bi-exclamation-triangle-fill';
        strongText = 'Warnung';
    }

    toastEl.innerHTML = `
        <div class="toast-header ${bgClass} rounded-top">
            <i class="bi ${iconClass} me-2"></i>
            <strong class="me-auto">${strongText}</strong>
        </div>
        <div class="toast-body toast-body-${message.tags}">${message.text}</div>
    `;

    showToast(toastEl);
}

// Инициализация Django сообщений при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Ищем скрытый контейнер с сообщениями
    const messagesContainer = document.getElementById('django-messages');

    if (messagesContainer) {
        const messageElements = messagesContainer.querySelectorAll('div[data-tags]');

        messageElements.forEach(el => {
            const message = {
                tags: el.getAttribute('data-tags'),
                text: el.getAttribute('data-text'),
                delay: parseInt(el.getAttribute('data-delay')) || 5000
            };

            if (message.tags && message.text) {
                createToast(message);
            }
        });

        // Удаляем контейнер после обработки
        messagesContainer.remove();
    }
});

// HTMX: обработка JSON ответов после HTMX запросов
document.body.addEventListener('htmx:afterRequest', function(evt) {
    const xhr = evt.detail.xhr;
    if (!xhr || xhr.status !== 200) return;

    // Проверяем Content-Type на JSON
    const contentType = xhr.getResponseHeader('Content-Type') || '';
    if (!contentType.includes('application/json')) return;

    try {
        const data = JSON.parse(xhr.responseText);
        if (data.messages && Array.isArray(data.messages)) {
            data.messages.forEach(msg => createToast(msg));
        }
    } catch (e) {
        console.warn('Ошибка парсинга JSON ответа:', e);
    }
});

// Обработка ошибок HTMX
document.body.addEventListener('htmx:responseError', function(evt) {
    createToast({
        tags: 'error',
        text: 'Ошибка сети. Попробуйте еще раз.',
        delay: 5000
    });
});

document.body.addEventListener('htmx:sendError', function(evt) {
    createToast({
        tags: 'error',
        text: 'Ошибка отправки запроса.',
        delay: 5000
    });
});