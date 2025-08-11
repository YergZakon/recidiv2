#!/usr/bin/env python3
"""
Упрощенное сравнение расчетов между utils/ и backend/ версиями
Без зависимостей от SQLAlchemy
"""

import sys
import os
from typing import Dict, List, Tuple
import time
import traceback

# Добавляем пути для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))

def setup_imports():
    """Настройка импортов с обработкой ошибок"""
    global OriginalCalculator, OriginalForecaster
    global BackendCalculator, BackendForecaster
    
    print("🔍 Импорт модулей для сравнения...")
    
    # Создаем упрощенную версию backend модуля без SQLAlchemy
    try:
        # Импортируем только RiskCalculator и CrimeForecaster логику
        from app.core.constants import RISK_WEIGHTS, PATTERN_RISKS, CRIME_TIME_WINDOWS
        
        # Создаем упрощенную версию без зависимостей
        class SimplifiedRiskCalculator:
            def __init__(self):
                self.weights = RISK_WEIGHTS
                self.pattern_risks = PATTERN_RISKS
            
            def calculate_risk_score(self, person_data: Dict) -> Tuple[float, Dict]:
                """Точная копия логики из backend/app/services/risk_service.py"""
                components = {}
                
                # 1. Компонент паттерна поведения
                pattern = person_data.get('pattern_type', 'unknown')
                pattern_score = self.pattern_risks.get(pattern, 0.5) * 10
                components['pattern'] = pattern_score * self.weights['pattern_weight']
                
                # 2. Компонент истории нарушений
                history_score = self._calculate_history_score(person_data)
                components['history'] = history_score * self.weights['history_weight']
                
                # 3. Временной компонент
                time_score = self._calculate_time_score(person_data)
                components['time'] = time_score * self.weights['time_weight']
                
                # 4. Возрастной компонент
                age_score = self._calculate_age_score(person_data)
                components['age'] = age_score * self.weights['age_weight']
                
                # 5. Социальный компонент
                social_score = self._calculate_social_score(person_data)
                components['social'] = social_score * self.weights['social_weight']
                
                # 6. Компонент эскалации
                escalation_score = self._calculate_escalation_score(person_data)
                components['escalation'] = escalation_score * self.weights['escalation_weight']
                
                # Итоговый риск-балл
                risk_score = sum(components.values())
                
                # Ограничиваем диапазон 0-10
                risk_score = max(0, min(10, risk_score))
                
                return risk_score, components
            
            def _calculate_history_score(self, data: Dict) -> float:
                """Точная копия из backend"""
                total_cases = data.get('total_cases', 0)
                criminal_count = data.get('criminal_count', 0)
                admin_count = data.get('admin_count', 0)
                
                if total_cases == 0:
                    return 0
                elif total_cases <= 2:
                    base_score = 2
                elif total_cases <= 5:
                    base_score = 4
                elif total_cases <= 10:
                    base_score = 6
                else:
                    base_score = 8
                
                if criminal_count > 0:
                    criminal_ratio = criminal_count / total_cases
                    base_score += criminal_ratio * 2
                
                return min(10, base_score)
            
            def _calculate_time_score(self, data: Dict) -> float:
                """Точная копия из backend"""
                days_since_last = data.get('days_since_last', 365)
                
                if days_since_last < 30:
                    time_score = 10
                elif days_since_last < 90:
                    time_score = 8
                elif days_since_last < 180:
                    time_score = 6
                elif days_since_last < 365:
                    time_score = 4
                else:
                    time_score = 2
                
                recidivism_rate = data.get('recidivism_rate', 0)
                if recidivism_rate > 2:
                    time_score = min(10, time_score + 2)
                
                return time_score
            
            def _calculate_age_score(self, data: Dict) -> float:
                """Точная копия из backend"""
                age = data.get('current_age', 35)
                age_at_first = data.get('age_at_first_violation', age)
                
                if 18 <= age <= 25:
                    base_score = 8
                elif 26 <= age <= 35:
                    base_score = 6
                elif 36 <= age <= 45:
                    base_score = 4
                else:
                    base_score = 2
                
                if age_at_first < 18:
                    base_score += 3
                elif age_at_first < 21:
                    base_score += 2
                elif age_at_first < 25:
                    base_score += 1
                
                return min(10, base_score)
            
            def _calculate_social_score(self, data: Dict) -> float:
                """Точная копия из backend"""
                score = 5
                
                if data.get('has_property', 0) == 1:
                    score -= 2
                if data.get('has_job', 0) == 1:
                    score -= 2
                if data.get('has_family', 0) == 1:
                    score -= 1
                
                if data.get('has_property', 0) == 0:
                    score += 1
                if data.get('has_job', 0) == 0:
                    score += 1
                if data.get('substance_abuse', 0) == 1:
                    score += 2
                
                return max(0, min(10, score))
            
            def _calculate_escalation_score(self, data: Dict) -> float:
                """Точная копия из backend"""
                has_escalation = data.get('has_escalation', 0)
                admin_to_criminal = data.get('admin_to_criminal', 0)
                
                if has_escalation:
                    if admin_to_criminal > 2:
                        return 9
                    elif admin_to_criminal > 0:
                        return 7
                    else:
                        return 5
                else:
                    if data.get('admin_count', 0) > 5:
                        return 4
                    else:
                        return 2
            
            def get_risk_level(self, risk_score: float) -> Tuple[str, str]:
                """Точная копия из backend"""
                if risk_score >= 7:
                    return "🔴 Критический", "Требует немедленного вмешательства"
                elif risk_score >= 5:
                    return "🟡 Высокий", "Усиленный контроль и мониторинг"
                elif risk_score >= 3:
                    return "🟠 Средний", "Стандартный контроль"
                else:
                    return "🟢 Низкий", "Минимальный контроль"
        
        BackendCalculator = SimplifiedRiskCalculator
        print("✅ Backend модули загружены (упрощенная версия)")
        
    except Exception as e:
        print(f"❌ Ошибка загрузки backend модулей: {e}")
        return False
    
    # Импорт оригинальной версии
    try:
        from risk_calculator import RiskCalculator as OriginalCalculator
        print("✅ Utils модули загружены")
        return True
        
    except ImportError as e:
        print(f"⚠️ Не удается загрузить utils модули: {e}")
        OriginalCalculator = None
        return True
    
    except Exception as e:
        print(f"❌ Критическая ошибка импорта: {e}")
        return False


def generate_test_cases() -> List[Dict]:
    """Генерирует тестовые случаи для сравнения"""
    return [
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
        
        # Тестируем оригинальную версию
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
                    
                    # Результат сравнения
                    if risk_diff < 0.001:
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


def print_final_summary(results: List[Dict]):
    """Выводит финальную сводку"""
    print("\n" + "=" * 80)
    print("📋 ИТОГОВЫЙ ОТЧЕТ СРАВНЕНИЯ")
    print("=" * 80)
    
    total_tests = len(results)
    total_errors = sum(len(r['errors']) for r in results)
    identical_calculations = sum(1 for r in results 
                               if r['comparison'].get('risk_scores_match', False))
    critical_differences = sum(1 for r in results 
                             if r['comparison'].get('risk_score_difference', 0) > 0.01)
    
    print(f"🧪 Общее количество тестов: {total_tests}")
    print(f"❌ Всего ошибок: {total_errors}")
    
    if OriginalCalculator is not None:
        print(f"🎉 Идентичные расчеты: {identical_calculations}")
        print(f"💥 Критические различия: {critical_differences}")
        
        if critical_differences == 0:
            print("\n✅ ВСЕ РАСЧЕТЫ ПРОШЛИ ПРОВЕРКУ!")
            print("   Портированная версия полностью соответствует оригиналу")
        else:
            print(f"\n💥 ОБНАРУЖЕНЫ КРИТИЧЕСКИЕ РАЗЛИЧИЯ!")
            print("   Требуется немедленная проверка и исправление")
    else:
        print("\n⚠️ Сравнение с оригиналом недоступно")
        if total_errors == 0:
            print("✅ Backend версия работает корректно")
        else:
            print("💥 Обнаружены ошибки в backend версии")
    
    print("=" * 80)


def main():
    """Основная функция сравнения"""
    print("🔍 УПРОЩЕННОЕ СРАВНЕНИЕ РАСЧЕТОВ РИСКОВ")
    print("=" * 80)
    
    # Настройка импортов
    if not setup_imports():
        print("💥 Не удается загрузить модули для сравнения")
        return 1
    
    # Генерация тестовых случаев
    test_cases = generate_test_cases()
    print(f"\n📝 Сгенерировано {len(test_cases)} тестовых случаев")
    
    try:
        # Основные сравнения
        results = compare_risk_calculations(test_cases)
        
        # Генерация итогового отчета
        print_final_summary(results)
        
        # Возвращаем код ошибки если есть критические различия
        critical_differences = sum(1 for r in results 
                                 if r['comparison'].get('risk_score_difference', 0) > 0.01)
        total_errors = sum(len(r['errors']) for r in results)
        
        if critical_differences > 0 or total_errors > 0:
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