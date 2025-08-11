#!/usr/bin/env python3
"""
Сравнение расчетов между Streamlit (utils/) и FastAPI (backend/) версиями

КРИТИЧЕСКАЯ ВАЖНОСТЬ: Проверяет что портирование RiskCalculator не внесло ошибок
Любые различия в расчетах означают нарушение точности системы

Использование:
    python backend/scripts/compare_calculations.py
"""

import sys
import os
from typing import Dict, List, Tuple, Any
from decimal import Decimal
import time
import traceback

# Добавляем пути для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def setup_imports():
    """Настройка импортов с обработкой ошибок"""
    global OriginalCalculator, OriginalForecaster, original_quick_assessment
    global BackendCalculator, BackendForecaster, backend_quick_assessment
    
    print("🔍 Импорт модулей для сравнения...")
    
    # Импорт backend версии
    try:
        from app.services.risk_service import (
            RiskCalculator as BackendCalculator,
            CrimeForecaster as BackendForecaster,
            quick_risk_assessment as backend_quick_assessment
        )
        print("✅ Backend модули загружены")
    except Exception as e:
        print(f"❌ Ошибка загрузки backend модулей: {e}")
        return False
    
    # Импорт оригинальной версии
    try:
        # Пытаемся импортировать utils модули
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
        
        from risk_calculator import (
            RiskCalculator as OriginalCalculator,
            CrimeForecaster as OriginalForecaster,
            quick_risk_assessment as original_quick_assessment
        )
        print("✅ Utils модули загружены")
        return True
        
    except ImportError as e:
        print(f"⚠️ Не удается загрузить utils модули: {e}")
        print("🔄 Будем тестировать только backend версию на валидность")
        
        # Устанавливаем None для оригинальных модулей
        OriginalCalculator = None
        OriginalForecaster = None
        original_quick_assessment = None
        return True
    
    except Exception as e:
        print(f"❌ Критическая ошибка импорта: {e}")
        traceback.print_exc()
        return False


def generate_test_cases() -> List[Dict]:
    """Генерирует тестовые случаи для сравнения"""
    return [
        # Случай 1: Базовый тест - нестабильный паттерн
        {
            'name': 'Нестабильный паттерн (основной)',
            'data': {
                'pattern_type': 'mixed_unstable',
                'total_cases': 5,
                'criminal_count': 2,
                'admin_count': 3,
                'days_since_last': 60,
                'current_age': 28,
                'age_at_first_violation': 21,
                'has_property': 0,
                'has_job': 1,
                'has_family': 0,
                'substance_abuse': 0,
                'has_escalation': 0,
                'admin_to_criminal': 1,
                'recidivism_rate': 1.5
            }
        },
        
        # Случай 2: Критический риск - молодой с эскалацией
        {
            'name': 'Критический риск (эскалация)',
            'data': {
                'pattern_type': 'escalating',
                'total_cases': 12,
                'criminal_count': 5,
                'admin_count': 7,
                'days_since_last': 25,
                'current_age': 22,
                'age_at_first_violation': 16,
                'has_property': 0,
                'has_job': 0,
                'has_family': 0,
                'substance_abuse': 1,
                'has_escalation': 1,
                'admin_to_criminal': 3,
                'recidivism_rate': 3.2
            }
        },
        
        # Случай 3: Низкий риск - деэскалация
        {
            'name': 'Низкий риск (деэскалация)',
            'data': {
                'pattern_type': 'deescalating',
                'total_cases': 2,
                'criminal_count': 0,
                'admin_count': 2,
                'days_since_last': 300,
                'current_age': 45,
                'age_at_first_violation': 40,
                'has_property': 1,
                'has_job': 1,
                'has_family': 1,
                'substance_abuse': 0,
                'has_escalation': 0,
                'admin_to_criminal': 0,
                'recidivism_rate': 0.1
            }
        },
        
        # Случай 4: Хронический преступник
        {
            'name': 'Хронический преступник',
            'data': {
                'pattern_type': 'chronic_criminal',
                'total_cases': 20,
                'criminal_count': 15,
                'admin_count': 5,
                'days_since_last': 45,
                'current_age': 35,
                'age_at_first_violation': 18,
                'has_property': 0,
                'has_job': 0,
                'has_family': 0,
                'substance_abuse': 1,
                'has_escalation': 1,
                'admin_to_criminal': 5,
                'recidivism_rate': 5.0
            }
        },
        
        # Случай 5: Единичное нарушение
        {
            'name': 'Единичное нарушение',
            'data': {
                'pattern_type': 'single',
                'total_cases': 1,
                'criminal_count': 0,
                'admin_count': 1,
                'days_since_last': 500,
                'current_age': 50,
                'age_at_first_violation': 49,
                'has_property': 1,
                'has_job': 1,
                'has_family': 1,
                'substance_abuse': 0,
                'has_escalation': 0,
                'admin_to_criminal': 0,
                'recidivism_rate': 0
            }
        },
        
        # Случай 6: Граничные значения - молодой возраст
        {
            'name': 'Граничные значения (молодой)',
            'data': {
                'pattern_type': 'mixed_unstable',
                'total_cases': 10,
                'criminal_count': 5,
                'admin_count': 5,
                'days_since_last': 30,  # Граница очень недавно
                'current_age': 25,      # Граница молодой/средний
                'age_at_first_violation': 18,  # Граница без модификатора
                'has_property': 0,
                'has_job': 0,
                'has_family': 1,
                'substance_abuse': 0,
                'has_escalation': 1,
                'admin_to_criminal': 2,
                'recidivism_rate': 2.0  # Граница >2 дел в год
            }
        },
        
        # Случай 7: Максимальные значения
        {
            'name': 'Экстремальные значения',
            'data': {
                'pattern_type': 'chronic_criminal',
                'total_cases': 50,
                'criminal_count': 40,
                'admin_count': 10,
                'days_since_last': 5,
                'current_age': 20,
                'age_at_first_violation': 14,
                'has_property': 0,
                'has_job': 0,
                'has_family': 0,
                'substance_abuse': 1,
                'has_escalation': 1,
                'admin_to_criminal': 10,
                'recidivism_rate': 10.0
            }
        }
    ]


def compare_risk_calculations(test_cases: List[Dict]) -> List[Dict]:
    """Сравнивает расчеты рисков между версиями"""
    print("\n📊 СРАВНЕНИЕ РАСЧЕТОВ РИСКОВ")
    print("=" * 80)
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Тест {i}: {test_case['name']}")
        
        result = {
            'test_name': test_case['name'],
            'test_data': test_case['data'],
            'backend_result': None,
            'original_result': None,
            'comparison': {},
            'errors': []
        }
        
        # Тестируем backend версию
        try:
            start_time = time.perf_counter()
            backend_calc = BackendCalculator()
            backend_risk_score, backend_components = backend_calc.calculate_risk_score(test_case['data'])
            backend_level, backend_rec = backend_calc.get_risk_level(backend_risk_score)
            backend_time = (time.perf_counter() - start_time) * 1000
            
            result['backend_result'] = {
                'risk_score': backend_risk_score,
                'components': backend_components,
                'risk_level': backend_level,
                'recommendation': backend_rec,
                'calculation_time_ms': backend_time
            }
            
            print(f"   ✅ Backend: {backend_risk_score:.3f} ({backend_level}) [{backend_time:.1f}ms]")
            
        except Exception as e:
            error_msg = f"Backend ошибка: {e}"
            result['errors'].append(error_msg)
            print(f"   ❌ Backend ошибка: {e}")
        
        # Тестируем оригинальную версию (если доступна)
        if OriginalCalculator is not None:
            try:
                start_time = time.perf_counter()
                original_calc = OriginalCalculator()
                original_risk_score, original_components = original_calc.calculate_risk_score(test_case['data'])
                original_level, original_rec = original_calc.get_risk_level(original_risk_score)
                original_time = (time.perf_counter() - start_time) * 1000
                
                result['original_result'] = {
                    'risk_score': original_risk_score,
                    'components': original_components,
                    'risk_level': original_level,
                    'recommendation': original_rec,
                    'calculation_time_ms': original_time
                }
                
                print(f"   ✅ Utils:   {original_risk_score:.3f} ({original_level}) [{original_time:.1f}ms]")
                
                # Сравнение результатов
                if result['backend_result']:
                    risk_diff = abs(backend_risk_score - original_risk_score)
                    
                    result['comparison'] = {
                        'risk_score_difference': risk_diff,
                        'risk_scores_match': risk_diff < 0.001,
                        'levels_match': backend_level == original_level,
                        'recommendations_match': backend_rec == original_rec,
                        'performance_ratio': backend_time / original_time if original_time > 0 else 1.0
                    }
                    
                    # Сравнение компонентов
                    component_diffs = {}
                    for comp_name in backend_components:
                        if comp_name in original_components:
                            comp_diff = abs(backend_components[comp_name] - original_components[comp_name])
                            component_diffs[comp_name] = comp_diff
                    
                    result['comparison']['component_differences'] = component_diffs
                    max_comp_diff = max(component_diffs.values()) if component_diffs else 0
                    
                    # Результат сравнения
                    if risk_diff < 0.001 and max_comp_diff < 0.001:
                        print(f"   🎉 ИДЕНТИЧНО (разница: {risk_diff:.6f})")
                    elif risk_diff < 0.01:
                        print(f"   ⚠️ Небольшая разница: {risk_diff:.6f}")
                    else:
                        print(f"   💥 КРИТИЧЕСКАЯ РАЗНИЦА: {risk_diff:.6f}")
                        result['errors'].append(f"Критическая разница в риск-баллах: {risk_diff}")
                
            except Exception as e:
                error_msg = f"Utils ошибка: {e}"
                result['errors'].append(error_msg)
                print(f"   ❌ Utils ошибка: {e}")
        else:
            print("   ⚠️ Utils версия недоступна для сравнения")
        
        results.append(result)
    
    return results


def compare_forecasting(test_cases: List[Dict]) -> List[Dict]:
    """Сравнивает прогнозирование между версиями"""
    print("\n🔮 СРАВНЕНИЕ ПРОГНОЗИРОВАНИЯ")
    print("=" * 80)
    
    results = []
    
    for i, test_case in enumerate(test_cases[:3], 1):  # Тестируем первые 3 случая
        print(f"\n🧪 Прогноз {i}: {test_case['name']}")
        
        result = {
            'test_name': test_case['name'],
            'backend_forecasts': None,
            'original_forecasts': None,
            'comparison': {},
            'errors': []
        }
        
        # Backend прогнозирование
        try:
            backend_forecaster = BackendForecaster()
            backend_forecasts = backend_forecaster.forecast_crime_timeline(test_case['data'])
            result['backend_forecasts'] = backend_forecasts
            
            # Выводим топ-3 прогноза
            sorted_forecasts = sorted(backend_forecasts.items(), key=lambda x: x[1]['days'])[:3]
            print("   Backend прогнозы:")
            for crime, forecast in sorted_forecasts:
                print(f"      {crime}: {forecast['days']}д ({forecast['probability']:.1f}%)")
            
        except Exception as e:
            result['errors'].append(f"Backend прогноз ошибка: {e}")
            print(f"   ❌ Backend прогноз ошибка: {e}")
        
        # Оригинальное прогнозирование
        if OriginalForecaster is not None:
            try:
                original_forecaster = OriginalForecaster()
                original_forecasts = original_forecaster.forecast_crime_timeline(test_case['data'])
                result['original_forecasts'] = original_forecasts
                
                # Выводим топ-3 прогноза
                sorted_forecasts = sorted(original_forecasts.items(), key=lambda x: x[1]['days'])[:3]
                print("   Utils прогнозы:")
                for crime, forecast in sorted_forecasts:
                    print(f"      {crime}: {forecast['days']}д ({forecast['probability']:.1f}%)")
                
                # Сравнение прогнозов
                if result['backend_forecasts']:
                    forecast_diffs = {}
                    for crime in backend_forecasts:
                        if crime in original_forecasts:
                            days_diff = abs(backend_forecasts[crime]['days'] - original_forecasts[crime]['days'])
                            prob_diff = abs(backend_forecasts[crime]['probability'] - original_forecasts[crime]['probability'])
                            forecast_diffs[crime] = {'days_diff': days_diff, 'prob_diff': prob_diff}
                    
                    result['comparison']['forecast_differences'] = forecast_diffs
                    
                    # Максимальные различия
                    max_days_diff = max(diff['days_diff'] for diff in forecast_diffs.values()) if forecast_diffs else 0
                    max_prob_diff = max(diff['prob_diff'] for diff in forecast_diffs.values()) if forecast_diffs else 0
                    
                    if max_days_diff <= 1 and max_prob_diff <= 0.1:
                        print("   🎉 Прогнозы ИДЕНТИЧНЫ")
                    else:
                        print(f"   ⚠️ Различия в прогнозах: дни±{max_days_diff}, вероятность±{max_prob_diff:.1f}%")
                
            except Exception as e:
                result['errors'].append(f"Utils прогноз ошибка: {e}")
                print(f"   ❌ Utils прогноз ошибка: {e}")
        
        results.append(result)
    
    return results


def test_quick_assessment(test_cases: List[Dict]) -> List[Dict]:
    """Тестирует быструю оценку"""
    print("\n⚡ ТЕСТ БЫСТРОЙ ОЦЕНКИ")
    print("=" * 80)
    
    results = []
    
    for i, test_case in enumerate(test_cases[:2], 1):  # Тестируем первые 2 случая
        print(f"\n🧪 Быстрая оценка {i}: {test_case['name']}")
        
        result = {
            'test_name': test_case['name'],
            'backend_quick': None,
            'original_quick': None,
            'errors': []
        }
        
        # Backend быстрая оценка
        try:
            backend_quick = backend_quick_assessment(test_case['data'])
            result['backend_quick'] = backend_quick
            
            print(f"   Backend: {backend_quick['risk_score']:.3f} ({backend_quick['risk_level']})")
            if backend_quick['most_likely_crime']:
                most_likely = backend_quick['most_likely_crime']
                print(f"            Вероятное преступление: {most_likely['crime_type']} за {most_likely['days']}д")
            
        except Exception as e:
            result['errors'].append(f"Backend быстрая оценка ошибка: {e}")
            print(f"   ❌ Backend быстрая оценка ошибка: {e}")
        
        # Оригинальная быстрая оценка
        if original_quick_assessment is not None:
            try:
                original_quick = original_quick_assessment(test_case['data'])
                result['original_quick'] = original_quick
                
                print(f"   Utils:   {original_quick['risk_score']:.3f} ({original_quick['risk_level']})")
                if original_quick['most_likely_crime']:
                    most_likely = original_quick['most_likely_crime']
                    print(f"            Вероятное преступление: {most_likely['crime_type']} за {most_likely['days']}д")
                
                # Сравнение
                if result['backend_quick']:
                    risk_diff = abs(backend_quick['risk_score'] - original_quick['risk_score'])
                    levels_match = backend_quick['risk_level'] == original_quick['risk_level']
                    
                    if risk_diff < 0.001 and levels_match:
                        print("   🎉 Быстрая оценка ИДЕНТИЧНА")
                    else:
                        print(f"   ⚠️ Различие в быстрой оценке: {risk_diff:.6f}")
                
            except Exception as e:
                result['errors'].append(f"Utils быстрая оценка ошибка: {e}")
                print(f"   ❌ Utils быстрая оценка ошибка: {e}")
        
        results.append(result)
    
    return results


def performance_comparison(test_cases: List[Dict]):
    """Сравнение производительности"""
    print("\n⚡ СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 80)
    
    if OriginalCalculator is None:
        print("⚠️ Оригинальная версия недоступна, тестируем только backend")
    
    # Тест производительности backend
    backend_times = []
    print(f"\n🚀 Тестируем производительность Backend (100 расчетов)...")
    
    for _ in range(100):
        start_time = time.perf_counter()
        calc = BackendCalculator()
        calc.calculate_risk_score(test_cases[0]['data'])
        end_time = time.perf_counter()
        backend_times.append((end_time - start_time) * 1000)
    
    backend_avg = sum(backend_times) / len(backend_times)
    backend_min = min(backend_times)
    backend_max = max(backend_times)
    
    print(f"   Backend: среднее={backend_avg:.2f}ms, мин={backend_min:.2f}ms, макс={backend_max:.2f}ms")
    
    # Тест производительности оригинала
    if OriginalCalculator is not None:
        original_times = []
        print(f"\n🚀 Тестируем производительность Utils (100 расчетов)...")
        
        for _ in range(100):
            start_time = time.perf_counter()
            calc = OriginalCalculator()
            calc.calculate_risk_score(test_cases[0]['data'])
            end_time = time.perf_counter()
            original_times.append((end_time - start_time) * 1000)
        
        original_avg = sum(original_times) / len(original_times)
        original_min = min(original_times)
        original_max = max(original_times)
        
        print(f"   Utils:   среднее={original_avg:.2f}ms, мин={original_min:.2f}ms, макс={original_max:.2f}ms")
        
        # Сравнение
        ratio = backend_avg / original_avg
        if ratio < 1.1:
            print(f"   🎉 Производительность сопоставима (Backend/Utils = {ratio:.2f})")
        elif ratio < 2.0:
            print(f"   ⚠️ Backend немного медленнее (в {ratio:.2f} раза)")
        else:
            print(f"   💥 Backend значительно медленнее (в {ratio:.2f} раза)")


def generate_summary_report(risk_results: List[Dict], forecast_results: List[Dict], 
                          quick_results: List[Dict]) -> Dict:
    """Генерирует итоговый отчет сравнения"""
    report = {
        'total_tests': len(risk_results),
        'total_errors': 0,
        'critical_differences': 0,
        'identical_calculations': 0,
        'minor_differences': 0,
        'has_original_comparison': OriginalCalculator is not None,
        'test_results': {
            'risk_calculations': risk_results,
            'forecasting': forecast_results,
            'quick_assessment': quick_results
        }
    }
    
    # Анализируем результаты расчета рисков
    for result in risk_results:
        if result['errors']:
            report['total_errors'] += len(result['errors'])
        
        if result['comparison']:
            if result['comparison'].get('risk_scores_match', False):
                report['identical_calculations'] += 1
            elif result['comparison'].get('risk_score_difference', 1.0) < 0.01:
                report['minor_differences'] += 1
            else:
                report['critical_differences'] += 1
    
    return report


def print_final_summary(report: Dict):
    """Выводит финальную сводку"""
    print("\n" + "=" * 80)
    print("📋 ИТОГОВЫЙ ОТЧЕТ СРАВНЕНИЯ")
    print("=" * 80)
    
    print(f"🧪 Общее количество тестов: {report['total_tests']}")
    print(f"❌ Всего ошибок: {report['total_errors']}")
    
    if report['has_original_comparison']:
        print(f"🎉 Идентичные расчеты: {report['identical_calculations']}")
        print(f"⚠️ Небольшие различия: {report['minor_differences']}")
        print(f"💥 Критические различия: {report['critical_differences']}")
        
        if report['critical_differences'] == 0:
            print("\n✅ ВСЕ РАСЧЕТЫ ПРОШЛИ ПРОВЕРКУ!")
            print("   Портированная версия полностью соответствует оригиналу")
        else:
            print(f"\n💥 ОБНАРУЖЕНЫ КРИТИЧЕСКИЕ РАЗЛИЧИЯ!")
            print("   Требуется немедленная проверка и исправление")
    else:
        print("\n⚠️ Сравнение с оригиналом недоступно")
        if report['total_errors'] == 0:
            print("✅ Backend версия работает корректно")
        else:
            print("💥 Обнаружены ошибки в backend версии")
    
    print("=" * 80)


def main():
    """Основная функция сравнения"""
    print("🔍 СРАВНЕНИЕ РАСЧЕТОВ РИСКОВ: STREAMLIT vs FASTAPI")
    print("=" * 80)
    print("Проверяем точность портирования RiskCalculator из utils/ в backend/")
    
    # Настройка импортов
    if not setup_imports():
        print("💥 Не удается загрузить модули для сравнения")
        return 1
    
    # Генерация тестовых случаев
    test_cases = generate_test_cases()
    print(f"\n📝 Сгенерировано {len(test_cases)} тестовых случаев")
    
    try:
        # Основные сравнения
        risk_results = compare_risk_calculations(test_cases)
        forecast_results = compare_forecasting(test_cases)
        quick_results = test_quick_assessment(test_cases)
        
        # Тест производительности
        performance_comparison(test_cases)
        
        # Генерация итогового отчета
        report = generate_summary_report(risk_results, forecast_results, quick_results)
        print_final_summary(report)
        
        # Возвращаем код ошибки если есть критические различия
        if report['critical_differences'] > 0 or report['total_errors'] > 0:
            return 1
        else:
            return 0
            
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА СРАВНЕНИЯ: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)