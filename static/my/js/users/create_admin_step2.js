document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admin-step2-form');
    if (!form) return;

    const submitBtn = form.querySelector('button[type="submit"]');
    const emailInput = form.querySelector('input[name="email"]');
    const phoneInput = form.querySelector('input[name="phone"]');
    const firstNameInput = form.querySelector('input[name="first_name"]');
    const lastNameInput = form.querySelector('input[name="last_name"]');
    const salutationSelect = form.querySelector('select[name="salutation"]');

    // Валидация в реальном времени
    if (emailInput) {
        emailInput.addEventListener('input', validateEmail);
        emailInput.addEventListener('blur', validateEmail);
    }

    if (phoneInput) {
        phoneInput.addEventListener('input', validatePhone);
        phoneInput.addEventListener('blur', validatePhone);
    }

    if (firstNameInput) {
        firstNameInput.addEventListener('blur', validateRequired.bind(null, firstNameInput, 'Vorname ist erforderlich'));
    }

    if (lastNameInput) {
        lastNameInput.addEventListener('blur', validateRequired.bind(null, lastNameInput, 'Nachname ist erforderlich'));
    }

    // Обработчик отправки формы
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Проводим финальную валидацию
        const isValid = validateEmail() &&
                        validatePhone() &&
                        validateRequired(firstNameInput, 'Vorname ist erforderlich') &&
                        validateRequired(lastNameInput, 'Nachname ist erforderlich') &&
                        validateSalutation();

        if (!isValid) {
            showToast('Bitte korrigieren Sie die Fehler im Formular', 'error');
            return;
        }

        showProgress();

        // Создаем FormData для отправки
        const formData = new FormData(form);

        // Отправляем запрос через fetch
        fetch(form.action, {
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

                // Если есть успешное сообщение, перенаправляем через короткое время
                const hasSuccess = data.messages.some(msg => msg.tags === 'success');
                if (hasSuccess) {
                    setTimeout(() => {
                        window.location.href = '/users/create-admin/step3/';
                    }, 1500);
                }
            }
        })
        .catch(error => {
            console.error('Ошибка сохранения профиля:', error);
            hideProgress();
            showToast('Fehler beim Speichern des Profils', 'error');
        });
    });

    function validateSalutation() {
        if (!salutationSelect) return true;

        const value = salutationSelect.value;
        clearFieldError(salutationSelect);

        if (!value) {
            setFieldError(salutationSelect, 'Anrede ist erforderlich');
            return false;
        }

        setFieldSuccess(salutationSelect);
        return true;
    }

    function validateEmail() {
        if (!emailInput) return true;

        const email = emailInput.value.trim();
        clearFieldError(emailInput);

        if (email === '') {
            return true; // Пустой email допустим
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) {
            setFieldError(emailInput, 'Ungültiges E-Mail-Format');
            return false;
        }

        setFieldSuccess(emailInput);
        return true;
    }

    function validatePhone() {
        if (!phoneInput) return true;

        const phone = phoneInput.value.trim();
        clearFieldError(phoneInput);

        if (phone === '') {
            return true; // Пустой телефон допустим
        }

        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{7,20}$/;

        if (!phoneRegex.test(phone)) {
            setFieldError(phoneInput, 'Ungültiges Telefonformat');
            return false;
        }

        setFieldSuccess(phoneInput);
        return true;
    }

    function validateRequired(field, errorMessage) {
        if (!field) return false;

        const value = field.value.trim();
        clearFieldError(field);

        if (value === '') {
            setFieldError(field, errorMessage);
            return false;
        }

        if (value.length > 50) {
            setFieldError(field, 'Maximal 50 Zeichen erlaubt');
            return false;
        }

        setFieldSuccess(field);
        return true;
    }

    function setFieldError(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');

        // Удаляем старые сообщения об ошибках
        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        // Добавляем новое сообщение об ошибке
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        field.closest('.mb-3').appendChild(errorDiv);
    }

    function setFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');

        // Удаляем сообщения об ошибках
        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    function clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');

        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    function showProgress() {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird gespeichert...';
        }
    }

    function hideProgress() {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i>Weiter zu Schritt 3';
        }
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

// Обновленный create_admin_step2.js с интеграцией управления контактами

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
        this.updateHiddenInputs();

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
            this.updateHiddenInputs();
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

    updateHiddenInputs() {
        const container = document.getElementById('hiddenContactInputs');
        if (!container) return;

        container.innerHTML = '';

        this.contacts.forEach((contact, index) => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = `contacts[${index}]`;
            input.value = JSON.stringify(contact);
            container.appendChild(input);
        });
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
            alert(message);
        }
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
            this.updateHiddenInputs();
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

    const submitBtn = form.querySelector('button[type="submit"]');
    const firstNameInput = form.querySelector('input[name="first_name"]');
    const lastNameInput = form.querySelector('input[name="last_name"]');
    const salutationSelect = form.querySelector('select[name="salutation"]');

    // Валидация в реальном времени для основных полей
    if (firstNameInput) {
        firstNameInput.addEventListener('blur', () => {
            validateRequired(firstNameInput, 'Vorname ist erforderlich');
        });
    }

    if (lastNameInput) {
        lastNameInput.addEventListener('blur', () => {
            validateRequired(lastNameInput, 'Nachname ist erforderlich');
        });
    }

    // Обработчик отправки формы
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Валидируем основные поля
        const isValid = validateRequired(firstNameInput, 'Vorname ist erforderlich') &&
                        validateRequired(lastNameInput, 'Nachname ist erforderlich') &&
                        validateSalutation();

        // Валидируем контакты
        const contactsValid = contactManager.validateAllContacts();

        if (!isValid || !contactsValid) {
            showToast('Bitte korrigieren Sie die Fehler im Formular', 'error');
            return;
        }

        showProgress();

        // Создаем FormData для отправки
        const formData = new FormData(form);

        // Добавляем данные контактов
        const contactsData = contactManager.getContactsData();
        formData.append('contacts_data', JSON.stringify(contactsData));

        // Отправляем запрос через fetch
        fetch(form.action, {
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

                // Если есть успешное сообщение, перенаправляем через короткое время
                const hasSuccess = data.messages.some(msg => msg.tags === 'success');
                if (hasSuccess) {
                    setTimeout(() => {
                        window.location.href = '/users/create-admin/step3/';
                    }, 1500);
                }
            }
        })
        .catch(error => {
            console.error('Ошибка сохранения профиля:', error);
            hideProgress();
            showToast('Fehler beim Speichern des Profils', 'error');
        });
    });

    function validateSalutation() {
        if (!salutationSelect) return true;

        const value = salutationSelect.value;
        clearFieldError(salutationSelect);

        if (!value) {
            setFieldError(salutationSelect, 'Anrede ist erforderlich');
            return false;
        }

        setFieldSuccess(salutationSelect);
        return true;
    }

    function validateRequired(field, errorMessage) {
        if (!field) return false;

        const value = field.value.trim();
        clearFieldError(field);

        if (value === '') {
            setFieldError(field, errorMessage);
            return false;
        }

        if (value.length > 50) {
            setFieldError(field, 'Maximal 50 Zeichen erlaubt');
            return false;
        }

        setFieldSuccess(field);
        return true;
    }

    function setFieldError(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');

        // Удаляем старые сообщения об ошибках
        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        // Добавляем новое сообщение об ошибке
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        field.closest('.mb-3').appendChild(errorDiv);
    }

    function setFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');

        // Удаляем сообщения об ошибках
        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    function clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');

        const existingError = field.closest('.mb-3').querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }

    function showProgress() {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Wird gespeichert...';
        }
    }

    function hideProgress() {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i>Weiter zu Schritt 3';
        }
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

    console.log('Create Admin Step 2 с Contact Manager инициализирован');
});

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Создаем глобальный экземпляр менеджера контактов
    window.contactManager = new ContactManager();

    // Если есть существующие данные, загружаем их
    // (это может быть полезно при редактировании формы)
    const existingContacts = window.initialContactsData || [];
    if (existingContacts.length > 0) {
        contactManager.loadContacts(existingContacts);
    }

    console.log('Contact Manager инициализирован');
});

});