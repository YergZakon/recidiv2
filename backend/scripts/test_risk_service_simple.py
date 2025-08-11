#!/usr/bin/env python3
"""
Простой тест RiskService без pytest зависимостей
"""

import sys
import os
from typing import Dict, List, Tuple

# Добавляем пути для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_risk_calculator_initialization():
    """Проверяет правильность инициализации калькулятора"""
    print("🧪 Тест инициализации RiskCalculator...")
    
    try:
        from app.core.constants import RISK_WEIGHTS, PATTERN_RISKS
        from app.services.risk_service import RiskCalculator
        
        calc = RiskCalculator()
        
        # Проверяем что веса загружены из констант
        assert calc.weights == RISK_WEIGHTS, "Веса не соответствуют константам"
        assert calc.pattern_risks == PATTERN_RISKS, "Паттерны не соответствуют константам"
        
        # Проверяем сумму весов
        weights_sum = sum(calc.weights.values())
        assert abs(weights_sum - 1.0) < 0.001, f"Сумма весов должна быть 1.0, получено {weights_sum}"
        
        print("   ✅ Инициализация прошла успешно")
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка инициализации: {e}")
        return False


def test_basic_risk_calculation():
    """Базовый тест расчета риска"""
    print("🧪 Тест базового расчета риска...")
    
    try:
        from app.services.risk_service import RiskCalculator
        
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
        
        print(f"   ✅ Риск-балл: {risk_score:.3f}, компоненты: {len(components)}")
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка расчета: {e}")
        return False


def test_risk_level_determination():
    """Тест определения уровня риска"""
    print("🧪 Тест определения уровней риска...")
    
    try:
        from app.services.risk_service import RiskCalculator
        
        calc = RiskCalculator()
        
        # Тестовые случаи для уровней риска
        level_tests = [
            (8.5, "🔴 Критический", "Требует немедленного вмешательства"),
            (6.0, "🟡 Высокий", "Усиленный контроль и мониторинг"),
            (4.0, "🟠 Средний", "Стандартный контроль"),
            (1.5, "🟢 Низкий", "Минимальный контроль"),
        ]
        
        for score, expected_level, expected_rec in level_tests:
            actual_level, actual_rec = calc.get_risk_level(score)
            
            assert actual_level == expected_level, \
                f"Уровень для {score}: ожидается '{expected_level}', получено '{actual_level}'"
            assert actual_rec == expected_rec, \
                f"Рекомендация для {score}: ожидается '{expected_rec}', получено '{actual_rec}'"
        
        print(f"   ✅ Все {len(level_tests)} уровней риска работают корректно")
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка определения уровней: {e}")
        return False


def test_crime_forecaster():
    """Тест прогнозирования преступлений"""
    print("🧪 Тест CrimeForecaster...")
    
    try:
        from app.services.risk_service import CrimeForecaster
        from app.core.constants import CRIME_TIME_WINDOWS
        
        forecaster = CrimeForecaster()
        
        assert forecaster.base_windows == CRIME_TIME_WINDOWS, "Временные окна не соответствуют константам"
        
        # Тестовые данные
        person_data = {
            'pattern_type': 'mixed_unstable',
            'total_cases': 5,
            'current_age': 25,
            'has_property': 0,
            'has_job': 1,
            'substance_abuse': 0
        }
        
        forecasts = forecaster.forecast_crime_timeline(person_data)
        
        # Проверяем что все типы преступлений присутствуют
        expected_crimes = set(CRIME_TIME_WINDOWS.keys())
        actual_crimes = set(forecasts.keys())
        
        assert expected_crimes == actual_crimes, \
            f"Неполный набор прогнозов. Ожидается {expected_crimes}, получено {actual_crimes}"
        
        # Проверяем каждый прогноз
        for crime_type, forecast in forecasts.items():
            assert isinstance(forecast, dict), f"Прогноз для '{crime_type}' должен быть словарем"
            
            required_keys = ['crime_type', 'days', 'probability', 'confidence']
            for key in required_keys:
                assert key in forecast, f"Отсутствует ключ '{key}' в прогнозе для '{crime_type}'"
            
            # Проверяем диапазоны значений
            assert 30 <= forecast['days'] <= 365, \
                f"Дни прогноза {forecast['days']} вне диапазона [30, 365] для '{crime_type}'"
            
            assert 5 <= forecast['probability'] <= 95, \
                f"Вероятность {forecast['probability']} вне диапазона [5, 95] для '{crime_type}'"
        
        print(f"   ✅ Прогнозы для {len(forecasts)} типов преступлений корректны")
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка прогнозирования: {e}")
        return False


def test_risk_service():
    """Тест обертки RiskService"""
    print("🧪 Тест RiskService...")
    
    try:
        from app.services.risk_service import RiskService
        
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
        assert isinstance(result['risk_score'], float), "risk_score должен быть float"
        assert isinstance(result['risk_components'], dict), "risk_components должен быть dict"
        assert isinstance(result['forecasts'], dict), "forecasts должен быть dict"
        assert 0 <= result['risk_score'] <= 10, "risk_score вне диапазона [0, 10]"
        
        print(f"   ✅ RiskService работает корректно, риск-балл: {result['risk_score']:.3f}")
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка RiskService: {e}")
        return False


def test_quick_assessment():
    """Тест быстрой оценки"""
    print("🧪 Тест быстрой оценки...")
    
    try:
        from app.services.risk_service import quick_risk_assessment, RiskCalculator
        
        person_data = {
            'pattern_type': 'escalating',
            'total_cases': 8,
            'criminal_count': 3,
            'current_age': 23,
            'days_since_last': 30
        }
        
        quick_result = quick_risk_assessment(person_data)
        
        # Проверяем структуру результата
        required_keys = ['risk_score', 'risk_level', 'recommendation', 'components', 'most_likely_crime']
        for key in required_keys:
            assert key in quick_result, f"Отсутствует ключ '{key}' в быстрой оценке"
        
        # Проверяем что результат соответствует полному расчету
        calc = RiskCalculator()
        full_risk_score, full_components = calc.calculate_risk_score(person_data)
        full_level, full_rec = calc.get_risk_level(full_risk_score)
        
        assert abs(quick_result['risk_score'] - full_risk_score) < 0.001, \
            f"Различие в риск-баллах быстрой ({quick_result['risk_score']}) и полной ({full_risk_score}) оценки"
        
        assert quick_result['risk_level'] == full_level, \
            f"Различие в уровнях риска быстрой ('{quick_result['risk_level']}') и полной ('{full_level}') оценки"
        
        print(f"   ✅ Быстрая оценка корректна, риск: {quick_result['risk_score']:.3f}")
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка быстрой оценки: {e}")
        return False


def test_data_validation():
    """Тест валидации данных"""
    print("🧪 Тест валидации данных...")
    
    try:
        from app.services.risk_service import RiskService
        
        service = RiskService()
        
        # Валидные данные
        valid_data = {
            'pattern_type': 'mixed_unstable',
            'total_cases': 3,
            'current_age': 25
        }
        
        is_valid, errors = service.validate_person_data(valid_data)
        assert is_valid, f"Валидные данные не прошли валидацию: {errors}"
        assert len(errors) == 0, f"Неожиданные ошибки для валидных данных: {errors}"
        
        # Невалидные данные
        invalid_data = {
            'pattern_type': 'unknown_pattern',
            'total_cases': -1,
            'current_age': 150
        }
        
        is_valid, errors = service.validate_person_data(invalid_data)
        assert not is_valid, "Невалидные данные прошли валидацию"
        assert len(errors) > 0, "Отсутствуют ошибки для невалидных данных"
        
        print(f"   ✅ Валидация данных работает корректно")
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка валидации: {e}")
        return False


def main():
    """Главная функция тестирования"""
    print("🔍 ТЕСТИРОВАНИЕ RISK SERVICE")
    print("=" * 80)
    
    tests = [
        test_risk_calculator_initialization,
        test_basic_risk_calculation,
        test_risk_level_determination,
        test_crime_forecaster,
        test_risk_service,
        test_quick_assessment,
        test_data_validation
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   💥 Критическая ошибка в тесте {test_func.__name__}: {e}")
            failed += 1
        
        print()
    
    print("=" * 80)
    print("📋 ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 80)
    print(f"✅ Пройдено тестов: {passed}")
    print(f"❌ Провалено тестов: {failed}")
    print(f"📊 Общее количество: {len(tests)}")
    
    if failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("   RiskService готов к использованию")
        return 0
    else:
        print(f"\n💥 ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        print("   Требуется исправление ошибок")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)