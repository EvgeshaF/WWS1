document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('mongo-form');
    const submitBtn = form.querySelector('button[type="submit"]');
    const container = document.getElementById('connection-progress-container');
    const bar = document.getElementById('connection-progress');

    // Отслеживаем начало HTMX запроса
    form.addEventListener('htmx:beforeRequest', () => {
        submitBtn.disabled = true;       // Деактивируем кнопку
        submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spinner-border spinner-border-sm me-1" role="status"></i>Verbindung wird getestet...';

        // Показываем прогресс-бар
        document.getElementById('progress-label').style.visibility = 'visible';
        document.getElementById('progress-bar-container').style.visibility = 'visible';
        bar.style.width = '0%';

        let progress = 0;
        window.progressInterval = setInterval(() => {
            progress += Math.floor(Math.random() * 10) + 5;
            if (progress > 90) progress = 90;
            bar.style.width = progress + '%';
        }, 200);
    });

    // Отслеживаем завершение HTMX запроса
    form.addEventListener('htmx:afterRequest', (event) => {
        clearInterval(window.progressInterval);

        // Проверяем успешность запроса
        if (event.detail.xhr.status === 200) {
            bar.style.width = '100%';
            bar.classList.remove('bg-danger');
            bar.classList.add('bg-primary');
        } else {
            bar.classList.remove('bg-primary');
            bar.classList.add('bg-danger');
            bar.style.width = '100%';
        }

        setTimeout(() => {
            // Скрываем прогресс-бар
            document.getElementById('progress-label').style.visibility = 'hidden';
            document.getElementById('progress-bar-container').style.visibility = 'hidden';
            bar.style.width = '0%';
            bar.classList.remove('bg-danger', 'bg-primary');
            bar.classList.add('bg-primary');
            submitBtn.disabled = false;   // Включаем кнопку обратно
            submitBtn.innerHTML = '<i class="bi bi-wifi me-1"></i>{{ text.btn }}';
        }, 1000);
    });

    // Обработка успешного подключения для перенаправления
    document.body.addEventListener('htmx:afterRequest', function (event) {
        if (event.target.id === 'mongo-form') {
            try {
                const response = JSON.parse(event.detail.xhr.responseText);
                if (response && response.messages) {
                    // Проверяем, есть ли сообщение об успехе
                    const hasSuccess = response.messages.some(msg => msg.tags === 'success');
                    if (hasSuccess) {
                        // Перенаправляем через небольшую задержку
                        setTimeout(() => {
                            window.location.href = '{% url "create_database_step2" %}';
                        }, 2000);
                    }
                }
            } catch (e) {
                // Если не JSON, игнорируем
            }
        }
    });
});