# company/views/__init__.py
# Централизованный импорт всех view функций

# Session manager
from .session import CompanySessionManager

# Company manager (если нужно будет перенести)
# from ..company_manager import CompanyManager

# Utils (импортируем из родительского каталога)
from ..company_utils import (
    render_toast_response,
    render_with_messages,
    check_mongodb_availability,
    get_legal_form_display_name,
)

# Registration views
from .registration import (
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
from .crud import (
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
from .extra import (
    company_stats_json,
    company_status,
    debug_company_data,
    export_company_data,
    import_company_data,
)

# Экспортируем все для удобства
__all__ = [
    # Session
    'CompanySessionManager',

    # Utils
    'render_toast_response',
    'render_with_messages',
    'check_mongodb_availability',
    'get_legal_form_display_name',

    # Registration
    'register_company',
    'register_company_step1',
    'register_company_step2',
    'register_company_step3',
    'register_company_step4',
    'register_company_step5',
    'company_validation_check',
    'validate_registration_data',

    # CRUD
    'company_info',
    'edit_company',
    'edit_company_step1',
    'edit_company_step2',
    'edit_company_step3',
    'edit_company_step4',
    'edit_company_step5',
    'delete_company',
    'set_primary_company',

    # Extra
    'company_stats_json',
    'company_status',
    'debug_company_data',
    'export_company_data',
    'import_company_data',
]