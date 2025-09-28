# company/company_session_views.py - ОБНОВЛЕНО для 5 шагов с банковскими данными

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
        """Возвращает статус завершения шагов (теперь 5 шагов) - ОБНОВЛЕНО для банковского шага"""
        session_data = CompanySessionManager.get_session_data(request)
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
            'step5_complete': True  # ИЗМЕНЕНО: шаг 5 всегда завершен (банковские данные опциональны)
        }