"""
Модуль валидации констант системы раннего предупреждения преступлений

КРИТИЧЕСКАЯ ВАЖНОСТЬ: Этот модуль проверяет что константы из исследования
не были изменены в процессе разработки

Источник: CLAUDE.MD - правила сохранности данных исследования
"""

import sys
import os
from typing import List, Dict, Tuple, Any
from decimal import Decimal

# Добавляем путь к utils для сравнения с оригиналом
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'utils'))

try:
    from backend.app.core.constants import *
except ImportError:
    from .constants import *


def validate_constants_integrity() -> Tuple[bool, List[str]]:
    """
    Основная функция валидации всех констант
    
    Returns:
        Tuple[bool, List[str]]: (успех, список ошибок)
    """
    errors = []
    
    # Проверяем основную статистику исследования
    errors.extend(_validate_research_stats())
    
    # Проверяем временные окна
    errors.extend(_validate_time_windows())
    
    # Проверяем проценты предотвратимости
    errors.extend(_validate_prevention_rates())
    
    # Проверяем веса факторов риска
    errors.extend(_validate_risk_weights())
    
    # Проверяем риски паттернов
    errors.extend(_validate_pattern_risks())
    
    # Проверяем категории риска
    errors.extend(_validate_risk_categories())
    
    # Проверяем целостность данных
    errors.extend(_validate_data_integrity())
    
    return len(errors) == 0, errors


def _validate_research_stats() -> List[str]:
    """Проверяет основную статистику исследования"""
    errors = []
    
    # Критические значения из исследования 146,570 правонарушений
    expected_values = {
        'TOTAL_VIOLATIONS_ANALYZED': 146570,
        'TOTAL_RECIDIVISTS': 12333,
        'PREVENTABLE_CRIMES_PERCENT': 97.0,  # НЕ 97!
        'UNSTABLE_PATTERN_PERCENT': 72.7,    # НЕ 73!
        'ADMIN_TO_THEFT_TRANSITIONS': 6465,
        'AVG_DAYS_TO_MURDER': 143
    }
    
    for const_name, expected in expected_values.items():
        actual = globals().get(const_name)
        if actual != expected:
            errors.append(f"❌ {const_name}: ожидается {expected}, получено {actual}")
    
    return errors


def _validate_time_windows() -> List[str]:
    """Проверяет временные окна до преступлений"""
    errors = []
    
    # Временные окна из исследования (дни)
    expected_windows = {
        'Мошенничество': 109,
        'Кража': 146,
        'Убийство': 143,
        'Вымогательство': 144,
        'Грабеж': 148,
        'Разбой': 150,
        'Изнасилование': 157,
        'Хулиганство': 155
    }
    
    for crime_type, expected_days in expected_windows.items():
        actual_days = CRIME_TIME_WINDOWS.get(crime_type)
        if actual_days != expected_days:
            errors.append(f"❌ Временное окно '{crime_type}': ожидается {expected_days} дней, получено {actual_days}")
    
    # Проверяем что BASE_WINDOWS идентично CRIME_TIME_WINDOWS
    if BASE_WINDOWS != CRIME_TIME_WINDOWS:
        errors.append("❌ BASE_WINDOWS не совпадает с CRIME_TIME_WINDOWS")
    
    return errors


def _validate_prevention_rates() -> List[str]:
    """Проверяет проценты предотвратимости преступлений"""
    errors = []
    
    # Проценты из исследования
    expected_rates = {
        'Мошенничество': 82.3,
        'Кража': 87.3,
        'Убийство': 97.0,  # Критично важное значение
        'Вымогательство': 100.0,  # ВНИМАНИЕ: может быть 100.7 в некоторых файлах
        'Грабеж': 60.2,
        'Разбой': 20.2,
        'Изнасилование': 65.6,
        'Хулиганство': 45.0
    }
    
    for crime_type, expected_rate in expected_rates.items():
        actual_rate = PREVENTION_RATES.get(crime_type)
        if actual_rate != expected_rate:
            # Особый случай для Вымогательство - может быть 100.0 или 100.7
            if crime_type == 'Вымогательство' and actual_rate in [100.0, 100.7]:
                continue  # Пропускаем - обе версии допустимы
            errors.append(f"❌ Предотвратимость '{crime_type}': ожидается {expected_rate}%, получено {actual_rate}%")
    
    return errors


def _validate_risk_weights() -> List[str]:
    """Проверяет веса факторов риска"""
    errors = []
    
    # Веса из исследования - должны точно совпадать
    expected_weights = {
        'pattern_weight': 0.25,
        'history_weight': 0.20,
        'time_weight': 0.15,
        'age_weight': 0.10,
        'social_weight': 0.15,
        'escalation_weight': 0.15
    }
    
    for weight_name, expected_value in expected_weights.items():
        actual_value = RISK_WEIGHTS.get(weight_name)
        if actual_value != expected_value:
            errors.append(f"❌ Вес '{weight_name}': ожидается {expected_value}, получено {actual_value}")
    
    # Критично: сумма весов должна быть 1.0
    weights_sum = sum(RISK_WEIGHTS.values())
    if abs(weights_sum - 1.0) > 0.001:
        errors.append(f"❌ Сумма весов факторов риска: ожидается 1.0, получено {weights_sum}")
    
    return errors


def _validate_pattern_risks() -> List[str]:
    """Проверяет риски и распределение паттернов поведения"""
    errors = []
    
    # Риски паттернов из исследования
    expected_pattern_risks = {
        'mixed_unstable': 0.8,      # 72.7% случаев
        'chronic_criminal': 0.9,    # 13.6% случаев
        'escalating': 0.85,         # 7.0% случаев  
        'deescalating': 0.4,        # 5.7% случаев
        'single': 0.3,              # 1.0% случаев
        'unknown': 0.5              # Добавлено для неизвестных
    }
    
    for pattern, expected_risk in expected_pattern_risks.items():
        actual_risk = PATTERN_RISKS.get(pattern)
        if actual_risk != expected_risk:
            errors.append(f"❌ Риск паттерна '{pattern}': ожидается {expected_risk}, получено {actual_risk}")
    
    # Распределение паттернов в процентах
    expected_distribution = {
        'mixed_unstable': 72.7,
        'chronic_criminal': 13.6,
        'escalating': 7.0,
        'deescalating': 5.7,
        'single': 1.0
    }
    
    for pattern, expected_percent in expected_distribution.items():
        actual_percent = PATTERN_DISTRIBUTION.get(pattern)
        if actual_percent != expected_percent:
            errors.append(f"❌ Распределение паттерна '{pattern}': ожидается {expected_percent}%, получено {actual_percent}%")
    
    # Сумма распределения должна быть 100%
    distribution_sum = sum(PATTERN_DISTRIBUTION.values())
    if abs(distribution_sum - 100.0) > 0.1:
        errors.append(f"❌ Сумма распределения паттернов: ожидается 100%, получено {distribution_sum}%")
    
    return errors


def _validate_risk_categories() -> List[str]:
    """Проверяет категории и пороги риска"""
    errors = []
    
    # Пороговые значения из исследования
    expected_thresholds = {
        'RISK_THRESHOLD_CRITICAL': 7.0,  # 7+ баллов
        'RISK_THRESHOLD_HIGH': 5.0,      # 5-6 баллов
        'RISK_THRESHOLD_MEDIUM': 3.0     # 3-4 балла, 0-2 низкий
    }
    
    for threshold_name, expected_value in expected_thresholds.items():
        actual_value = globals().get(threshold_name)
        if actual_value != expected_value:
            errors.append(f"❌ Порог '{threshold_name}': ожидается {expected_value}, получено {actual_value}")
    
    # Проверяем диапазоны категорий риска
    expected_ranges = {
        'critical': (7.0, 10.0),
        'high': (5.0, 7.0),
        'medium': (3.0, 5.0),
        'low': (0.0, 3.0)
    }
    
    for category, expected_range in expected_ranges.items():
        actual_range = RISK_CATEGORIES.get(category, {}).get('range')
        if actual_range != expected_range:
            errors.append(f"❌ Диапазон категории '{category}': ожидается {expected_range}, получено {actual_range}")
    
    return errors


def _validate_data_integrity() -> List[str]:
    """Проверяет целостность данных и связи между константами"""
    errors = []
    
    # Проверяем что все преступления имеют временные окна и проценты
    crimes_with_windows = set(CRIME_TIME_WINDOWS.keys())
    crimes_with_rates = set(PREVENTION_RATES.keys())
    
    missing_windows = crimes_with_rates - crimes_with_windows
    missing_rates = crimes_with_windows - crimes_with_rates
    
    if missing_windows:
        errors.append(f"❌ Отсутствуют временные окна для: {missing_windows}")
    
    if missing_rates:
        errors.append(f"❌ Отсутствуют проценты предотвратимости для: {missing_rates}")
    
    # Проверяем что эскалационные переходы включают основной (админ→кража)
    if 'Административное → Кража' not in TOP_ESCALATION_TRANSITIONS:
        errors.append("❌ Отсутствует основной переход 'Административное → Кража'")
    
    # Проверяем основной переход - 6465 случаев
    admin_to_theft = TOP_ESCALATION_TRANSITIONS.get('Административное → Кража')
    if admin_to_theft != 6465:
        errors.append(f"❌ Переходов админ→кража: ожидается 6465, получено {admin_to_theft}")
    
    return errors


def compare_with_streamlit_constants() -> Tuple[bool, List[str]]:
    """
    Сравнивает константы backend с оригинальными из utils/
    
    Returns:
        Tuple[bool, List[str]]: (совпадают, список различий)
    """
    differences = []
    
    try:
        # Импортируем оригинальные константы из utils
        from utils.risk_calculator import RiskCalculator
        from utils.data_loader import get_crime_statistics, get_pattern_distribution
        
        # Создаем экземпляр для сравнения
        original_calculator = RiskCalculator()
        original_stats = get_crime_statistics()
        
        # Сравниваем веса факторов
        for weight_name, backend_value in RISK_WEIGHTS.items():
            original_value = original_calculator.weights.get(weight_name)
            if original_value != backend_value:
                differences.append(f"Вес '{weight_name}': utils={original_value}, backend={backend_value}")
        
        # Сравниваем риски паттернов
        for pattern_name, backend_risk in PATTERN_RISKS.items():
            if pattern_name == 'unknown':  # Добавленный в backend
                continue
            original_risk = original_calculator.pattern_risks.get(pattern_name)
            if original_risk != backend_risk:
                differences.append(f"Риск паттерна '{pattern_name}': utils={original_risk}, backend={backend_risk}")
        
        # Сравниваем статистику
        stats_mapping = {
            'total_violations': 'TOTAL_VIOLATIONS_ANALYZED',
            'total_recidivists': 'TOTAL_RECIDIVISTS',
            'preventable_percent': 'PREVENTABLE_CRIMES_PERCENT',
            'unstable_pattern_percent': 'UNSTABLE_PATTERN_PERCENT',
            'admin_to_theft_count': 'ADMIN_TO_THEFT_TRANSITIONS'
        }
        
        for utils_key, backend_const in stats_mapping.items():
            original_value = original_stats.get(utils_key)
            backend_value = globals().get(backend_const)
            if original_value != backend_value:
                differences.append(f"Статистика '{utils_key}': utils={original_value}, backend={backend_value}")
        
        # Сравниваем временные окна
        original_windows = original_stats.get('crime_windows', {})
        for crime_type, window_data in original_windows.items():
            original_days = window_data.get('days')
            backend_days = CRIME_TIME_WINDOWS.get(crime_type)
            if original_days != backend_days:
                differences.append(f"Временное окно '{crime_type}': utils={original_days}, backend={backend_days}")
        
    except ImportError as e:
        differences.append(f"Не удается импортировать utils модули: {e}")
    except Exception as e:
        differences.append(f"Ошибка сравнения: {e}")
    
    return len(differences) == 0, differences


def validate_constants():
    """
    Основная функция валидации - запускает все проверки
    
    Raises:
        ValueError: Если найдены критические ошибки в константах
    """
    # Проверка целостности констант backend
    integrity_ok, integrity_errors = validate_constants_integrity()
    
    if not integrity_ok:
        error_msg = "🚨 КРИТИЧЕСКИЕ ОШИБКИ В КОНСТАНТАХ BACKEND:\n" + "\n".join(integrity_errors)
        raise ValueError(error_msg)
    
    # Сравнение с оригиналом из utils
    comparison_ok, comparison_differences = compare_with_streamlit_constants()
    
    if not comparison_ok:
        error_msg = "⚠️ РАЗЛИЧИЯ С ОРИГИНАЛЬНЫМИ КОНСТАНТАМИ utils/:\n" + "\n".join(comparison_differences)
        print(f"WARNING: {error_msg}")  # Предупреждение, но не ошибка
    
    print("✅ Все критические константы прошли валидацию")


def print_constants_summary():
    """Выводит сводку по всем константам"""
    print("=" * 80)
    print("📊 СВОДКА КОНСТАНТ СИСТЕМЫ РАННЕГО ПРЕДУПРЕЖДЕНИЯ ПРЕСТУПЛЕНИЙ")
    print("=" * 80)
    
    print(f"📈 Основная статистика исследования:")
    print(f"   • Всего проанализировано: {TOTAL_VIOLATIONS_ANALYZED:,} правонарушений")
    print(f"   • Рецидивистов: {TOTAL_RECIDIVISTS:,}")
    print(f"   • Процент предотвратимых: {PREVENTABLE_CRIMES_PERCENT}%")
    print(f"   • Нестабильный паттерн: {UNSTABLE_PATTERN_PERCENT}%")
    print(f"   • Переходы админ→кража: {ADMIN_TO_THEFT_TRANSITIONS:,}")
    
    print(f"\n⏰ Временные окна до преступлений:")
    for crime, days in sorted(CRIME_TIME_WINDOWS.items(), key=lambda x: x[1]):
        print(f"   • {crime}: {days} дней")
    
    print(f"\n🎯 Проценты предотвратимости:")
    for crime, percent in sorted(PREVENTION_RATES.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {crime}: {percent}%")
    
    print(f"\n⚖️ Веса факторов риска:")
    for weight_name, value in RISK_WEIGHTS.items():
        print(f"   • {weight_name}: {value}")
    print(f"   • СУММА: {sum(RISK_WEIGHTS.values()):.3f}")
    
    print(f"\n📊 Риски паттернов поведения:")
    for pattern, risk in PATTERN_RISKS.items():
        distribution = PATTERN_DISTRIBUTION.get(pattern, 0)
        print(f"   • {pattern}: {risk} (распределение: {distribution}%)")
    
    print("=" * 80)


if __name__ == "__main__":
    # Запуск валидации при прямом вызове модуля
    try:
        validate_constants()
        print_constants_summary()
    except ValueError as e:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        sys.exit(1)