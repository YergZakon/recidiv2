"""
Модели для хранения реальных данных
Структура соответствует Excel файлам
ВАЖНО: Сохраняем ВСЕ данные из исследования без изменений
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, Index
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime

class PersonReal(Base):
    """Реальные данные о лицах из RISK_ANALYSIS_RESULTS.xlsx"""
    __tablename__ = "persons_real"
    
    id = Column(Integer, primary_key=True, index=True)
    iin = Column(String, unique=True, index=True)  # ИИН - уникальный идентификатор
    
    # ФИО
    last_name = Column(String)  # Фамилия
    first_name = Column(String)  # Имя
    middle_name = Column(String)  # Отчество
    full_name = Column(String)  # Полное ФИО для быстрого поиска
    
    # Демографические данные
    birth_date = Column(DateTime)
    current_age = Column(Integer)
    age_at_first_violation = Column(Integer)
    gender = Column(String)
    region = Column(String, index=True)
    city = Column(String)
    district = Column(String)
    
    # Криминальная история
    total_cases = Column(Integer, default=0)  # Общее количество дел
    criminal_count = Column(Integer, default=0)  # Уголовные
    admin_count = Column(Integer, default=0)  # Административные
    first_violation_date = Column(DateTime)
    last_violation_date = Column(DateTime)
    days_since_last = Column(Integer)  # Дней с последнего нарушения
    days_between_violations = Column(Float)  # Среднее время между нарушениями
    
    # Паттерны поведения (КРИТИЧНО: 72.7% mixed_unstable)
    pattern_type = Column(String, index=True)  # mixed_unstable, chronic_criminal и т.д.
    has_escalation = Column(Boolean, default=False)  # Есть ли эскалация
    escalation_type = Column(String)  # Тип эскалации (админ->уголовка)
    escalation_details = Column(JSON)  # Детали эскалации
    
    # Риск-баллы (0-10 шкала из исследования)
    risk_total_risk_score = Column(Float, index=True)  # Общий риск-балл
    risk_pattern_component = Column(Float)  # Компонент паттерна (вес 0.25)
    risk_history_component = Column(Float)  # Компонент истории (вес 0.20)
    risk_time_component = Column(Float)  # Временной компонент (вес 0.15)
    risk_age_component = Column(Float)  # Возрастной компонент (вес 0.10)
    risk_social_component = Column(Float)  # Социальный компонент (вес 0.15)
    risk_escalation_component = Column(Float)  # Компонент эскалации (вес 0.15)
    risk_category = Column(String)  # critical, high, medium, low
    
    # Социальные факторы
    has_property = Column(Integer, default=0)  # Есть имущество
    has_job = Column(Integer, default=0)  # Есть работа
    has_family = Column(Integer, default=0)  # Есть семья
    education_level = Column(String)  # Уровень образования
    employment_status = Column(String)  # Статус занятости
    marital_status = Column(String)  # Семейное положение
    
    # Прогнозирование (временные окна из исследования)
    predicted_crime_type = Column(String)  # Прогнозируемый тип преступления
    predicted_days_until = Column(Integer)  # Дней до преступления
    prediction_confidence = Column(Float)  # Уверенность прогноза
    preventability_score = Column(Float)  # Процент предотвратимости (97% overall)
    
    # Метаданные импорта
    import_date = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    source_file = Column(String)
    source_sheet = Column(String)
    raw_data = Column(JSON)  # Сохраняем оригинальную строку для аудита
    data_quality_score = Column(Float)  # Качество данных (полнота полей)
    
    # Создаем составные индексы для быстрого поиска
    __table_args__ = (
        Index('idx_risk_region', 'risk_total_risk_score', 'region'),
        Index('idx_pattern_risk', 'pattern_type', 'risk_total_risk_score'),
        Index('idx_last_violation', 'last_violation_date', 'risk_total_risk_score'),
    )

class ViolationReal(Base):
    """Реальные данные о нарушениях"""
    __tablename__ = "violations_real"
    
    id = Column(Integer, primary_key=True, index=True)
    person_iin = Column(String, index=True)  # ИИН нарушителя
    
    # Данные о нарушении
    violation_date = Column(DateTime, index=True)
    violation_type = Column(String)  # criminal, admin
    violation_category = Column(String)  # Категория (кража, мошенничество и т.д.)
    article_number = Column(String)  # Статья УК/КоАП
    article_description = Column(Text)
    
    # Тяжесть и последствия
    severity = Column(String)  # severe, serious, moderate, minor
    punishment_type = Column(String)  # Тип наказания
    punishment_duration = Column(String)  # Срок наказания
    fine_amount = Column(Float)  # Размер штрафа
    
    # Локация
    region = Column(String)
    city = Column(String)
    district = Column(String)
    location_details = Column(Text)
    
    # Контекст
    victim_count = Column(Integer)
    damage_amount = Column(Float)
    weapon_used = Column(Boolean, default=False)
    group_crime = Column(Boolean, default=False)
    repeat_offense = Column(Boolean, default=False)
    
    # Метаданные
    import_date = Column(DateTime, default=func.now())
    source_file = Column(String)
    raw_data = Column(JSON)

class CrimeTransition(Base):
    """Переходы админ->уголовка из crime_analysis_results.xlsx
    КРИТИЧНО: 6,465 переходов админ->кража
    """
    __tablename__ = "crime_transitions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Типы переходов
    admin_violation = Column(String, index=True)  # Тип админ нарушения
    criminal_offense = Column(String, index=True)  # Тип уголовного преступления
    
    # Статистика переходов
    transition_count = Column(Integer)  # Количество переходов
    total_persons = Column(Integer)  # Всего людей с таким переходом
    
    # Временные характеристики (КРИТИЧНО: сохранить временные окна)
    avg_days = Column(Float)  # Среднее время перехода
    min_days = Column(Integer)  # Минимальное время
    max_days = Column(Integer)  # Максимальное время
    median_days = Column(Float)  # Медианное время
    
    # Предотвратимость (КРИТИЧНО: 97% предотвратимых)
    preventable_count = Column(Integer)  # Количество предотвратимых
    preventable_percent = Column(Float)  # Процент предотвратимости
    
    # Факторы риска
    avg_age_at_transition = Column(Float)
    most_common_region = Column(String)
    risk_factors = Column(JSON)  # Дополнительные факторы
    
    # Метаданные
    source_file = Column(String)
    import_date = Column(DateTime, default=func.now())
    calculation_date = Column(DateTime)

class CrimeTimeWindow(Base):
    """Временные окна для различных преступлений
    КРИТИЧНО: Сохранить все окна из исследования
    """
    __tablename__ = "crime_time_windows"
    
    id = Column(Integer, primary_key=True)
    crime_type = Column(String, unique=True, index=True)
    
    # Временные окна в днях (из исследования)
    window_days = Column(Integer)  # Основное окно
    min_days = Column(Integer)  # Минимальное время
    max_days = Column(Integer)  # Максимальное время
    median_days = Column(Float)  # Медиана
    
    # Статистика
    total_cases = Column(Integer)  # Всего случаев
    recidivist_cases = Column(Integer)  # Случаев рецидива
    recidivism_rate = Column(Float)  # Процент рецидива
    
    # Предотвратимость
    preventability_score = Column(Float)  # Процент предотвратимости
    intervention_effectiveness = Column(Float)  # Эффективность вмешательства
    
    # Факторы
    key_risk_factors = Column(JSON)
    recommended_interventions = Column(JSON)
    
    # Метаданные
    source = Column(String, default="research_2024")
    last_updated = Column(DateTime, default=func.now())

class RiskAssessmentHistory(Base):
    """История расчетов риска для аудита"""
    __tablename__ = "risk_assessment_history"
    
    id = Column(Integer, primary_key=True, index=True)
    person_iin = Column(String, index=True)
    
    # Результаты расчета
    risk_score = Column(Float)
    risk_category = Column(String)
    components = Column(JSON)  # Все компоненты расчета
    
    # Контекст расчета
    calculated_at = Column(DateTime, default=func.now(), index=True)
    calculated_by = Column(String)  # system, user_id
    calculation_reason = Column(String)  # scheduled, manual, api_request
    
    # Прогнозы на момент расчета
    predictions = Column(JSON)
    recommendations = Column(JSON)
    
    # Метаданные
    algorithm_version = Column(String, default="v1.0")
    data_snapshot = Column(JSON)  # Снимок данных на момент расчета

# Инициализация критических временных окон
CRITICAL_TIME_WINDOWS = {
    "Мошенничество": 109,
    "Кража": 146,
    "Убийство": 143,
    "Вымогательство": 144,
    "Грабеж": 148,
    "Разбой": 150,
    "Изнасилование": 157,
    "Хулиганство": 175
}