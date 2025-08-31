
        document.addEventListener('DOMContentLoaded', () => {
            const form = document.getElementById('admin-step3-form');
            const submitBtn = document.getElementById('create-admin-btn');
            const progressContainer = document.getElementById('create-admin-progress-container');
            const progressBar = document.getElementById('admin-progress');
            const currentStepSpan = document.getElementById('current-step');

            // Отслеживаем начало HTMX запроса
            form.addEventListener('htmx:beforeRequest', () => {
                console.log('🚀 Начинаем создание администратора...');

                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split spinner-border spinner-border-sm me-1" role="status"></i>Wird erstellt...';

                // Показываем прогресс-бар
                progressContainer.style.display = 'block';
                progressBar.style.width = '0%';
                currentStepSpan.textContent = 'Validierung der Eingaben...';

                // Симулируем прогресс
                let progress = 0;
                const steps = [
                    'Validierung der Eingaben...',
                    'Verbindung zur Datenbank...',
                    'Überprüfung auf doppelte Benutzer...',
                    'Erstelle Administrator...',
                    'Speichern in der Datenbank...',
                    'Überprüfung der Speicherung...',
                    'Abschluss...'
                ];

                let stepIndex = 0;
                window.adminProgressInterval = setInterval(() => {
                    progress += Math.floor(Math.random() * 12) + 8;
                    if (progress > 95) progress = 95;

                    progressBar.style.width = progress + '%';

                    // Обновляем текущий шаг
                    const expectedStepIndex = Math.floor((progress / 100) * steps.length);
                    if (expectedStepIndex !== stepIndex && expectedStepIndex < steps.length) {
                        stepIndex = expectedStepIndex;
                        currentStepSpan.textContent = steps[stepIndex];

                        // Анимация смены шага
                        currentStepSpan.style.opacity = '0.6';
                        setTimeout(() => {
                            currentStepSpan.style.opacity = '1';
                        }, 200);
                    }
                }, 400);
            });

            // Отслеживаем завершение HTMX запроса
            form.addEventListener('htmx:afterRequest', (event) => {
                console.log('📋 HTMX запрос завершен:', event.detail.xhr.status);

                clearInterval(window.adminProgressInterval);

                const xhr = event.detail.xhr;

                if (xhr.status === 200) {
                    console.log('✅ HTTP 200 - запрос успешен');

                    progressBar.style.width = '100%';
                    progressBar.classList.remove('bg-danger');
                    progressBar.classList.add('bg-success');
                    currentStepSpan.textContent = 'Administrator erfolgreich erstellt!';
                    currentStepSpan.style.color = '#198754';

                } else {
                    console.log('❌ HTTP ошибка:', xhr.status);

                    progressBar.classList.remove('bg-success');
                    progressBar.classList.add('bg-danger');
                    progressBar.style.width = '100%';
                    currentStepSpan.textContent = 'Fehler beim Erstellen!';
                    currentStepSpan.style.color = '#dc3545';
                }

                // Скрываем прогресс через 2 секунды
                setTimeout(() => {
                    progressContainer.style.display = 'none';
                    progressBar.style.width = '0%';
                    progressBar.classList.remove('bg-danger', 'bg-success');
                    progressBar.classList.add('bg-success');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-person-plus me-1"></i>{{ text.btn }}';

                    // Сброс стилей
                    currentStepSpan.style.color = '';
                    currentStepSpan.textContent = 'Validierung...';
                }, 2000);
            });

            // УЛУЧШЕННАЯ обработка успешного создания администратора
            document.body.addEventListener('htmx:afterRequest', function (event) {
                if (event.target.id === 'admin-step3-form') {
                    const xhr = event.detail.xhr;
                    console.log('🔍 Анализируем ответ...', {
                        status: xhr.status,
                        responseText: xhr.responseText.substring(0, 200) + '...'
                    });

                    if (xhr.status === 200) {
                        try {
                            const response = JSON.parse(xhr.responseText);
                            console.log('📄 JSON ответ:', response);

                            if (response && response.messages && Array.isArray(response.messages)) {
                                // Ищем сообщение об успехе
                                const hasSuccess = response.messages.some(msg => {
                                    const isSuccess = msg.tags === 'success' &&
                                        (msg.text.includes('erfolgreich erstellt') ||
                                         msg.text.includes('successfully created'));
                                    console.log('🔍 Проверяем сообщение:', {
                                        tags: msg.tags,
                                        text: msg.text.substring(0, 50) + '...',
                                        isSuccess: isSuccess
                                    });
                                    return isSuccess;
                                });

                                if (hasSuccess) {
                                    console.log('🎉 УСПЕХ! Администратор создан, перенаправляем...');

                                    // Показываем финальное уведомление
                                    showToast(
                                        'Administrator wurde erfolgreich erstellt! Weiterleitung zur Startseite...',
                                        'success',
                                        4000
                                    );

                                    // Перенаправляем через 4 секунды
                                    setTimeout(() => {
                                        console.log('🔄 Выполняем перенаправление на главную...');
                                        window.location.href = '/';
                                    }, 4000);
                                } else {
                                    console.log('⚠️  Сообщение об успехе не найдено');

                                    // Проверяем наличие ошибок
                                    const hasError = response.messages.some(msg =>
                                        msg.tags === 'error' || msg.tags === 'danger'
                                    );

                                    if (hasError) {
                                        console.log('❌ Найдены ошибки в ответе');
                                    }
                                }
                            } else {
                                console.log('⚠️  Неожиданная структура ответа:', response);
                            }
                        } catch (e) {
                            console.error('❌ Ошибка парсинга JSON:', e);
                            console.log('📄 Сырой ответ:', xhr.responseText);

                            // Если JSON не парсится, но статус 200, возможно произошел редирект
                            if (xhr.responseText.includes('erfolgreich') ||
                                xhr.responseText.includes('success') ||
                                xhr.responseText.includes('Administrator')) {
                                console.log('🔍 Обнаружен успех в тексте ответа');
                                setTimeout(() => {
                                    console.log('🔄 Перенаправляем по тексту...');
                                    window.location.href = '/';
                                }, 3000);
                            }
                        }
                    } else {
                        console.error('❌ HTTP ошибка:', xhr.status, xhr.statusText);
                    }
                }
            });

            // Включаем/отключаем зависимые чекбоксы
            const superAdminCheckbox = document.getElementById('{{ form.is_super_admin.id_for_label }}');
            const dependentCheckboxes = [
                document.getElementById('{{ form.can_manage_users.id_for_label }}'),
                document.getElementById('{{ form.can_manage_database.id_for_label }}'),
                document.getElementById('{{ form.can_view_logs.id_for_label }}'),
                document.getElementById('{{ form.can_manage_settings.id_for_label }}')
            ];

            if (superAdminCheckbox) {
                superAdminCheckbox.addEventListener('change', function () {
                    dependentCheckboxes.forEach(checkbox => {
                        if (checkbox) {
                            checkbox.checked = this.checked;
                            checkbox.disabled = this.checked;

                            // Визуальная индикация
                            const label = checkbox.closest('.form-check');
                            if (this.checked) {
                                label.style.opacity = '0.6';
                            } else {
                                label.style.opacity = '1';
                            }
                        }
                    });
                });

                // Инициализация состояния при загрузке
                if (superAdminCheckbox.checked) {
                    superAdminCheckbox.dispatchEvent(new Event('change'));
                }
            }
        });

