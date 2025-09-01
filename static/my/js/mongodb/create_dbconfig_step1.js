document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('mongo-form');
    const submitBtn = form.querySelector('button[type="submit"]');
    const progressContainer = document.getElementById('connection-progress-container');
    const progressLabel = document.getElementById('progress-label');
    const progressBarContainer = document.getElementById('progress-bar-container');
    const progressBar = document.getElementById('connection-progress');

    // Обработчик отправки формы
    form.addEventListener('submit', function(e) {
        // Показываем прогресс-бар
        if (progressContainer && progressLabel && progressBarContainer) {
            progressLabel.style.visibility = 'visible';
            progressBarContainer.style.visibility = 'visible';
            progressBar.style.width = '30%';
        }

        // Меняем кнопку
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spin me-1"></i>Wird geprüft...';
        }

        // Симулируем прогресс
        setTimeout(() => {
            if (progressBar) progressBar.style.width = '60%';
        }, 500);

        setTimeout(() => {
            if (progressBar) progressBar.style.width = '90%';
        }, 1000);
    });

    // Обработчик успешного ответа HTMX
    document.addEventListener('htmx:afterRequest', function(event) {
        if (event.detail.xhr.status === 200) {
            // Проверяем, содержит ли ответ сообщение об успехе
            try {
                const response = JSON.parse(event.detail.xhr.responseText);
                if (response.messages && response.messages.some(msg => msg.tags === 'success')) {
                    // Успешная проверка соединения - перенаправляем на следующий шаг
                    setTimeout(() => {
                        window.location.href = '/mongodb/create/step2/';
                    }, 2000);
                    return;
                }
            } catch (e) {
                // Игнорируем ошибки парсинга JSON
            }
        }

        // В случае ошибки сбрасываем состояние
        resetFormState();
    });

    // Обработчик ошибки HTMX
    document.addEventListener('htmx:responseError', function(event) {
        resetFormState();
    });

    function resetFormState() {
        // Скрываем прогресс-бар
        if (progressContainer && progressLabel && progressBarContainer) {
            progressLabel.style.visibility = 'hidden';
            progressBarContainer.style.visibility = 'hidden';
            progressBar.style.width = '0%';
        }

        // Восстанавливаем кнопку
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-wifi me-1"></i>Verbindung prüfen';
        }
    }

    // Добавляем стили для анимации загрузки
    const style = document.createElement('style');
    style.textContent = `
        .spin {
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
});