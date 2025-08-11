# 🧹 Руководство по очистке тестовых данных

Это руководство поможет удалить все тестовые/демо данные и оставить только реальные данные из Excel файлов исследования.

## 🎯 Что будет удалено и что останется

### ✅ ОСТАЕТСЯ (реальные данные):
- `persons_real` - 146,570 реальных людей из Excel
- `violations_real` - реальные нарушения 
- `crime_transitions` - 6,465 переходов админ→кража
- `crime_time_windows` - временные окна преступлений
- `risk_assessment_history` - история расчетов
- `alembic_version` - версии миграций

### ❌ УДАЛЯЕТСЯ (тестовые данные):
- Все тестовые/демо таблицы
- Сгенерированные данные
- Временные таблицы

## 🚀 Способы очистки

### 1. Через скрипт (Рекомендуется)

```bash
cd backend
source venv/bin/activate
python scripts/cleanup_test_data.py
```

**Преимущества:**
- Интерактивное подтверждение
- Детальная проверка
- Резервное копирование метрик
- Полная верификация результатов

### 2. Через API

```bash
# Удалить только тестовые данные (безопасно)
curl -X DELETE "http://localhost:8001/api/import/clear-test-data?confirm=true"

# Проверить результат
curl "http://localhost:8001/api/persons/real/statistics"
```

### 3. Через веб-интерфейс

1. Откройте: http://localhost:8001/docs
2. Найдите: `DELETE /api/import/clear-test-data`
3. Установите: `confirm = true`
4. Нажмите: Execute

## 🔍 Проверка результатов

После очистки проверьте что реальные данные остались:

```bash
# Статистика реальных данных
curl "http://localhost:8001/api/persons/real/statistics"

# Должно показать примерно:
# - total_persons: ~146,570
# - expected_total: 146,570  
# - completeness: ~100%
```

## ⚠️ Важные замечания

### ✅ БЕЗОПАСНО:
- `DELETE /api/import/clear-test-data` - удаляет только тестовые данные
- `python scripts/cleanup_test_data.py` - с проверками и подтверждениями

### ⚠️ ОПАСНО:
- `DELETE /api/import/clear-all` - удаляет ВСЕ данные включая реальные!

## 📊 Что проверить после очистки

1. **Реальные данные сохранены:**
   ```bash
   curl "http://localhost:8001/api/persons/real/statistics"
   ```

2. **Поиск работает:**
   ```bash
   curl "http://localhost:8001/api/persons/real/search/123456789012"
   ```

3. **Критические константы соблюдены:**
   - ~146,570 человек
   - ~12,333 рецидивистов  
   - ~72.7% нестабильный паттерн

## 🔄 Если что-то пошло не так

### Восстановление данных:
```bash
cd backend
python scripts/initial_import.py
```

### Полная переустановка БД:
```bash
# Удалить БД
DROP DATABASE crime_prevention;

# Создать заново
CREATE DATABASE crime_prevention;

# Применить миграции
source venv/bin/activate
alembic upgrade head

# Импортировать данные
python scripts/initial_import.py
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `tail -f logs/app.log`
2. Проверьте БД: подключитесь к PostgreSQL
3. Запустите диагностику: `python scripts/analyze_excel_structure.py`

---

**💡 Совет:** Всегда делайте резервную копию БД перед масштабными изменениями!

```bash
pg_dump crime_prevention > backup_$(date +%Y%m%d_%H%M%S).sql
```