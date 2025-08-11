# 📋 MIGRATION CHECKLIST

## 🚨 КРИТИЧЕСКИ ВАЖНО - ПЕРЕД НАЧАЛОМ РАБОТЫ

- [ ] **Прочитан файл CLAUDE.MD полностью**
- [ ] **Сделан backup всех файлов utils/ и pages/**
- [ ] **Streamlit версия тестируется: `streamlit run main.py`**
- [ ] **Все Excel файлы в папке data/ присутствуют**

---

## 📊 1. КОНСТАНТЫ ИЗ ИССЛЕДОВАНИЯ (КРИТИЧЕСКИЙ ПРИОРИТЕТ)

### 1.1 Временные окна (в днях) ⏰
- [ ] `Мошенничество: 109 дней` → `backend/app/core/constants.py`
- [ ] `Кража: 146 дней` → `backend/app/core/constants.py`
- [ ] `Убийство: 143 дня` → `backend/app/core/constants.py`
- [ ] `Вымогательство: 144 дня` → `backend/app/core/constants.py`
- [ ] `Грабеж: 148 дней` → `backend/app/core/constants.py`
- [ ] `Разбой: 150 дней` → `backend/app/core/constants.py`
- [ ] `Изнасилование: 157 дней` → `backend/app/core/constants.py`

### 1.2 Проценты предотвратимости 🎯
- [ ] `Мошенничество: 82.3%` → `backend/app/core/constants.py`
- [ ] `Кража: 87.3%` → `backend/app/core/constants.py`
- [ ] `Убийство: 97.0%` → `backend/app/core/constants.py`
- [ ] `Вымогательство: 100.0%` → `backend/app/core/constants.py` ⚠️ (проверить 100.7 в коде)
- [ ] `Грабеж: 60.2%` → `backend/app/core/constants.py`
- [ ] `Разбой: 20.2%` → `backend/app/core/constants.py`
- [ ] `Изнасилование: 65.6%` → `backend/app/core/constants.py`

### 1.3 Веса факторов риска ⚖️
- [ ] `pattern_weight: 0.25` → `backend/app/core/constants.py`
- [ ] `history_weight: 0.20` → `backend/app/core/constants.py`
- [ ] `time_weight: 0.15` → `backend/app/core/constants.py`
- [ ] `age_weight: 0.10` → `backend/app/core/constants.py`
- [ ] `social_weight: 0.15` → `backend/app/core/constants.py`
- [ ] `escalation_weight: 0.15` → `backend/app/core/constants.py`

### 1.4 Риски по паттернам поведения 📈
- [ ] `mixed_unstable: 0.8 (72.7%)` → `backend/app/core/constants.py`
- [ ] `chronic_criminal: 0.9 (13.6%)` → `backend/app/core/constants.py`
- [ ] `escalating: 0.85 (7%)` → `backend/app/core/constants.py`
- [ ] `deescalating: 0.4 (5.7%)` → `backend/app/core/constants.py`
- [ ] `single: 0.3 (1%)` → `backend/app/core/constants.py`

### 1.5 Статистика исследования 📋
- [ ] `Всего проанализировано: 146,570` → `backend/app/core/constants.py`
- [ ] `Рецидивистов: 12,333` → `backend/app/core/constants.py`
- [ ] `Процент предотвратимых: 97.0%` → `backend/app/core/constants.py`
- [ ] `Нестабильный паттерн: 72.7%` → `backend/app/core/constants.py`
- [ ] `Переходы админ→кража: 6,465` → `backend/app/core/constants.py`

### 1.6 Категории риска 🚦
- [ ] `Критический: 7-10 баллов (🔴)` → `backend/app/core/constants.py`
- [ ] `Высокий: 5-6 баллов (🟡)` → `backend/app/core/constants.py`
- [ ] `Средний: 3-4 балла (🟠)` → `backend/app/core/constants.py`
- [ ] `Низкий: 0-2 балла (🟢)` → `backend/app/core/constants.py`

---

## 🔄 2. ПОРТИРОВАНИЕ ФУНКЦИЙ utils/ → backend/services/

### 2.1 utils/risk_calculator.py → backend/app/services/risk_service.py

#### Класс RiskCalculator
- [ ] `__init__()` → Инициализация весов и рисков
- [ ] `calculate_risk_score()` → Основная функция расчета (0-10)
- [ ] `_calculate_history_score()` → Компонент истории нарушений
- [ ] `_calculate_time_score()` → Временной компонент
- [ ] `_calculate_age_score()` → Возрастной компонент
- [ ] `_calculate_social_score()` → Социальный компонент
- [ ] `_calculate_escalation_score()` → Компонент эскалации
- [ ] `get_risk_level()` → Определение уровня риска и рекомендаций
- [ ] `calculate_crime_probability()` → Вероятность конкретного преступления

#### Класс CrimeForecaster
- [ ] `__init__()` → Инициализация временных окон
- [ ] `forecast_crime_timeline()` → Прогнозы для всех типов преступлений
- [ ] `_calculate_single_forecast()` → Прогноз для одного типа
- [ ] `_get_age_modifier()` → Возрастной модификатор
- [ ] `_get_pattern_modifier()` → Модификатор паттерна
- [ ] `_get_social_modifier()` → Социальный модификатор
- [ ] `_calculate_confidence()` → Уровень уверенности
- [ ] `_get_timeline_risk_level()` → Риск по временной шкале

#### Вспомогательные функции
- [ ] `quick_risk_assessment()` → Быстрая оценка риска

### 2.2 utils/data_loader.py → backend/app/services/data_service.py

#### Загрузка данных
- [ ] `load_all_data()` → Загрузка Excel файлов
- [ ] `get_risk_data()` → Получение данных о рисках
- [ ] `get_crime_statistics()` → Статистика преступлений
- [ ] `get_pattern_distribution()` → Распределение паттернов

#### Поиск и валидация
- [ ] `validate_iin()` → Валидация ИИН
- [ ] `search_person_by_iin()` → Поиск по ИИН
- [ ] `get_risk_category()` → Категория риска по баллу

#### Аналитика
- [ ] `get_escalation_patterns()` → Паттерны эскалации
- [ ] `calculate_statistics_summary()` → Сводная статистика

#### Утилиты
- [ ] `parse_date()` → Парсинг дат
- [ ] `days_between()` → Разница в днях

### 2.3 utils/forecasting.py → backend/app/services/forecast_service.py

#### Класс TimelineVisualizer (логика, не визуализация)
- [ ] `_generate_risk_curve()` → Генерация кривой риска
- [ ] `_get_fill_color()` → Цветовая схема

#### Класс InterventionPlanner
- [ ] `__init__()` → База рекомендаций по типам преступлений
- [ ] `create_intervention_plan()` → Персональный план вмешательства

#### Функции отчетности
- [ ] `generate_risk_report()` → Полный отчет о рисках
- [ ] `format_risk_summary()` → Форматирование сводки

---

## 📡 3. API ENDPOINTS ПОКРЫТИЕ

### 3.1 Базовые endpoints
- [ ] `GET /` → Health check
- [ ] `GET /api/v1/info` → Информация о системе
- [ ] `GET /api/v1/version` → Версия API

### 3.2 Авторизация
- [ ] `POST /api/v1/auth/login` → Вход в систему
- [ ] `POST /api/v1/auth/logout` → Выход
- [ ] `GET /api/v1/auth/me` → Текущий пользователь

### 3.3 Статистика (main.py функционал)
- [ ] `GET /api/v1/statistics/summary` → Общая статистика системы
- [ ] `GET /api/v1/statistics/patterns` → Распределение паттернов
- [ ] `GET /api/v1/statistics/crimes` → Статистика преступлений
- [ ] `GET /api/v1/statistics/escalations` → Паттерны эскалации

### 3.4 Работа с лицами (4_Поиск_по_ИИН.py)
- [ ] `GET /api/v1/persons/search/{iin}` → Поиск по ИИН
- [ ] `POST /api/v1/persons/validate-iin` → Валидация ИИН
- [ ] `GET /api/v1/persons/{person_id}` → Данные лица по ID

### 3.5 Расчет рисков (risk_calculator.py)
- [ ] `POST /api/v1/risks/calculate` → Расчет риск-балла
- [ ] `POST /api/v1/risks/quick-assessment` → Быстрая оценка
- [ ] `GET /api/v1/risks/levels` → Описание уровней риска

### 3.6 Прогнозирование (5_Временные_прогнозы.py)
- [ ] `POST /api/v1/forecasts/timeline` → Прогноз временных окон
- [ ] `POST /api/v1/forecasts/single` → Прогноз для одного типа
- [ ] `POST /api/v1/forecasts/probability` → Вероятность преступления

### 3.7 Списки рисков (3_Списки_лиц_риска.py)
- [ ] `GET /api/v1/risks/high-risk` → Список лиц высокого риска
- [ ] `GET /api/v1/risks/critical` → Критический риск
- [ ] `GET /api/v1/risks/by-category/{category}` → По категории

### 3.8 Региональная аналитика (2_Статус_регионов.py)
- [ ] `GET /api/v1/regions/status` → Статус всех регионов
- [ ] `GET /api/v1/regions/{region_id}/statistics` → Статистика региона
- [ ] `GET /api/v1/regions/heatmap` → Данные для тепловой карты

### 3.9 Временные карты (1_Карта_временных_окон.py)
- [ ] `GET /api/v1/timelines/crime-windows` → Временные окна преступлений
- [ ] `POST /api/v1/timelines/personal` → Персональная временная шкала
- [ ] `GET /api/v1/timelines/calendar` → Календарные данные

### 3.10 Планы вмешательства
- [ ] `POST /api/v1/interventions/plan` → Создание плана
- [ ] `GET /api/v1/interventions/programs` → Доступные программы
- [ ] `POST /api/v1/interventions/gantt` → Диаграмма Ганта

---

## 🎨 4. FRONTEND КОМПОНЕНТЫ (pages/ → src/)

### 4.1 main.py → src/pages/Dashboard.tsx
- [ ] **Основные метрики** (97%, 143 дня, 72.7%, 6,465)
- [ ] **Статус системы** (файлы данных, модули)
- [ ] **График временных окон** (Plotly → Recharts)
- [ ] **Диаграмма паттернов** (круговая диаграмма)
- [ ] **Боковая панель** (статистика, уровни риска)
- [ ] **Навигационные карточки**

### 4.2 4_Поиск_по_ИИН.py → src/pages/PersonSearch.tsx
- [ ] **Поле ввода ИИН** с валидацией
- [ ] **Карточка лица** (персональная информация)
- [ ] **Спидометр риска** (RiskGauge компонент)
- [ ] **Компоненты риска** (детализация баллов)
- [ ] **История нарушений** (таблица/список)
- [ ] **Рекомендации** по работе

### 4.3 3_Списки_лиц_риска.py → src/pages/RiskList.tsx
- [ ] **Фильтры по уровню риска** (критический, высокий, средний, низкий)
- [ ] **Таблица лиц** с сортировкой и пагинацией
- [ ] **Цветовые индикаторы** риска
- [ ] **Поиск и фильтрация** по различным критериям
- [ ] **Экспорт данных** в CSV/Excel
- [ ] **Bulk операции** (массовые действия)

### 4.4 5_Временные_прогнозы.py → src/pages/Forecasts.tsx
- [ ] **Форма ввода данных лица**
- [ ] **Timeline компонент** (временная шкала рисков)
- [ ] **Календарная тепловая карта** (HeatMap)
- [ ] **Список прогнозов** (таблица с вероятностями)
- [ ] **Доверительные интервалы** на графике
- [ ] **План вмешательства** (Gantt диаграмма)

### 4.5 1_Карта_временных_окон.py → src/pages/TimelineMap.tsx
- [ ] **Интерактивный график** временных окон
- [ ] **Селектор типов преступлений**
- [ ] **Фильтры по времени** (30, 90, 180, 365 дней)
- [ ] **Детализация по типам** (hover эффекты)
- [ ] **Легенда и подсказки**
- [ ] **Экспорт графика**

### 4.6 2_Статус_регионов.py → src/pages/RegionStatus.tsx
- [ ] **Карта регионов** (если есть геоданные)
- [ ] **Светофор статусов** (зеленый/желтый/красный)
- [ ] **Таблица регионов** с метриками
- [ ] **Детализация по региону** (клик для подробностей)
- [ ] **Сравнительная аналитика**
- [ ] **Тренды по времени**

---

## 🧩 5. ПЕРЕИСПОЛЬЗУЕМЫЕ КОМПОНЕНТЫ

### 5.1 src/components/RiskGauge/
- [ ] **RiskGauge.tsx** → Спидометр риска (0-10)
- [ ] **Цветовая схема** → Зеленый/Оранжевый/Красный
- [ ] **Анимации** → Плавные переходы значений
- [ ] **Размеры** → Маленький, средний, большой

### 5.2 src/components/Timeline/
- [ ] **RiskTimeline.tsx** → Временная шкала рисков
- [ ] **InteractivePlot.tsx** → Интерактивные графики
- [ ] **Доверительные интервалы** → Затенение областей
- [ ] **Маркеры событий** → Вертикальные линии

### 5.3 src/components/PersonCard/
- [ ] **PersonInfo.tsx** → Основная информация
- [ ] **RiskSummary.tsx** → Сводка по рискам
- [ ] **ViolationHistory.tsx** → История нарушений
- [ ] **Recommendations.tsx** → Рекомендации

### 5.4 src/components/Dashboard/
- [ ] **MetricCard.tsx** → Карточки метрик
- [ ] **StatisticsWidget.tsx** → Виджеты статистики
- [ ] **SystemStatus.tsx** → Статус системы
- [ ] **NavigationGrid.tsx** → Сетка навигации

### 5.5 src/components/Calendar/
- [ ] **HeatMap.tsx** → Календарная тепловая карта
- [ ] **DateRange.tsx** → Выбор диапазона дат
- [ ] **RiskCalendar.tsx** → Календарь с индикаторами риска

### 5.6 src/components/Gantt/
- [ ] **InterventionGantt.tsx** → Диаграмма Ганта планов
- [ ] **TaskTimeline.tsx** → Временная линия задач
- [ ] **ProgramCard.tsx** → Карточки программ

---

## 🧪 6. КРИТИЧЕСКИЕ ТЕСТЫ

### 6.1 Тесты расчетов (backend/tests/test_risk_service.py)
- [ ] **test_risk_score_calculation()** → Точность расчета риск-балла
- [ ] **test_risk_components()** → Проверка каждого компонента
- [ ] **test_risk_levels()** → Корректность уровней риска
- [ ] **test_pattern_risks()** → Риски по паттернам поведения
- [ ] **test_age_modifiers()** → Возрастные модификаторы
- [ ] **test_time_factors()** → Временные факторы

### 6.2 Тесты прогнозирования (backend/tests/test_forecast_service.py)
- [ ] **test_crime_timeline()** → Временные окна преступлений
- [ ] **test_probability_calculation()** → Расчет вероятностей
- [ ] **test_confidence_levels()** → Уровни уверенности
- [ ] **test_intervention_plans()** → Планы вмешательств

### 6.3 Тесты данных (backend/tests/test_data_service.py)
- [ ] **test_iin_validation()** → Валидация ИИН
- [ ] **test_person_search()** → Поиск по ИИН
- [ ] **test_statistics_calculation()** → Расчет статистики
- [ ] **test_pattern_distribution()** → Распределение паттернов

### 6.4 Тесты констант (backend/tests/test_constants.py)
- [ ] **test_crime_windows()** → Временные окна из исследования
- [ ] **test_preventability_rates()** → Проценты предотвратимости
- [ ] **test_risk_weights()** → Веса факторов риска
- [ ] **test_pattern_risks()** → Риски паттернов
- [ ] **test_research_stats()** → Статистика исследования

### 6.5 Интеграционные тесты (backend/tests/test_integration.py)
- [ ] **test_full_risk_assessment()** → Полная оценка риска
- [ ] **test_api_responses()** → Корректность API ответов
- [ ] **test_data_consistency()** → Согласованность данных
- [ ] **test_performance()** → Производительность расчетов

---

## 📊 7. СРАВНЕНИЕ РЕЗУЛЬТАТОВ (КРИТИЧНО!)

### 7.1 Контрольные тесты
- [ ] **Streamlit vs FastAPI** → Один и тот же ИИН дает одинаковый риск-балл
- [ ] **Временные окна** → Прогнозы совпадают с точностью до дня
- [ ] **Статистика** → Все показатели 146,570 / 12,333 / 97% неизменны
- [ ] **Паттерны** → Распределение 72.7% / 13.6% / 7% точное
- [ ] **Категории риска** → Пороги 7+ / 5-6 / 3-4 / 0-2 сохранены

### 7.2 Тестовые случаи
- [ ] **Тестовый ИИН #1** → Риск-балл X.X в обеих системах
- [ ] **Тестовый ИИН #2** → Временное окно Y дней в обеих системах
- [ ] **Общая статистика** → Суммы и проценты идентичны
- [ ] **Edge cases** → Крайние случаи (мин/макс значения)

---

## 🚀 8. РАЗВЕРТЫВАНИЕ И ИНФРАСТРУКТУРА

### 8.1 База данных
- [ ] **PostgreSQL** установлен и настроен
- [ ] **Alembic миграции** созданы для всех таблиц
- [ ] **Данные импортированы** из Excel файлов
- [ ] **Индексы** созданы для поиска по ИИН
- [ ] **Backup стратегия** настроена

### 8.2 Backend деплой
- [ ] **FastAPI сервер** запускается без ошибок
- [ ] **Environment variables** настроены
- [ ] **CORS** правильно сконфигурирован
- [ ] **JWT авторизация** работает
- [ ] **Health check** endpoint отвечает

### 8.3 Frontend деплой
- [ ] **React приложение** собирается без ошибок
- [ ] **TypeScript** компиляция успешна
- [ ] **Все страницы** доступны по роутам
- [ ] **API интеграция** работает
- [ ] **Responsive дизайн** на всех устройствах

### 8.4 Docker контейнеры
- [ ] **Backend Dockerfile** оптимизирован
- [ ] **Frontend Dockerfile** оптимизирован
- [ ] **docker-compose.yml** настроен
- [ ] **Nginx** конфигурация готова
- [ ] **Все сервисы** запускаются одной командой

---

## 📈 9. ПРОИЗВОДИТЕЛЬНОСТЬ И МОНИТОРИНГ

### 9.1 Performance метрики
- [ ] **Время ответа API** < 200ms для расчета риска
- [ ] **Загрузка страниц** < 2s для основных страниц
- [ ] **Memory usage** оптимизирован
- [ ] **Database queries** оптимизированы с индексами

### 9.2 Мониторинг
- [ ] **Health check** endpoints для всех сервисов
- [ ] **Логирование** настроено (уровни debug/info/error)
- [ ] **Error tracking** для критических ошибок
- [ ] **Metrics collection** для бизнес-метрик

---

## 🔒 10. БЕЗОПАСНОСТЬ И КАЧЕСТВО

### 10.1 Безопасность
- [ ] **Нет hardcoded секретов** в коде
- [ ] **Environment variables** для всех настроек
- [ ] **JWT токены** с ограниченным временем жизни
- [ ] **CORS** настроен только для нужных доменов
- [ ] **Input validation** на всех endpoints

### 10.2 Качество кода
- [ ] **Linting** (ESLint для frontend, flake8/black для backend)
- [ ] **Type checking** (TypeScript, mypy)
- [ ] **Code coverage** > 80% для критических модулей
- [ ] **Documentation** для всех API endpoints
- [ ] **Comments** в коде на русском языке

---

## ✅ 11. ФИНАЛЬНАЯ ПРОВЕРКА

### 11.1 Функциональность
- [ ] **Все 5 страниц** Streamlit имеют аналоги в React
- [ ] **Все функции** из utils/ портированы в services/
- [ ] **Все константы** из исследования сохранены
- [ ] **Streamlit версия** продолжает работать
- [ ] **Новая версия** проходит все тесты

### 11.2 Пользовательский опыт
- [ ] **UI соответствует** оригиналу по функциональности
- [ ] **Скорость работы** не хуже оригинала
- [ ] **Все графики** отображаются корректно
- [ ] **Поиск по ИИН** работает мгновенно
- [ ] **Экспорт данных** доступен

### 11.3 Техническая готовность
- [ ] **Production environment** настроен
- [ ] **CI/CD pipeline** работает
- [ ] **Backup & restore** протестированы
- [ ] **Rollback план** готов к выполнению
- [ ] **Документация** обновлена

---

## 🚨 КРИТИЧЕСКИЕ STOP-ТОЧКИ

**НЕМЕДЛЕННО ОСТАНОВИ РАБОТУ ЕСЛИ:**

❌ **Риск-балл отличается** от оригинала более чем на 0.01  
❌ **Временные окна изменились** (109→146→143 дня должны остаться)  
❌ **Константы изменены** (72.7%, 97%, 146,570, 12,333)  
❌ **Streamlit перестал работать** (`streamlit run main.py`)  
❌ **Потеряны данные** из Excel файлов  

**В ЭТИХ СЛУЧАЯХ:**
1. Останови все изменения
2. Восстанови из backup
3. Проанализируй причину
4. Исправь проблему
5. Повтори проверку

---

## 📋 СТАТУСЫ ВЫПОЛНЕНИЯ

**ОБОЗНАЧЕНИЯ:**
- ✅ **Выполнено и протестировано**
- 🟡 **В процессе выполнения**  
- ❌ **Не выполнено**
- ⚠️ **Требует внимания**
- 🔄 **Требует ретеста**

---

**Последнее обновление**: 2024-12-13  
**Версия чеклиста**: 1.0  
**Критический reminder**: ВСЕ константы из исследования 146,570 правонарушений должны остаться неизменными!