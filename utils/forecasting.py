"""
Модуль прогнозирования и визуализации временных линий
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import streamlit as st

class TimelineVisualizer:
    """
    Создание интерактивных временных визуализаций
    """
    
    def __init__(self):
        # Цветовая схема для разных типов преступлений
        self.crime_colors = {
            'Мошенничество': '#e74c3c',
            'Кража': '#f39c12',
            'Убийство': '#8e44ad',
            'Грабеж': '#3498db',
            'Разбой': '#27ae60',
            'Хулиганство': '#f1c40f',
            'Вымогательство': '#e67e22',
            'Изнасилование': '#c0392b'
        }
    
    def create_risk_timeline(self, forecasts: Dict[str, Dict], 
                           selected_crimes: List[str] = None,
                           time_horizon: int = 365) -> go.Figure:
        """
        Создает интерактивную временную шкалу рисков
        """
        if selected_crimes is None:
            selected_crimes = list(forecasts.keys())[:4]  # Топ-4 по умолчанию
        
        fig = go.Figure()
        
        # Создаем временную шкалу с единообразными типами
        today = datetime.now()
        dates = [today + timedelta(days=i) for i in range(0, time_horizon + 1, 7)]
        
        # Добавляем линии для каждого типа преступления
        for crime_type in selected_crimes:
            if crime_type in forecasts:
                forecast = forecasts[crime_type]
                
                # Проверяем корректность данных прогноза
                if not isinstance(forecast, dict):
                    continue
                    
                # Безопасное извлечение данных с fallback значениями
                try:
                    probability = float(forecast.get('probability', 50.0))
                    ci_lower = int(forecast.get('ci_lower', 30))
                    ci_upper = int(forecast.get('ci_upper', 90))
                    days = int(forecast.get('days', 90))
                except (ValueError, TypeError):
                    # Если данные некорректны, пропускаем
                    continue
                
                # Безопасное преобразование даты прогноза
                forecast_date = forecast.get('date')
                if forecast_date is None:
                    forecast_date = today + timedelta(days=days)
                elif isinstance(forecast_date, str):
                    try:
                        forecast_date = pd.to_datetime(forecast_date)
                    except:
                        forecast_date = today + timedelta(days=days)
                elif not isinstance(forecast_date, (datetime, pd.Timestamp)):
                    forecast_date = today + timedelta(days=days)
                
                # Создаем кривую риска
                try:
                    risk_curve = self._generate_risk_curve(
                        dates, today, forecast_date, 
                        probability, ci_lower, ci_upper
                    )
                except Exception as e:
                    # Если не удается создать кривую, пропускаем
                    continue
                
                # Основная линия
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=risk_curve['risk'],
                    mode='lines',
                    name=f"{crime_type} ({probability:.0f}%)",
                    line=dict(
                        color=self.crime_colors.get(crime_type, '#95a5a6'),
                        width=3
                    ),
                    hovertemplate=(
                        f'<b>{crime_type}</b><br>' +
                        'Дата: %{x|%d.%m.%Y}<br>' +
                        'Риск: %{y:.0f}%<br>' +
                        '<extra></extra>'
                    )
                ))
                
                # Доверительный интервал - обеспечиваем единообразие типов
                ci_dates = dates + dates[::-1]
                ci_values = risk_curve['ci_upper'] + risk_curve['ci_lower'][::-1]
                
                fig.add_trace(go.Scatter(
                    x=ci_dates,
                    y=ci_values,
                    fill='toself',
                    fillcolor=self._get_fill_color(crime_type),
                    line=dict(color='rgba(255,255,255,0)'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # Вертикальная линия на прогнозируемую дату - с дополнительными проверками
                try:
                    # Убеждаемся что forecast_date это правильный datetime объект
                    if hasattr(forecast_date, 'to_pydatetime'):
                        forecast_date = forecast_date.to_pydatetime()
                    
                    fig.add_vline(
                        x=forecast_date,
                        line_dash="dash",
                        line_color=self.crime_colors.get(crime_type, '#95a5a6'),
                        annotation_text=f"{crime_type}<br>{days}д",
                        annotation_position="top"
                    )
                except Exception as e:
                    # Если add_vline не работает, добавляем вертикальную линию как Scatter
                    fig.add_trace(go.Scatter(
                        x=[forecast_date, forecast_date],
                        y=[0, 100],
                        mode='lines',
                        line=dict(
                            color=self.crime_colors.get(crime_type, '#95a5a6'),
                            dash='dash',
                            width=2
                        ),
                        showlegend=False,
                        hoverinfo='skip',
                        name=f"{crime_type} прогноз"
                    ))
        
        # Настройка макета
        fig.update_layout(
            title="Временная шкала изменения рисков",
            xaxis_title="Дата",
            yaxis_title="Уровень риска (%)",
            height=500,
            hovermode='x unified',
            yaxis=dict(range=[0, 100]),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        # Добавляем зоны риска
        fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1)
        fig.add_hrect(y0=40, y1=70, fillcolor="orange", opacity=0.1)
        fig.add_hrect(y0=0, y1=40, fillcolor="green", opacity=0.1)
        
        return fig
    
    def create_calendar_heatmap(self, forecasts: Dict[str, Dict]) -> go.Figure:
        """
        Создает календарную тепловую карту критических дат
        """
        # Подготовка данных для календаря
        dates = []
        risks = []
        texts = []
        
        today = datetime.now()
        
        for i in range(365):
            date = today + timedelta(days=i)
            dates.append(date)
            
            # Рассчитываем общий риск на эту дату
            daily_risk = 0
            daily_crimes = []
            
            for crime_type, forecast in forecasts.items():
                # Проверяем близость к прогнозируемой дате
                days_to_forecast = (forecast['date'] - date).days
                
                if -30 <= days_to_forecast <= 30:
                    # В критическом окне (±30 дней от прогноза)
                    crime_risk = forecast['probability'] * (1 - abs(days_to_forecast) / 30)
                    daily_risk = max(daily_risk, crime_risk)
                    if crime_risk > 50:
                        daily_crimes.append(crime_type)
            
            risks.append(daily_risk)
            texts.append(f"{date.strftime('%d.%m')}<br>" + 
                        "<br>".join(daily_crimes[:3]))  # Максимум 3 преступления
        
        # Создаем календарную визуализацию
        df_calendar = pd.DataFrame({
            'date': dates,
            'risk': risks,
            'text': texts,
            'week': [d.isocalendar()[1] for d in dates],
            'weekday': [d.weekday() for d in dates],
            'month': [d.month for d in dates]
        })
        
        # Группируем по месяцам
        fig = go.Figure()
        
        for month in df_calendar['month'].unique():
            month_data = df_calendar[df_calendar['month'] == month]
            
            fig.add_trace(go.Scatter(
                x=month_data['week'],
                y=month_data['weekday'],
                mode='markers+text',
                marker=dict(
                    size=25,
                    color=month_data['risk'],
                    colorscale='RdYlGn_r',
                    cmin=0,
                    cmax=100,
                    showscale=True
                ),
                text=month_data['date'].dt.day,
                textposition="middle center",
                hovertext=month_data['text'],
                hoverinfo='text',
                showlegend=False
            ))
        
        fig.update_layout(
            title="Календарь критических дат",
            xaxis_title="Неделя года",
            yaxis_title="День недели",
            height=400,
            yaxis=dict(
                ticktext=['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
                tickvals=list(range(7))
            )
        )
        
        return fig
    
    def create_risk_gauge(self, risk_score: float) -> go.Figure:
        """
        Создает спидометр риска
        """
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk_score,
            title={'text': "Риск-балл"},
            delta={'reference': 5, 'increasing': {'color': "red"}},
            gauge={
                'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 3], 'color': '#27ae60'},
                    {'range': [3, 5], 'color': '#f39c12'},
                    {'range': [5, 7], 'color': '#e67e22'},
                    {'range': [7, 10], 'color': '#e74c3c'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 9
                }
            }
        ))
        
        fig.update_layout(height=300)
        return fig
    
    def _generate_risk_curve(self, dates: List[datetime], today: datetime,
                           forecast_date: datetime, max_prob: float,
                           ci_lower: int, ci_upper: int) -> Dict[str, List[float]]:
        """
        Генерирует кривую риска с доверительными интервалами
        """
        # Проверяем входные данные
        if not dates or not isinstance(max_prob, (int, float)):
            return {'risk': [0], 'ci_upper': [0], 'ci_lower': [0]}
            
        # Безопасное вычисление дней до прогноза
        try:
            forecast_days = (forecast_date - today).days
            # Убеждаемся что forecast_days разумный
            if forecast_days < 0:
                forecast_days = 30  # Fallback к 30 дням
            elif forecast_days > 1000:
                forecast_days = 365  # Ограничиваем годом
        except (TypeError, AttributeError):
            forecast_days = 90  # Fallback значение
        
        risk_values = []
        ci_upper_values = []
        ci_lower_values = []
        
        for date in dates:
            try:
                days_from_now = (date - today).days
            except (TypeError, AttributeError):
                days_from_now = 0  # Fallback
            
            # Основная кривая риска (логистическая функция)
            if days_from_now < forecast_days:
                # Нарастание риска
                if forecast_days > 0:
                    x = (days_from_now / forecast_days) * 6 - 3
                    risk = max_prob / (1 + np.exp(-x))
                else:
                    risk = max_prob * 0.1
            else:
                # Спад риска после пика
                decay = np.exp(-0.01 * (days_from_now - forecast_days))
                risk = max_prob * 0.7 * decay
            
            # Убеждаемся что риск в разумных пределах
            risk = max(0, min(100, risk))
            
            # Доверительные интервалы
            if ci_lower <= days_from_now <= ci_upper:
                ci_width = 0.2 * max_prob
            else:
                ci_width = 0.1 * max_prob
            
            risk_values.append(float(risk))
            ci_upper_values.append(float(min(100, risk + ci_width)))
            ci_lower_values.append(float(max(0, risk - ci_width)))
        
        return {
            'risk': risk_values,
            'ci_upper': ci_upper_values,
            'ci_lower': ci_lower_values
        }
    
    def _get_fill_color(self, crime_type: str) -> str:
        """
        Получает полупрозрачный цвет для заливки
        """
        base_color = self.crime_colors.get(crime_type, '#95a5a6')
        # Конвертируем в rgba с прозрачностью
        return f'rgba{tuple(int(base_color[i:i+2], 16) for i in (1, 3, 5)) + (0.2,)}'


class InterventionPlanner:
    """
    Планировщик превентивных мероприятий
    """
    
    def __init__(self):
        # База рекомендаций по типам преступлений
        self.interventions = {
            'Кража': {
                'programs': ['Трудоустройство', 'Финансовое консультирование', 
                           'Социальная помощь'],
                'urgency': 'high',
                'duration': 90
            },
            'Мошенничество': {
                'programs': ['Правовое просвещение', 'Финансовая грамотность',
                           'Этическое воспитание'],
                'urgency': 'critical',
                'duration': 60
            },
            'Убийство': {
                'programs': ['Управление гневом', 'Психологическая помощь',
                           'Контроль алкоголя', 'Медиация конфликтов'],
                'urgency': 'critical',
                'duration': 120
            },
            'Грабеж': {
                'programs': ['Социальная адаптация', 'Трудоустройство',
                           'Реабилитация'],
                'urgency': 'high',
                'duration': 90
            },
            'Разбой': {
                'programs': ['Интенсивный контроль', 'Психологическая коррекция',
                           'Социальная поддержка'],
                'urgency': 'critical',
                'duration': 120
            },
            'Хулиганство': {
                'programs': ['Досуговые программы', 'Спорт', 'Общественные работы'],
                'urgency': 'medium',
                'duration': 60
            },
            'Вымогательство': {
                'programs': ['Правовое воспитание', 'Экономическая поддержка',
                           'Психологическая помощь'],
                'urgency': 'high',
                'duration': 90
            },
            'Изнасилование': {
                'programs': ['Психиатрическая помощь', 'Контроль поведения',
                           'Терапия'],
                'urgency': 'critical',
                'duration': 180
            }
        }
    
    def create_intervention_plan(self, person_data: Dict, forecasts: Dict[str, Dict]) -> Dict:
        """
        Создает персональный план вмешательства
        """
        plan = {
            'priority_level': None,
            'programs': [],
            'timeline': [],
            'monitoring_frequency': None,
            'responsible_agencies': []
        }
        
        # Определяем приоритетность
        risk_score = person_data.get('risk_total_risk_score', 0)
        
        if risk_score >= 7:
            plan['priority_level'] = "🔴 Критический приоритет"
            plan['monitoring_frequency'] = "Ежедневно"
        elif risk_score >= 5:
            plan['priority_level'] = "🟡 Высокий приоритет"
            plan['monitoring_frequency'] = "2-3 раза в неделю"
        else:
            plan['priority_level'] = "🟢 Стандартный приоритет"
            plan['monitoring_frequency'] = "Еженедельно"
        
        # Собираем программы из прогнозов
        all_programs = set()
        timeline_events = []
        
        for crime_type, forecast in forecasts.items():
            if forecast['probability'] > 50:  # Только вероятные преступления
                intervention = self.interventions.get(crime_type, {})
                
                # Добавляем программы
                programs = intervention.get('programs', [])
                all_programs.update(programs)
                
                # Добавляем в timeline
                start_date = datetime.now()
                deadline = forecast['date'] - timedelta(days=30)  # За 30 дней до прогноза
                
                timeline_events.append({
                    'crime_type': crime_type,
                    'start_date': start_date,
                    'deadline': deadline,
                    'programs': programs,
                    'urgency': intervention.get('urgency', 'medium')
                })
        
        plan['programs'] = list(all_programs)
        plan['timeline'] = sorted(timeline_events, key=lambda x: x['deadline'])
        
        # Определяем ответственные службы
        if any('Трудоустройство' in p for p in plan['programs']):
            plan['responsible_agencies'].append("Служба занятости")
        if any('Психолог' in p for p in plan['programs']):
            plan['responsible_agencies'].append("Психологическая служба")
        if any('Социальн' in p for p in plan['programs']):
            plan['responsible_agencies'].append("Социальная защита")
        if risk_score >= 5:
            plan['responsible_agencies'].append("Полиция (участковый)")
        
        return plan
    
    def create_intervention_gantt(self, plan: Dict) -> go.Figure:
        """
        Создает диаграмму Ганта для плана вмешательства
        """
        if not plan['timeline']:
            return None
        
        # Подготовка данных для Ганта
        tasks = []
        
        for event in plan['timeline']:
            for program in event['programs']:
                tasks.append({
                    'Task': program,
                    'Start': event['start_date'],
                    'Finish': event['deadline'],
                    'Crime': event['crime_type'],
                    'Urgency': event['urgency']
                })
        
        if not tasks:
            return None
        
        df_gantt = pd.DataFrame(tasks)
        
        # Цвета по срочности
        urgency_colors = {
            'critical': '#e74c3c',
            'high': '#f39c12',
            'medium': '#3498db'
        }
        
        fig = px.timeline(
            df_gantt,
            x_start="Start",
            x_end="Finish",
            y="Task",
            color="Urgency",
            color_discrete_map=urgency_colors,
            title="План превентивных мероприятий"
        )
        
        fig.update_yaxes(categoryorder="category ascending")
        fig.update_layout(height=400)
        
        return fig


# Вспомогательные функции для интеграции с UI

@st.cache_data
def generate_risk_report(person_data: Dict) -> Dict:
    """
    Генерирует полный отчет о рисках для человека
    """
    from .risk_calculator import RiskCalculator, CrimeForecaster
    
    # Расчет риска
    calculator = RiskCalculator()
    risk_score, components = calculator.calculate_risk_score(person_data)
    risk_level, recommendation = calculator.get_risk_level(risk_score)
    
    # Прогнозы
    forecaster = CrimeForecaster()
    forecasts = forecaster.forecast_crime_timeline(person_data)
    
    # План вмешательства
    planner = InterventionPlanner()
    intervention_plan = planner.create_intervention_plan(person_data, forecasts)
    
    return {
        'risk_score': risk_score,
        'risk_level': risk_level,
        'risk_components': components,
        'recommendation': recommendation,
        'forecasts': forecasts,
        'intervention_plan': intervention_plan
    }

def format_risk_summary(report: Dict) -> str:
    """
    Форматирует сводку о рисках для отображения
    """
    summary = f"""
    ### 📊 Сводка оценки риска
    
    **Риск-балл:** {report['risk_score']:.1f}/10 {report['risk_level']}
    
    **Рекомендация:** {report['recommendation']}
    
    **Компоненты риска:**
    - Паттерн поведения: {report['risk_components']['pattern']:.1f}
    - История нарушений: {report['risk_components']['history']:.1f}
    - Временной фактор: {report['risk_components']['time']:.1f}
    - Возрастной фактор: {report['risk_components']['age']:.1f}
    - Социальные факторы: {report['risk_components']['social']:.1f}
    - Факторы эскалации: {report['risk_components']['escalation']:.1f}
    
    **Приоритет вмешательства:** {report['intervention_plan']['priority_level']}
    
    **Частота мониторинга:** {report['intervention_plan']['monitoring_frequency']}
    """
    
    return summary