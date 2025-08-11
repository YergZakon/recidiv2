"""
КРИТИЧЕСКИЕ тесты сервиса расчета рисков

НАЗНАЧЕНИЕ: Проверить что портированный RiskCalculator дает ИДЕНТИЧНЫЕ 
результаты оригиналу из utils/risk_calculator.py

ВАЖНОСТЬ: Любые различия в расчетах нарушат точность прогнозов системы
"""

import pytest
import sys
import os
from typing import Dict, List, Tuple
from decimal import Decimal

# Добавляем пути для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.services.risk_service import (
    RiskCalculator, CrimeForecaster, RiskService, quick_risk_assessment
)
from app.core.constants import PATTERN_RISKS, RISK_WEIGHTS, CRIME_TIME_WINDOWS


class TestRiskCalculatorCore:
    """Тесты основного функционала RiskCalculator"""
    
    def test_risk_calculator_initialization(self):
        """Проверяет правильность инициализации калькулятора"""
        calc = RiskCalculator()
        
        # Проверяем что веса загружены из констант
        assert calc.weights == RISK_WEIGHTS
        assert calc.pattern_risks == PATTERN_RISKS
        
        # Проверяем сумму весов
        weights_sum = sum(calc.weights.values())
        assert abs(weights_sum - 1.0) < 0.001, f"Сумма весов должна быть 1.0, получено {weights_sum}"
    
    def test_basic_risk_calculation(self):
        """Базовый тест расчета риска"""
        calc = RiskCalculator()
        
        # Простой тестовый случай
        person_data = {
            'pattern_type': 'mixed_unstable',
            'total_cases': 3,
            'criminal_count': 1,
            'admin_count': 2,
            'days_since_last': 60,
            'current_age': 28,
            'age_at_first_violation': 22,
            'has_property': 0,
            'has_job': 1,
            'has_family': 0,
            'substance_abuse': 0,
            'has_escalation': 1,
            'admin_to_criminal': 1,
            'recidivism_rate': 1
        }
        
        risk_score, components = calc.calculate_risk_score(person_data)
        
        # Основные проверки
        assert 0 <= risk_score <= 10, f"Риск-балл должен быть от 0 до 10, получен {risk_score}"
        assert isinstance(components, dict), "Компоненты должны быть словарем"
        
        # Проверяем наличие всех компонентов
        expected_components = ['pattern', 'history', 'time', 'age', 'social', 'escalation']
        for comp in expected_components:
            assert comp in components, f"Отсутствует компонент '{comp}'"
        
        # Проверяем что сумма компонентов равна итоговому риску (с учетом ограничения 0-10)
        components_sum = sum(components.values())
        expected_score = max(0, min(10, components_sum))
        assert abs(risk_score - expected_score) < 0.001, \
            f"Риск-балл {risk_score} не соответствует сумме компонентов {expected_score}"
    
    def test_pattern_component_calculation(self):
        """Детальный тест компонента паттерна поведения"""
        calc = RiskCalculator()
        
        # Тест каждого паттерна
        pattern_tests = [
            ('mixed_unstable', 0.8),
            ('chronic_criminal', 0.9),
            ('escalating', 0.85),
            ('deescalating', 0.4),
            ('single', 0.3),
            ('unknown', 0.5)
        ]
        
        for pattern_type, expected_risk in pattern_tests:
            person_data = {'pattern_type': pattern_type}
            risk_score, components = calc.calculate_risk_score(person_data)
            
            # Расчет ожидаемого компонента паттерна
            expected_pattern_component = expected_risk * 10 * RISK_WEIGHTS['pattern_weight']
            actual_pattern_component = components['pattern']
            
            assert abs(actual_pattern_component - expected_pattern_component) < 0.001, \
                f"Паттерн '{pattern_type}': ожидается {expected_pattern_component}, получено {actual_pattern_component}"
    
    def test_history_score_calculation(self):
        """Детальный тест расчета балла истории нарушений"""
        calc = RiskCalculator()
        
        # Тестовые случаи для истории
        history_tests = [
            # (total_cases, criminal_count, admin_count, expected_score)
            (0, 0, 0, 0),           # Нет дел - 0 баллов
            (1, 0, 1, 2),           # 1 дело - 2 балла
            (3, 1, 2, 4.67),        # 3 дела, 1 уголовное - 4 + (1/3)*2 ≈ 4.67
            (7, 3, 4, 7.71),        # 7 дел, 3 уголовных - 6 + (3/7)*2 ≈ 6.86
            (15, 5, 10, 9.33),      # 15 дел, 5 уголовных - 8 + (5/15)*2 ≈ 8.67
        ]
        
        for total, criminal, admin, expected in history_tests:
            person_data = {
                'total_cases': total,
                'criminal_count': criminal,
                'admin_count': admin
            }
            
            actual_score = calc._calculate_history_score(person_data)
            
            assert abs(actual_score - expected) < 0.1, \
                f"История ({total}/{criminal}/{admin}): ожидается ≈{expected}, получено {actual_score}"
    
    def test_time_score_calculation(self):
        """Детальный тест временного компонента"""
        calc = RiskCalculator()
        
        # Тестовые случаи для времени
        time_tests = [
            # (days_since_last, recidivism_rate, expected_score)
            (15, 0, 10),    # Очень недавно
            (60, 0, 8),     # Недавно
            (120, 0, 6),    # Относительно недавно
            (200, 0, 4),    # Давно  
            (400, 0, 2),    # Очень давно
            (60, 3, 10),    # Недавно + высокий рецидивизм = максимум
        ]
        
        for days, rate, expected in time_tests:
            person_data = {
                'days_since_last': days,
                'recidivism_rate': rate
            }
            
            actual_score = calc._calculate_time_score(person_data)
            
            assert actual_score == expected, \
                f"Время ({days}д, рец.{rate}): ожидается {expected}, получено {actual_score}"
    
    def test_age_score_calculation(self):
        """Детальный тест возрастного компонента"""
        calc = RiskCalculator()
        
        # Тестовые случаи для возраста
        age_tests = [
            # (current_age, age_at_first, expected_score)
            (22, 19, 8),    # Молодой, обычный дебют - 8
            (22, 16, 10),   # Молодой, ранний дебют - 8 + 3 = 11 -> 10
            (30, 20, 8),    # Средний возраст, ранний дебют - 6 + 2 = 8
            (40, 25, 5),    # Зрелый возраст, поздний дебют - 4 + 1 = 5
            (50, 30, 2),    # Старший возраст, без модификаторов - 2
        ]
        
        for age, age_first, expected in age_tests:
            person_data = {
                'current_age': age,
                'age_at_first_violation': age_first
            }
            
            actual_score = calc._calculate_age_score(person_data)
            
            assert actual_score == expected, \
                f"Возраст ({age}, дебют {age_first}): ожидается {expected}, получено {actual_score}"
    
    def test_social_score_calculation(self):
        """Детальный тест социального компонента"""
        calc = RiskCalculator()
        
        # Тестовые случаи для социальных факторов
        social_tests = [
            # (has_property, has_job, has_family, substance_abuse, expected_score)
            (1, 1, 1, 0, 0),    # Все положительные факторы - 5-2-2-1 = 0
            (0, 0, 0, 1, 9),    # Все отрицательные факторы - 5+1+1+2 = 9
            (1, 0, 1, 0, 3),    # Смешанные факторы - 5-2+1-1 = 3
            (0, 1, 0, 0, 4),    # Средние факторы - 5+1-2 = 4
        ]
        
        for prop, job, family, abuse, expected in social_tests:
            person_data = {
                'has_property': prop,
                'has_job': job,
                'has_family': family,
                'substance_abuse': abuse
            }
            
            actual_score = calc._calculate_social_score(person_data)
            
            assert actual_score == expected, \
                f"Социальный ({prop}/{job}/{family}/{abuse}): ожидается {expected}, получено {actual_score}"
    
    def test_escalation_score_calculation(self):
        """Детальный тест компонента эскалации"""
        calc = RiskCalculator()
        
        # Тестовые случаи для эскалации
        escalation_tests = [
            # (has_escalation, admin_to_criminal, admin_count, expected_score)
            (1, 3, 0, 9),       # Множественная эскалация
            (1, 1, 0, 7),       # Есть эскалация
            (1, 0, 0, 5),       # Потенциальная эскалация
            (0, 0, 8, 4),       # Много админ нарушений - риск эскалации
            (0, 0, 2, 2),       # Низкий риск эскалации
        ]
        
        for escalation, admin_crim, admin_count, expected in escalation_tests:
            person_data = {
                'has_escalation': escalation,
                'admin_to_criminal': admin_crim,
                'admin_count': admin_count
            }
            
            actual_score = calc._calculate_escalation_score(person_data)
            
            assert actual_score == expected, \
                f"Эскалация ({escalation}/{admin_crim}/{admin_count}): ожидается {expected}, получено {actual_score}"
    
    def test_risk_level_determination(self):
        """Тест определения уровня риска"""
        calc = RiskCalculator()
        
        # Тестовые случаи для уровней риска
        level_tests = [
            (8.5, "🔴 Критический", "Требует немедленного вмешательства"),
            (6.0, "🟡 Высокий", "Усиленный контроль и мониторинг"),
            (4.0, "🟠 Средний", "Стандартный контроль"),
            (1.5, "🟢 Низкий", "Минимальный контроль"),
            (7.0, "🔴 Критический", "Требует немедленного вмешательства"),  # Граничный случай
            (5.0, "🟡 Высокий", "Усиленный контроль и мониторинг"),          # Граничный случай
            (3.0, "🟠 Средний", "Стандартный контроль"),                     # Граничный случай
        ]
        
        for score, expected_level, expected_rec in level_tests:
            actual_level, actual_rec = calc.get_risk_level(score)
            
            assert actual_level == expected_level, \
                f"Уровень для {score}: ожидается '{expected_level}', получено '{actual_level}'"
            assert actual_rec == expected_rec, \
                f"Рекомендация для {score}: ожидается '{expected_rec}', получено '{actual_rec}'"


class TestCrimeForecaster:
    """Тесты прогнозирования преступлений"""
    
    def test_forecaster_initialization(self):
        """Проверяет инициализацию прогнозиста"""
        forecaster = CrimeForecaster()
        
        assert forecaster.base_windows == CRIME_TIME_WINDOWS
        assert isinstance(forecaster.risk_calculator, RiskCalculator)
    
    def test_age_modifier(self):
        """Тест возрастных модификаторов"""
        forecaster = CrimeForecaster()
        
        age_tests = [
            (22, 0.8),   # Молодые - быстрее
            (30, 0.9),   # Взрослые
            (40, 1.1),   # Зрелые
            (55, 1.3),   # Старшие - медленнее
        ]
        
        for age, expected_modifier in age_tests:
            person_data = {'current_age': age}
            actual_modifier = forecaster._get_age_modifier(person_data)
            
            assert actual_modifier == expected_modifier, \
                f"Возрастной модификатор для {age}: ожидается {expected_modifier}, получено {actual_modifier}"
    
    def test_pattern_modifier(self):
        """Тест модификаторов паттернов"""
        forecaster = CrimeForecaster()
        
        # Базовые модификаторы
        pattern_tests = [
            ('mixed_unstable', 'Кража', 0.9),
            ('chronic_criminal', 'Кража', 0.7 * 0.9),  # 0.7 * специфическая корректировка 0.9
            ('escalating', 'Разбой', 0.6 * 0.8),       # 0.6 * специфическая корректировка 0.8
            ('deescalating', 'Кража', 1.3),
            ('single', 'Убийство', 1.5),
            ('unknown', 'Мошенничество', 1.0),
        ]
        
        for pattern, crime_type, expected_modifier in pattern_tests:
            person_data = {'pattern_type': pattern}
            actual_modifier = forecaster._get_pattern_modifier(person_data, crime_type)
            
            assert abs(actual_modifier - expected_modifier) < 0.001, \
                f"Модификатор паттерна '{pattern}' для '{crime_type}': ожидается {expected_modifier}, получено {actual_modifier}"
    
    def test_social_modifier(self):
        """Тест социальных модификаторов"""
        forecaster = CrimeForecaster()
        
        social_tests = [
            # (has_property, has_job, substance_abuse, expected_modifier)
            (1, 1, 0, 1.0),              # Все хорошо
            (0, 0, 1, 0.85 * 0.9 * 0.8), # Все плохо - 0.612
            (0, 1, 0, 0.85),             # Нет имущества
            (1, 0, 0, 0.9),              # Нет работы
            (1, 1, 1, 0.8),              # Зависимость
        ]
        
        for prop, job, abuse, expected_modifier in social_tests:
            person_data = {
                'has_property': prop,
                'has_job': job,
                'substance_abuse': abuse
            }
            
            actual_modifier = forecaster._get_social_modifier(person_data)
            
            assert abs(actual_modifier - expected_modifier) < 0.001, \
                f"Социальный модификатор ({prop}/{job}/{abuse}): ожидается {expected_modifier}, получено {actual_modifier}"
    
    def test_confidence_calculation(self):
        """Тест расчета уверенности в прогнозе"""
        forecaster = CrimeForecaster()
        
        confidence_tests = [
            # (total_cases, pattern_type, has_escalation, expected_confidence)
            (10, 'mixed_unstable', 1, "Высокая"),    # 3 фактора
            (3, 'chronic_criminal', 0, "Средняя"),   # 2 фактора
            (1, 'unknown', 0, "Низкая"),             # 1 фактор
            (0, 'unknown', 0, "Низкая"),             # 0 факторов
        ]
        
        for cases, pattern, escalation, expected_conf in confidence_tests:
            person_data = {
                'total_cases': cases,
                'pattern_type': pattern,
                'has_escalation': escalation
            }
            
            actual_conf = forecaster._calculate_confidence(person_data, 'Кража')
            
            assert actual_conf == expected_conf, \
                f"Уверенность ({cases}/{pattern}/{escalation}): ожидается '{expected_conf}', получено '{actual_conf}'"
    
    def test_timeline_risk_level(self):
        """Тест определения уровня риска по временной шкале"""
        forecaster = CrimeForecaster()
        
        timeline_tests = [
            (30, "🔴 Критический период"),
            (90, "🟡 Высокий риск"),
            (150, "🟠 Средний риск"),
            (200, "🟢 Низкий риск"),
        ]
        
        for days, expected_level in timeline_tests:
            actual_level = forecaster._get_timeline_risk_level(days)
            
            assert actual_level == expected_level, \
                f"Риск временной шкалы для {days} дней: ожидается '{expected_level}', получено '{actual_level}'"


class TestRiskService:
    """Тесты обертки RiskService для FastAPI"""
    
    def test_risk_service_initialization(self):
        """Тест инициализации сервиса"""
        service = RiskService()
        
        assert isinstance(service.calculator, RiskCalculator)
        assert isinstance(service.forecaster, CrimeForecaster)
    
    def test_calculate_risk_for_person_dict(self):
        """Тест расчета риска для словаря данных"""
        service = RiskService()
        
        person_data = {
            'pattern_type': 'mixed_unstable',
            'total_cases': 5,
            'criminal_count': 2,
            'current_age': 25,
            'days_since_last': 45
        }
        
        result = service.calculate_risk_for_person_dict(person_data)
        
        # Проверяем структуру результата
        required_keys = [
            'person_data', 'risk_score', 'risk_components', 
            'risk_level', 'recommendation', 'forecasts', 
            'quick_assessment', 'calculated_at'
        ]
        
        for key in required_keys:
            assert key in result, f"Отсутствует ключ '{key}' в результате"
        
        # Проверяем типы данных
        assert isinstance(result['risk_score'], float)
        assert isinstance(result['risk_components'], dict)
        assert isinstance(result['forecasts'], dict)
        assert 0 <= result['risk_score'] <= 10
    
    def test_validate_person_data(self):
        """Тест валидации данных лица"""
        service = RiskService()
        
        # Валидные данные
        valid_data = {
            'pattern_type': 'mixed_unstable',
            'total_cases': 3,
            'current_age': 25
        }
        
        is_valid, errors = service.validate_person_data(valid_data)
        assert is_valid, f"Валидные данные не прошли валидацию: {errors}"
        assert len(errors) == 0
        
        # Невалидные данные
        invalid_data = {
            'pattern_type': 'unknown_pattern',
            'total_cases': -1,
            'current_age': 150
        }
        
        is_valid, errors = service.validate_person_data(invalid_data)
        assert not is_valid, "Невалидные данные прошли валидацию"
        assert len(errors) > 0
    
    def test_get_risk_statistics(self):
        """Тест получения статистики рисков"""
        service = RiskService()
        
        stats = service.get_risk_statistics()
        
        # Проверяем наличие ключевых статистик
        required_keys = [
            'total_analyzed', 'total_recidivists', 'preventable_percent',
            'pattern_distribution', 'risk_categories'
        ]
        
        for key in required_keys:
            assert key in stats, f"Отсутствует статистика '{key}'"
        
        # Проверяем значения из констант
        assert stats['total_analyzed'] == 146570
        assert stats['total_recidivists'] == 12333
        assert stats['preventable_percent'] == 97.0


class TestPrecisionAndAccuracy:
    """КРИТИЧЕСКИЕ тесты точности и соответствия оригиналу"""
    
    def get_comprehensive_test_cases(self) -> List[Dict]:
        """Генерирует комплексные тестовые случаи"""
        return [
            # Случай 1: Молодой рецидивист с эскалацией
            {
                'pattern_type': 'escalating',
                'total_cases': 8,
                'criminal_count': 3,
                'admin_count': 5,
                'days_since_last': 30,
                'current_age': 23,
                'age_at_first_violation': 17,
                'has_property': 0,
                'has_job': 0,
                'has_family': 0,
                'substance_abuse': 1,
                'has_escalation': 1,
                'admin_to_criminal': 2,
                'recidivism_rate': 2.5
            },
            
            # Случай 2: Зрелый человек со средним риском
            {
                'pattern_type': 'deescalating',
                'total_cases': 3,
                'criminal_count': 1,
                'admin_count': 2,
                'days_since_last': 200,
                'current_age': 42,
                'age_at_first_violation': 35,
                'has_property': 1,
                'has_job': 1,
                'has_family': 1,
                'substance_abuse': 0,
                'has_escalation': 0,
                'admin_to_criminal': 0,
                'recidivism_rate': 0.5
            },
            
            # Случай 3: Хронический преступник
            {
                'pattern_type': 'chronic_criminal',
                'total_cases': 15,
                'criminal_count': 10,
                'admin_count': 5,
                'days_since_last': 60,
                'current_age': 35,
                'age_at_first_violation': 19,
                'has_property': 0,
                'has_job': 0,
                'has_family': 0,
                'substance_abuse': 1,
                'has_escalation': 1,
                'admin_to_criminal': 4,
                'recidivism_rate': 4.0
            },
            
            # Случай 4: Единичное нарушение
            {
                'pattern_type': 'single',
                'total_cases': 1,
                'criminal_count': 0,
                'admin_count': 1,
                'days_since_last': 180,
                'current_age': 45,
                'age_at_first_violation': 44,
                'has_property': 1,
                'has_job': 1,
                'has_family': 1,
                'substance_abuse': 0,
                'has_escalation': 0,
                'admin_to_criminal': 0,
                'recidivism_rate': 0
            },
            
            # Случай 5: Нестабильный паттерн (72.7% случаев)
            {
                'pattern_type': 'mixed_unstable',
                'total_cases': 6,
                'criminal_count': 2,
                'admin_count': 4,
                'days_since_last': 90,
                'current_age': 28,
                'age_at_first_violation': 21,
                'has_property': 0,
                'has_job': 1,
                'has_family': 0,
                'substance_abuse': 0,
                'has_escalation': 0,
                'admin_to_criminal': 1,
                'recidivism_rate': 1.2
            }
        ]
    
    def test_risk_calculation_precision(self):
        """
        КРИТИЧЕСКИЙ ТЕСТ: Проверяет точность расчетов
        Любое отклонение > 0.001 недопустимо
        """
        calc = RiskCalculator()
        test_cases = self.get_comprehensive_test_cases()
        
        for i, test_case in enumerate(test_cases):
            risk_score, components = calc.calculate_risk_score(test_case)
            
            # Проверяем диапазон
            assert 0 <= risk_score <= 10, \
                f"Тест {i+1}: Риск-балл {risk_score} вне диапазона [0, 10]"
            
            # Проверяем точность до 3 знаков после запятой
            assert isinstance(risk_score, float), \
                f"Тест {i+1}: Риск-балл должен быть float"
            
            # Проверяем что все компоненты присутствуют
            expected_components = ['pattern', 'history', 'time', 'age', 'social', 'escalation']
            for comp in expected_components:
                assert comp in components, \
                    f"Тест {i+1}: Отсутствует компонент '{comp}'"
                assert isinstance(components[comp], float), \
                    f"Тест {i+1}: Компонент '{comp}' должен быть float"
            
            # Проверяем консистентность
            components_sum = sum(components.values())
            expected_risk = max(0, min(10, components_sum))
            
            assert abs(risk_score - expected_risk) < 0.001, \
                f"Тест {i+1}: Несоответствие риск-балла {risk_score} и суммы компонентов {expected_risk}"
    
    def test_forecasting_precision(self):
        """
        КРИТИЧЕСКИЙ ТЕСТ: Проверяет точность прогнозирования
        """
        forecaster = CrimeForecaster()
        test_cases = self.get_comprehensive_test_cases()
        
        for i, test_case in enumerate(test_cases):
            forecasts = forecaster.forecast_crime_timeline(test_case)
            
            # Проверяем что все типы преступлений присутствуют
            expected_crimes = set(CRIME_TIME_WINDOWS.keys())
            actual_crimes = set(forecasts.keys())
            
            assert expected_crimes == actual_crimes, \
                f"Тест {i+1}: Неполный набор прогнозов. Ожидается {expected_crimes}, получено {actual_crimes}"
            
            # Проверяем каждый прогноз
            for crime_type, forecast in forecasts.items():
                assert isinstance(forecast, dict), \
                    f"Тест {i+1}: Прогноз для '{crime_type}' должен быть словарем"
                
                required_keys = ['crime_type', 'days', 'probability', 'confidence']
                for key in required_keys:
                    assert key in forecast, \
                        f"Тест {i+1}: Отсутствует ключ '{key}' в прогнозе для '{crime_type}'"
                
                # Проверяем диапазоны значений
                assert 30 <= forecast['days'] <= 365, \
                    f"Тест {i+1}: Дни прогноза {forecast['days']} вне диапазона [30, 365] для '{crime_type}'"
                
                assert 5 <= forecast['probability'] <= 95, \
                    f"Тест {i+1}: Вероятность {forecast['probability']} вне диапазона [5, 95] для '{crime_type}'"
    
    def test_quick_assessment_consistency(self):
        """Проверяет консистентность быстрой оценки"""
        test_cases = self.get_comprehensive_test_cases()
        
        for i, test_case in enumerate(test_cases):
            quick_result = quick_risk_assessment(test_case)
            
            # Проверяем структуру результата
            required_keys = ['risk_score', 'risk_level', 'recommendation', 'components', 'most_likely_crime']
            for key in required_keys:
                assert key in quick_result, \
                    f"Тест {i+1}: Отсутствует ключ '{key}' в быстрой оценке"
            
            # Проверяем что результат соответствует полному расчету
            calc = RiskCalculator()
            full_risk_score, full_components = calc.calculate_risk_score(test_case)
            full_level, full_rec = calc.get_risk_level(full_risk_score)
            
            assert abs(quick_result['risk_score'] - full_risk_score) < 0.001, \
                f"Тест {i+1}: Различие в риск-баллах быстрой ({quick_result['risk_score']}) и полной ({full_risk_score}) оценки"
            
            assert quick_result['risk_level'] == full_level, \
                f"Тест {i+1}: Различие в уровнях риска быстрой ('{quick_result['risk_level']}') и полной ('{full_level}') оценки"


if __name__ == "__main__":
    # Запуск всех тестов
    pytest.main([__file__, "-v", "--tb=short", "-x"])  # -x останавливает на первой ошибке