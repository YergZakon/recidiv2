"""
Константы системы раннего предупреждения преступлений

КРИТИЧНО: ВСЕ значения основаны на анализе 146,570 правонарушений
НЕ ИЗМЕНЯТЬ без согласования с исследовательской группой

Источники:
- utils/risk_calculator.py (строки 18-35, 306-315, 236-245)
- utils/data_loader.py (строки 94-107, 142-145)
- utils/forecasting.py (строки 306-315, 364-412)
- main.py (строки 135-151)

Последняя синхронизация с исследованием: 2024-12-13
"""

from typing import Dict, Tuple, Final
from decimal import Decimal

# =============================================================================
# ОСНОВНАЯ СТАТИСТИКА ИССЛЕДОВАНИЯ
# =============================================================================

# Источник: utils/data_loader.py строки 94-98, main.py строки 135-141
TOTAL_VIOLATIONS_ANALYZED: Final[int] = 146570
TOTAL_RECIDIVISTS: Final[int] = 12333
PREVENTABLE_CRIMES_PERCENT: Final[float] = 97.0  # НЕ округлять до 97!
UNSTABLE_PATTERN_PERCENT: Final[float] = 72.7   # НЕ округлять до 73!
ADMIN_TO_THEFT_TRANSITIONS: Final[int] = 6465

# Средние значения
AVG_DAYS_TO_MURDER: Final[int] = 143
AVG_TIME_TO_CRIME: Final[int] = 143

# =============================================================================
# ВРЕМЕННЫЕ ОКНА ДО ПРЕСТУПЛЕНИЙ (ДНИ)
# =============================================================================

# Источник: utils/risk_calculator.py строки 306-315, utils/forecasting.py
# Источник: utils/data_loader.py строки 100-107, main.py строки 143-149
CRIME_TIME_WINDOWS: Final[Dict[str, int]] = {
    'Мошенничество': 109,
    'Кража': 146,
    'Убийство': 143,
    'Вымогательство': 144,
    'Грабеж': 148,
    'Разбой': 150,
    'Изнасилование': 157,
    'Хулиганство': 155
}

# Альтернативные названия для обратной совместимости
BASE_WINDOWS: Final[Dict[str, int]] = CRIME_TIME_WINDOWS.copy()

# =============================================================================
# ПРОЦЕНТЫ ПРЕДОТВРАТИМОСТИ ПО ТИПАМ ПРЕСТУПЛЕНИЙ
# =============================================================================

# Источник: utils/risk_calculator.py строки 236-245
# Источник: utils/data_loader.py строки 100-107
# Источник: pages/1_🗺️_Карта_временных_окон.py строки 60-68, 122
PREVENTION_RATES: Final[Dict[str, float]] = {
    'Мошенничество': 82.3,
    'Кража': 87.3,
    'Убийство': 97.0,
    'Вымогательство': 100.0,  # ВНИМАНИЕ: в некоторых файлах 100.7, требует уточнения
    'Грабеж': 60.2,
    'Разбой': 20.2,
    'Изнасилование': 65.6,
    'Хулиганство': 45.0
}

# Базовые вероятности из исследования (для расчетов)
BASE_CRIME_PROBABILITIES: Final[Dict[str, float]] = PREVENTION_RATES.copy()

# =============================================================================
# ВЕСА ФАКТОРОВ РИСКА
# =============================================================================

# Источник: utils/risk_calculator.py строки 18-25
# КРИТИЧНО: Сумма весов должна равняться 1.0
RISK_WEIGHTS: Final[Dict[str, float]] = {
    'pattern_weight': 0.25,      # Паттерн поведения
    'history_weight': 0.20,      # История нарушений  
    'time_weight': 0.15,         # Временной фактор
    'age_weight': 0.10,          # Возрастной фактор
    'social_weight': 0.15,       # Социальные факторы
    'escalation_weight': 0.15    # Факторы эскалации
}

# Проверка суммы весов
_WEIGHTS_SUM = sum(RISK_WEIGHTS.values())
assert abs(_WEIGHTS_SUM - 1.0) < 0.001, f"Сумма весов должна быть 1.0, получили {_WEIGHTS_SUM}"

# =============================================================================
# РИСКИ ПО ПАТТЕРНАМ ПОВЕДЕНИЯ
# =============================================================================

# Источник: utils/risk_calculator.py строки 28-35
# Источник: utils/data_loader.py строки 142-145 (распределение процентов)
PATTERN_RISKS: Final[Dict[str, float]] = {
    'mixed_unstable': 0.8,       # 72.7% всех случаев - нестабильное поведение
    'chronic_criminal': 0.9,     # 13.6% всех случаев - хронические преступники
    'escalating': 0.85,          # 7.0% всех случаев - опасная тенденция эскалации
    'deescalating': 0.4,         # 5.7% всех случаев - снижение риска
    'single': 0.3,               # 1.0% всех случаев - единичные нарушения
    'unknown': 0.5               # Неизвестный паттерн (не из исследования)
}

# Процентное распределение паттернов в исследовании
PATTERN_DISTRIBUTION: Final[Dict[str, float]] = {
    'mixed_unstable': 72.7,      # Нестабильное поведение
    'chronic_criminal': 13.6,    # Хронические преступники  
    'escalating': 7.0,           # Эскалация
    'deescalating': 5.7,         # Деэскалация
    'single': 1.0                # Единичные случаи
}

# Проверка суммы процентов
_PATTERN_SUM = sum(PATTERN_DISTRIBUTION.values())
assert abs(_PATTERN_SUM - 100.0) < 0.1, f"Сумма процентов паттернов должна быть 100%, получили {_PATTERN_SUM}%"

# =============================================================================
# КАТЕГОРИИ РИСКА И ПОРОГОВЫЕ ЗНАЧЕНИЯ
# =============================================================================

# Источник: utils/risk_calculator.py строки 214-221
# Источник: utils/data_loader.py строки 147-158
RISK_CATEGORIES: Final[Dict[str, Dict[str, any]]] = {
    'critical': {
        'range': (7.0, 10.0),
        'label': '🔴 Критический',
        'color': '#dc2626',
        'description': 'Требует немедленного вмешательства'
    },
    'high': {
        'range': (5.0, 7.0),
        'label': '🟡 Высокий', 
        'color': '#f59e0b',
        'description': 'Усиленный контроль и мониторинг'
    },
    'medium': {
        'range': (3.0, 5.0),
        'label': '🟠 Средний',
        'color': '#f97316', 
        'description': 'Стандартный контроль'
    },
    'low': {
        'range': (0.0, 3.0),
        'label': '🟢 Низкий',
        'color': '#059669',
        'description': 'Минимальный контроль'
    }
}

# Пороговые значения для быстрого доступа
RISK_THRESHOLD_CRITICAL: Final[float] = 7.0
RISK_THRESHOLD_HIGH: Final[float] = 5.0
RISK_THRESHOLD_MEDIUM: Final[float] = 3.0

# =============================================================================
# ЦВЕТОВАЯ СХЕМА ДЛЯ ВИЗУАЛИЗАЦИИ
# =============================================================================

# Источник: utils/forecasting.py строки 20-29
CRIME_COLORS: Final[Dict[str, str]] = {
    'Мошенничество': '#e74c3c',
    'Кража': '#f39c12', 
    'Убийство': '#8e44ad',
    'Грабеж': '#3498db',
    'Разбой': '#27ae60',
    'Хулиганство': '#f1c40f',
    'Вымогательство': '#e67e22',
    'Изнасилование': '#c0392b'
}

# Цвета для уровней риска
RISK_COLORS: Final[Dict[str, str]] = {
    'critical': '#e74c3c',    # Красный
    'high': '#f39c12',        # Оранжевый  
    'medium': '#fd7e14',      # Темно-оранжевый
    'low': '#27ae60'          # Зеленый
}

# =============================================================================
# НАСТРОЙКИ ПРОГНОЗИРОВАНИЯ
# =============================================================================

# Источник: utils/forecasting.py, utils/risk_calculator.py
DEFAULT_FORECAST_HORIZON_DAYS: Final[int] = 365
MIN_FORECAST_DAYS: Final[int] = 30
MAX_FORECAST_DAYS: Final[int] = 365

# Модификаторы для возраста (источник: utils/risk_calculator.py строки 143-160)
AGE_MODIFIERS: Final[Dict[str, Tuple[int, int, float]]] = {
    'young': (18, 25, 0.8),      # Молодые - высокий риск, быстрее
    'adult': (26, 35, 0.9),      # Взрослые
    'mature': (36, 45, 1.1),     # Зрелые
    'senior': (46, 100, 1.3)     # Старшие - медленнее
}

# Модификаторы уверенности
CONFIDENCE_THRESHOLDS: Final[Dict[str, int]] = {
    'high': 3,      # 3+ фактора = высокая уверенность
    'medium': 2,    # 2 фактора = средняя уверенность  
    'low': 1        # 1 фактор = низкая уверенность
}

# =============================================================================
# ДАННЫЕ ЭСКАЛАЦИИ АДМИНИСТАТИВНОЕ → УГОЛОВНОЕ
# =============================================================================

# Источник: utils/data_loader.py строки 222-226
TOP_ESCALATION_TRANSITIONS: Final[Dict[str, int]] = {
    'Административное → Кража': 6465,
    'Административное → Мошенничество': 1968,
    'Административное → Грабеж': 771,
    'Административное → Побои': 587,
    'Административное → Наркотики': 645
}

# =============================================================================
# НАСТРОЙКИ ФАЙЛОВ ДАННЫХ
# =============================================================================

# Источник: utils/data_loader.py строки 16-22
REQUIRED_DATA_FILES: Final[Tuple[str, ...]] = (
    'RISK_ANALYSIS_RESULTS.xlsx',
    'ML_DATASET_COMPLETE.xlsx', 
    'crime_analysis_results.xlsx',
    'serious_crimes_analysis.xlsx',
    'risk_escalation_matrix.xlsx'
)

DATA_DIR: Final[str] = 'data'

# Колонки в основных таблицах
RISK_DATA_COLUMNS: Final[Tuple[str, ...]] = (
    'ИИН',
    'risk_total_risk_score', 
    'pattern_type'
)

# =============================================================================
# ПРОГРАММЫ ВМЕШАТЕЛЬСТВА
# =============================================================================

# Источник: utils/forecasting.py строки 364-412
INTERVENTION_PROGRAMS: Final[Dict[str, Dict[str, any]]] = {
    'Кража': {
        'programs': ('Трудоустройство', 'Финансовое консультирование', 'Социальная помощь'),
        'urgency': 'high',
        'duration': 90
    },
    'Мошенничество': {
        'programs': ('Правовое просвещение', 'Финансовая грамотность', 'Этическое воспитание'),
        'urgency': 'critical',
        'duration': 60
    },
    'Убийство': {
        'programs': ('Управление гневом', 'Психологическая помощь', 'Контроль алкоголя', 'Медиация конфликтов'),
        'urgency': 'critical', 
        'duration': 120
    },
    'Грабеж': {
        'programs': ('Социальная адаптация', 'Трудоустройство', 'Реабилитация'),
        'urgency': 'high',
        'duration': 90
    },
    'Разбой': {
        'programs': ('Интенсивный контроль', 'Психологическая коррекция', 'Социальная поддержка'),
        'urgency': 'critical',
        'duration': 120
    },
    'Хулиганство': {
        'programs': ('Досуговые программы', 'Спорт', 'Общественные работы'),
        'urgency': 'medium',
        'duration': 60
    },
    'Вымогательство': {
        'programs': ('Правовое воспитание', 'Экономическая поддержка', 'Психологическая помощь'),
        'urgency': 'high',
        'duration': 90
    },
    'Изнасилование': {
        'programs': ('Психиатрическая помощь', 'Контроль поведения', 'Терапия'),
        'urgency': 'critical',
        'duration': 180
    }
}

# =============================================================================
# ВАЛИДАЦИОННЫЕ ФУНКЦИИ
# =============================================================================

def validate_iin_checksum(iin: str) -> bool:
    """
    Валидация контрольной суммы ИИН РК
    Источник: utils/data_loader.py строки 160-179
    """
    if not iin or len(iin) != 12 or not iin.isdigit():
        return False
    
    # Упрощенная проверка - в production нужна полная
    return True


def get_risk_category_by_score(score: float) -> str:
    """
    Определяет категорию риска по баллу
    Источник: utils/data_loader.py строки 147-158
    """
    if score >= RISK_THRESHOLD_CRITICAL:
        return RISK_CATEGORIES['critical']['label']
    elif score >= RISK_THRESHOLD_HIGH:
        return RISK_CATEGORIES['high']['label']
    elif score >= RISK_THRESHOLD_MEDIUM:
        return RISK_CATEGORIES['medium']['label'] 
    else:
        return RISK_CATEGORIES['low']['label']


def get_risk_level_key(score: float) -> str:
    """
    Возвращает ключ уровня риска для фронтенда (без эмодзи)
    """
    if score >= RISK_THRESHOLD_CRITICAL:
        return 'critical'
    elif score >= RISK_THRESHOLD_HIGH:
        return 'high'
    elif score >= RISK_THRESHOLD_MEDIUM:
        return 'medium' 
    else:
        return 'low'


def get_crime_color(crime_type: str) -> str:
    """
    Возвращает цвет для типа преступления
    """
    return CRIME_COLORS.get(crime_type, '#95a5a6')

# =============================================================================
# МЕТАИНФОРМАЦИЯ О КОНСТАНТАХ
# =============================================================================

CONSTANTS_VERSION: Final[str] = '1.0.0'
LAST_RESEARCH_SYNC: Final[str] = '2024-12-13'
RESEARCH_DATA_SOURCE: Final[str] = 'Анализ 146,570 правонарушений КПСиСУ РК'

# Критические значения для проверки целостности
CRITICAL_CHECKSUM: Final[Dict[str, any]] = {
    'total_violations': TOTAL_VIOLATIONS_ANALYZED,
    'total_recidivists': TOTAL_RECIDIVISTS,
    'preventable_percent': PREVENTABLE_CRIMES_PERCENT,
    'unstable_pattern': UNSTABLE_PATTERN_PERCENT,
    'murder_days': CRIME_TIME_WINDOWS['Убийство'],
    'pattern_risks_sum': sum(PATTERN_RISKS.values()),
    'weights_sum': sum(RISK_WEIGHTS.values())
}

# Проверка критических значений при импорте модуля
def _validate_constants():
    """Проверяет критические константы при импорте модуля"""
    errors = []
    
    if TOTAL_VIOLATIONS_ANALYZED != 146570:
        errors.append(f"TOTAL_VIOLATIONS_ANALYZED изменено: {TOTAL_VIOLATIONS_ANALYZED} != 146570")
    
    if TOTAL_RECIDIVISTS != 12333:
        errors.append(f"TOTAL_RECIDIVISTS изменено: {TOTAL_RECIDIVISTS} != 12333")
        
    if PREVENTABLE_CRIMES_PERCENT != 97.0:
        errors.append(f"PREVENTABLE_CRIMES_PERCENT изменено: {PREVENTABLE_CRIMES_PERCENT} != 97.0")
        
    if UNSTABLE_PATTERN_PERCENT != 72.7:
        errors.append(f"UNSTABLE_PATTERN_PERCENT изменено: {UNSTABLE_PATTERN_PERCENT} != 72.7")
        
    if CRIME_TIME_WINDOWS['Убийство'] != 143:
        errors.append(f"Убийство время изменено: {CRIME_TIME_WINDOWS['Убийство']} != 143")
    
    if abs(sum(RISK_WEIGHTS.values()) - 1.0) > 0.001:
        errors.append(f"Сумма весов != 1.0: {sum(RISK_WEIGHTS.values())}")
    
    if errors:
        raise ValueError("КРИТИЧЕСКАЯ ОШИБКА - Константы исследования изменены:\n" + "\n".join(errors))

# Автоматическая проверка при импорте
_validate_constants()

# =============================================================================
# ЭКСПОРТ ДЛЯ ИМПОРТА
# =============================================================================

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
    'AGE_MODIFIERS',
    'CONFIDENCE_THRESHOLDS',
    
    # Эскалация и данные
    'TOP_ESCALATION_TRANSITIONS',
    'REQUIRED_DATA_FILES',
    'RISK_DATA_COLUMNS',
    
    # Программы вмешательства
    'INTERVENTION_PROGRAMS',
    
    # Функции
    'validate_iin_checksum',
    'get_risk_category_by_score', 
    'get_risk_level_key',
    'get_crime_color',
    
    # Метаинформация
    'CONSTANTS_VERSION',
    'CRITICAL_CHECKSUM'
]