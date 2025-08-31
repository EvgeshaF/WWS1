
        document.addEventListener('DOMContentLoaded', () => {
            const form = document.getElementById('mongo-login-form');
            const submitBtn = form.querySelector('button[type="submit"]');
            const container = document.getElementById('auth-progress-container');
            const bar = document.getElementById('auth-progress');

            // Отслеживаем начало HTMX запроса
            form.addEventListener('htmx:beforeRequest', () => {
                submitBtn.disabled = true;       // Деактивируем кнопку

                // Показываем прогресс-бар
                document.getElementById('auth-progress-label').style.visibility = 'visible';
                document.getElementById('auth-progress-bar-container').style.visibility = 'visible';
                bar.style.width = '0%';

                let progress = 0;
                window.authProgressInterval = setInterval(() => {
                    progress += Math.floor(Math.random() * 15) + 10;
                    if (progress > 85) progress = 85;
                    bar.style.width = progress + '%';
                }, 300);
            });

            // Отслеживаем завершение HTMX запроса
            form.addEventListener('htmx:afterRequest', (event) => {
                clearInterval(window.authProgressInterval);

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
                    document.getElementById('auth-progress-label').style.visibility = 'hidden';
                    document.getElementById('auth-progress-bar-container').style.visibility = 'hidden';
                    bar.style.width = '0%';
                    bar.classList.remove('bg-danger', 'bg-primary');
                    submitBtn.disabled = false;   // Включаем кнопку обратно
                }, 1000);
            });

            // Обработка успешной авторизации для перенаправления
            document.body.addEventListener('htmx:afterRequest', function(event) {
                if (event.target.id === 'mongo-login-form') {
                    try {
                        const response = JSON.parse(event.detail.xhr.responseText);
                        if (response && response.messages) {
                            // Проверяем, есть ли сообщение об успехе
                            const hasSuccess = response.messages.some(msg => msg.tags === 'success');
                            if (hasSuccess) {
                                // Перенаправляем через небольшую задержку
                                setTimeout(() => {
                                    window.location.href = '/';
                                }, 2000);
                            }
                        }
                    } catch (e) {
                        // Если не JSON, игнорируем
                    }
                }
            });
        });
