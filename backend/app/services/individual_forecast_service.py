"""
Сервис индивидуального прогнозирования для каждого лица

Основан на анализе:
- Персональной истории нарушений
- Временных интервалов между преступлениями
- Паттернов эскалации
- Возрастных и социальных факторов
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics
import math
from collections import Counter, defaultdict

from app.core.constants import (
    CRIME_TIME_WINDOWS,
    RISK_WEIGHTS,
    PATTERN_DISTRIBUTION,
    INTERVENTION_PROGRAMS
)


class IndividualForecastService:
    """Сервис для создания персонализированных прогнозов"""
    
    def __init__(self):
        self.base_windows = CRIME_TIME_WINDOWS
        self.risk_weights = RISK_WEIGHTS
        
    def calculate_individual_forecast(
        self, 
        person_data: Dict,
        violations: List[Dict]
    ) -> Dict:
        """
        Рассчитывает индивидуальный прогноз для конкретного лица
        
        Args:
            person_data: Данные о лице
            violations: История нарушений
            
        Returns:
            Персонализированный прогноз с учетом истории
        """
        
        # Анализ истории нарушений
        violation_analysis = self._analyze_violation_history(violations)
        
        # Определение персонального паттерна поведения
        behavior_pattern = self._determine_behavior_pattern(violations)
        
        # Расчет индивидуальных временных окон
        individual_windows = self._calculate_individual_windows(
            violations, 
            violation_analysis,
            person_data
        )
        
        # Создание прогнозов для каждого типа преступления
        forecasts = []
        for crime_type, base_days in self.base_windows.items():
            forecast = self._create_crime_forecast(
                crime_type,
                base_days,
                individual_windows.get(crime_type, base_days),
                violation_analysis,
                behavior_pattern,
                person_data
            )
            forecasts.append(forecast)
        
        # Сортировка по вероятности
        forecasts.sort(key=lambda x: x['probability'], reverse=True)
        
        # Определение критических периодов
        critical_periods = self._identify_critical_periods(forecasts, violations)
        
        return {
            'person_id': person_data.get('id'),
            'forecasts': forecasts,
            'behavior_pattern': behavior_pattern,
            'risk_factors': violation_analysis,
            'critical_periods': critical_periods,
            'confidence_level': self._calculate_confidence(violations),
            'calculated_at': datetime.now().isoformat()
        }
    
    def _analyze_violation_history(self, violations: List[Dict]) -> Dict:
        """Анализирует историю нарушений"""
        
        if not violations:
            return {
                'total_violations': 0,
                'crime_types': {},
                'avg_interval_days': 0,
                'trend': 'no_data',
                'escalation_detected': False
            }
        
        # Сортировка по дате
        sorted_violations = sorted(violations, key=lambda x: x['violation_date'])
        
        # Подсчет по типам
        crime_types = Counter()
        for v in violations:
            crime_type = self._extract_crime_type(v['violation_type'])
            crime_types[crime_type] += 1
        
        # Расчет интервалов между нарушениями
        intervals = []
        for i in range(1, len(sorted_violations)):
            prev_date = datetime.fromisoformat(sorted_violations[i-1]['violation_date'])
            curr_date = datetime.fromisoformat(sorted_violations[i]['violation_date'])
            interval_days = (curr_date - prev_date).days
            intervals.append(interval_days)
        
        avg_interval = statistics.mean(intervals) if intervals else 365
        
        # Определение тренда (ускорение/замедление)
        trend = 'stable'
        if len(intervals) >= 3:
            recent_avg = statistics.mean(intervals[-3:])
            early_avg = statistics.mean(intervals[:3])
            if recent_avg < early_avg * 0.7:
                trend = 'accelerating'
            elif recent_avg > early_avg * 1.3:
                trend = 'decelerating'
        
        # Детекция эскалации (переход к более тяжким)
        escalation = self._detect_escalation(sorted_violations)
        
        return {
            'total_violations': len(violations),
            'crime_types': dict(crime_types),
            'avg_interval_days': avg_interval,
            'min_interval_days': min(intervals) if intervals else 0,
            'max_interval_days': max(intervals) if intervals else 0,
            'trend': trend,
            'escalation_detected': escalation,
            'last_violation_days_ago': self._days_since_last_violation(sorted_violations)
        }
    
    def _determine_behavior_pattern(self, violations: List[Dict]) -> Dict:
        """Определяет паттерн поведения на основе истории"""
        
        if len(violations) < 2:
            return {
                'type': 'insufficient_data',
                'confidence': 0.3,
                'description': 'Недостаточно данных для определения паттерна'
            }
        
        # Анализ типов преступлений
        crime_types = [self._extract_crime_type(v['violation_type']) for v in violations]
        unique_types = len(set(crime_types))
        total_crimes = len(crime_types)
        
        # Анализ временных интервалов
        sorted_violations = sorted(violations, key=lambda x: x['violation_date'])
        intervals = []
        for i in range(1, len(sorted_violations)):
            prev_date = datetime.fromisoformat(sorted_violations[i-1]['violation_date'])
            curr_date = datetime.fromisoformat(sorted_violations[i]['violation_date'])
            intervals.append((curr_date - prev_date).days)
        
        # Коэффициент вариации интервалов
        if intervals:
            mean_interval = statistics.mean(intervals)
            std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
            cv = std_interval / mean_interval if mean_interval > 0 else 0
        else:
            cv = 0
        
        # Определение паттерна
        pattern_type = 'mixed_unstable'
        confidence = 0.5
        
        if unique_types == 1:
            # Специализация на одном типе
            pattern_type = 'specialized'
            confidence = 0.8
            description = f'Специализация на {crime_types[0]}'
        elif unique_types / total_crimes < 0.3:
            # Повторяющиеся преступления
            pattern_type = 'repetitive'
            confidence = 0.7
            description = 'Повторяющийся паттерн преступлений'
        elif cv < 0.3:
            # Регулярные интервалы
            pattern_type = 'periodic'
            confidence = 0.75
            description = f'Периодичность ~{int(mean_interval)} дней'
        elif cv > 0.7:
            # Нерегулярные интервалы
            pattern_type = 'chaotic'
            confidence = 0.6
            description = 'Хаотичный паттерн без четкой периодичности'
        else:
            # Смешанный паттерн
            pattern_type = 'mixed'
            confidence = 0.65
            description = 'Смешанный паттерн поведения'
        
        # Проверка на эскалацию
        if self._detect_escalation(sorted_violations):
            pattern_type = 'escalating'
            confidence = 0.85
            description = 'Эскалация тяжести преступлений'
        
        return {
            'type': pattern_type,
            'confidence': confidence,
            'description': description,
            'unique_crime_types': unique_types,
            'avg_interval': int(mean_interval) if intervals else 0,
            'variability': cv
        }
    
    def _calculate_individual_windows(
        self, 
        violations: List[Dict],
        analysis: Dict,
        person_data: Dict
    ) -> Dict[str, int]:
        """Рассчитывает индивидуальные временные окна для каждого типа преступления"""
        
        individual_windows = {}
        
        for crime_type, base_days in self.base_windows.items():
            # Начинаем с базового окна
            adjusted_days = base_days
            
            # Корректировка на основе истории
            if crime_type in analysis['crime_types']:
                crime_count = analysis['crime_types'][crime_type]
                
                # Чем больше преступлений этого типа, тем короче окно
                frequency_factor = 1.0 - (crime_count * 0.05)  # -5% за каждое преступление
                frequency_factor = max(0.3, frequency_factor)  # Минимум 30% от базового
                adjusted_days *= frequency_factor
            
            # Корректировка на основе тренда
            if analysis['trend'] == 'accelerating':
                adjusted_days *= 0.7  # Ускорение = короче окно
            elif analysis['trend'] == 'decelerating':
                adjusted_days *= 1.3  # Замедление = длиннее окно
            
            # Корректировка на основе последнего нарушения
            days_since_last = analysis['last_violation_days_ago']
            if days_since_last < 30:
                adjusted_days *= 0.8  # Недавнее нарушение = выше риск
            elif days_since_last > 180:
                adjusted_days *= 1.2  # Давно не было = ниже риск
            
            # Возрастная корректировка
            age = person_data.get('current_age', 30)
            if age < 25:
                adjusted_days *= 0.85  # Молодые = выше риск
            elif age > 40:
                adjusted_days *= 1.15  # Старше = ниже риск
            
            # Корректировка на эскалацию
            if analysis['escalation_detected'] and crime_type in ['Убийство', 'Разбой', 'Грабеж']:
                adjusted_days *= 0.6  # Эскалация = выше риск тяжких
            
            individual_windows[crime_type] = max(7, int(adjusted_days))  # Минимум 7 дней
        
        return individual_windows
    
    def _create_crime_forecast(
        self,
        crime_type: str,
        base_days: int,
        individual_days: int,
        analysis: Dict,
        pattern: Dict,
        person_data: Dict
    ) -> Dict:
        """Создает прогноз для конкретного типа преступления"""
        
        # Базовая вероятность
        base_probability = 50.0
        
        # Корректировка на основе истории
        if crime_type in analysis['crime_types']:
            crime_count = analysis['crime_types'][crime_type]
            total_crimes = analysis['total_violations']
            crime_ratio = crime_count / total_crimes if total_crimes > 0 else 0
            
            # Увеличиваем вероятность пропорционально доле этого типа
            base_probability += crime_ratio * 30
            
            # Дополнительный бонус за повторяемость
            if crime_count >= 3:
                base_probability += 15
        else:
            # Новый тип преступления - ниже вероятность
            base_probability -= 20
        
        # Корректировка на основе паттерна
        pattern_adjustments = {
            'specialized': 20 if crime_type in analysis['crime_types'] else -30,
            'repetitive': 15,
            'periodic': 10,
            'chaotic': 0,
            'mixed': 5,
            'escalating': 25 if crime_type in ['Убийство', 'Разбой'] else -5,
            'insufficient_data': -10
        }
        base_probability += pattern_adjustments.get(pattern['type'], 0)
        
        # Корректировка на основе временного фактора
        days_since_last = analysis['last_violation_days_ago']
        if days_since_last > individual_days * 0.8:
            base_probability += 10  # Приближается время
        
        # Корректировка на основе тренда
        if analysis['trend'] == 'accelerating':
            base_probability += 15
        elif analysis['trend'] == 'decelerating':
            base_probability -= 10
        
        # Финальная вероятность (0-100)
        probability = max(5, min(95, base_probability))
        
        # Расчет доверительного интервала
        confidence_width = 30 - (pattern['confidence'] * 20)  # Чем выше уверенность, тем уже интервал
        ci_lower = max(1, individual_days - int(individual_days * confidence_width / 100))
        ci_upper = individual_days + int(individual_days * confidence_width / 100)
        
        # Определение уровня риска
        if probability >= 70:
            risk_level = 'critical'
        elif probability >= 50:
            risk_level = 'high'
        elif probability >= 30:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Расчет предотвратимости
        preventability = self._calculate_preventability(crime_type, pattern, analysis)
        
        return {
            'crime_type': crime_type,
            'probability': round(probability, 1),
            'days_until': individual_days,
            'date_predicted': (datetime.now() + timedelta(days=individual_days)).isoformat(),
            'confidence_interval': {
                'lower': ci_lower,
                'upper': ci_upper
            },
            'confidence': pattern['confidence'],
            'risk_level': risk_level,
            'preventability': preventability,
            'factors': {
                'historical_frequency': crime_type in analysis['crime_types'],
                'pattern_match': pattern['type'],
                'trend': analysis['trend'],
                'days_since_last': days_since_last
            }
        }
    
    def _identify_critical_periods(self, forecasts: List[Dict], violations: List[Dict]) -> List[Dict]:
        """Определяет критические периоды повышенного риска"""
        
        critical_periods = []
        
        # Группировка прогнозов по временным периодам
        period_groups = defaultdict(list)
        for forecast in forecasts:
            if forecast['probability'] >= 40:  # Только значимые риски
                period_key = forecast['days_until'] // 30  # Группировка по месяцам
                period_groups[period_key].append(forecast)
        
        # Анализ каждого периода
        for period_months, period_forecasts in period_groups.items():
            if len(period_forecasts) >= 2:  # Множественные риски
                start_days = min(f['days_until'] for f in period_forecasts)
                end_days = max(f['days_until'] for f in period_forecasts)
                avg_probability = statistics.mean(f['probability'] for f in period_forecasts)
                
                critical_periods.append({
                    'start_date': (datetime.now() + timedelta(days=start_days)).isoformat(),
                    'end_date': (datetime.now() + timedelta(days=end_days)).isoformat(),
                    'risk_level': 'high' if avg_probability >= 60 else 'medium',
                    'crime_types': [f['crime_type'] for f in period_forecasts],
                    'avg_probability': round(avg_probability, 1),
                    'recommended_interventions': self._recommend_interventions(period_forecasts)
                })
        
        return sorted(critical_periods, key=lambda x: x['start_date'])
    
    def _recommend_interventions(self, forecasts: List[Dict]) -> List[str]:
        """Рекомендует программы вмешательства для критического периода"""
        
        interventions = set()
        
        for forecast in forecasts:
            crime_type = forecast['crime_type']
            if crime_type in INTERVENTION_PROGRAMS:
                programs = INTERVENTION_PROGRAMS[crime_type]['programs']
                interventions.update(programs[:2])  # Топ-2 программы для каждого типа
        
        return list(interventions)
    
    def _extract_crime_type(self, violation_type: str) -> str:
        """Извлекает тип преступления из описания"""
        
        crime_keywords = {
            'Кража': ['кража', 'хищение', 'воровство'],
            'Грабеж': ['грабеж', 'грабёж'],
            'Разбой': ['разбой'],
            'Мошенничество': ['мошенничество', 'обман'],
            'Убийство': ['убийство', 'убийств'],
            'Изнасилование': ['изнасилование', 'насилие'],
            'Хулиганство': ['хулиганство', 'хулиган'],
            'Вымогательство': ['вымогательство', 'вымогател']
        }
        
        violation_lower = violation_type.lower()
        
        for crime_type, keywords in crime_keywords.items():
            for keyword in keywords:
                if keyword in violation_lower:
                    return crime_type
        
        # Если не найдено специфичное - определяем по типу
        if 'уголов' in violation_lower:
            return 'Кража'  # По умолчанию для уголовных
        elif 'администр' in violation_lower:
            return 'Хулиганство'  # По умолчанию для административных
        
        return 'Прочее'
    
    def _detect_escalation(self, sorted_violations: List[Dict]) -> bool:
        """Определяет наличие эскалации в тяжести преступлений"""
        
        if len(sorted_violations) < 3:
            return False
        
        severity_scores = []
        for v in sorted_violations:
            if 'убийств' in v['violation_type'].lower():
                severity_scores.append(10)
            elif 'разбой' in v['violation_type'].lower():
                severity_scores.append(8)
            elif 'грабеж' in v['violation_type'].lower() or 'грабёж' in v['violation_type'].lower():
                severity_scores.append(7)
            elif 'изнасилование' in v['violation_type'].lower():
                severity_scores.append(9)
            elif 'вымогательство' in v['violation_type'].lower():
                severity_scores.append(6)
            elif 'мошенничество' in v['violation_type'].lower():
                severity_scores.append(5)
            elif 'кража' in v['violation_type'].lower():
                severity_scores.append(4)
            elif 'хулиганство' in v['violation_type'].lower():
                severity_scores.append(3)
            else:
                severity_scores.append(2)
        
        # Проверяем тренд увеличения тяжести
        recent_avg = statistics.mean(severity_scores[-3:])
        early_avg = statistics.mean(severity_scores[:3])
        
        return recent_avg > early_avg * 1.5
    
    def _days_since_last_violation(self, sorted_violations: List[Dict]) -> int:
        """Подсчитывает дни с последнего нарушения"""
        
        if not sorted_violations:
            return 9999
        
        last_date = datetime.fromisoformat(sorted_violations[-1]['violation_date'])
        return (datetime.now() - last_date).days
    
    def _calculate_confidence(self, violations: List[Dict]) -> float:
        """Рассчитывает уровень уверенности в прогнозе"""
        
        if len(violations) < 2:
            return 0.3
        elif len(violations) < 5:
            return 0.5
        elif len(violations) < 10:
            return 0.7
        else:
            return 0.85
    
    def _calculate_preventability(self, crime_type: str, pattern: Dict, analysis: Dict) -> float:
        """Рассчитывает предотвратимость преступления"""
        
        base_preventability = 70.0
        
        # Корректировка на основе типа преступления
        crime_preventability = {
            'Кража': 80,
            'Мошенничество': 75,
            'Хулиганство': 85,
            'Грабеж': 70,
            'Вымогательство': 65,
            'Разбой': 60,
            'Изнасилование': 55,
            'Убийство': 50
        }
        base_preventability = crime_preventability.get(crime_type, 70)
        
        # Корректировка на основе паттерна
        if pattern['type'] == 'periodic':
            base_preventability += 10  # Предсказуемый паттерн легче предотвратить
        elif pattern['type'] == 'chaotic':
            base_preventability -= 10  # Хаотичный паттерн сложнее предотвратить
        elif pattern['type'] == 'escalating':
            base_preventability -= 15  # Эскалация сложнее для предотвращения
        
        # Корректировка на основе тренда
        if analysis['trend'] == 'decelerating':
            base_preventability += 5  # Замедление = легче предотвратить
        elif analysis['trend'] == 'accelerating':
            base_preventability -= 5  # Ускорение = сложнее предотвратить
        
        return max(20, min(95, base_preventability))