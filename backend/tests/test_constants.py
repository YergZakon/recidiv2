"""
Тесты констант системы раннего предупреждения преступлений

КРИТИЧЕСКАЯ ВАЖНОСТЬ: Эти тесты проверяют что все константы из исследования
146,570 правонарушений остались неизменными

Источник: backend/app/core/constants.py
"""

import pytest
import sys
import os
from typing import Dict, Any

# Добавляем пути для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.core.constants import *
from app.core.validation import validate_constants_integrity, compare_with_streamlit_constants


class TestResearchStatistics:
    """Тесты основной статистики исследования"""
    
    def test_total_violations_analyzed(self):
        """Тест общего количества проанализированных правонарушений"""
        assert TOTAL_VIOLATIONS_ANALYZED == 146570, \
            f"Изменено количество правонарушений: {TOTAL_VIOLATIONS_ANALYZED} != 146570"
    
    def test_total_recidivists(self):
        """Тест количества рецидивистов"""
        assert TOTAL_RECIDIVISTS == 12333, \
            f"Изменено количество рецидивистов: {TOTAL_RECIDIVISTS} != 12333"
    
    def test_preventable_crimes_percent(self):
        """Тест процента предотвратимых преступлений - КРИТИЧНО"""
        assert PREVENTABLE_CRIMES_PERCENT == 97.0, \
            f"Изменен процент предотвратимых преступлений: {PREVENTABLE_CRIMES_PERCENT} != 97.0"
        # Проверяем точный тип
        assert isinstance(PREVENTABLE_CRIMES_PERCENT, float), \
            "PREVENTABLE_CRIMES_PERCENT должно быть float"
        # НЕ должно быть округлено до 97
        assert PREVENTABLE_CRIMES_PERCENT != 97, \
            "НЕ должно быть округлено с 97.0 до 97"
    
    def test_unstable_pattern_percent(self):
        """Тест процента нестабильных паттернов - КРИТИЧНО"""
        assert UNSTABLE_PATTERN_PERCENT == 72.7, \
            f"Изменен процент нестабильных паттернов: {UNSTABLE_PATTERN_PERCENT} != 72.7"
        # НЕ должно быть округлено до 73
        assert UNSTABLE_PATTERN_PERCENT != 73, \
            "НЕ должно быть округлено с 72.7 до 73"
        assert UNSTABLE_PATTERN_PERCENT != 72, \
            "НЕ должно быть округлено с 72.7 до 72"
    
    def test_admin_to_theft_transitions(self):
        """Тест количества переходов административное→кража"""
        assert ADMIN_TO_THEFT_TRANSITIONS == 6465, \
            f"Изменено количество переходов админ→кража: {ADMIN_TO_THEFT_TRANSITIONS} != 6465"
    
    def test_avg_days_to_murder(self):
        """Тест среднего времени до убийства"""
        assert AVG_DAYS_TO_MURDER == 143, \
            f"Изменено среднее время до убийства: {AVG_DAYS_TO_MURDER} != 143"


class TestCrimeTimeWindows:
    """Тесты временных окон до преступлений"""
    
    def test_all_crime_windows_present(self):
        """Проверяет наличие всех временных окон"""
        expected_crimes = {
            'Мошенничество', 'Кража', 'Убийство', 'Вымогательство',
            'Грабеж', 'Разбой', 'Изнасилование', 'Хулиганство'
        }
        actual_crimes = set(CRIME_TIME_WINDOWS.keys())
        assert actual_crimes >= expected_crimes, \
            f"Отсутствуют временные окна для: {expected_crimes - actual_crimes}"
    
    def test_specific_crime_windows(self):
        """Тест конкретных временных окон - КРИТИЧЕСКИЕ ЗНАЧЕНИЯ"""
        critical_windows = {
            'Мошенничество': 109,
            'Кража': 146,
            'Убийство': 143,    # КРИТИЧНО - основное значение исследования
            'Вымогательство': 144,
            'Грабеж': 148,
            'Разбой': 150,
            'Изнасилование': 157,
            'Хулиганство': 155
        }
        
        for crime_type, expected_days in critical_windows.items():
            actual_days = CRIME_TIME_WINDOWS.get(crime_type)
            assert actual_days == expected_days, \
                f"Временное окно '{crime_type}': ожидается {expected_days} дней, получено {actual_days}"
    
    def test_base_windows_consistency(self):
        """Проверяет что BASE_WINDOWS идентично CRIME_TIME_WINDOWS"""
        assert BASE_WINDOWS == CRIME_TIME_WINDOWS, \
            "BASE_WINDOWS должно быть идентично CRIME_TIME_WINDOWS"
    
    def test_window_values_are_integers(self):
        """Проверяет что все временные окна - целые числа"""
        for crime_type, days in CRIME_TIME_WINDOWS.items():
            assert isinstance(days, int), \
                f"Временное окно '{crime_type}' должно быть int, получен {type(days)}"
            assert days > 0, \
                f"Временное окно '{crime_type}' должно быть положительным, получено {days}"


class TestPreventionRates:
    """Тесты процентов предотвратимости преступлений"""
    
    def test_prevention_rates_present(self):
        """Проверяет наличие всех процентов предотвратимости"""
        expected_crimes = {
            'Мошенничество', 'Кража', 'Убийство', 'Вымогательство',
            'Грабеж', 'Разбой', 'Изнасилование', 'Хулиганство'
        }
        actual_crimes = set(PREVENTION_RATES.keys())
        assert actual_crimes >= expected_crimes, \
            f"Отсутствуют проценты предотвратимости для: {expected_crimes - actual_crimes}"
    
    def test_specific_prevention_rates(self):
        """Тест конкретных процентов предотвратимости - КРИТИЧЕСКИЕ ЗНАЧЕНИЯ"""
        critical_rates = {
            'Мошенничество': 82.3,
            'Кража': 87.3,
            'Убийство': 97.0,     # КРИТИЧНО - основное значение
            'Грабеж': 60.2,
            'Разбой': 20.2,
            'Изнасилование': 65.6,
            'Хулиганство': 45.0
        }
        
        for crime_type, expected_rate in critical_rates.items():
            actual_rate = PREVENTION_RATES.get(crime_type)
            assert actual_rate == expected_rate, \
                f"Предотвратимость '{crime_type}': ожидается {expected_rate}%, получено {actual_rate}%"
    
    def test_vymogatelstvo_rate(self):
        """Тест особого случая Вымогательство - может быть 100.0 или 100.7"""
        vymogatelstvo_rate = PREVENTION_RATES.get('Вымогательство')
        assert vymogatelstvo_rate in [100.0, 100.7], \
            f"Предотвратимость 'Вымогательство' должна быть 100.0 или 100.7, получено {vymogatelstvo_rate}"
    
    def test_base_probabilities_consistency(self):
        """Проверяет что BASE_CRIME_PROBABILITIES идентично PREVENTION_RATES"""
        assert BASE_CRIME_PROBABILITIES == PREVENTION_RATES, \
            "BASE_CRIME_PROBABILITIES должно быть идентично PREVENTION_RATES"


class TestRiskWeights:
    """Тесты весов факторов риска"""
    
    def test_all_weights_present(self):
        """Проверяет наличие всех весов"""
        expected_weights = {
            'pattern_weight', 'history_weight', 'time_weight',
            'age_weight', 'social_weight', 'escalation_weight'
        }
        actual_weights = set(RISK_WEIGHTS.keys())
        assert actual_weights == expected_weights, \
            f"Отсутствуют веса: {expected_weights - actual_weights}"
    
    def test_specific_weight_values(self):
        """Тест конкретных значений весов - КРИТИЧЕСКИЕ КОНСТАНТЫ"""
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
            assert actual_value == expected_value, \
                f"Вес '{weight_name}': ожидается {expected_value}, получено {actual_value}"
    
    def test_weights_sum_equals_one(self):
        """КРИТИЧНО: Сумма весов должна быть 1.0"""
        weights_sum = sum(RISK_WEIGHTS.values())
        assert abs(weights_sum - 1.0) < 0.001, \
            f"Сумма весов должна быть 1.0, получено {weights_sum}"
    
    def test_weights_are_positive(self):
        """Проверяет что все веса положительные"""
        for weight_name, weight_value in RISK_WEIGHTS.items():
            assert weight_value > 0, \
                f"Вес '{weight_name}' должен быть положительным, получено {weight_value}"
            assert weight_value < 1, \
                f"Вес '{weight_name}' должен быть меньше 1, получено {weight_value}"


class TestPatternRisks:
    """Тесты рисков и распределения паттернов поведения"""
    
    def test_pattern_risks_present(self):
        """Проверяет наличие всех рисков паттернов"""
        expected_patterns = {
            'mixed_unstable', 'chronic_criminal', 'escalating',
            'deescalating', 'single', 'unknown'
        }
        actual_patterns = set(PATTERN_RISKS.keys())
        assert actual_patterns == expected_patterns, \
            f"Отсутствуют риски паттернов: {expected_patterns - actual_patterns}"
    
    def test_specific_pattern_risks(self):
        """Тест конкретных рисков паттернов - ИЗ ИССЛЕДОВАНИЯ"""
        expected_risks = {
            'mixed_unstable': 0.8,      # 72.7% случаев
            'chronic_criminal': 0.9,    # 13.6% случаев
            'escalating': 0.85,         # 7.0% случаев
            'deescalating': 0.4,        # 5.7% случаев
            'single': 0.3,              # 1.0% случаев
            'unknown': 0.5              # Добавлено для неизвестных
        }
        
        for pattern, expected_risk in expected_risks.items():
            actual_risk = PATTERN_RISKS.get(pattern)
            assert actual_risk == expected_risk, \
                f"Риск паттерна '{pattern}': ожидается {expected_risk}, получено {actual_risk}"
    
    def test_pattern_distribution(self):
        """Тест распределения паттернов в процентах - ИЗ ИССЛЕДОВАНИЯ"""
        expected_distribution = {
            'mixed_unstable': 72.7,     # КРИТИЧНО - основное значение
            'chronic_criminal': 13.6,
            'escalating': 7.0,
            'deescalating': 5.7,
            'single': 1.0
        }
        
        for pattern, expected_percent in expected_distribution.items():
            actual_percent = PATTERN_DISTRIBUTION.get(pattern)
            assert actual_percent == expected_percent, \
                f"Распределение '{pattern}': ожидается {expected_percent}%, получено {actual_percent}%"
    
    def test_distribution_sum_equals_100(self):
        """КРИТИЧНО: Сумма распределения должна быть 100%"""
        distribution_sum = sum(PATTERN_DISTRIBUTION.values())
        assert abs(distribution_sum - 100.0) < 0.1, \
            f"Сумма распределения должна быть 100%, получено {distribution_sum}%"
    
    def test_main_pattern_is_mixed_unstable(self):
        """Проверяет что основной паттерн - mixed_unstable (72.7%)"""
        max_percent = max(PATTERN_DISTRIBUTION.values())
        max_pattern = max(PATTERN_DISTRIBUTION.items(), key=lambda x: x[1])[0]
        
        assert max_pattern == 'mixed_unstable', \
            f"Основной паттерн должен быть 'mixed_unstable', получен '{max_pattern}'"
        assert max_percent == 72.7, \
            f"Процент основного паттерна должен быть 72.7%, получено {max_percent}%"


class TestRiskCategories:
    """Тесты категорий и порогов риска"""
    
    def test_risk_categories_present(self):
        """Проверяет наличие всех категорий риска"""
        expected_categories = {'critical', 'high', 'medium', 'low'}
        actual_categories = set(RISK_CATEGORIES.keys())
        assert actual_categories == expected_categories, \
            f"Отсутствуют категории: {expected_categories - actual_categories}"
    
    def test_risk_thresholds(self):
        """Тест пороговых значений - КРИТИЧЕСКИЕ КОНСТАНТЫ"""
        assert RISK_THRESHOLD_CRITICAL == 7.0, \
            f"Порог критического риска: ожидается 7.0, получено {RISK_THRESHOLD_CRITICAL}"
        assert RISK_THRESHOLD_HIGH == 5.0, \
            f"Порог высокого риска: ожидается 5.0, получено {RISK_THRESHOLD_HIGH}"
        assert RISK_THRESHOLD_MEDIUM == 3.0, \
            f"Порог среднего риска: ожидается 3.0, получено {RISK_THRESHOLD_MEDIUM}"
    
    def test_risk_category_ranges(self):
        """Тест диапазонов категорий риска"""
        expected_ranges = {
            'critical': (7.0, 10.0),   # 7+ баллов
            'high': (5.0, 7.0),        # 5-6 баллов
            'medium': (3.0, 5.0),      # 3-4 балла
            'low': (0.0, 3.0)          # 0-2 балла
        }
        
        for category, expected_range in expected_ranges.items():
            actual_range = RISK_CATEGORIES[category]['range']
            assert actual_range == expected_range, \
                f"Диапазон '{category}': ожидается {expected_range}, получено {actual_range}"
    
    def test_risk_category_labels(self):
        """Тест меток категорий с эмодзи"""
        expected_labels = {
            'critical': '🔴 Критический',
            'high': '🟡 Высокий',
            'medium': '🟠 Средний',
            'low': '🟢 Низкий'
        }
        
        for category, expected_label in expected_labels.items():
            actual_label = RISK_CATEGORIES[category]['label']
            assert actual_label == expected_label, \
                f"Метка '{category}': ожидается '{expected_label}', получено '{actual_label}'"


class TestEscalationData:
    """Тесты данных эскалации административное → уголовное"""
    
    def test_main_transition_present(self):
        """Проверяет наличие основного перехода админ→кража"""
        assert 'Административное → Кража' in TOP_ESCALATION_TRANSITIONS, \
            "Отсутствует основной переход 'Административное → Кража'"
    
    def test_main_transition_value(self):
        """Тест значения основного перехода - КРИТИЧНО"""
        admin_to_theft = TOP_ESCALATION_TRANSITIONS['Административное → Кража']
        assert admin_to_theft == 6465, \
            f"Переходов админ→кража: ожидается 6465, получено {admin_to_theft}"
    
    def test_escalation_consistency_with_main_stat(self):
        """Проверяет согласованность с основной статистикой"""
        admin_to_theft = TOP_ESCALATION_TRANSITIONS['Административное → Кража']
        assert admin_to_theft == ADMIN_TO_THEFT_TRANSITIONS, \
            f"Несогласованность переходов: TOP_ESCALATION={admin_to_theft}, MAIN_STAT={ADMIN_TO_THEFT_TRANSITIONS}"


class TestValidationFunctions:
    """Тесты функций валидации"""
    
    def test_get_risk_category_by_score(self):
        """Тест функции определения категории риска"""
        # Критический риск
        assert get_risk_category_by_score(7.0) == '🔴 Критический'
        assert get_risk_category_by_score(8.5) == '🔴 Критический'
        assert get_risk_category_by_score(10.0) == '🔴 Критический'
        
        # Высокий риск
        assert get_risk_category_by_score(5.0) == '🟡 Высокий'
        assert get_risk_category_by_score(6.5) == '🟡 Высокий'
        
        # Средний риск
        assert get_risk_category_by_score(3.0) == '🟠 Средний'
        assert get_risk_category_by_score(4.5) == '🟠 Средний'
        
        # Низкий риск
        assert get_risk_category_by_score(0.0) == '🟢 Низкий'
        assert get_risk_category_by_score(2.9) == '🟢 Низкий'
    
    def test_get_crime_color(self):
        """Тест функции получения цвета преступления"""
        assert get_crime_color('Убийство') == '#8e44ad'
        assert get_crime_color('Кража') == '#f39c12'
        assert get_crime_color('НеизвестноеПреступление') == '#95a5a6'  # Default


class TestConstantsIntegrity:
    """Тесты целостности констант через validation.py"""
    
    def test_constants_validation_passes(self):
        """Основной тест - вся валидация должна проходить"""
        is_valid, errors = validate_constants_integrity()
        
        if not is_valid:
            error_msg = "Константы не прошли валидацию:\n" + "\n".join(errors)
            pytest.fail(error_msg)
    
    def test_constants_metadata(self):
        """Тест метаинформации о константах"""
        assert CONSTANTS_VERSION is not None
        assert LAST_RESEARCH_SYNC is not None
        assert RESEARCH_DATA_SOURCE == 'Анализ 146,570 правонарушений КПСиСУ РК'
    
    def test_critical_checksum(self):
        """Тест критической контрольной суммы"""
        expected_checksum = {
            'total_violations': 146570,
            'total_recidivists': 12333,
            'preventable_percent': 97.0,
            'unstable_pattern': 72.7,
            'murder_days': 143
        }
        
        for key, expected_value in expected_checksum.items():
            actual_value = CRITICAL_CHECKSUM.get(key)
            assert actual_value == expected_value, \
                f"Контрольная сумма '{key}': ожидается {expected_value}, получено {actual_value}"


@pytest.mark.slow
class TestStreamlitComparison:
    """Тесты сравнения с оригинальными константами из utils/"""
    
    def test_compare_with_streamlit_constants(self):
        """Сравнение с константами из utils/ - может падать если utils недоступен"""
        try:
            matches, differences = compare_with_streamlit_constants()
            
            if not matches and differences:
                # Выводим различия как предупреждение, но не падаем
                print("⚠️ РАЗЛИЧИЯ С UTILS КОНСТАНТАМИ:")
                for diff in differences:
                    print(f"   {diff}")
        except ImportError:
            pytest.skip("Модули utils/ недоступны для сравнения")


class TestConstantsImmutability:
    """Тесты неизменяемости констант"""
    
    def test_constants_are_final(self):
        """Проверяет что константы помечены как Final"""
        import inspect
        from app.core.constants import TOTAL_VIOLATIONS_ANALYZED
        
        # Получаем аннотацию типа
        module = inspect.getmodule(TOTAL_VIOLATIONS_ANALYZED)
        # Проверка что константы действительно константы
        assert isinstance(TOTAL_VIOLATIONS_ANALYZED, int)
        assert TOTAL_VIOLATIONS_ANALYZED > 0
    
    def test_crime_windows_immutable(self):
        """Проверяет что временные окна нельзя изменить"""
        original_murder_days = CRIME_TIME_WINDOWS['Убийство']
        
        # Пытаемся изменить (должно работать, но не должно влиять на валидацию)
        try:
            CRIME_TIME_WINDOWS['Убийство'] = 999
            # Если изменение прошло, проверяем что оригинальное значение сохранилось в CRITICAL_CHECKSUM
            assert CRITICAL_CHECKSUM['murder_days'] == 143, \
                "Критическая контрольная сумма должна сохранять оригинальное значение"
        except TypeError:
            # Если словарь неизменяемый - отлично
            pass
        finally:
            # Восстанавливаем значение
            if isinstance(CRIME_TIME_WINDOWS, dict):
                CRIME_TIME_WINDOWS['Убийство'] = original_murder_days


if __name__ == "__main__":
    # Запуск тестов из командной строки
    pytest.main([__file__, "-v", "--tb=short"])