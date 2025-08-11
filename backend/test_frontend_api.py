#!/usr/bin/env python3
"""
Тест API для симуляции вызовов фронтенда
"""
import requests
import json
import sys

def test_search_by_iin():
    """Тестирует поиск по ИИН как это делает фронтенд"""
    
    url = "http://127.0.0.1:8001/api/persons/search/010126551420"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        print("🔍 Тестируем API поиск по ИИН...")
        print(f"URL: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API вернул 200 OK")
            
            # Проверяем структуру ответа
            if 'person' in data:
                print(f"✅ Person найден: {data['person']['full_name']}")
                print(f"   ИИН: {data['person']['iin']}")
                
            if 'risk_calculation' in data:
                print(f"✅ Risk calculation: {data['risk_calculation']['risk_score']} ({data['risk_calculation']['risk_level']})")
                
            if 'forecast_timeline' in data:
                print(f"✅ Forecast timeline: {len(data['forecast_timeline']['forecasts'])} прогнозов")
                first_forecast = data['forecast_timeline']['forecasts'][0]
                print(f"   Первый прогноз: {first_forecast['crime_type']} - {first_forecast['risk_level']}")
                
            if 'violations' in data:
                print(f"✅ Violations: {len(data['violations'])} нарушений")
                
            # Проверяем типы данных
            print("\n📊 Проверка типов данных:")
            print(f"   person.id: {type(data['person']['id'])} = {data['person']['id']}")
            print(f"   risk_level: {type(data['risk_calculation']['risk_level'])} = '{data['risk_calculation']['risk_level']}'")
            
            forecast_risk = data['forecast_timeline']['forecasts'][0]['risk_level']
            print(f"   forecast.risk_level: {type(forecast_risk)} = '{forecast_risk}'")
            
            print("\n✅ Все данные корректны для фронтенда!")
            return True
            
        else:
            print(f"❌ API вернул ошибку {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Детали: {error_data}")
            except:
                print(f"   Текст ошибки: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        print(f"   Response: {response.text[:500]}...")
        return False
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Запуск теста API фронтенда")
    print("=" * 50)
    
    success = test_search_by_iin()
    
    if success:
        print("\n✅ Все тесты прошли успешно!")
        sys.exit(0)
    else:
        print("\n❌ Тесты не прошли!")
        sys.exit(1)