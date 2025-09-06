// Исправленный файл create_admin_step2.js с улучшенной обработкой ошибок

// Управление контактами
class ContactManager {
    constructor() {
        this.contacts = [];
        this.editingIndex = -1;
        this.contactTypeLabels = {
            'email': 'E-Mail',
            'phone': 'Telefon',
            'mobile': 'Mobil',
            'fax': 'Fax',
            'website': 'Website',
            'linkedin': 'LinkedIn',
            'xing': 'XING',
            'other': 'Sonstige'
        };
        this.contactTypeIcons = {
            'email': 'bi-envelope',
            'phone': 'bi-telephone',
            'mobile': 'bi-phone',
            'fax': 'bi-printer',
            'website': 'bi-globe',
            'linkedin': 'bi-linkedin',
            'xing': 'bi-person-badge',
            'other': 'bi-question-circle'
        };
    }

    init() {
        this.bindEvents();
        this.updateTable();
        this.setupValidation();
        this.setupFormSubmission();
    }

    bindEvents() {
        // Кнопка добавления контакта
        const addBtn = document.getElementById('addContactBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => {
                this.openModal();
            });
        }

        // Кнопка сохранения в модальном окне
        const saveBtn = document.getElementById('saveContactBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveContact();
            });
        }

        // Кнопка подтверждения удаления
        const confirmBtn = document.getElementById('confirmDeleteBtn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                this.deleteContact();
            });
        }

        // Изменение типа контакта для динамических подсказок
        const typeSelect = document.getElementById('contactType');
        if (typeSelect) {
            typeSelect.addEventListener('change', (e) => {
                this.updateContactHints(e.target.value);
            });
        }

        // Валидация в реальном времени
        const valueInput = document.getElementById('contactValue');
        if (valueInput) {
            valueInput.addEventListener('input', () => {
                this.validateContactValue();
            });
        }

        // Сброс формы при закрытии модального окна
        const modal = document.getElementById('contactModal');
        if (modal) {
            modal.addEventListener('hidden.bs.modal', () => {
                this.resetForm();
            });
        }
    }

    setupFormSubmission() {
        const form = document.getElementById('admin-step2-form');
        if (!form) return;

        // Обработчик отправки формы
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            // Валидируем основные поля
            const firstNameInput = form.querySelector('input[name="first_name"]');
            const lastNameInput = form.querySelector('input[name="last_name"]');
            const salutationSelect = form.querySelector('select[name="salutation"]');

            const isValid = this.validateRequired(firstNameInput, 'Vorname ist erforderlich') &&
                            this.validateRequired(lastNameInput, 'Nachname ist erforderlich') &&
                            this.validateSalutation(salutationSelect);

            // Валидируем контакты
            const contactsValid = this.validateAllContacts();

            if (!isValid || !contactsValid) {
                this.showAlert('Bitte korrigieren Sie die Fehler im Formular', 'error');
                return;
            }

            // Показываем прогресс
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird gespeichert...';
            }

            // Создаем FormData для отправки
            const formData = new FormData(form);

            // Добавляем данные контактов
            const contactsData = this.getContactsData();
            formData.append('contacts_data', JSON.stringify(contactsData));

            // ИСПРАВЛЕНО: улучшенная обработка ошибок
            fetch('/users/create-admin/step2/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'HX-Request': 'true'
                }
            })
            .then(response => {
                console.log('Response status:', response.status);
                console.log('Response headers:', response.headers);

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                // Проверяем Content-Type
                const contentType = response.headers.get('Content-Type');
                console.log('Content-Type:', contentType);

                if (!contentType || !contentType.includes('application/json')) {
                    // Если не JSON, читаем как текст для отладки
                    return response.text().then(text => {
                        console.error('Non-JSON response:', text);
                        throw new Error('Server returned non-JSON response');
                    });
                }

                return response.json();
            })
            .then(data => {
                console.log('JSON response:', data);

                // Скрываем прогресс
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i>Weiter zu Schritt 3';
                }

                // Обрабатываем сообщения
                if (data.messages && Array.isArray(data.messages)) {
                    data.messages.forEach(message => {
                        this.showAlert(message.text, message.tags);
                    });

                    // Если есть успешное сообщение, перенаправляем через короткое время
                    const hasSuccess = data.messages.some(msg => msg.tags === 'success');
                    if (hasSuccess) {
                        setTimeout(() => {
                            window.location.href = '/users/create-admin/step3/';
                        }, 1500);
                    }
                } else {
                    console.warn('No messages in response or messages is not array:', data);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);

                // Скрываем прогресс
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i>Weiter zu Schritt 3';
                }

                // Показываем ошибку пользователю
                if (error.message.includes('non-JSON')) {
                    this.showAlert('Server hat eine ungültige Antwort gesendet. Bitte versuchen Sie es erneut.', 'error');
                } else {
                    this.showAlert('Fehler beim Speichern des Profils: ' + error.message, 'error');
                }
            });
        });
    }

    // Вспомогательные функции валидации
    validateRequired(field, errorMessage) {
        if (!field) return false;

        const value = field.value.trim();
        this.clearFieldError(field);

        if (value === '') {
            this.setFieldError(field, errorMessage);
            return false;
        }

        if (value.length > 50) {
            this.setFieldError(field, 'Maximal 50 Zeichen erlaubt');
            return false;
        }

        this.setFieldSuccess(field);
        return true;
    }

    validateSalutation(salutationSelect) {
        if (!salutationSelect) return true;

        const value = salutationSelect.value;
        this.clearFieldError(salutationSelect);

        if (!value) {
            this.setFieldError(salutationSelect, 'Anrede ist erforderlich');
            return false;
        }

        this.setFieldSuccess(salutationSelect);
        return true;
    }

    setFieldError(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');

        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        field.closest('.mb-3').appendChild(errorDiv);
    }

    setFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');

        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');

        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    setupValidation() {
        const form = document.getElementById('contactForm');
        if (!form) return;

        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });
    }

    openModal(index = -1) {
        this.editingIndex = index;
        const modalElement = document.getElementById('contactModal');
        if (!modalElement) return;

        const modal = new bootstrap.Modal(modalElement);
        const modalTitle = document.getElementById('contactModalLabel');
        const saveBtn = document.getElementById('saveContactBtn');

        if (index >= 0) {
            // Режим редактирования
            const contact = this.contacts[index];
            modalTitle.innerHTML = '<i class="bi bi-pencil me-2"></i>Kontakt bearbeiten';
            saveBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Aktualisieren';

            // Заполняем форму данными
            this.setFieldValue('contactType', contact.type);
            this.setFieldValue('contactValue', contact.value);
            this.setFieldValue('contactLabel', contact.label || '');
            this.setCheckboxValue('contactPrimary', contact.primary || false);

            this.updateContactHints(contact.type);
        } else {
            // Режим добавления
            modalTitle.innerHTML = '<i class="bi bi-person-vcard me-2"></i>Kontakt hinzufügen';
            saveBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Speichern';
            this.resetForm();
        }

        modal.show();
    }

    setFieldValue(fieldId, value) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.value = value;
        }
    }

    setCheckboxValue(fieldId, checked) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.checked = checked;
        }
    }

    resetForm() {
        const form = document.getElementById('contactForm');
        if (!form) return;

        form.reset();

        // Очищаем валидацию
        form.querySelectorAll('.is-invalid, .is-valid').forEach(el => {
            el.classList.remove('is-invalid', 'is-valid');
        });

        this.updateContactHints('');
    }

    updateContactHints(type) {
        const valueInput = document.getElementById('contactValue');
        const hintElement = document.getElementById('contactHint');

        if (!valueInput || !hintElement) return;

        const hints = {
            'email': 'Geben Sie eine gültige E-Mail-Adresse ein (z.B. max@example.com)',
            'phone': 'Geben Sie eine Telefonnummer ein (z.B. +49 123 456789)',
            'mobile': 'Geben Sie eine Mobilnummer ein (z.B. +49 170 1234567)',
            'fax': 'Geben Sie eine Faxnummer ein (z.B. +49 123 456789)',
            'website': 'Geben Sie eine Website-URL ein (z.B. https://www.example.com)',
            'linkedin': 'Geben Sie Ihr LinkedIn-Profil ein (z.B. linkedin.com/in/username)',
            'xing': 'Geben Sie Ihr XING-Profil ein (z.B. xing.com/profile/username)',
            'other': 'Geben Sie die entsprechenden Kontaktdaten ein'
        };

        const placeholders = {
            'email': 'beispiel@domain.com',
            'phone': '+49 123 456789',
            'mobile': '+49 170 1234567',
            'fax': '+49 123 456789',
            'website': 'https://www.example.com',
            'linkedin': 'linkedin.com/in/username',
            'xing': 'xing.com/profile/username',
            'other': 'Kontaktdaten eingeben...'
        };

        if (type && hints[type]) {
            hintElement.innerHTML = `<i class="bi bi-lightbulb me-1"></i>${hints[type]}`;
            valueInput.placeholder = placeholders[type];
        } else {
            hintElement.innerHTML = '<i class="bi bi-lightbulb me-1"></i>Geben Sie die entsprechenden Kontaktdaten ein';
            valueInput.placeholder = 'Kontaktdaten eingeben...';
        }
    }

    validateField(field) {
        if (!field) return true;

        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        switch (field.id) {
            case 'contactType':
                if (!value) {
                    isValid = false;
                    errorMessage = 'Kontakttyp ist erforderlich';
                }
                break;

            case 'contactValue':
                if (!value) {
                    isValid = false;
                    errorMessage = 'Kontaktdaten sind erforderlich';
                } else {
                    isValid = this.validateContactValue();
                    if (!isValid) {
                        errorMessage = this.getValidationError();
                    }
                }
                break;
        }

        this.setFieldValidation(field, isValid, errorMessage);
        return isValid;
    }

    validateContactValue() {
        const typeField = document.getElementById('contactType');
        const valueField = document.getElementById('contactValue');

        if (!typeField || !valueField) return false;

        const type = typeField.value;
        const value = valueField.value.trim();

        if (!value) return false;

        switch (type) {
            case 'email':
                return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
            case 'phone':
            case 'mobile':
            case 'fax':
                return /^[\+]?[0-9\s\-\(\)]{7,20}$/.test(value);
            case 'website':
                return /^https?:\/\/.+\..+$/.test(value) || /^www\..+\..+$/.test(value);
            case 'linkedin':
                return value.includes('linkedin.com') || /^[a-zA-Z0-9\-_]+$/.test(value);
            case 'xing':
                return value.includes('xing.com') || /^[a-zA-Z0-9\-_]+$/.test(value);
            default:
                return value.length >= 3;
        }
    }

    getValidationError() {
        const typeField = document.getElementById('contactType');
        if (!typeField) return 'Ungültiges Format';

        const type = typeField.value;

        const errors = {
            'email': 'Ungültiges E-Mail-Format',
            'phone': 'Ungültiges Telefonformat',
            'mobile': 'Ungültiges Mobilnummer-Format',
            'fax': 'Ungültiges Faxnummer-Format',
            'website': 'Ungültiges Website-Format (muss mit http:// oder https:// beginnen)',
            'linkedin': 'Ungültiges LinkedIn-Profil-Format',
            'xing': 'Ungültiges XING-Profil-Format',
            'other': 'Kontaktdaten müssen mindestens 3 Zeichen lang sein'
        };

        return errors[type] || 'Ungültiges Format';
    }

    setFieldValidation(field, isValid, errorMessage = '') {
        if (!field) return;

        const feedback = field.parentElement.querySelector('.invalid-feedback');

        field.classList.remove('is-valid', 'is-invalid');

        if (isValid) {
            field.classList.add('is-valid');
            if (feedback) feedback.textContent = '';
        } else {
            field.classList.add('is-invalid');
            if (feedback) feedback.textContent = errorMessage;
        }
    }

    saveContact() {
        const form = document.getElementById('contactForm');
        if (!form) return;

        const typeField = document.getElementById('contactType');
        const valueField = document.getElementById('contactValue');
        const labelField = document.getElementById('contactLabel');
        const primaryField = document.getElementById('contactPrimary');

        // Валидируем все поля
        const isTypeValid = this.validateField(typeField);
        const isValueValid = this.validateField(valueField);

        if (!isTypeValid || !isValueValid) {
            this.showAlert('Bitte korrigieren Sie die Fehler im Formular', 'error');
            return;
        }

        const contactData = {
            type: typeField.value,
            value: valueField.value.trim(),
            label: labelField ? labelField.value.trim() : '',
            primary: primaryField ? primaryField.checked : false
        };

        // Если это основной контакт, снимаем флаг с других
        if (contactData.primary) {
            this.contacts.forEach(contact => contact.primary = false);
        }

        if (this.editingIndex >= 0) {
            // Обновляем существующий контакт
            this.contacts[this.editingIndex] = contactData;
            this.showAlert('Kontakt erfolgreich aktualisiert', 'success');
        } else {
            // Добавляем новый контакт
            this.contacts.push(contactData);
            this.showAlert('Kontakt erfolgreich hinzugefügt', 'success');
        }

        this.updateTable();
        this.updateContactsDataInput();

        // Закрываем модальное окно
        const modalElement = document.getElementById('contactModal');
        if (modalElement) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) {
                modal.hide();
            }
        }
    }

    confirmDelete(index) {
        this.deletingIndex = index;
        const modalElement = document.getElementById('deleteContactModal');
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }
    }

    deleteContact() {
        if (this.deletingIndex >= 0) {
            this.contacts.splice(this.deletingIndex, 1);
            this.updateTable();
            this.updateContactsDataInput();
            this.showAlert('Kontakt erfolgreich gelöscht', 'info');

            const modalElement = document.getElementById('deleteContactModal');
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                }
            }
        }
    }

    updateTable() {
        const tableBody = document.getElementById('contactsTableBody');
        const placeholder = document.getElementById('emptyContactsPlaceholder');
        const table = document.getElementById('contactsTable');

        if (!tableBody || !placeholder || !table) return;

        if (this.contacts.length === 0) {
            table.style.display = 'none';
            placeholder.style.display = 'block';
            return;
        }

        table.style.display = 'table';
        placeholder.style.display = 'none';

        tableBody.innerHTML = this.contacts.map((contact, index) => {
            return this.createContactRow(contact, index);
        }).join('');
    }

    createContactRow(contact, index) {
        const typeIcon = this.contactTypeIcons[contact.type] || 'bi-question-circle';
        const typeLabel = this.contactTypeLabels[contact.type] || contact.type;
        const primaryStar = contact.primary ? '<i class="bi bi-star-fill primary-contact-star me-1" title="Hauptkontakt"></i>' : '';
        const labelText = contact.label ? `<div class="contact-label">${this.escapeHtml(contact.label)}</div>` : '';

        return `
            <tr>
                <td>
                    <span class="contact-type-badge contact-type-${contact.type}">
                        <i class="bi ${typeIcon} me-1"></i>
                        ${typeLabel}
                    </span>
                    ${labelText}
                </td>
                <td>
                    ${primaryStar}
                    <code class="contact-value">${this.escapeHtml(contact.value)}</code>
                </td>
                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-outline-primary action-btn me-1" 
                            onclick="contactManager.openModal(${index})" 
                            title="Bearbeiten">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-danger action-btn" 
                            onclick="contactManager.confirmDelete(${index})" 
                            title="Löschen">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    updateContactsDataInput() {
        const input = document.getElementById('contactsDataInput');
        if (input) {
            input.value = JSON.stringify(this.contacts);
            console.log('Обновлены данные контактов в скрытом поле:', this.contacts.length);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showAlert(message, type = 'info') {
        // Используем глобальную функцию showToast если есть, иначе простой alert
        if (typeof window.showToast === 'function') {
            window.showToast(message, type);
        } else {
            // Создаем простой toast если нет глобальной функции
            this.createSimpleToast(message, type);
        }
    }

    createSimpleToast(message, type) {
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
        }, 5000);
    }

    // Валидация всех контактов для отправки формы
    validateAllContacts() {
        if (this.contacts.length === 0) {
            this.showAlert('Bitte fügen Sie mindestens einen Kontakt hinzu', 'warning');
            return false;
        }

        // Проверяем наличие email
        const hasEmail = this.contacts.some(contact => contact.type === 'email');
        if (!hasEmail) {
            this.showAlert('Bitte fügen Sie mindestens eine E-Mail-Adresse hinzu', 'warning');
            return false;
        }

        return true;
    }

    // Метод для получения данных контактов
    getContactsData() {
        return this.contacts;
    }

    // Метод для загрузки существующих контактов
    loadContacts(contactsData) {
        if (Array.isArray(contactsData)) {
            this.contacts = contactsData;
            this.updateTable();
            this.updateContactsDataInput();
        }
    }
}

// Основной код для формы Step 2
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admin-step2-form');
    if (!form) return;

    // Инициализируем менеджер контактов
    window.contactManager = new ContactManager();
    contactManager.init();

    // Если есть существующие данные контактов, загружаем их
    const existingContacts = window.initialContactsData || [];
    if (existingContacts.length > 0) {
        contactManager.loadContacts(existingContacts);
    }

    console.log('Create Admin Step 2 с Contact Manager инициализирован');
    console.log('Загружено контактов:', existingContacts.length);
});