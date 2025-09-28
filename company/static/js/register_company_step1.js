                                                 document.addEventListener('DOMContentLoaded', function () {
    console.log('Инициализируем Select2 для шага 1 компании');

    // Настройки локализации
    $.fn.select2.defaults.set('language', 'de');

    const legalForm = document.querySelector('#legal_form');
    const ceoSalutation = document.querySelector('#ceo_salutation');
    const ceoTitle = document.querySelector('#ceo_title');

    // ==================== Rechtsform ====================
    if (legalForm) {
        $(`#${legalForm.dataset.fieldId}`).select2({
            theme: 'bootstrap-5',
            placeholder: 'Rechtsform auswählen...',
            allowClear: false,
            minimumResultsForSearch: Infinity,
            width: '100%'
        }).on('select2:select', function (e) {
            console.log('Выбрана rechtsform:', e.params.data.id, '-', e.params.data.text);
            $(this).closest('.mb-3').find('.invalid-feedback').hide();
        });
    }

    // ==================== CEO Anrede ====================
    if (ceoSalutation) {
        $(`#${ceoSalutation.dataset.fieldId}`).select2({
            theme: 'bootstrap-5',
            placeholder: 'Anrede auswählen...',
            allowClear: false,
            minimumResultsForSearch: Infinity,
            width: '100%'
        }).on('select2:select', function (e) {
            console.log('Выбрана CEO Anrede:', e.params.data.id, '-', e.params.data.text);
            $(this).closest('.mb-3').find('.invalid-feedback').hide();
        });
    }

    // ==================== CEO Titel ====================
    if (ceoTitle) {
        $(`#${ceoTitle.dataset.fieldId}`).select2({
            theme: 'bootstrap-5',
            placeholder: 'Titel suchen oder auswählen...',
            allowClear: true,
            width: '100%',
            language: {
                noResults: () => 'Keine Ergebnisse gefunden',
                searching: () => 'Suche läuft...',
                inputTooShort: () => 'Bitte geben Sie mindestens 1 Zeichen ein',
                removeAllItems: () => 'Alle Elemente entfernen'
            },
            matcher: function (params, data) {
                if ($.trim(params.term) === '') return data;
                if (typeof data.text === 'undefined') return null;
                const term = params.term.toLowerCase();
                if (data.text.toLowerCase().includes(term) || data.id.toLowerCase().includes(term)) {
                    return data;
                }
                return null;
            }
        }).on('select2:select', function (e) {
            console.log('Выбран CEO Titel:', e.params.data.id, '-', e.params.data.text);
            $(this).closest('.mb-3').find('.invalid-feedback').hide();
        }).on('select2:clear', function () {
            console.log('CEO Titel очищен');
        });
    }

    console.log('Select2 для шага 1 компании успешно инициализирован');

    // ===== Закрытие модального окна =====
    window.closeModal = function () {
        if (confirm('Möchten Sie das Fenster schließen? Ungesicherte Änderungen gehen verloren.')) {
            window.location.href = '/';
        }
    };

    // ===== Обработка формы =====
    const form = document.getElementById('company-step1-form');
    if (!form) return;

    const continueBtn = document.getElementById('continue-btn');
    const saveAndCloseBtn = document.getElementById('save-and-close-btn');
    const postUrl = form.dataset.url;
    const nextUrl = form.dataset.nextUrl;

    if (saveAndCloseBtn) {
        saveAndCloseBtn.addEventListener('click', function () {
            submitForm('save_and_close');
        });
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        submitForm('continue');
    });

    function submitForm(action) {
        const activeBtn = action === 'save_and_close' ? saveAndCloseBtn : continueBtn;

        if (activeBtn) {
            activeBtn.disabled = true;
            activeBtn.innerHTML = action === 'save_and_close'
                ? '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird gesichert...'
                : '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird validiert...';
        }

        const formData = new FormData(form);
        formData.append('action', action);

        fetch(postUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'HX-Request': 'true'
            }
        })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (activeBtn) {
                    activeBtn.disabled = false;
                    activeBtn.innerHTML = action === 'save_and_close'
                        ? '<i class="bi bi-check-circle me-1"></i>Sichern & Schließen'
                        : '<i class="bi bi-arrow-right me-1"></i>Weiter';
                }

                if (data.success !== undefined && data.action === 'save_and_close') {
                    if (data.messages) {
                        data.messages.forEach(msg => showToast(msg.text, msg.tags, msg.delay));
                    }
                    if (data.success) {
                        setTimeout(() => {
                            window.location.href = data.redirect_url || '/';
                        }, 1500);
                    }
                    return;
                }

                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(msg => showToast(msg.text, msg.tags, msg.delay));

                    const hasSuccess = data.messages.some(msg => msg.tags === 'success');
                    if (hasSuccess && action === 'continue') {
                        setTimeout(() => {
                            window.location.href = nextUrl;
                        }, 1500);
                    }
                }
            })
            .catch(error => {
                console.error('Ошибка отправки формы:', error);
                if (activeBtn) {
                    activeBtn.disabled = false;
                    activeBtn.innerHTML = action === 'save_and_close'
                        ? '<i class="bi bi-check-circle me-1"></i>Sichern & Schließen'
                        : '<i class="bi bi-arrow-right me-1"></i>Weiter';
                }
                showToast('Fehler beim Senden des Formulars', 'error');
            });
    }
});

// ===== Глобальная функция тостов =====
if (typeof window.showToast === 'undefined') {
    window.showToast = function (message, type = 'info', delay = 5000) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(toast);
        setTimeout(() => {
            if (toast.parentNode) toast.remove();
        }, delay);
    };
}
