// company/static/js/company_info.js
// JavaScript для страницы информации о компании

document.addEventListener('DOMContentLoaded', function () {
    // Анимация прогресс-бара
    document.querySelectorAll('.completion-fill').forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => bar.style.width = width, 500);
    });

    // Подтверждение удаления
    const deleteForm = document.querySelector('#deleteCompanyModal form');
    if (deleteForm) {
        deleteForm.addEventListener('submit', function (e) {
            const companyNameElement = document.querySelector('[data-company-name]');
            const companyName = companyNameElement ? companyNameElement.dataset.companyName : 'diese Firma';
            if (!confirm(`Sind Sie sicher, dass Sie "${companyName}" löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.`)) {
                e.preventDefault();
            }
        });
    }

    // Клик по контактам для копирования
    document.querySelectorAll('a[href^="mailto:"], a[href^="tel:"]').forEach(link => {
        link.addEventListener('click', function (e) {
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                const text = this.textContent.trim();
                navigator.clipboard.writeText(text).then(() => {
                    showToast(`"${text}" in die Zwischenablage kopiert`, 'success', 2000);
                });
            }
        });
    });

    // Клик по IBAN для копирования
    document.querySelectorAll('.iban-display').forEach(iban => {
        iban.style.cursor = 'pointer';
        iban.title = 'Klicken zum Kopieren';
        iban.addEventListener('click', function () {
            const text = this.textContent.trim();
            navigator.clipboard.writeText(text.replace(/\s/g, '')).then(() => {
                showToast(`IBAN "${text}" in die Zwischenablage kopiert`, 'success', 2000);
            });
        });
    });

    // Hover эффекты для банковских данных
    document.querySelectorAll('.iban-display').forEach(iban => {
        iban.addEventListener('mouseenter', function () {
            this.style.backgroundColor = 'rgba(33, 150, 243, 0.2)';
            this.style.transform = 'scale(1.02)';
            this.style.transition = 'all 0.2s ease';
        });
        iban.addEventListener('mouseleave', function () {
            this.style.backgroundColor = 'rgba(33, 150, 243, 0.1)';
            this.style.transform = 'scale(1)';
        });
    });

    // Анимация появления банковских карточек
    if (document.querySelector('.banking-card')) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'slideInUp 0.5s ease-out';
                }
            });
        });

        document.querySelectorAll('.banking-card').forEach(card => {
            observer.observe(card);
        });
    }

    // Проверка наличия банковских данных и показ предупреждения
    const hasBankingDataElement = document.querySelector('[data-has-banking]');
    const hasBankingData = hasBankingDataElement ? hasBankingDataElement.dataset.hasBanking === 'true' : false;
    const editCompanyUrl = document.querySelector('[data-edit-url]')?.dataset.editUrl || '';
    
    if (!hasBankingData && editCompanyUrl) {
        // Показываем ненавязчивое предложение добавить банковские данные
        setTimeout(() => {
            const bankingReminder = document.createElement('div');
            bankingReminder.className = 'alert alert-info alert-dismissible fade show position-fixed';
            bankingReminder.style.cssText = 'bottom: 100px; right: 20px; z-index: 998; max-width: 350px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);';
            bankingReminder.innerHTML = `
                <h6 class="alert-heading">💡 Tipp: Bankdaten hinzufügen</h6>
                <p class="mb-2 small">Vervollständigen Sie Ihr Firmenprofil mit Bankverbindungsdaten für eine professionelle Rechnungsstellung.</p>
                <div class="d-flex gap-2">
                    <a href="${editCompanyUrl}" class="btn btn-info btn-sm">
                        <i class="bi bi-bank me-1"></i>Jetzt hinzufügen
                    </a>
                    <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-dismiss="alert">
                        Später
                    </button>
                </div>
            `;

            document.body.appendChild(bankingReminder);

            // Автоматически скрыть через 15 секунд
            setTimeout(() => {
                if (bankingReminder.parentNode) {
                    bankingReminder.remove();
                }
            }, 15000);
        }, 3000); // Показать через 3 секунды после загрузки
    }

    // Улучшенная анимация статистических карточек
    document.querySelectorAll('.stat-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.style.animation = 'fadeInUp 0.6s ease-out both';
    });

    // Эффект печатающегося текста для процента завершенности
    const completionText = document.querySelector('.completion-text');
    if (completionText) {
        const finalText = completionText.textContent;
        completionText.textContent = '0% vollständig';

        let currentPercent = 0;
        const targetPercent = parseInt(finalText);
        const increment = Math.ceil(targetPercent / 50);

        const counter = setInterval(() => {
            currentPercent += increment;
            if (currentPercent >= targetPercent) {
                currentPercent = targetPercent;
                clearInterval(counter);
            }
            completionText.textContent = `${currentPercent}% vollständig`;
        }, 30);
    }

    // Улучшенное копирование BIC кодов
    document.querySelectorAll('code').forEach(code => {
        if (code.textContent.match(/^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$/)) {
            code.style.cursor = 'pointer';
            code.title = 'BIC kopieren';
            code.addEventListener('click', function () {
                navigator.clipboard.writeText(this.textContent).then(() => {
                    showToast(`BIC "${this.textContent}" kopiert`, 'success', 2000);
                });
            });
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function (e) {
        // Ctrl+E для Bearbeiten
        if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
            e.preventDefault();
            const editButton = document.querySelector('a[href*="edit_company"]');
            if (editButton) {
                editButton.click();
            }
        }

        // Ctrl+D для Download/Export
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            const exportButton = document.querySelector('a[href*="export_company"]');
            if (exportButton) {
                exportButton.click();
            }
        }
    });

    // Показать подсказки о горячих клавишах
    const showKeyboardHints = () => {
        showToast('Tastenkombinationen: Strg+E (Bearbeiten), Strg+D (Export)', 'info', 4000);
    };

    // Показать подсказку через 10 секунд после загрузки
    setTimeout(showKeyboardHints, 10000);

    // Добавляем CSS анимации динамически
    addDynamicStyles();
});

// Функция уведомлений с улучшенными стилями
function showToast(message, type = 'info', delay = 3000) {
    const toast = document.createElement('div');
    const alertType = type === 'error' ? 'danger' : type;
    toast.className = `alert alert-${alertType} alert-dismissible fade show position-fixed`;
    toast.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 400px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border: none;
        border-radius: 10px;
    `;

    const icon = {
        'success': '✅',
        'info': 'ℹ️',
        'warning': '⚠️',
        'danger': '❌',
        'error': '❌'
    }[alertType] || 'ℹ️';

    toast.innerHTML = `
        <div class="d-flex align-items-center">
            <span class="me-2" style="font-size: 1.2em;">${icon}</span>
            <div class="flex-grow-1">${message}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    document.body.appendChild(toast);

    // Анимация появления
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    }, 10);

    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.transform = 'translateX(100%)';
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }
    }, delay);
}

// Добавляем CSS анимации динамически
function addDynamicStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInUp {
            from {
                transform: translateY(30px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        @keyframes fadeInUp {
            from {
                transform: translateY(20px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        .alert {
            transition: all 0.3s ease;
            transform: translateX(100%);
            opacity: 0;
        }

        .iban-display:hover {
            box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3) !important;
        }

        .floating-actions .btn {
            transition: all 0.2s ease;
        }

        .floating-actions .btn:hover {
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .stat-card {
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .stat-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(255, 255, 255, 0.3);
        }

        /* Улучшенные стили для badge */
        .bank-type-badge {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
            100% {
                transform: scale(1);
            }
        }

        /* Респонсивные улучшения */
        @media (max-width: 768px) {
            .floating-actions {
                flex-direction: column;
                gap: 0.25rem;
            }

            .floating-actions .btn {
                width: 100%;
                font-size: 0.875rem;
            }

            .iban-display {
                font-size: 0.9rem;
                word-break: break-all;
            }

            .alert {
                max-width: 90vw !important;
                min-width: auto !important;
            }
        }
    `;
    document.head.appendChild(style);
}