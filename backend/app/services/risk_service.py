"""
Сервис расчета рисков для системы раннего предупреждения преступлений

ПОРТИРОВАНО ИЗ: utils/risk_calculator.py
КРИТИЧНО: ВСЕ формулы и коэффициенты ДОЛЖНЫ быть идентичны оригиналу

Основан на анализе 146,570 правонарушений
Любые изменения только с пометкой # CHANGED: причина
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List
from sqlalchemy.orm import Session

from app.core.constants import (
    RISK_WEIGHTS, PATTERN_RISKS, PREVENTION_RATES, CRIME_TIME_WINDOWS,
    RISK_THRESHOLD_CRITICAL, RISK_THRESHOLD_HIGH, RISK_THRESHOLD_MEDIUM,
    get_risk_category_by_score
)


class RiskCalculator:
    """
    ORIGINAL: Точная копия из utils/risk_calculator.py
    Калькулятор риск-баллов на основе множественных факторов
    """
    
    def __init__(self):
        # ORIGINAL: Веса факторов (откалиброваны на основе исследования)
        # CHANGED: Использует константы из app.core.constants вместо hardcode
        self.weights = RISK_WEIGHTS
        
        # ORIGINAL: Базовые риски по паттернам (из исследования)  
        # CHANGED: Использует константы из app.core.constants вместо hardcode
        self.pattern_risks = PATTERN_RISKS
    
    def calculate_risk_score(self, person_data: Dict) -> Tuple[float, Dict]:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 37-81
        Рассчитывает комплексный риск-балл от 0 до 10
        
        Args:
            person_data: Словарь с данными о человеке
            
        Returns:
            risk_score: Риск-балл (0-10)
            components: Детализация по компонентам
        """
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
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 83-108
        Оценка на основе истории правонарушений (0-10)
        """
        total_cases = data.get('total_cases', 0)
        criminal_count = data.get('criminal_count', 0)
        admin_count = data.get('admin_count', 0)
        
        # Базовый балл по количеству дел
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
        
        # Модификатор по соотношению уголовных/административных
        if criminal_count > 0:
            criminal_ratio = criminal_count / total_cases
            base_score += criminal_ratio * 2  # До +2 баллов за уголовные
        
        return min(10, base_score)
    
    def _calculate_time_score(self, data: Dict) -> float:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 110-133
        Оценка на основе временных факторов (0-10)
        """
        # Дни с последнего нарушения
        days_since_last = data.get('days_since_last', 365)
        
        if days_since_last < 30:
            time_score = 10  # Очень недавно
        elif days_since_last < 90:
            time_score = 8   # Недавно
        elif days_since_last < 180:
            time_score = 6   # Относительно недавно
        elif days_since_last < 365:
            time_score = 4   # Давно
        else:
            time_score = 2   # Очень давно
        
        # Учитываем скорость рецидива
        recidivism_rate = data.get('recidivism_rate', 0)
        if recidivism_rate > 2:  # Более 2 дел в год
            time_score = min(10, time_score + 2)
        
        return time_score
    
    def _calculate_age_score(self, data: Dict) -> float:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 135-160
        Оценка на основе возраста (0-10)
        """
        age = data.get('current_age', 35)
        age_at_first = data.get('age_at_first_violation', age)
        
        # Базовый балл по текущему возрасту
        if 18 <= age <= 25:
            base_score = 8  # Молодые - высокий риск
        elif 26 <= age <= 35:
            base_score = 6  # Средний возраст
        elif 36 <= age <= 45:
            base_score = 4  # Зрелый возраст
        else:
            base_score = 2  # Старший возраст
        
        # Модификатор за ранний криминальный дебют
        if age_at_first < 18:
            base_score += 3
        elif age_at_first < 21:
            base_score += 2
        elif age_at_first < 25:
            base_score += 1
        
        return min(10, base_score)
    
    def _calculate_social_score(self, data: Dict) -> float:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 162-184
        Оценка социальных факторов (0-10)
        """
        score = 5  # Базовый средний балл
        
        # Факторы, снижающие риск
        if data.get('has_property', 0) == 1:
            score -= 2  # Наличие имущества
        if data.get('has_job', 0) == 1:
            score -= 2  # Наличие работы
        if data.get('has_family', 0) == 1:
            score -= 1  # Семья
        
        # Факторы, повышающие риск
        if data.get('has_property', 0) == 0:
            score += 1  # Отсутствие имущества
        if data.get('has_job', 0) == 0:
            score += 1  # Безработица
        if data.get('substance_abuse', 0) == 1:
            score += 2  # Зависимости
        
        return max(0, min(10, score))
    
    def _calculate_escalation_score(self, data: Dict) -> float:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 186-204
        Оценка тенденции к эскалации (0-10)
        """
        has_escalation = data.get('has_escalation', 0)
        admin_to_criminal = data.get('admin_to_criminal', 0)
        
        if has_escalation:
            if admin_to_criminal > 2:
                return 9  # Множественная эскалация
            elif admin_to_criminal > 0:
                return 7  # Есть эскалация
            else:
                return 5  # Потенциальная эскалация
        else:
            if data.get('admin_count', 0) > 5:
                return 4  # Много админ нарушений - риск эскалации
            else:
                return 2  # Низкий риск эскалации
    
    def get_risk_level(self, risk_score: float) -> Tuple[str, str]:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 206-221
        Определяет уровень риска и рекомендации
        
        Returns:
            level: Уровень риска
            recommendation: Рекомендация по работе
        """
        if risk_score >= 7:
            return "🔴 Критический", "Требует немедленного вмешательства"
        elif risk_score >= 5:
            return "🟡 Высокий", "Усиленный контроль и мониторинг"
        elif risk_score >= 3:
            return "🟠 Средний", "Стандартный контроль"
        else:
            return "🟢 Низкий", "Минимальный контроль"
    
    def calculate_crime_probability(self, person_data: Dict, crime_type: str, days_ahead: int = 180) -> float:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 223-294
        Рассчитывает вероятность конкретного типа преступления
        
        Args:
            person_data: Данные о человеке
            crime_type: Тип преступления
            days_ahead: Период прогноза в днях
            
        Returns:
            probability: Вероятность в процентах (0-100)
        """
        # ORIGINAL: Базовые вероятности из исследования
        # CHANGED: Использует PREVENTION_RATES из констант
        base_probabilities = PREVENTION_RATES
        
        base_prob = base_probabilities.get(crime_type, 50.0)
        
        # Получаем риск-балл
        risk_score, _ = self.calculate_risk_score(person_data)
        
        # Модификаторы вероятности
        risk_modifier = risk_score / 10  # 0-1
        
        # ORIGINAL: Временной модификатор (чем ближе срок, тем выше вероятность)
        # CHANGED: Использует CRIME_TIME_WINDOWS из констант
        time_windows = CRIME_TIME_WINDOWS
        
        expected_days = time_windows.get(crime_type, 140)
        time_modifier = 1.0
        
        if days_ahead < expected_days * 0.5:
            time_modifier = 0.6
        elif days_ahead < expected_days:
            time_modifier = 0.8
        elif days_ahead < expected_days * 1.5:
            time_modifier = 1.0
        else:
            time_modifier = 0.7
        
        # Паттерн-специфичные модификаторы
        pattern = person_data.get('pattern_type', 'unknown')
        pattern_modifier = 1.0
        
        if pattern == 'chronic_criminal' and crime_type in ['Кража', 'Грабеж']:
            pattern_modifier = 1.3
        elif pattern == 'escalating' and crime_type in ['Грабеж', 'Разбой']:
            pattern_modifier = 1.2
        elif pattern == 'mixed_unstable':
            pattern_modifier = 1.1
        
        # Итоговая вероятность
        probability = base_prob * risk_modifier * time_modifier * pattern_modifier
        
        # Ограничиваем диапазон 5-95%
        return max(5, min(95, probability))


class CrimeForecaster:
    """
    ORIGINAL: Точная копия из utils/risk_calculator.py строки 297-459
    Прогнозирование времени до возможного преступления
    """
    
    def __init__(self):
        self.risk_calculator = RiskCalculator()
        
        # ORIGINAL: Средние временные окна из исследования (в днях)
        # CHANGED: Использует CRIME_TIME_WINDOWS из констант
        self.base_windows = CRIME_TIME_WINDOWS
    
    def forecast_crime_timeline(self, person_data: Dict) -> Dict[str, Dict]:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 317-333
        Прогнозирует временные окна для различных типов преступлений
        
        Returns:
            forecasts: Словарь с прогнозами по типам преступлений
        """
        forecasts = {}
        
        for crime_type, base_days in self.base_windows.items():
            forecast = self._calculate_single_forecast(person_data, crime_type, base_days)
            forecasts[crime_type] = forecast
        
        # Сортируем по дням до события
        sorted_forecasts = dict(sorted(forecasts.items(), key=lambda x: x[1]['days']))
        
        return sorted_forecasts
    
    def _calculate_single_forecast(self, person_data: Dict, crime_type: str, base_days: int) -> Dict:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 335-379
        Рассчитывает прогноз для конкретного типа преступления
        """
        # Базовые модификаторы
        age_modifier = self._get_age_modifier(person_data)
        pattern_modifier = self._get_pattern_modifier(person_data, crime_type)
        social_modifier = self._get_social_modifier(person_data)
        
        # Расчет дней с проверкой типов
        try:
            forecast_days = int(base_days * age_modifier * pattern_modifier * social_modifier)
            forecast_days = max(30, min(365, forecast_days))  # Ограничиваем диапазон
        except (TypeError, ValueError):
            forecast_days = int(base_days)  # Fallback к базовому значению
            forecast_days = max(30, min(365, forecast_days))
        
        # Доверительный интервал
        ci_lower = int(forecast_days * 0.7)
        ci_upper = int(forecast_days * 1.4)
        
        # Вероятность
        probability = self.risk_calculator.calculate_crime_probability(
            person_data, crime_type, forecast_days
        )
        
        # Дата прогноза с проверкой
        try:
            forecast_date = datetime.now() + timedelta(days=forecast_days)
        except (TypeError, ValueError):
            forecast_date = datetime.now() + timedelta(days=base_days)
        
        # Уровень уверенности
        confidence = self._calculate_confidence(person_data, crime_type)
        
        return {
            'crime_type': crime_type,
            'days': forecast_days,
            'date': forecast_date,
            'probability': float(probability),  # Убеждаемся что это число
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'confidence': confidence,
            'risk_level': self._get_timeline_risk_level(forecast_days)
        }
    
    def _get_age_modifier(self, data: Dict) -> float:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 381-392
        Возрастной модификатор для прогноза
        """
        age = data.get('current_age', 35)
        
        if age < 25:
            return 0.8  # Молодые - быстрее
        elif age < 35:
            return 0.9
        elif age < 45:
            return 1.1
        else:
            return 1.3  # Старшие - медленнее
    
    def _get_pattern_modifier(self, data: Dict, crime_type: str) -> float:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 394-415
        Модификатор на основе паттерна поведения
        """
        pattern = data.get('pattern_type', 'unknown')
        
        modifiers = {
            'mixed_unstable': 0.9,
            'chronic_criminal': 0.7,
            'escalating': 0.6,
            'deescalating': 1.3,
            'single': 1.5,
            'unknown': 1.0
        }
        
        base_modifier = modifiers.get(pattern, 1.0)
        
        # Специфические корректировки
        if pattern == 'chronic_criminal' and crime_type in ['Кража', 'Грабеж']:
            base_modifier *= 0.9
        elif pattern == 'escalating' and crime_type in ['Разбой', 'Убийство']:
            base_modifier *= 0.8
        
        return base_modifier
    
    def _get_social_modifier(self, data: Dict) -> float:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 417-428
        Социальный модификатор
        """
        modifier = 1.0
        
        if data.get('has_property', 0) == 0:
            modifier *= 0.85
        if data.get('has_job', 0) == 0:
            modifier *= 0.9
        if data.get('substance_abuse', 0) == 1:
            modifier *= 0.8
        
        return modifier
    
    def _calculate_confidence(self, data: Dict, crime_type: str) -> str:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 430-447
        Рассчитывает уровень уверенности в прогнозе
        """
        # Факторы, влияющие на уверенность
        factors = 0
        
        if data.get('total_cases', 0) > 5:
            factors += 1  # Много данных
        if data.get('pattern_type', 'unknown') != 'unknown':
            factors += 1  # Известный паттерн
        if data.get('has_escalation', 0) == 1:
            factors += 1  # Есть тренд
        
        if factors >= 3:
            return "Высокая"
        elif factors >= 2:
            return "Средняя"
        else:
            return "Низкая"
    
    def _get_timeline_risk_level(self, days: int) -> str:
        """
        ORIGINAL: Точная копия из utils/risk_calculator.py строки 449-458
        Определяет уровень риска по временной шкале
        """
        if days < 60:
            return "🔴 Критический период"
        elif days < 120:
            return "🟡 Высокий риск"
        elif days < 180:
            return "🟠 Средний риск"
        else:
            return "🟢 Низкий риск"


# ORIGINAL: Точная копия из utils/risk_calculator.py строки 461-486
def quick_risk_assessment(person_data: Dict) -> Dict:
    """
    Быстрая оценка риска для использования в интерфейсе
    """
    calculator = RiskCalculator()
    risk_score, components = calculator.calculate_risk_score(person_data)
    risk_level, recommendation = calculator.get_risk_level(risk_score)
    
    # Определяем наиболее вероятное преступление
    forecaster = CrimeForecaster()
    forecasts = forecaster.forecast_crime_timeline(person_data)
    
    # Берем самое вероятное (первое в отсортированном списке)
    if forecasts:
        most_likely = next(iter(forecasts.values()))
    else:
        most_likely = None
    
    return {
        'risk_score': risk_score,
        'risk_level': risk_level,
        'recommendation': recommendation,
        'components': components,
        'most_likely_crime': most_likely
    }


# ===== НОВЫЙ КОД ДЛЯ BACKEND ИНТЕГРАЦИИ =====

class RiskService:
    """
    Обертка для работы с SQLAlchemy и интеграции в FastAPI
    НЕ изменяет оригинальную логику расчетов!
    """
    
    def __init__(self, db: Optional[Session] = None):
        self.calculator = RiskCalculator()  # ОРИГИНАЛЬНЫЙ калькулятор
        self.forecaster = CrimeForecaster()  # ОРИГИНАЛЬНЫЙ прогнозист
        self.db = db
    
    def calculate_risk_for_person_dict(self, person_data: Dict) -> Dict:
        """
        Рассчитывает риск для данных в формате словаря (как в оригинале)
        
        Args:
            person_data: Словарь с данными лица (формат как в utils/)
            
        Returns:
            Полный результат оценки риска
        """
        # Используем ОРИГИНАЛЬНЫЙ калькулятор без изменений
        risk_score, components = self.calculator.calculate_risk_score(person_data)
        risk_level, recommendation = self.calculator.get_risk_level(risk_score)
        
        # Прогнозы временных окон
        forecasts = self.forecaster.forecast_crime_timeline(person_data)
        
        # Быстрая оценка
        quick_assessment = quick_risk_assessment(person_data)
        
        return {
            'person_data': person_data,
            'risk_score': risk_score,
            'risk_components': components,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'forecasts': forecasts,
            'quick_assessment': quick_assessment,
            'calculated_at': datetime.utcnow().isoformat()
        }
    
    def calculate_risk_batch(self, persons_data: List[Dict]) -> List[Dict]:
        """
        Пакетный расчет рисков для множества лиц
        
        Args:
            persons_data: Список словарей с данными лиц
            
        Returns:
            Список результатов оценки рисков
        """
        results = []
        
        for person_data in persons_data:
            try:
                result = self.calculate_risk_for_person_dict(person_data)
                results.append(result)
            except Exception as e:
                # Логируем ошибку, но продолжаем обработку
                error_result = {
                    'person_data': person_data,
                    'error': str(e),
                    'risk_score': 0.0,
                    'calculated_at': datetime.utcnow().isoformat()
                }
                results.append(error_result)
        
        return results
    
    def get_risk_statistics(self) -> Dict:
        """
        Возвращает статистику по рискам (использует константы)
        """
        from app.core.constants import (
            TOTAL_VIOLATIONS_ANALYZED, TOTAL_RECIDIVISTS, 
            PREVENTABLE_CRIMES_PERCENT, PATTERN_DISTRIBUTION
        )
        
        return {
            'total_analyzed': TOTAL_VIOLATIONS_ANALYZED,
            'total_recidivists': TOTAL_RECIDIVISTS,
            'preventable_percent': PREVENTABLE_CRIMES_PERCENT,
            'pattern_distribution': PATTERN_DISTRIBUTION,
            'risk_categories': {
                'critical_threshold': RISK_THRESHOLD_CRITICAL,
                'high_threshold': RISK_THRESHOLD_HIGH, 
                'medium_threshold': RISK_THRESHOLD_MEDIUM
            }
        }
    
    def validate_person_data(self, person_data: Dict) -> Tuple[bool, List[str]]:
        """
        Валидация данных лица перед расчетом риска
        
        Returns:
            Tuple[bool, List[str]]: (валидны ли данные, список ошибок)
        """
        errors = []
        
        # Проверяем обязательные поля
        required_fields = ['pattern_type', 'total_cases', 'current_age']
        for field in required_fields:
            if field not in person_data:
                errors.append(f"Отсутствует поле '{field}'")
        
        # Проверяем типы данных
        if 'total_cases' in person_data and not isinstance(person_data['total_cases'], int):
            errors.append("Поле 'total_cases' должно быть числом")
        
        if 'current_age' in person_data and not isinstance(person_data['current_age'], int):
            errors.append("Поле 'current_age' должно быть числом")
        
        # Проверяем значения
        if 'total_cases' in person_data and person_data['total_cases'] < 0:
            errors.append("Количество дел не может быть отрицательным")
            
        if 'current_age' in person_data and not (0 < person_data['current_age'] < 120):
            errors.append("Некорректный возраст")
        
        if 'pattern_type' in person_data:
            valid_patterns = set(PATTERN_RISKS.keys())
            if person_data['pattern_type'] not in valid_patterns:
                errors.append(f"Неизвестный паттерн '{person_data['pattern_type']}'")
        
        return len(errors) == 0, errors


# Для обратной совместимости с оригинальными именами
RiskCalculatorBackend = RiskCalculator
CrimeForecasterBackend = CrimeForecaster