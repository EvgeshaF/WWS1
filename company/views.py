# company/views.py - ОБНОВЛЕНО: импорты из нового каталога views/
# Основной файл для импорта всех view функций

# Импортируем все из подкаталога views
from .views import *

# Для совместимости можно оставить прямые импорты (опционально)
# Это позволит не ломать существующие импорты из других частей системы

# Session manager
from .views.session import CompanySessionManager

# Company manager (остается в корне)
from .company_manager import CompanyManager

# Utils (остаются в корне)
from .company_utils import (
    render_toast_response,
    render_with_messages,
    check_mongodb_availability,
    get_legal_form_display_name,
)

# Registration views
from .views.registration import (
    register_company,
    register_company_step1,
    register_company_step2,
    register_company_step3,
    register_company_step4,
    register_company_step5,
    company_validation_check,
    validate_registration_data,
)

# CRUD views
from .views.crud import (
    company_info,
    edit_company,
    edit_company_step1,
    edit_company_step2,
    edit_company_step3,
    edit_company_step4,
    edit_company_step5,
    delete_company,
    set_primary_company,
)

# Extra views
from .views.extra import (
    company_stats_json,
    company_status,
    debug_company_data,
    export_company_data,
    import_company_data,
)