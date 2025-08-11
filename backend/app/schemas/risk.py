"""
Pydantic схемы для API запросов и ответов по расчету рисков

ОСНОВАНО НА: Структуре данных из utils/risk_calculator.py
НАЗНАЧЕНИЕ: Валидация входных данных и форматирование ответов API

КРИТИЧНО: Все поля должны соответствовать структуре данных 
из оригинального Streamlit приложения
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

from app.core.constants import PATTERN_RISKS


class PatternType(str, Enum):
    """Допустимые типы паттернов поведения"""
    MIXED_UNSTABLE = "mixed_unstable"        # 72.7% всех случаев
    CHRONIC_CRIMINAL = "chronic_criminal"    # 13.6% - высокий риск
    ESCALATING = "escalating"                # 7% - опасная тенденция  
    DEESCALATING = "deescalating"            # 5.7% - снижение риска
    SINGLE = "single"                        # 1% - единичные случаи
    UNKNOWN = "unknown"                      # Неизвестный паттерн


class RiskCalculationRequest(BaseModel):
    """
    Запрос на расчет риска
    Структура ИДЕНТИЧНА входным данным utils/risk_calculator.py
    """
    
    # ОСНОВНАЯ ИДЕНТИФИКАЦИЯ
    iin: Optional[str] = Field(None, description="ИИН человека (для логирования)")
    
    # ПАТТЕРН ПОВЕДЕНИЯ (ОБЯЗАТЕЛЬНО)
    pattern_type: PatternType = Field(
        ..., 
        description="Тип паттерна поведения из анализа 146,570 нарушений"
    )
    
    # ИСТОРИЯ НАРУШЕНИЙ (ОБЯЗАТЕЛЬНО)
    total_cases: int = Field(
        ..., 
        ge=0, 
        description="Общее количество дел"
    )
    criminal_count: int = Field(
        0, 
        ge=0, 
        description="Количество уголовных дел"
    )
    admin_count: int = Field(
        0, 
        ge=0, 
        description="Количество административных нарушений"
    )
    
    # ВРЕМЕННЫЕ ФАКТОРЫ
    days_since_last: int = Field(
        365, 
        ge=0, 
        description="Дней с последнего нарушения"
    )
    recidivism_rate: float = Field(
        0.0, 
        ge=0.0, 
        description="Дел в год (скорость рецидива)"
    )
    
    # ВОЗРАСТНЫЕ ФАКТОРЫ (ОБЯЗАТЕЛЬНО)
    current_age: int = Field(
        ..., 
        ge=14, 
        le=100, 
        description="Текущий возраст"
    )
    age_at_first_violation: Optional[int] = Field(
        None, 
        ge=14, 
        le=100, 
        description="Возраст при первом нарушении"
    )
    
    # СОЦИАЛЬНЫЕ ФАКТОРЫ (0/1)
    has_property: int = Field(
        0, 
        ge=0, 
        le=1, 
        description="Наличие имущества (0-нет, 1-есть)"
    )
    has_job: int = Field(
        0, 
        ge=0, 
        le=1, 
        description="Наличие работы (0-нет, 1-есть)"
    )
    has_family: int = Field(
        0, 
        ge=0, 
        le=1, 
        description="Наличие семьи (0-нет, 1-есть)"
    )
    substance_abuse: int = Field(
        0, 
        ge=0, 
        le=1, 
        description="Злоупотребление веществами (0-нет, 1-есть)"
    )
    
    # ФАКТОРЫ ЭСКАЛАЦИИ
    has_escalation: int = Field(
        0, 
        ge=0, 
        le=1, 
        description="Наличие эскалации (0-нет, 1-есть)"
    )
    admin_to_criminal: int = Field(
        0, 
        ge=0, 
        description="Количество переходов от административных к уголовным"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "iin": "123456789012",
                "pattern_type": "mixed_unstable",
                "total_cases": 5,
                "criminal_count": 2,
                "admin_count": 3,
                "days_since_last": 45,
                "current_age": 28,
                "age_at_first_violation": 22,
                "has_property": 0,
                "has_job": 1,
                "has_family": 0,
                "substance_abuse": 0,
                "has_escalation": 1,
                "admin_to_criminal": 1,
                "recidivism_rate": 1.2
            }
        }
    
    @validator('criminal_count')
    def validate_criminal_count(cls, v, values):
        """Уголовных дел не может быть больше общего количества"""
        if 'total_cases' in values and v > values['total_cases']:
            raise ValueError('criminal_count cannot exceed total_cases')
        return v
    
    @validator('admin_count')
    def validate_admin_count(cls, v, values):
        """Административных дел не может быть больше общего количества"""
        if 'total_cases' in values and v > values['total_cases']:
            raise ValueError('admin_count cannot exceed total_cases')
        return v
    
    @validator('age_at_first_violation')
    def validate_first_violation_age(cls, v, values):
        """Возраст первого нарушения не может быть больше текущего"""
        if v is not None and 'current_age' in values and v > values['current_age']:
            raise ValueError('age_at_first_violation cannot exceed current_age')
        return v
    
    def to_calculator_dict(self) -> Dict:
        """Конвертация в формат для RiskCalculator (как в utils/)"""
        data = self.dict(exclude_none=True)
        
        # Если возраст первого нарушения не указан, используем текущий
        if 'age_at_first_violation' not in data:
            data['age_at_first_violation'] = data['current_age']
        
        # Автозаполнение admin_count если не указан
        if data.get('admin_count') == 0 and data.get('criminal_count', 0) < data.get('total_cases', 0):
            data['admin_count'] = data['total_cases'] - data.get('criminal_count', 0)
            
        return data


class RiskComponentsResponse(BaseModel):
    """Детализация компонентов риска"""
    pattern: float = Field(..., description="Компонент паттерна поведения")
    history: float = Field(..., description="Компонент истории нарушений")
    time: float = Field(..., description="Временной компонент")
    age: float = Field(..., description="Возрастной компонент") 
    social: float = Field(..., description="Социальный компонент")
    escalation: float = Field(..., description="Компонент эскалации")


class RiskCalculationResponse(BaseModel):
    """
    Ответ с результатами расчета риска
    Структура соответствует выводу utils/risk_calculator.py
    """
    
    # ОСНОВНОЙ РЕЗУЛЬТАТ
    risk_score: float = Field(
        ..., 
        ge=0, 
        le=10, 
        description="Риск-балл от 0 до 10"
    )
    risk_level: str = Field(
        ..., 
        description="Уровень риска с эмодзи (🔴 Критический, 🟡 Высокий, 🟠 Средний, 🟢 Низкий)"
    )
    risk_category: str = Field(
        ..., 
        description="Категория риска без эмодзи (Критический, Высокий, Средний, Низкий)"
    )
    recommendation: str = Field(
        ..., 
        description="Рекомендация по работе с лицом"
    )
    
    # ДЕТАЛИЗАЦИЯ
    components: RiskComponentsResponse = Field(
        ..., 
        description="Разбивка по компонентам риска"
    )
    
    # ВХОДНЫЕ ДАННЫЕ (для аудита)
    person_data: Dict[str, Any] = Field(
        ..., 
        description="Данные использованные для расчета"
    )
    
    # МЕТАДАННЫЕ
    calculated_at: datetime = Field(
        ..., 
        description="Время расчета"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "risk_score": 5.76,
                "risk_level": "🟡 Высокий",
                "risk_category": "Высокий", 
                "recommendation": "Усиленный контроль и мониторинг",
                "components": {
                    "pattern": 2.0,
                    "history": 0.8, 
                    "time": 1.2,
                    "age": 0.8,
                    "social": 0.75,
                    "escalation": 0.21
                },
                "person_data": {
                    "pattern_type": "mixed_unstable",
                    "total_cases": 5,
                    "current_age": 28
                },
                "calculated_at": "2024-01-15T10:30:00"
            }
        }


class CrimeForecastItem(BaseModel):
    """Элемент прогноза преступления"""
    crime_type: str = Field(..., description="Тип преступления")
    days: int = Field(..., ge=30, le=365, description="Дней до события")
    date: datetime = Field(..., description="Прогнозируемая дата")
    probability: float = Field(..., ge=5.0, le=95.0, description="Вероятность в процентах")
    confidence: str = Field(..., description="Уровень уверенности (Высокая, Средняя, Низкая)")
    risk_level: str = Field(..., description="Риск по временной шкале")
    ci_lower: int = Field(..., description="Нижняя граница доверительного интервала")
    ci_upper: int = Field(..., description="Верхняя граница доверительного интервала")


class CrimeForecastResponse(BaseModel):
    """Ответ с прогнозами преступлений"""
    forecasts: List[CrimeForecastItem] = Field(
        ..., 
        description="Список прогнозов, отсортированных по времени"
    )
    person_iin: Optional[str] = Field(None, description="ИИН лица")
    total_forecasts: int = Field(..., description="Общее количество прогнозов")
    calculated_at: datetime = Field(..., description="Время расчета")
    
    class Config:
        json_schema_extra = {
            "example": {
                "forecasts": [
                    {
                        "crime_type": "Кража",
                        "days": 89,
                        "date": "2024-04-15T12:00:00",
                        "probability": 65.3,
                        "confidence": "Высокая",
                        "risk_level": "🟡 Высокий риск",
                        "ci_lower": 62,
                        "ci_upper": 125
                    }
                ],
                "total_forecasts": 8,
                "calculated_at": "2024-01-15T10:30:00"
            }
        }


class QuickAssessmentResponse(BaseModel):
    """Быстрая оценка риска"""
    risk_score: float = Field(..., ge=0, le=10)
    risk_level: str
    recommendation: str
    components: RiskComponentsResponse
    most_likely_crime: Optional[CrimeForecastItem] = Field(
        None, 
        description="Наиболее вероятное преступление"
    )
    calculated_at: datetime


class ValidationErrorResponse(BaseModel):
    """Ответ при ошибке валидации"""
    detail: str
    field_errors: List[Dict[str, str]] = Field(default_factory=list)
    
    
class RiskStatisticsResponse(BaseModel):
    """Статистика по рискам из исследования"""
    total_analyzed: int = Field(146570, description="Всего проанализировано нарушений")
    total_recidivists: int = Field(12333, description="Всего рецидивистов") 
    preventable_crimes_percent: float = Field(97.0, description="Процент предотвратимых преступлений")
    
    # Распределение по категориям риска
    risk_distribution: Dict[str, int] = Field(
        default_factory=lambda: {
            "critical": 1856,  # 15%
            "high": 3083,      # 25%
            "medium": 4316,    # 35%
            "low": 3078        # 25%
        }
    )
    
    # Распределение по паттернам
    pattern_distribution: Dict[str, float] = Field(
        default_factory=lambda: {
            "mixed_unstable": 72.7,
            "chronic_criminal": 13.6,
            "escalating": 7.0,
            "deescalating": 5.7,
            "single": 1.0
        }
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_analyzed": 146570,
                "total_recidivists": 12333,
                "preventable_crimes_percent": 97.0,
                "risk_distribution": {
                    "critical": 1856,
                    "high": 3083,
                    "medium": 4316,
                    "low": 3078
                },
                "pattern_distribution": {
                    "mixed_unstable": 72.7,
                    "chronic_criminal": 13.6,
                    "escalating": 7.0,
                    "deescalating": 5.7,
                    "single": 1.0
                }
            }
        }


class BatchRiskRequest(BaseModel):
    """Запрос на пакетный расчет рисков"""
    persons: List[RiskCalculationRequest] = Field(
        ..., 
        min_items=1, 
        max_items=100, 
        description="Список лиц для расчета (максимум 100)"
    )


class BatchRiskResponse(BaseModel):
    """Ответ на пакетный расчет"""
    results: List[RiskCalculationResponse] = Field(..., description="Результаты расчетов")
    total_processed: int = Field(..., description="Всего обработано")
    errors: List[Dict[str, str]] = Field(default_factory=list, description="Ошибки при обработке")
    calculated_at: datetime