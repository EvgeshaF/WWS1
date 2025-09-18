document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admin-step3-form');
    if (!form) return;

    const submitBtn = document.getElementById('create-admin-btn');
    const progressContainer = document.getElementById('create-admin-progress-container');
    const progressLabel = document.getElementById('admin-progress-label');
    const progressBar = document.getElementById('admin-progress');
    const creationDetails = document.getElementById('admin-creation-details');
    const currentStep = document.getElementById('current-step');

    let progressInterval = null;
    let creationSteps = [
        'Validierung der Eingaben...',
        'Benutzer wird erstellt...',
        'Berechtigungen werden gesetzt...',
        'Profildaten werden gespeichert...',
        'Sicherheitseinstellungen werden angewendet...',
        'Administrator wird aktiviert...'
    ];
    let currentStepIndex = 0;

    // Обработчик изменения чекбоксов для зависимостей
    const superAdminCheckbox = form.querySelector('input[name="is_super_admin"]');
    const otherPermissions = [
        'can_manage_users',
        'can_manage_database',
        'can_view_logs',
        'can_manage_settings'
    ];

    if (superAdminCheckbox) {
        superAdminCheckbox.addEventListener('change', function() {
            if (this.checked) {
                // При выборе Super Admin автоматически выбираем все остальные права
                otherPermissions.forEach(permName => {
                    const checkbox = form.querySelector(`input[name="${permName}"]`);
                    if (checkbox) {
                        checkbox.checked = true;
                        checkbox.disabled = true;
                    }
                });
            } else {
                // При снятии Super Admin разблокируем остальные права
                otherPermissions.forEach(permName => {
                    const checkbox = form.querySelector(`input[name="${permName}"]`);
                    if (checkbox) {
                        checkbox.disabled = false;
                    }
                });
            }
        });

        // Инициализируем состояние при загрузке
        if (superAdminCheckbox.checked) {
            superAdminCheckbox.dispatchEvent(new Event('change'));
        }
    }

    // Обработчик отправки формы
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Показываем прогресс и блокируем форму
        showProgress();

        // Создаем FormData для отправки
        const formData = new FormData(form);

        // FIXED: Corrected URL to use namespace
        fetch('/users/create-admin/step3/', {
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

                // Если есть успешное сообщение, перенаправляем на главную
                const hasSuccess = data.messages.some(msg => msg.tags === 'success');
                if (hasSuccess) {
                    // Показываем финальный шаг
                    if (currentStep) {
                        currentStep.textContent = 'Administrator erfolgreich erstellt!';
                    }

                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                }
            }
        })
        .catch(error => {
            console.error('Ошибка создания администратора:', error);
            hideProgress();
            showToast('Kritischer Fehler beim Erstellen des Administrators', 'error');
        });
    });

    function showProgress() {
        if (!submitBtn) return;

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird erstellt...';

        if (progressContainer) {
            progressContainer.style.display = 'block';
        }

        if (progressLabel) {
            progressLabel.style.visibility = 'visible';
        }

        if (creationDetails) {
            creationDetails.style.visibility = 'visible';
        }

        let progress = 0;
        currentStepIndex = 0;

        progressInterval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 90) progress = 90;

            if (progressBar) {
                progressBar.style.width = progress + '%';
            }

            // Обновляем текущий шаг
            if (currentStep && currentStepIndex < creationSteps.length - 1) {
                if (progress > (currentStepIndex + 1) * 15) {
                    currentStepIndex++;
                    currentStep.textContent = creationSteps[currentStepIndex];
                }
            }
        }, 400);
    }

    function hideProgress() {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }

        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-person-plus me-1"></i>Administrator erstellen';
        }

        // Завершаем прогресс-бар
        if (progressBar) {
            progressBar.style.width = '100%';
        }

        setTimeout(() => {
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
            if (progressBar) {
                progressBar.style.width = '0%';
            }
        }, 2000);
    }

    // Глобальная функция для показа тостов (если не определена)
    if (typeof window.showToast === 'undefined') {
        window.showToast = function(message, type = 'info', delay = 5000) {
            const toast = document.createElement('div');
            toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
            toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            toast.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;

            document.body.appendChild(toast);

            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, delay);
        };
    }
});