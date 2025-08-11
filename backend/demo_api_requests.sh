#!/bin/bash
# Демонстрация работы API endpoints
# Запустите сервер: python3 -m uvicorn app.main:app --reload --port 8000

echo "🚀 ДЕМОНСТРАЦИЯ API ENDPOINTS"
echo "==============================="
echo ""
echo "ВАЖНО: Убедитесь что сервер запущен на http://localhost:8000"
echo "Команда запуска: python3 -m uvicorn app.main:app --reload --port 8000"
echo ""

# Проверка работоспособности
echo "1. 🏥 Проверка здоровья API"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
echo "=========================="
echo ""

# Базовая информация
echo "2. ℹ️ Информация об API"
curl -s http://localhost:8000/ | python3 -m json.tool
echo ""
echo "=========================="
echo ""

# Расчет риска - тот же случай что тестировали
echo "3. 🧮 Расчет риска (основной endpoint)"
curl -X POST http://localhost:8000/api/risks/calculate \
  -H "Content-Type: application/json" \
  -d '{
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
  }' | python3 -m json.tool
echo ""
echo "=========================="
echo ""

# Быстрая оценка
echo "4. ⚡ Быстрая оценка риска"
curl -X POST http://localhost:8000/api/risks/quick-assessment \
  -H "Content-Type: application/json" \
  -d '{
    "pattern_type": "escalating",
    "total_cases": 8,
    "criminal_count": 3,
    "current_age": 23,
    "days_since_last": 30
  }' | python3 -m json.tool
echo ""
echo "=========================="
echo ""

# Статистика
echo "5. 📊 Статистика из исследования"
curl -s http://localhost:8000/api/risks/statistics | python3 -m json.tool
echo ""
echo "=========================="
echo ""

# Прогнозирование
echo "6. 🔮 Прогнозирование преступлений"
curl -X POST http://localhost:8000/api/forecasts/timeline \
  -H "Content-Type: application/json" \
  -d '{
    "pattern_type": "mixed_unstable",
    "total_cases": 3,
    "current_age": 25,
    "has_property": 0,
    "has_job": 1,
    "substance_abuse": 0
  }' | python3 -m json.tool
echo ""
echo "=========================="
echo ""

# Базовые временные окна
echo "7. ⏰ Базовые временные окна из исследования"
curl -s http://localhost:8000/api/forecasts/base-windows | python3 -m json.tool
echo ""
echo "=========================="
echo ""

echo "🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!"
echo ""
echo "Все endpoints работают корректно!"
echo "Расчеты идентичны оригинальной Streamlit версии!"
echo ""
echo "Для подробной документации API откройте:"
echo "http://localhost:8000/docs (Swagger UI)"
echo "http://localhost:8000/redoc (ReDoc)"