"""
Модуль расчета риск-баллов и оценки вероятности рецидива
Основан на результатах анализа 146,570 правонарушений
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

class RiskCalculator:
    """
    Калькулятор риск-баллов на основе множественных факторов
    """
    
    def __init__(self):
        # Веса факторов (откалиброваны на основе исследования)
        self.weights = {
            'pattern_weight': 0.25,      # Паттерн поведения
            'history_weight': 0.20,      # История нарушений
            'time_weight': 0.15,         # Временной фактор
            'age_weight': 0.10,          # Возрастной фактор
            'social_weight': 0.15,       # Социальные факторы
            'escalation_weight': 0.15    # Факторы эскалации
        }
        
        # Базовые риски по паттернам (из исследования)
        self.pattern_risks = {
            'mixed_unstable': 0.8,       # 72.7% всех случаев
            'chronic_criminal': 0.9,     # 13.6% - высокий риск
            'escalating': 0.85,          # 7% - опасная тенденция
            'deescalating': 0.4,         # 5.7% - снижение риска
            'single': 0.3,               # 1% - единичные случаи
            'unknown': 0.5               # Неизвестный паттерн
        }
    
    def calculate_risk_score(self, person_data: Dict) -> Tuple[float, Dict]:
        """
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
        Рассчитывает вероятность конкретного типа преступления
        
        Args:
            person_data: Данные о человеке
            crime_type: Тип преступления
            days_ahead: Период прогноза в днях
            
        Returns:
            probability: Вероятность в процентах (0-100)
        """
        # Базовые вероятности из исследования
        base_probabilities = {
            'Кража': 87.3,
            'Мошенничество': 82.3,
            'Убийство': 97.0,
            'Грабеж': 60.2,
            'Разбой': 20.2,
            'Вымогательство': 100.0,
            'Изнасилование': 65.6,
            'Хулиганство': 45.0
        }
        
        base_prob = base_probabilities.get(crime_type, 50.0)
        
        # Получаем риск-балл
        risk_score, _ = self.calculate_risk_score(person_data)
        
        # Модификаторы вероятности
        risk_modifier = risk_score / 10  # 0-1
        
        # Временной модификатор (чем ближе срок, тем выше вероятность)
        time_windows = {
            'Мошенничество': 109,
            'Кража': 146,
            'Убийство': 143,
            'Грабеж': 148,
            'Разбой': 150,
            'Изнасилование': 157,
            'Вымогательство': 144,
            'Хулиганство': 155
        }
        
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
    Прогнозирование времени до возможного преступления
    """
    
    def __init__(self):
        self.risk_calculator = RiskCalculator()
        
        # Средние временные окна из исследования (в днях)
        self.base_windows = {
            'Мошенничество': 109,
            'Кража': 146,
            'Убийство': 143,
            'Вымогательство': 144,
            'Грабеж': 148,
            'Разбой': 150,
            'Изнасилование': 157,
            'Хулиганство': 155
        }
    
    def forecast_crime_timeline(self, person_data: Dict) -> Dict[str, Dict]:
        """
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
        """Возрастной модификатор для прогноза"""
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
        """Модификатор на основе паттерна поведения"""
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
        """Социальный модификатор"""
        modifier = 1.0
        
        if data.get('has_property', 0) == 0:
            modifier *= 0.85
        if data.get('has_job', 0) == 0:
            modifier *= 0.9
        if data.get('substance_abuse', 0) == 1:
            modifier *= 0.8
        
        return modifier
    
    def _calculate_confidence(self, data: Dict, crime_type: str) -> str:
        """Рассчитывает уровень уверенности в прогнозе"""
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
        """Определяет уровень риска по временной шкале"""
        if days < 60:
            return "🔴 Критический период"
        elif days < 120:
            return "🟡 Высокий риск"
        elif days < 180:
            return "🟠 Средний риск"
        else:
            return "🟢 Низкий риск"


# Функция для быстрого расчета риска
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