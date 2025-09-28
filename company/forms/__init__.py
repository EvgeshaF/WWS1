# company/forms/__init__.py
# Централизованный импорт всех форм для удобства использования

# Импортируем утилиты
from .utils import (
    get_salutations_from_mongodb,
    get_default_salutation_choices,
    get_titles_from_mongodb,
    get_default_title_choices,
    get_countries_from_mongodb,
    get_default_country_choices,
    get_industries_from_mongodb,
    get_default_industry_choices,
)

# Импортируем все формы
from .step1 import CompanyBasicDataForm
from .step2 import CompanyRegistrationForm
from .step3 import CompanyAddressForm
from .step4 import CompanyContactForm
from .step5 import CompanyBankingForm

# Legacy import для совместимости
from .step5 import CompanyRegistrationFormLegacy

# Экспортируем все для удобства импорта
__all__ = [
    # Утилиты
    'get_salutations_from_mongodb',
    'get_default_salutation_choices',
    'get_titles_from_mongodb',
    'get_default_title_choices',
    'get_countries_from_mongodb',
    'get_default_country_choices',
    'get_industries_from_mongodb',
    'get_default_industry_choices',

    # Формы по шагам
    'CompanyBasicDataForm',
    'CompanyRegistrationForm',
    'CompanyAddressForm',
    'CompanyContactForm',
    'CompanyBankingForm',

    # Legacy
    'CompanyRegistrationFormLegacy',
]