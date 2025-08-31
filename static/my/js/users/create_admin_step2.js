
        document.addEventListener('DOMContentLoaded', () => {
            const form = document.getElementById('admin-step2-form');
            const submitBtn = form.querySelector('button[type="submit"]');

            // Отслеживаем начало HTMX запроса
            form.addEventListener('htmx:beforeRequest', () => {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="bi bi-person-check spinner-border spinner-border-sm me-1" role="status"></i>Wird validiert...';
            });

            // Отслеживаем завершение HTMX запроса
            form.addEventListener('htmx:afterRequest', (event) => {
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i>{{ text.btn }}';
                }, 1000);
            });

            // Обработка успешной валидации для перенаправления
            document.body.addEventListener('htmx:afterRequest', function(event) {
                if (event.target.id === 'admin-step2-form') {
                    try {
                        const response = JSON.parse(event.detail.xhr.responseText);
                        if (response && response.messages) {
                            // Проверяем, есть ли сообщение об успехе
                            const hasSuccess = response.messages.some(msg => msg.tags === 'success');
                            if (hasSuccess) {
                                // Перенаправляем через небольшую задержку
                                setTimeout(() => {
                                    window.location.href = '{% url "create_admin_step3" %}';
                                }, 2000);
                            }
                        }
                    } catch (e) {
                        // Если не JSON, игнорируем
                    }
                }
            });
        });
