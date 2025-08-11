"""
Core модули системы раннего предупреждения преступлений

Экспорт всех критических констант из исследования 146,570 правонарушений
"""

# Импорт всех констант для удобного доступа
from .constants import (
    # Основная статистика исследования
    TOTAL_VIOLATIONS_ANALYZED,
    TOTAL_RECIDIVISTS,
    PREVENTABLE_CRIMES_PERCENT,
    UNSTABLE_PATTERN_PERCENT,
    ADMIN_TO_THEFT_TRANSITIONS,
    AVG_DAYS_TO_MURDER,
    
    # Временные окна до преступлений
    CRIME_TIME_WINDOWS,
    BASE_WINDOWS,
    
    # Проценты предотвратимости
    PREVENTION_RATES,
    BASE_CRIME_PROBABILITIES,
    
    # Веса факторов риска
    RISK_WEIGHTS,
    
    # Риски и распределение паттернов
    PATTERN_RISKS,
    PATTERN_DISTRIBUTION,
    
    # Категории риска и пороги
    RISK_CATEGORIES,
    RISK_THRESHOLD_CRITICAL,
    RISK_THRESHOLD_HIGH,
    RISK_THRESHOLD_MEDIUM,
    
    # Цвета для визуализации
    CRIME_COLORS,
    RISK_COLORS,
    
    # Настройки прогнозирования
    DEFAULT_FORECAST_HORIZON_DAYS,
    MIN_FORECAST_DAYS,
    MAX_FORECAST_DAYS,
    AGE_MODIFIERS,
    CONFIDENCE_THRESHOLDS,
    
    # Данные эскалации
    TOP_ESCALATION_TRANSITIONS,
    
    # Настройки файлов данных
    REQUIRED_DATA_FILES,
    DATA_DIR,
    RISK_DATA_COLUMNS,
    
    # Программы вмешательства
    INTERVENTION_PROGRAMS,
    
    # Функции валидации
    validate_iin_checksum,
    get_risk_category_by_score,
    get_crime_color,
    
    # Метаинформация
    CONSTANTS_VERSION,
    CRITICAL_CHECKSUM,
    LAST_RESEARCH_SYNC,
    RESEARCH_DATA_SOURCE
)

# Импорт функций валидации
from .validation import (
    validate_constants_integrity,
    compare_with_streamlit_constants,
    validate_constants,
    print_constants_summary
)

# Версия core модуля
__version__ = "1.0.0"

# Автоматическая валидация при импорте core модуля
try:
    from .validation import validate_constants
    validate_constants()
    print("✅ Core модуль загружен, все константы валидированы")
except Exception as e:
    print(f"⚠️ Предупреждение при валидации констант: {e}")

__all__ = [
    # Основная статистика
    'TOTAL_VIOLATIONS_ANALYZED',
    'TOTAL_RECIDIVISTS',
    'PREVENTABLE_CRIMES_PERCENT',
    'UNSTABLE_PATTERN_PERCENT', 
    'ADMIN_TO_THEFT_TRANSITIONS',
    'AVG_DAYS_TO_MURDER',
    
    # Временные окна
    'CRIME_TIME_WINDOWS',
    'BASE_WINDOWS',
    
    # Предотвратимость
    'PREVENTION_RATES',
    'BASE_CRIME_PROBABILITIES',
    
    # Веса и риски
    'RISK_WEIGHTS',
    'PATTERN_RISKS', 
    'PATTERN_DISTRIBUTION',
    
    # Категории риска
    'RISK_CATEGORIES',
    'RISK_THRESHOLD_CRITICAL',
    'RISK_THRESHOLD_HIGH',
    'RISK_THRESHOLD_MEDIUM',
    
    # Цвета и визуализация
    'CRIME_COLORS',
    'RISK_COLORS',
    
    # Прогнозирование
    'DEFAULT_FORECAST_HORIZON_DAYS',
    'MIN_FORECAST_DAYS',
    'MAX_FORECAST_DAYS',
    'AGE_MODIFIERS',
    'CONFIDENCE_THRESHOLDS',
    
    # Эскалация и данные
    'TOP_ESCALATION_TRANSITIONS',
    'REQUIRED_DATA_FILES',
    'DATA_DIR',
    'RISK_DATA_COLUMNS',
    
    # Программы вмешательства
    'INTERVENTION_PROGRAMS',
    
    # Функции
    'validate_iin_checksum',
    'get_risk_category_by_score',
    'get_crime_color',
    'validate_constants_integrity',
    'compare_with_streamlit_constants', 
    'validate_constants',
    'print_constants_summary',
    
    # Метаинформация
    'CONSTANTS_VERSION',
    'CRITICAL_CHECKSUM',
    'LAST_RESEARCH_SYNC',
    'RESEARCH_DATA_SOURCE'
]