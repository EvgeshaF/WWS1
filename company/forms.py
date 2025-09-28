# company/forms.py - ОБНОВЛЕНО: перенаправление на новую модульную структуру
# Этот файл остается для обратной совместимости

# Импортируем все из новой структуры forms/
from .forms import *

# Для полной обратной совместимости можно также явно импортировать основные классы:
from .forms.step1 import CompanyBasicDataForm
from .forms.step2 import CompanyRegistrationForm
from .forms.step3 import CompanyAddressForm
from .forms.step4 import CompanyContactForm
from .forms.step5 import CompanyBankingForm, CompanyRegistrationFormLegacy

from .forms.utils import (
    get_salutations_from_mongodb,
    get_default_salutation_choices,
    get_titles_from_mongodb,
    get_default_title_choices,
    get_countries_from_mongodb,
    get_default_country_choices,
    get_industries_from_mongodb,
    get_default_industry_choices,
)

# Для совместимости с существующими импортами типа:
# from company.forms import CompanyBasicDataForm
__all__ = [
    'CompanyBasicDataForm',
    'CompanyRegistrationForm',
    'CompanyAddressForm',
    'CompanyContactForm',
    'CompanyBankingForm',
    'CompanyRegistrationFormLegacy',
    'get_salutations_from_mongodb',
    'get_default_salutation_choices',
    'get_titles_from_mongodb',
    'get_default_title_choices',
    'get_countries_from_mongodb',
    'get_default_country_choices',
    'get_industries_from_mongodb',
    'get_default_industry_choices',
]