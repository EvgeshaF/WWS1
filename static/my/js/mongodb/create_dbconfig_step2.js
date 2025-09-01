document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('mongo-login-form');
    if (!form) return;

    const submitBtn = form.querySelector('button[type="submit"]');
    const progressContainer = document.getElementById('auth-progress-container');
    const progressLabel = document.getElementById('auth-progress-label');
    const progressBar = document.getElementById('auth-progress');
    const progressBarContainer = document.getElementById('auth-progress-bar-container');

    let progressInterval = null;

    // Обработчик отправки формы
    form.addEventListener('submit', function(e) {
        e.preventDefault();
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
                        window.location.href = '/mongodb/create/step3/';
                    }, 1500);
                }
            }
        })
        .catch(error => {
            console.error('Ошибка отправки формы:', error);
            hideProgress();
            showToast('Authentifizierungsfehler', 'error');
        });
    });

    function showProgress() {
        if (!submitBtn || !progressLabel || !progressBarContainer || !progressBar) return;

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Authentifizierung...';

        progressLabel.style.visibility = 'visible';
        progressBarContainer.style.visibility = 'visible';

        let progress = 0;
        progressInterval = setInterval(() => {
            progress += Math.random() * 12;
            if (progress > 85) progress = 85;
            progressBar.style.width = progress + '%';
        }, 250);
    }

    function hideProgress() {
        if (!submitBtn || !progressLabel || !progressBarContainer || !progressBar) return;

        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }

        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-box-arrow-in-right me-1"></i>Anmelden';

        // Завершаем прогресс-бар
        progressBar.style.width = '100%';

        setTimeout(() => {
            progressLabel.style.visibility = 'hidden';
            progressBarContainer.style.visibility = 'hidden';
            progressBar.style.width = '0%';
        }, 500);
    }

    // Глобальная функция для показа тостов (если не определена)
    if (typeof window.showToast === 'undefined') {
        window.showToast = function(message, type = 'info', delay = 5000) {
            // Создаем простой toast если нет готовой системы
            const toast = document.createElement('div');
            toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
            toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            toast.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;

            document.body.appendChild(toast);

            // Автоматически удаляем через delay
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, delay);
        };
    }
});