document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('create-db-form');
    const submitBtn = form.querySelector('button[type="submit"]');
    const container = document.getElementById('create-db-progress-container');
    const bar = document.getElementById('db-progress');

    // Отслеживаем начало HTMX запроса
    form.addEventListener('htmx:beforeRequest', () => {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="bi bi-database-gear spinner-border spinner-border-sm me-1" role="status"></i>Wird erstellt...';

        // Показываем прогресс-бар и детали
        document.getElementById('db-progress-label').style.visibility = 'visible';
        document.getElementById('db-progress-bar-container').style.visibility = 'visible';
        document.getElementById('collection-progress').style.visibility = 'visible';
        bar.style.width = '0%';

        // Список коллекций для симуляции
        const collections = [
            'Initialisierung...',
            'basic_communications',
            'basic_countrys',
            'basic_payments',
            'basic_roles',
            'basic_salutations',
            'basic_titles',
            'basic_units',
            'system_info',
            'Abschluss...'
        ];

        let progress = 0;
        let collectionIndex = 0;
        const currentCollectionSpan = document.getElementById('current-collection');

        window.dbProgressInterval = setInterval(() => {
            progress += Math.floor(Math.random() * 8) + 5;
            if (progress > 95) progress = 95;

            bar.style.width = progress + '%';

            // Обновляем текущую коллекцию
            const expectedCollectionIndex = Math.floor((progress / 100) * collections.length);
            if (expectedCollectionIndex !== collectionIndex && expectedCollectionIndex < collections.length) {
                collectionIndex = expectedCollectionIndex;
                currentCollectionSpan.innerHTML = `Erstelle: ${collections[collectionIndex]}`;

                // Добавляем небольшую анимацию при смене коллекции
                currentCollectionSpan.style.opacity = '0.6';
                setTimeout(() => {
                    currentCollectionSpan.style.opacity = '1';
                }, 150);
            }
        }, 300);
    });

    // Отслеживаем завершение HTMX запроса
    form.addEventListener('htmx:afterRequest', (event) => {
        clearInterval(window.dbProgressInterval);

        // Проверяем успешность запроса
        if (event.detail.xhr.status === 200) {
            bar.style.width = '100%';
            bar.classList.remove('bg-danger');
            bar.classList.add('bg-success');
        } else {
            bar.classList.remove('bg-primary');
            bar.classList.add('bg-danger');
            bar.style.width = '100%';
        }

        setTimeout(() => {
            // Финальные сообщения
            const currentCollectionSpan = document.getElementById('current-collection');
            if (event.detail.xhr.status === 200) {
                currentCollectionSpan.innerHTML = '✓ Alle Kollektionen erfolgreich erstellt!';
                currentCollectionSpan.style.color = '#198754';
            } else {
                currentCollectionSpan.innerHTML = '✗ Fehler beim Erstellen der Kollektionen';
                currentCollectionSpan.style.color = '#dc3545';
            }

            setTimeout(() => {
                // Скрываем прогресс-бар и детали
                document.getElementById('db-progress-label').style.visibility = 'hidden';
                document.getElementById('db-progress-bar-container').style.visibility = 'hidden';
                document.getElementById('collection-progress').style.visibility = 'hidden';
                bar.style.width = '0%';
                bar.classList.remove('bg-danger', 'bg-success');
                bar.classList.add('bg-primary');
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-database-add me-1"></i>{{ text.btn }}';

                // Сброс стилей текста
                currentCollectionSpan.style.color = '';
                currentCollectionSpan.innerHTML = 'Initialisierung...';
            }, 2000);
        }, 500);
    });

    // Обработка успешного создания БД для перенаправления
    document.body.addEventListener('htmx:afterRequest', function (event) {
        if (event.target.id === 'create-db-form') {
            try {
                const response = JSON.parse(event.detail.xhr.responseText);
                if (response && response.messages) {
                    // Проверяем, есть ли сообщение об успехе
                    const hasSuccess = response.messages.some(msg => msg.tags === 'success');
                    if (hasSuccess) {
                        // Перенаправляем через небольшую задержку
                        setTimeout(() => {
                            window.location.href = '/';
                        }, 3000);
                    }
                }
            } catch (e) {
                // Если не JSON, игнорируем
            }
        }
    });
});
