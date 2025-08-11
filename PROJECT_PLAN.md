# 📋 PROJECT PLAN: Миграция системы раннего предупреждения преступлений

## 📊 1. ТЕКУЩАЯ АРХИТЕКТУРА

### 1.1 Технологический стек
- **Frontend/Backend**: Streamlit (монолит)
- **База данных**: Excel файлы (.xlsx)
- **Визуализация**: Plotly
- **Обработка данных**: Pandas, NumPy
- **Развертывание**: Локальный запуск через `streamlit run main.py`

### 1.2 Структура файлов
```
recidiv/
├── main.py                      # Точка входа Streamlit (482 строки)
├── pages/                       # Страницы Streamlit приложения
│   ├── 1_🗺️_Карта_временных_окон.py
│   ├── 2_🚦_Статус_регионов.py
│   ├── 3_👥_Списки_лиц_риска.py
│   ├── 4_🔍_Поиск_по_ИИН.py
│   └── 5_⏰_Временные_прогнозы.py
├── utils/                       # Бизнес-логика
│   ├── risk_calculator.py      # Расчет рисков (486 строк)
│   ├── forecasting.py          # Прогнозирование (580 строк)
│   └── data_loader.py          # Загрузка данных (294 строки)
└── data/                        # Excel файлы с данными
    ├── RISK_ANALYSIS_RESULTS.xlsx
    ├── ML_DATASET_COMPLETE.xlsx
    ├── crime_analysis_results.xlsx
    ├── serious_crimes_analysis.xlsx
    └── risk_escalation_matrix.xlsx
```

### 1.3 Ключевые компоненты

#### **utils/risk_calculator.py**
- `RiskCalculator` - расчет риск-баллов (0-10)
- `CrimeForecaster` - прогнозирование временных окон
- `quick_risk_assessment()` - быстрая оценка

#### **utils/data_loader.py**
- `load_all_data()` - загрузка Excel файлов
- `get_risk_data()` - получение данных о рисках
- `search_person_by_iin()` - поиск по ИИН
- `get_crime_statistics()` - статистика преступлений

#### **utils/forecasting.py**
- `TimelineVisualizer` - визуализация временных линий
- `InterventionPlanner` - планирование вмешательств
- `generate_risk_report()` - генерация отчетов

### 1.4 Объем данных
- **146,570** проанализированных правонарушений
- **12,333** рецидивистов в базе
- **5** Excel файлов с данными
- **8** типов преступлений с временными окнами

## 🎯 2. ЦЕЛЕВАЯ АРХИТЕКТУРА

### 2.1 Технологический стек

#### Backend
- **Framework**: FastAPI 0.104+
- **База данных**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Миграции**: Alembic
- **Авторизация**: JWT (RS256)
- **Кэширование**: Redis (опционально)
- **Валидация**: Pydantic v2

#### Frontend
- **Framework**: React 18+
- **Язык**: TypeScript
- **Стилизация**: Tailwind CSS
- **Графики**: Recharts / Plotly.js
- **HTTP клиент**: Axios
- **State management**: Redux Toolkit
- **Routing**: React Router v6

#### DevOps
- **Контейнеризация**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Reverse proxy**: Nginx
- **Мониторинг**: Prometheus + Grafana
- **Логирование**: ELK Stack (опционально)

### 2.2 Целевая структура
```
recidiv/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI приложение
│   │   ├── config.py               # Настройки из .env
│   │   ├── database.py             # SQLAlchemy engine
│   │   ├── api/v1/
│   │   │   ├── auth.py            # JWT endpoints
│   │   │   ├── persons.py         # CRUD лиц
│   │   │   ├── risks.py           # Расчет рисков
│   │   │   ├── forecasts.py       # Прогнозы
│   │   │   ├── statistics.py      # Статистика
│   │   │   ├── interventions.py   # Планы вмешательств
│   │   │   └── regions.py         # Региональная аналитика
│   │   ├── models/                 # SQLAlchemy модели
│   │   ├── schemas/                # Pydantic схемы
│   │   ├── services/               # Бизнес-логика
│   │   ├── core/
│   │   │   ├── constants.py       # Константы исследования
│   │   │   ├── security.py        # JWT логика
│   │   │   └── exceptions.py      # Кастомные исключения
│   │   └── utils/                  # Вспомогательные функции
│   ├── alembic/                    # Миграции БД
│   ├── tests/                      # Pytest тесты
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/             # Переиспользуемые компоненты
│   │   ├── pages/                  # Страницы приложения
│   │   ├── services/               # API клиент
│   │   ├── store/                  # Redux store
│   │   ├── types/                  # TypeScript типы
│   │   └── utils/                  # Утилиты
│   ├── public/
│   └── package.json
│
├── docker/
│   ├── backend/Dockerfile
│   ├── frontend/Dockerfile
│   └── nginx/nginx.conf
│
├── docker-compose.yml
├── .github/workflows/               # CI/CD
│
├── utils/                           # СОХРАНЯЕМ - reference implementation
├── pages/                           # СОХРАНЯЕМ - Streamlit версия
├── main.py                          # СОХРАНЯЕМ - для сравнения
└── CLAUDE.MD                        # КРИТИЧЕСКИЕ ПРАВИЛА
```

## 🔄 3. КАРТА МИГРАЦИИ ФУНКЦИЙ

### 3.1 Модуль risk_calculator.py

| Текущий компонент | Целевой путь | Приоритет |
|-------------------|--------------|-----------|
| `RiskCalculator.calculate_risk_score()` | `backend/app/services/risk_service.py` | КРИТИЧЕСКИЙ |
| `RiskCalculator.get_risk_level()` | `backend/app/services/risk_service.py` | КРИТИЧЕСКИЙ |
| `RiskCalculator.calculate_crime_probability()` | `backend/app/services/risk_service.py` | КРИТИЧЕСКИЙ |
| `CrimeForecaster.forecast_crime_timeline()` | `backend/app/services/forecast_service.py` | КРИТИЧЕСКИЙ |
| `CrimeForecaster._calculate_single_forecast()` | `backend/app/services/forecast_service.py` | ВЫСОКИЙ |
| `quick_risk_assessment()` | `backend/app/api/v1/risks.py` | ВЫСОКИЙ |

### 3.2 Модуль data_loader.py

| Текущий компонент | Целевой путь | Приоритет |
|-------------------|--------------|-----------|
| `load_all_data()` | `backend/app/services/data_import_service.py` | ВЫСОКИЙ |
| `get_risk_data()` | `backend/app/services/person_service.py` | КРИТИЧЕСКИЙ |
| `get_crime_statistics()` | `backend/app/services/statistics_service.py` | ВЫСОКИЙ |
| `search_person_by_iin()` | `backend/app/services/person_service.py` | КРИТИЧЕСКИЙ |
| `validate_iin()` | `backend/app/utils/validators.py` | СРЕДНИЙ |
| `get_pattern_distribution()` | `backend/app/services/statistics_service.py` | СРЕДНИЙ |
| `calculate_statistics_summary()` | `backend/app/services/statistics_service.py` | СРЕДНИЙ |

### 3.3 Модуль forecasting.py

| Текущий компонент | Целевой путь | Приоритет |
|-------------------|--------------|-----------|
| `TimelineVisualizer.create_risk_timeline()` | `frontend/src/components/Timeline/RiskTimeline.tsx` | ВЫСОКИЙ |
| `TimelineVisualizer.create_calendar_heatmap()` | `frontend/src/components/Calendar/HeatMap.tsx` | СРЕДНИЙ |
| `TimelineVisualizer.create_risk_gauge()` | `frontend/src/components/RiskGauge/RiskGauge.tsx` | ВЫСОКИЙ |
| `InterventionPlanner.create_intervention_plan()` | `backend/app/services/intervention_service.py` | КРИТИЧЕСКИЙ |
| `InterventionPlanner.create_intervention_gantt()` | `frontend/src/components/Gantt/InterventionGantt.tsx` | СРЕДНИЙ |
| `generate_risk_report()` | `backend/app/services/report_service.py` | ВЫСОКИЙ |

### 3.4 Страницы Streamlit → React

| Streamlit страница | React компонент | API endpoints |
|-------------------|-----------------|---------------|
| `main.py` | `src/pages/Dashboard.tsx` | `/api/v1/statistics/summary` |
| `1_Карта_временных_окон.py` | `src/pages/TimelineMap.tsx` | `/api/v1/forecasts/timeline` |
| `2_Статус_регионов.py` | `src/pages/RegionStatus.tsx` | `/api/v1/regions/status` |
| `3_Списки_лиц_риска.py` | `src/pages/RiskList.tsx` | `/api/v1/persons/high-risk` |
| `4_Поиск_по_ИИН.py` | `src/pages/PersonSearch.tsx` | `/api/v1/persons/{iin}` |
| `5_Временные_прогнозы.py` | `src/pages/Forecasts.tsx` | `/api/v1/forecasts/personal` |

## ⚠️ 4. КРИТИЧЕСКИЕ КОНСТАНТЫ ДЛЯ СОХРАНЕНИЯ

### 4.1 Временные окна (в днях)
```python
CRIME_WINDOWS = {
    'Мошенничество': 109,
    'Кража': 146,
    'Убийство': 143,
    'Вымогательство': 144,
    'Грабеж': 148,
    'Разбой': 150,
    'Изнасилование': 157
}
```

### 4.2 Проценты предотвратимости
```python
PREVENTABILITY = {
    'Мошенничество': 82.3,
    'Кража': 87.3,
    'Убийство': 97.0,
    'Вымогательство': 100.0,  # В коде 100.7, уточнить!
    'Грабеж': 60.2,
    'Разбой': 20.2,
    'Изнасилование': 65.6
}
```

### 4.3 Веса факторов риска
```python
RISK_WEIGHTS = {
    'pattern_weight': 0.25,      # Паттерн поведения
    'history_weight': 0.20,      # История нарушений
    'time_weight': 0.15,         # Временной фактор
    'age_weight': 0.10,          # Возрастной фактор
    'social_weight': 0.15,       # Социальные факторы
    'escalation_weight': 0.15    # Факторы эскалации
}
```

### 4.4 Риски по паттернам
```python
PATTERN_RISKS = {
    'mixed_unstable': 0.8,       # 72.7% всех случаев
    'chronic_criminal': 0.9,     # 13.6% - высокий риск
    'escalating': 0.85,          # 7% - опасная тенденция
    'deescalating': 0.4,         # 5.7% - снижение риска
    'single': 0.3,               # 1% - единичные случаи
}
```

### 4.5 Ключевые статистики
```python
RESEARCH_STATS = {
    'total_violations': 146_570,
    'total_recidivists': 12_333,
    'preventable_percent': 97.0,
    'unstable_pattern_percent': 72.7,
    'admin_to_theft_transitions': 6_465,
    'avg_days_to_murder': 143
}
```

### 4.6 Категории риска
```python
RISK_CATEGORIES = {
    'critical': {'range': (7, 10), 'label': '🔴 Критический'},
    'high': {'range': (5, 7), 'label': '🟡 Высокий'},
    'medium': {'range': (3, 5), 'label': '🟠 Средний'},
    'low': {'range': (0, 3), 'label': '🟢 Низкий'}
}
```

## 🚨 5. РИСКИ И ИХ МИТИГАЦИЯ

### 5.1 Технические риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Потеря точности расчетов при переносе | ВЫСОКАЯ | КРИТИЧЕСКОЕ | 1. Юнит-тесты для каждой формулы<br>2. Сравнение результатов со Streamlit<br>3. Использование Decimal для точных вычислений |
| Изменение констант исследования | СРЕДНЯЯ | КРИТИЧЕСКОЕ | 1. Вынести все константы в отдельный модуль<br>2. Code review каждого PR<br>3. Автотесты на проверку констант |
| Потеря данных при миграции в PostgreSQL | СРЕДНЯЯ | ВЫСОКОЕ | 1. Поэтапная миграция<br>2. Backup исходных Excel<br>3. Валидация после импорта |
| Несовместимость версий библиотек | НИЗКАЯ | СРЕДНЕЕ | 1. Фиксация версий в requirements.txt<br>2. Использование Docker<br>3. Тестирование в изолированной среде |
| Проблемы с производительностью | СРЕДНЯЯ | СРЕДНЕЕ | 1. Индексы в БД<br>2. Кэширование Redis<br>3. Пагинация в API |

### 5.2 Бизнес-риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Недоступность системы при миграции | ВЫСОКАЯ | ВЫСОКОЕ | 1. Параллельная работа двух версий<br>2. Поэтапный переход<br>3. Rollback план |
| Неправильная интерпретация данных | СРЕДНЯЯ | КРИТИЧЕСКОЕ | 1. Документация каждого поля<br>2. Обучение пользователей<br>3. Сохранение UI паттернов |
| Потеря доверия пользователей | НИЗКАЯ | ВЫСОКОЕ | 1. A/B тестирование<br>2. Постепенный переход<br>3. Обратная связь |

### 5.3 Организационные риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Недостаток экспертизы в новом стеке | СРЕДНЯЯ | СРЕДНЕЕ | 1. Обучение команды<br>2. Привлечение консультантов<br>3. Подробная документация |
| Изменение требований в процессе | ВЫСОКАЯ | СРЕДНЕЕ | 1. Agile подход<br>2. Регулярные демо<br>3. MVP first |

## 📅 6. ПОРЯДОК ВЫПОЛНЕНИЯ ЗАДАЧ

### SPRINT 1: Подготовка инфраструктуры (3 дня)

#### День 1: Настройка окружения
- [ ] Создание структуры папок backend/frontend
- [ ] Инициализация Git репозитория с правильным .gitignore
- [ ] Настройка Docker окружения
- [ ] Установка PostgreSQL и создание схемы БД

#### День 2: Перенос констант и базовая настройка
- [ ] Создание `backend/app/core/constants.py` со ВСЕМИ константами
- [ ] Настройка SQLAlchemy моделей (Person, Violation, RiskAssessment)
- [ ] Создание Alembic миграций
- [ ] Импорт данных из Excel в PostgreSQL

#### День 3: Базовый FastAPI каркас
- [ ] Настройка FastAPI приложения с CORS
- [ ] Создание базовых endpoints (health check, версия API)
- [ ] Настройка JWT авторизации
- [ ] Создание Pydantic схем

### SPRINT 2: Портирование core бизнес-логики (5 дней)

#### День 4-5: Перенос RiskCalculator
- [ ] Создание `backend/app/services/risk_service.py`
- [ ] Портирование всех методов расчета риска
- [ ] Создание endpoint `/api/v1/risks/calculate`
- [ ] Написание тестов и сравнение с оригиналом

#### День 6-7: Перенос CrimeForecaster
- [ ] Создание `backend/app/services/forecast_service.py`
- [ ] Портирование прогнозирования временных окон
- [ ] Создание endpoint `/api/v1/forecasts/timeline`
- [ ] Тестирование точности прогнозов

#### День 8: Перенос data_loader функций
- [ ] Создание `backend/app/services/person_service.py`
- [ ] Реализация поиска по ИИН
- [ ] Создание endpoints для работы с лицами
- [ ] Валидация данных

### SPRINT 3: API endpoints и сервисы (4 дня)

#### День 9: Статистика и аналитика
- [ ] Создание `backend/app/services/statistics_service.py`
- [ ] Endpoint `/api/v1/statistics/summary`
- [ ] Endpoint `/api/v1/statistics/patterns`
- [ ] Кэширование результатов

#### День 10: Планирование вмешательств
- [ ] Создание `backend/app/services/intervention_service.py`
- [ ] Портирование InterventionPlanner
- [ ] Endpoint `/api/v1/interventions/plan`
- [ ] Генерация отчетов

#### День 11: Региональная аналитика
- [ ] Создание `backend/app/services/region_service.py`
- [ ] Endpoint `/api/v1/regions/status`
- [ ] Агрегация данных по регионам
- [ ] Тепловые карты

#### День 12: Интеграционное тестирование
- [ ] End-to-end тесты API
- [ ] Performance тестирование
- [ ] Проверка безопасности
- [ ] Документация OpenAPI

### SPRINT 4: Frontend разработка (5 дней)

#### День 13: Базовая структура React
- [ ] Создание React приложения с TypeScript
- [ ] Настройка Tailwind CSS
- [ ] Настройка Redux Toolkit
- [ ] Создание API клиента (Axios)

#### День 14: Компоненты визуализации
- [ ] RiskGauge компонент (спидометр риска)
- [ ] Timeline компонент (временная шкала)
- [ ] PersonCard компонент (карточка лица)
- [ ] Интеграция с Recharts/Plotly

#### День 15: Основные страницы
- [ ] Dashboard страница
- [ ] PersonSearch страница (поиск по ИИН)
- [ ] RiskList страница (списки риска)
- [ ] Навигация и routing

#### День 16: Дополнительные страницы
- [ ] TimelineMap страница
- [ ] RegionStatus страница
- [ ] Forecasts страница
- [ ] Интеграция с backend API

#### День 17: UI/UX полировка
- [ ] Responsive дизайн
- [ ] Обработка ошибок
- [ ] Loading states
- [ ] Уведомления (toast)

### SPRINT 5: DevOps и деплой (3 дня)

#### День 18: Docker и контейнеризация
- [ ] Dockerfile для backend
- [ ] Dockerfile для frontend
- [ ] docker-compose.yml
- [ ] Nginx конфигурация

#### День 19: CI/CD настройка
- [ ] GitHub Actions workflows
- [ ] Автоматические тесты
- [ ] Линтеры и форматеры
- [ ] Деплой на staging

#### День 20: Production подготовка
- [ ] Настройка мониторинга
- [ ] Настройка логирования
- [ ] Backup стратегия
- [ ] Документация для ops

### SPRINT 6: Финализация (2 дня)

#### День 21: Тестирование и сравнение
- [ ] Полное сравнение результатов с оригиналом
- [ ] User Acceptance Testing
- [ ] Performance оптимизация
- [ ] Security audit

#### День 22: Документация и передача
- [ ] Техническая документация
- [ ] Руководство пользователя
- [ ] Обучение команды
- [ ] Планирование поддержки

## 📊 7. МЕТРИКИ УСПЕХА

### Технические метрики
- [ ] 100% совпадение риск-баллов с оригиналом (допуск ±0.01)
- [ ] Время ответа API < 200ms для расчета риска
- [ ] Доступность системы > 99.9%
- [ ] Test coverage > 80%
- [ ] 0 критических уязвимостей безопасности

### Бизнес-метрики
- [ ] Сохранение всех 146,570 записей о правонарушениях
- [ ] Точность прогнозов не ниже оригинала
- [ ] Все временные окна соответствуют исследованию
- [ ] Все проценты предотвратимости сохранены

### Качественные метрики
- [ ] Streamlit версия продолжает работать
- [ ] Новая версия проходит все acceptance критерии
- [ ] Документация покрывает все аспекты системы
- [ ] Команда обучена работе с новой системой

## 🔄 8. ROLLBACK ПЛАН

### Условия для rollback
1. Расхождение в расчетах > 1%
2. Потеря критических данных
3. Недоступность системы > 1 часа
4. Критические ошибки безопасности

### Процедура rollback
1. Остановка новой версии
2. Переключение DNS на старую версию
3. Восстановление БД из backup
4. Анализ причин и исправление
5. Повторная попытка миграции

## 📝 9. КОНТРОЛЬНЫЕ ТОЧКИ

### После каждого спринта
- [ ] Code review всех изменений
- [ ] Сравнение результатов с оригиналом
- [ ] Проверка сохранности констант
- [ ] Работоспособность Streamlit версии
- [ ] Обновление документации

### Перед production деплоем
- [ ] Полное regression тестирование
- [ ] Performance тестирование под нагрузкой
- [ ] Security assessment
- [ ] Backup всех данных
- [ ] Готовность rollback плана

## 📚 10. ДОКУМЕНТАЦИЯ

### Требуемые документы
1. **API документация** (OpenAPI/Swagger)
2. **Архитектурная документация** (C4 диаграммы)
3. **Руководство пользователя** (с скриншотами)
4. **Руководство администратора** (деплой, мониторинг)
5. **Справочник констант** (все значения из исследования)
6. **Тестовая документация** (test cases)
7. **Миграционное руководство** (для данных)

---

**Последнее обновление**: 2024-12-13  
**Версия плана**: 1.0  
**Ответственный**: Crime Prevention System Team  
**Критический reminder**: НИКОГДА не изменять константы из исследования!