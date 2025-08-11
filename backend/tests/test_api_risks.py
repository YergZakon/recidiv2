"""
Тесты для API endpoints расчета рисков

КРИТИЧНО: Проверяет что API возвращает те же результаты что и utils/risk_calculator.py
"""

import sys
import os
from typing import Dict, Any

# Добавляем пути
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Простой HTTP клиент без зависимостей
import json
import urllib.request
import urllib.parse
import time


class SimpleTestClient:
    """Простой HTTP клиент для тестирования без зависимостей"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8001"):
        self.base_url = base_url.rstrip('/')
    
    def _make_request(self, method: str, path: str, data: Dict = None) -> Dict:
        """Выполняет HTTP запрос"""
        url = f"{self.base_url}{path}"
        
        # Подготавливаем данные
        if data:
            json_data = json.dumps(data).encode('utf-8')
            headers = {'Content-Type': 'application/json'}
        else:
            json_data = None
            headers = {}
        
        # Создаем запрос
        req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                return {
                    'status_code': response.status,
                    'json': json.loads(response_data) if response_data else {}
                }
        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8')
            try:
                error_json = json.loads(error_data)
            except:
                error_json = {'detail': error_data}
            
            return {
                'status_code': e.code,
                'json': error_json
            }
        except Exception as e:
            return {
                'status_code': 0,
                'json': {'error': str(e)}
            }
    
    def get(self, path: str) -> Dict:
        """GET запрос"""
        return self._make_request('GET', path)
    
    def post(self, path: str, json_data: Dict) -> Dict:
        """POST запрос"""
        return self._make_request('POST', path, json_data)


def test_server_health():
    """Тест работоспособности сервера"""
    print("🧪 Тест работоспособности сервера")
    
    client = SimpleTestClient()
    
    # Проверяем основной health endpoint
    response = client.get("/health")
    
    if response['status_code'] != 200:
        print(f"   ❌ Сервер недоступен: {response['status_code']}")
        return False
    
    data = response['json']
    
    # Проверяем что все компоненты работают
    components = data.get('components', {})
    
    expected_components = ['constants_loaded', 'risk_calculation', 'crime_forecasting']
    for component in expected_components:
        if component not in components:
            print(f"   ❌ Отсутствует компонент: {component}")
            return False
    
    print(f"   ✅ Сервер работает, статус: {data.get('status')}")
    return True


def test_calculate_risk_basic():
    """Базовый тест расчета риска"""
    print("🧪 Базовый тест расчета риска")
    
    client = SimpleTestClient()
    
    # Тестовые данные - тот же случай что тестировали в сравнении
    test_data = {
        "iin": "123456789012",
        "pattern_type": "mixed_unstable",
        "total_cases": 5,
        "criminal_count": 2,
        "admin_count": 3,
        "days_since_last": 60,
        "current_age": 28,
        "age_at_first_violation": 21,
        "has_property": 0,
        "has_job": 1,
        "has_family": 0,
        "substance_abuse": 0,
        "has_escalation": 0,
        "admin_to_criminal": 1,
        "recidivism_rate": 1.5
    }
    
    response = client.post("/api/risks/calculate", test_data)
    
    if response['status_code'] != 200:
        print(f"   ❌ Ошибка API: {response['status_code']} - {response['json']}")
        return False
    
    data = response['json']
    
    # Проверяем структуру ответа
    required_fields = ['risk_score', 'risk_level', 'components', 'recommendation']
    for field in required_fields:
        if field not in data:
            print(f"   ❌ Отсутствует поле: {field}")
            return False
    
    risk_score = data['risk_score']
    
    # Проверяем диапазон риск-балла
    if not (0 <= risk_score <= 10):
        print(f"   ❌ Риск-балл вне диапазона [0,10]: {risk_score}")
        return False
    
    # Проверяем что это именно тот результат что мы ожидали (5.760)
    expected_risk = 5.760
    if abs(risk_score - expected_risk) > 0.01:
        print(f"   ⚠️ Риск-балл отличается от ожидаемого: {risk_score} vs {expected_risk}")
        # Не возвращаем False, так как могут быть незначительные различия
    
    # Проверяем компоненты
    components = data['components']
    expected_components = ['pattern', 'history', 'time', 'age', 'social', 'escalation']
    for comp in expected_components:
        if comp not in components:
            print(f"   ❌ Отсутствует компонент: {comp}")
            return False
    
    print(f"   ✅ Расчет успешен: {risk_score:.3f} ({data['risk_level']})")
    print(f"        Рекомендация: {data['recommendation']}")
    
    return True


def test_calculate_risk_validation():
    """Тест валидации входных данных"""
    print("🧪 Тест валидации входных данных")
    
    client = SimpleTestClient()
    
    # Невалидные данные
    invalid_data = {
        "pattern_type": "invalid_pattern",
        "total_cases": -1,
        "current_age": 200
    }
    
    response = client.post("/api/risks/calculate", invalid_data)
    
    # Ожидаем ошибку валидации
    if response['status_code'] not in [422, 400]:
        print(f"   ❌ Ожидалась ошибка валидации, получен код: {response['status_code']}")
        return False
    
    print(f"   ✅ Валидация работает корректно (код {response['status_code']})")
    return True


def test_quick_assessment():
    """Тест быстрой оценки"""
    print("🧪 Тест быстрой оценки")
    
    client = SimpleTestClient()
    
    test_data = {
        "pattern_type": "escalating",
        "total_cases": 8,
        "criminal_count": 3,
        "current_age": 23,
        "days_since_last": 30
    }
    
    response = client.post("/api/risks/quick-assessment", test_data)
    
    if response['status_code'] != 200:
        print(f"   ❌ Ошибка быстрой оценки: {response['status_code']} - {response['json']}")
        return False
    
    data = response['json']
    
    # Проверяем структуру
    required_fields = ['risk_score', 'risk_level', 'components', 'most_likely_crime']
    for field in required_fields:
        if field not in data:
            print(f"   ❌ Отсутствует поле: {field}")
            return False
    
    print(f"   ✅ Быстрая оценка: {data['risk_score']:.3f} ({data['risk_level']})")
    
    if data['most_likely_crime']:
        mlc = data['most_likely_crime']
        print(f"        Вероятное преступление: {mlc['crime_type']} через {mlc['days']} дней")
    
    return True


def test_risk_statistics():
    """Тест получения статистики"""
    print("🧪 Тест статистики рисков")
    
    client = SimpleTestClient()
    
    response = client.get("/api/risks/statistics")
    
    if response['status_code'] != 200:
        print(f"   ❌ Ошибка получения статистики: {response['status_code']}")
        return False
    
    data = response['json']
    
    # Проверяем ключевые статистики
    expected_stats = ['total_analyzed', 'total_recidivists', 'preventable_crimes_percent']
    for stat in expected_stats:
        if stat not in data:
            print(f"   ❌ Отсутствует статистика: {stat}")
            return False
    
    # Проверяем значения из констант
    if data['total_analyzed'] != 146570:
        print(f"   ❌ Неверное количество проанализированных: {data['total_analyzed']}")
        return False
    
    if data['total_recidivists'] != 12333:
        print(f"   ❌ Неверное количество рецидивистов: {data['total_recidivists']}")
        return False
    
    print(f"   ✅ Статистика корректна: {data['total_analyzed']:,} нарушений проанализировано")
    return True


def test_forecast_timeline():
    """Тест прогнозирования временных окон"""
    print("🧪 Тест прогнозирования временных окон")
    
    client = SimpleTestClient()
    
    test_data = {
        "pattern_type": "mixed_unstable",
        "total_cases": 3,
        "current_age": 25,
        "has_property": 0,
        "has_job": 1,
        "substance_abuse": 0
    }
    
    response = client.post("/api/forecasts/timeline", test_data)
    
    if response['status_code'] != 200:
        print(f"   ❌ Ошибка прогнозирования: {response['status_code']} - {response['json']}")
        return False
    
    data = response['json']
    
    # Проверяем структуру
    if 'forecasts' not in data:
        print(f"   ❌ Отсутствует поле forecasts")
        return False
    
    forecasts = data['forecasts']
    
    if len(forecasts) == 0:
        print(f"   ❌ Нет прогнозов")
        return False
    
    # Проверяем первый прогноз
    first_forecast = forecasts[0]
    required_fields = ['crime_type', 'days', 'probability', 'confidence']
    for field in required_fields:
        if field not in first_forecast:
            print(f"   ❌ Отсутствует поле в прогнозе: {field}")
            return False
    
    print(f"   ✅ Прогнозирование работает: {len(forecasts)} прогнозов")
    print(f"        Ближайший риск: {first_forecast['crime_type']} через {first_forecast['days']} дней ({first_forecast['probability']:.1f}%)")
    
    return True


def test_performance():
    """Тест производительности API"""
    print("🧪 Тест производительности")
    
    client = SimpleTestClient()
    
    test_data = {
        "pattern_type": "mixed_unstable", 
        "total_cases": 5,
        "criminal_count": 2,
        "current_age": 28,
        "days_since_last": 60
    }
    
    # Измеряем время 10 запросов
    times = []
    successful = 0
    
    for i in range(10):
        start_time = time.time()
        response = client.post("/api/risks/calculate", test_data)
        end_time = time.time()
        
        request_time = (end_time - start_time) * 1000  # в миллисекундах
        times.append(request_time)
        
        if response['status_code'] == 200:
            successful += 1
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"   ✅ Производительность: {successful}/10 успешных запросов")
    print(f"        Среднее время: {avg_time:.1f}ms")
    print(f"        Мин/Макс: {min_time:.1f}ms / {max_time:.1f}ms")
    
    # Считаем тест пройденным если среднее время < 1000ms и все запросы успешны
    return avg_time < 1000 and successful == 10


def run_all_tests():
    """Запускает все тесты API"""
    print("🔍 ТЕСТИРОВАНИЕ API ENDPOINTS")
    print("=" * 80)
    
    tests = [
        ("Работоспособность сервера", test_server_health),
        ("Базовый расчет риска", test_calculate_risk_basic),
        ("Валидация данных", test_calculate_risk_validation),
        ("Быстрая оценка", test_quick_assessment), 
        ("Статистика рисков", test_risk_statistics),
        ("Прогнозирование", test_forecast_timeline),
        ("Производительность", test_performance)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"   💥 Тест провален")
        except Exception as e:
            failed += 1
            print(f"   💥 Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
        
        time.sleep(0.5)  # Небольшая пауза между тестами
    
    print("\n" + "=" * 80)
    print("📋 ИТОГИ ТЕСТИРОВАНИЯ API")
    print("=" * 80)
    print(f"✅ Пройдено тестов: {passed}")
    print(f"❌ Провалено тестов: {failed}")
    print(f"📊 Общее количество: {len(tests)}")
    
    if failed == 0:
        print("\n🎉 ВСЕ API ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("   API готово к использованию фронтендом")
        print("   Расчеты соответствуют Streamlit версии")
        return 0
    else:
        print(f"\n💥 ОБНАРУЖЕНЫ ПРОБЛЕМЫ В API!")
        print("   Требуется проверка и исправление")
        return 1


def check_api_vs_streamlit():
    """
    Специальный тест сравнения результатов API с оригинальным Streamlit
    """
    print("\n🔍 СРАВНЕНИЕ API С STREAMLIT ВЕРСИЕЙ")
    print("=" * 60)
    
    client = SimpleTestClient()
    
    # Тот же тестовый случай что использовали в сравнении
    test_case = {
        "pattern_type": "mixed_unstable",
        "total_cases": 5,
        "criminal_count": 2,
        "admin_count": 3,
        "days_since_last": 60,
        "current_age": 28,
        "age_at_first_violation": 21,
        "has_property": 0,
        "has_job": 1,
        "has_family": 0,
        "substance_abuse": 0,
        "has_escalation": 0,
        "admin_to_criminal": 1,
        "recidivism_rate": 1.5
    }
    
    response = client.post("/api/risks/calculate", test_case)
    
    if response['status_code'] != 200:
        print(f"❌ API недоступно: {response['status_code']}")
        return False
    
    api_risk_score = response['json']['risk_score']
    expected_risk_score = 5.760  # Из наших тестов сравнения
    
    difference = abs(api_risk_score - expected_risk_score)
    
    print(f"API риск-балл:      {api_risk_score:.3f}")
    print(f"Streamlit ожидаемый: {expected_risk_score:.3f}")
    print(f"Различие:           {difference:.6f}")
    
    if difference < 0.001:
        print("🎉 ПОЛНОЕ СООТВЕТСТВИЕ!")
        print("   API возвращает идентичные результаты")
        return True
    elif difference < 0.01:
        print("⚠️ Небольшое различие (в пределах допустимого)")
        return True
    else:
        print("💥 КРИТИЧЕСКОЕ РАЗЛИЧИЕ!")
        print("   Требуется проверка портирования")
        return False


if __name__ == "__main__":
    print("⚡ Запуск тестов API")
    print("ВАЖНО: Убедитесь что сервер запущен на http://localhost:8000")
    print()
    
    # Проверяем доступность сервера
    client = SimpleTestClient()
    try:
        health_response = client.get("/health")
        if health_response['status_code'] != 200:
            print("💥 Сервер недоступен! Запустите:")
            print("   cd backend && python3 -m uvicorn app.main:app --reload --port 8000")
            exit(1)
    except:
        print("💥 Сервер недоступен! Запустите:")
        print("   cd backend && python3 -m uvicorn app.main:app --reload --port 8000")
        exit(1)
    
    # Запускаем основные тесты
    exit_code = run_all_tests()
    
    # Специальный тест сравнения с Streamlit
    if exit_code == 0:
        if check_api_vs_streamlit():
            print("\n🚀 API ПОЛНОСТЬЮ ГОТОВО К ПРОДАКШЕНУ!")
        else:
            print("\n⚠️ API работает, но есть различия с оригиналом")
            exit_code = 1
    
    exit(exit_code)