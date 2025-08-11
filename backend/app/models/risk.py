"""
SQLAlchemy модели для хранения результатов оценки рисков

Сохраняет результаты расчетов из RiskCalculator для аудита и анализа
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class RiskAssessment(Base):
    """
    Результаты оценки риска для конкретного лица
    Сохраняет ВСЕ компоненты расчета для аудита
    """
    __tablename__ = "risk_assessments"
    
    # Основная информация
    id = Column(Integer, primary_key=True, index=True)
    person_iin = Column(String(12), index=True, nullable=False, comment="ИИН лица")
    
    # ОСНОВНОЙ РЕЗУЛЬТАТ
    risk_score = Column(Float, nullable=False, comment="Риск-балл 0-10 с точностью 0.01")
    risk_category = Column(String(50), nullable=False, comment="Критический/Высокий/Средний/Низкий")
    recommendation = Column(Text, nullable=False, comment="Рекомендация по работе с лицом")
    
    # КОМПОНЕНТЫ РИСКА (детализация расчета)
    pattern_component = Column(Float, nullable=False, comment="Компонент паттерна поведения")
    history_component = Column(Float, nullable=False, comment="Компонент истории нарушений") 
    time_component = Column(Float, nullable=False, comment="Временной компонент")
    age_component = Column(Float, nullable=False, comment="Возрастной компонент")
    social_component = Column(Float, nullable=False, comment="Социальный компонент")
    escalation_component = Column(Float, nullable=False, comment="Компонент эскалации")
    
    # ВХОДНЫЕ ДАННЫЕ ДЛЯ РАСЧЕТА (для аудита)
    input_data = Column(JSON, nullable=False, comment="Исходные данные использованные для расчета")
    
    # МЕТАДАННЫЕ
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="Время расчета")
    calculated_by = Column(String(100), comment="Кто производил расчет")
    version = Column(String(10), default="1.0", comment="Версия алгоритма расчета")
    
    # ВАЛИДНОСТЬ
    is_valid = Column(Boolean, default=True, comment="Актуален ли расчет")
    invalidated_at = Column(DateTime, comment="Время признания недействительным")
    invalidation_reason = Column(Text, comment="Причина признания недействительным")
    
    def __repr__(self):
        return f"<RiskAssessment(iin={self.person_iin}, score={self.risk_score}, category={self.risk_category})>"
    
    def to_dict(self):
        """Конвертация в словарь для JSON API"""
        return {
            'id': self.id,
            'person_iin': self.person_iin,
            'risk_score': self.risk_score,
            'risk_category': self.risk_category,
            'recommendation': self.recommendation,
            'components': {
                'pattern': self.pattern_component,
                'history': self.history_component,
                'time': self.time_component,
                'age': self.age_component,
                'social': self.social_component,
                'escalation': self.escalation_component
            },
            'input_data': self.input_data,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
            'calculated_by': self.calculated_by,
            'version': self.version,
            'is_valid': self.is_valid
        }


class CrimeForecast(Base):
    """
    Прогнозы временных окон до различных типов преступлений
    Сохраняет результаты CrimeForecaster
    """
    __tablename__ = "crime_forecasts"
    
    # Основная информация
    id = Column(Integer, primary_key=True, index=True)
    person_iin = Column(String(12), index=True, nullable=False, comment="ИИН лица")
    risk_assessment_id = Column(Integer, ForeignKey("risk_assessments.id"), comment="Связь с оценкой риска")
    
    # ПРОГНОЗ
    crime_type = Column(String(50), nullable=False, index=True, comment="Тип преступления")
    forecast_days = Column(Integer, nullable=False, comment="Прогнозируемое количество дней до события")
    forecast_date = Column(DateTime, nullable=False, comment="Прогнозируемая дата события")
    
    # ВЕРОЯТНОСТЬ И УВЕРЕННОСТЬ
    probability = Column(Float, nullable=False, comment="Вероятность события в процентах 0-100")
    confidence_level = Column(String(20), nullable=False, comment="Высокая/Средняя/Низкая")
    
    # ДОВЕРИТЕЛЬНЫЙ ИНТЕРВАЛ
    ci_lower = Column(Integer, nullable=False, comment="Нижняя граница доверительного интервала (дни)")
    ci_upper = Column(Integer, nullable=False, comment="Верхняя граница доверительного интервала (дни)")
    
    # УРОВЕНЬ РИСКА ПО ВРЕМЕННОЙ ШКАЛЕ
    timeline_risk_level = Column(String(50), nullable=False, comment="Критический период/Высокий риск/и т.д.")
    
    # ВХОДНЫЕ ДАННЫЕ
    base_days = Column(Integer, nullable=False, comment="Базовое количество дней из исследования")
    age_modifier = Column(Float, comment="Возрастной модификатор")
    pattern_modifier = Column(Float, comment="Модификатор паттерна")
    social_modifier = Column(Float, comment="Социальный модификатор")
    
    # МЕТАДАННЫЕ
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    version = Column(String(10), default="1.0", comment="Версия алгоритма прогнозирования")
    
    # Связь с оценкой риска
    risk_assessment = relationship("RiskAssessment", backref="forecasts")
    
    def __repr__(self):
        return f"<CrimeForecast(iin={self.person_iin}, crime={self.crime_type}, days={self.forecast_days})>"
    
    def to_dict(self):
        """Конвертация в словарь для JSON API"""
        return {
            'id': self.id,
            'person_iin': self.person_iin,
            'crime_type': self.crime_type,
            'forecast_days': self.forecast_days,
            'forecast_date': self.forecast_date.isoformat() if self.forecast_date else None,
            'probability': self.probability,
            'confidence_level': self.confidence_level,
            'confidence_interval': {
                'lower': self.ci_lower,
                'upper': self.ci_upper
            },
            'timeline_risk_level': self.timeline_risk_level,
            'base_days': self.base_days,
            'modifiers': {
                'age': self.age_modifier,
                'pattern': self.pattern_modifier,
                'social': self.social_modifier
            },
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
            'version': self.version
        }


class RiskCalculationLog(Base):
    """
    Лог всех расчетов рисков для аудита и отладки
    """
    __tablename__ = "risk_calculation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ЧТО рассчитывали
    person_iin = Column(String(12), index=True, comment="ИИН лица")
    calculation_type = Column(String(50), nullable=False, index=True, comment="risk_assessment/forecast/quick")
    
    # РЕЗУЛЬТАТ
    success = Column(Boolean, nullable=False, comment="Успешен ли расчет")
    result_data = Column(JSON, comment="Результат расчета")
    error_message = Column(Text, comment="Сообщение об ошибке если расчет не удался")
    
    # ВХОДНЫЕ ДАННЫЕ
    input_data = Column(JSON, nullable=False, comment="Данные переданные на вход")
    
    # ПРОИЗВОДИТЕЛЬНОСТЬ
    calculation_time_ms = Column(Integer, comment="Время расчета в миллисекундах")
    
    # МЕТАДАННЫЕ
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(String(100), comment="ID пользователя запросившего расчет")
    session_id = Column(String(100), comment="ID сессии")
    ip_address = Column(String(45), comment="IP адрес запроса")
    
    # ВЕРСИИ
    algorithm_version = Column(String(10), default="1.0", comment="Версия алгоритма")
    constants_version = Column(String(10), comment="Версия констант")
    
    def __repr__(self):
        return f"<RiskCalculationLog(iin={self.person_iin}, type={self.calculation_type}, success={self.success})>"


class PersonRiskHistory(Base):
    """
    История изменения риск-баллов для конкретного лица
    Позволяет отслеживать динамику риска во времени
    """
    __tablename__ = "person_risk_history"
    
    id = Column(Integer, primary_key=True, index=True)
    person_iin = Column(String(12), index=True, nullable=False)
    
    # ИЗМЕНЕНИЕ РИСКА
    previous_risk_score = Column(Float, comment="Предыдущий риск-балл")
    current_risk_score = Column(Float, nullable=False, comment="Текущий риск-балл")
    risk_change = Column(Float, comment="Изменение риска (+ увеличение, - уменьшение)")
    
    # ПРИЧИНА ИЗМЕНЕНИЯ
    change_reason = Column(String(200), comment="Причина изменения риска")
    trigger_event = Column(String(100), comment="Событие спровоцировавшее пересчет")
    
    # КАТЕГОРИЯ РИСКА
    previous_category = Column(String(50), comment="Предыдущая категория риска")
    current_category = Column(String(50), nullable=False, comment="Текущая категория риска")
    category_changed = Column(Boolean, default=False, comment="Изменилась ли категория риска")
    
    # КОМПОНЕНТЫ РИСКА (для анализа что именно изменилось)
    component_changes = Column(JSON, comment="Изменения по компонентам риска")
    
    # МЕТАДАННЫЕ
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    calculated_by = Column(String(100), comment="Кто произвел пересчет")
    
    def __repr__(self):
        return f"<PersonRiskHistory(iin={self.person_iin}, change={self.risk_change})>"


class RiskStatistics(Base):
    """
    Агрегированная статистика по рискам на определенную дату
    """
    __tablename__ = "risk_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # ДАТА СТАТИСТИКИ
    date = Column(DateTime, nullable=False, index=True, comment="Дата на которую рассчитана статистика")
    
    # ОБЩИЕ ПОКАЗАТЕЛИ
    total_assessments = Column(Integer, nullable=False, comment="Общее количество оценок риска")
    total_unique_persons = Column(Integer, comment="Количество уникальных лиц")
    
    # ПО КАТЕГОРИЯМ РИСКА
    critical_risk_count = Column(Integer, default=0, comment="Критический риск (7-10)")
    high_risk_count = Column(Integer, default=0, comment="Высокий риск (5-6)")
    medium_risk_count = Column(Integer, default=0, comment="Средний риск (3-4)")
    low_risk_count = Column(Integer, default=0, comment="Низкий риск (0-2)")
    
    # СРЕДНИЕ ЗНАЧЕНИЯ
    avg_risk_score = Column(Float, comment="Средний риск-балл")
    median_risk_score = Column(Float, comment="Медианный риск-балл")
    
    # ПО КОМПОНЕНТАМ
    avg_pattern_component = Column(Float, comment="Средний компонент паттерна")
    avg_history_component = Column(Float, comment="Средний компонент истории")
    avg_time_component = Column(Float, comment="Средний временной компонент")
    avg_age_component = Column(Float, comment="Средний возрастной компонент")
    avg_social_component = Column(Float, comment="Средний социальный компонент")
    avg_escalation_component = Column(Float, comment="Средний компонент эскалации")
    
    # ПРОГНОЗЫ
    total_forecasts = Column(Integer, comment="Общее количество прогнозов")
    avg_forecast_days = Column(Float, comment="Среднее количество дней до прогнозируемого события")
    high_probability_forecasts = Column(Integer, comment="Прогнозы с вероятностью >70%")
    
    # МЕТАДАННЫЕ
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    version = Column(String(10), default="1.0")
    
    def __repr__(self):
        return f"<RiskStatistics(date={self.date}, total={self.total_assessments})>"


# Создание индексов для производительности
from sqlalchemy import Index

# Индексы для быстрого поиска
Index('idx_risk_iin_date', RiskAssessment.person_iin, RiskAssessment.calculated_at)
Index('idx_risk_score_category', RiskAssessment.risk_score, RiskAssessment.risk_category)
Index('idx_forecast_iin_crime', CrimeForecast.person_iin, CrimeForecast.crime_type)
Index('idx_forecast_date_prob', CrimeForecast.forecast_date, CrimeForecast.probability)
Index('idx_log_timestamp_success', RiskCalculationLog.timestamp, RiskCalculationLog.success)
Index('idx_history_iin_timestamp', PersonRiskHistory.person_iin, PersonRiskHistory.timestamp)