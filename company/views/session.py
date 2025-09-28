# company/views/session.py - ОБНОВЛЕНО для обязательных банковских данных в шаге 5

class CompanySessionManager:
    """Менеджер для управления данными многошагового процесса регистрации"""

    SESSION_KEY = 'company_registration_data'

    @staticmethod
    def get_session_data(request):
        """Получает данные из сессии"""
        return request.session.get(CompanySessionManager.SESSION_KEY, {})

    @staticmethod
    def set_session_data(request, data):
        """Сохраняет данные в сессию"""
        request.session[CompanySessionManager.SESSION_KEY] = data
        request.session.modified = True

    @staticmethod
    def update_session_data(request, step_data):
        """Обновляет данные конкретного шага"""
        session_data = CompanySessionManager.get_session_data(request)
        session_data.update(step_data)
        CompanySessionManager.set_session_data(request, session_data)

    @staticmethod
    def clear_session_data(request):
        """Очищает данные сессии"""
        if CompanySessionManager.SESSION_KEY in request.session:
            del request.session[CompanySessionManager.SESSION_KEY]
            request.session.modified = True

    @staticmethod
    def get_completion_status(request):
        """ОБНОВЛЕНО: Возвращает статус завершения шагов (теперь шаг 5 требует банковские данные)"""
        session_data = CompanySessionManager.get_session_data(request)

        # Проверяем основные обязательные банковские поля для шага 5
        step5_required_fields = ['bank_name', 'iban', 'bic', 'account_holder']
        step5_complete = all([
            session_data.get(field) and str(session_data.get(field)).strip()
            for field in step5_required_fields
        ])

        return {
            'step1_complete': 'company_name' in session_data and 'legal_form' in session_data,
            'step2_complete': (
                    'registration_data_processed' in session_data and
                    'all_registration_fields_complete' in session_data and
                    all([
                        session_data.get('commercial_register'),
                        session_data.get('tax_number'),
                        session_data.get('vat_id'),
                        session_data.get('tax_id')
                    ])
            ),
            'step3_complete': 'street' in session_data and 'city' in session_data,
            'step4_complete': 'email' in session_data and 'phone' in session_data,
            'step5_complete': step5_complete  # ИЗМЕНЕНО: теперь проверяет обязательные банковские поля
        }

    @staticmethod
    def validate_banking_data(session_data):
        """НОВАЯ ФУНКЦИЯ: Валидирует банковские данные"""
        required_fields = ['bank_name', 'iban', 'bic', 'account_holder']

        # Проверяем наличие всех обязательных полей
        for field in required_fields:
            if not session_data.get(field) or not str(session_data.get(field)).strip():
                return False, f"{field} ist erforderlich"

        # Дополнительная валидация форматов
        import re

        # Валидация IBAN
        iban = session_data.get('iban', '').replace(' ', '').upper()
        if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$', iban):
            return False, "IBAN: Ungültiges Format"

        # Валидация BIC
        bic = session_data.get('bic', '').upper()
        if not re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', bic):
            return False, "BIC: Ungültiges Format"

        return True, "Banking data valid"

    @staticmethod
    def get_banking_completion_percentage(session_data):
        """НОВАЯ ФУНКЦИЯ: Возвращает процент завершенности банковских данных"""
        required_fields = ['bank_name', 'iban', 'bic', 'account_holder']
        optional_fields = ['bank_address', 'account_type', 'secondary_bank_name',
                           'secondary_iban', 'secondary_bic', 'banking_notes']

        # Подсчитываем заполненные обязательные поля
        required_filled = sum(1 for field in required_fields
                              if session_data.get(field) and str(session_data.get(field)).strip())

        # Подсчитываем заполненные опциональные поля
        optional_filled = sum(1 for field in optional_fields
                              if session_data.get(field) and str(session_data.get(field)).strip())

        # Процент основан на обязательных полях (100% = все обязательные заполнены)
        # Опциональные поля добавляют бонусные проценты
        required_percentage = (required_filled / len(required_fields)) * 100
        optional_bonus = (optional_filled / len(optional_fields)) * 20  # Максимум 20% бонуса

        total_percentage = min(required_percentage + optional_bonus, 120)  # Максимум 120%

        return {
            'required_percentage': required_percentage,
            'optional_bonus': optional_bonus,
            'total_percentage': total_percentage,
            'required_complete': required_filled == len(required_fields),
            'optional_count': optional_filled
        }