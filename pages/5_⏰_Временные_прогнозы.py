"""
⏰ Временные прогнозы
Персональные прогнозы временных окон до возможных преступлений
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import sys
from datetime import datetime, timedelta
import json

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импорт из наших модулей
try:
    from utils.data_loader import (
        load_all_data,
        get_risk_data,
        get_crime_statistics
    )
    from utils.risk_calculator import (
        RiskCalculator,
        CrimeForecaster,
        quick_risk_assessment
    )
    from utils.forecasting import (
        TimelineVisualizer,
        InterventionPlanner,
        generate_risk_report
    )
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    st.warning("⚠️ Модули utils не найдены. Работаем в демо-режиме.")

# Настройка страницы
st.set_page_config(
    page_title="Временные прогнозы",
    page_icon="⏰",
    layout="wide"
)

# Кастомные стили
st.markdown("""
<style>
    .forecast-card {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .timeline-item {
        position: relative;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #2196f3;
        background-color: #f5f5f5;
    }
    .risk-level-critical {
        background-color: #ffebee;
        border-left-color: #f44336;
    }
    .risk-level-high {
        background-color: #fff8e1;
        border-left-color: #ff9800;
    }
    .risk-level-medium {
        background-color: #e8f5e9;
        border-left-color: #4caf50;
    }
    .calendar-day {
        display: inline-block;
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        margin: 2px;
        border-radius: 5px;
        font-size: 12px;
    }
    .day-critical { background-color: #ef5350; color: white; }
    .day-high { background-color: #ffa726; color: white; }
    .day-medium { background-color: #66bb6a; color: white; }
    .day-low { background-color: #e0e0e0; }
    .recommendation-box {
        background-color: #e1f5fe;
        border: 1px solid #03a9f4;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .stat-box {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.title("⏰ Временные прогнозы")
st.markdown("### Персональные прогнозы временных окон до возможных преступлений")

# Функция загрузки данных
@st.cache_data
def load_forecast_data():
    """Загружаем данные для прогнозирования"""
    
    if MODULES_AVAILABLE:
        try:
            # Загружаем реальные данные
            risk_df = get_risk_data()
            if risk_df is not None and not risk_df.empty:
                return risk_df
        except Exception as e:
            st.error(f"Ошибка загрузки данных: {e}")
    
    # Создаем демо-данные
    np.random.seed(42)
    n_people = 100
    
    demo_data = {
        'ИИН': [f"{np.random.randint(100000, 999999)}{np.random.randint(100000, 999999)}" for _ in range(n_people)],
        'ФИО': [f"Тестовый Пользователь {i:03d}" for i in range(1, n_people + 1)],
        'current_age': np.random.normal(35, 12, n_people).clip(18, 70).astype(int),
        'gender': np.random.choice(['М', 'Ж'], n_people, p=[0.85, 0.15]),
        'pattern_type': np.random.choice([
            'mixed_unstable', 'chronic_criminal', 'escalating', 'deescalating', 'single'
        ], n_people, p=[0.727, 0.136, 0.07, 0.057, 0.01]),
        'total_cases': np.random.poisson(4, n_people) + 1,
        'criminal_count': np.random.poisson(1.5, n_people),
        'admin_count': np.random.poisson(2.5, n_people),
        'risk_total_risk_score': np.random.beta(2, 5, n_people) * 10,
        'last_violation_date': [
            datetime.now() - timedelta(days=np.random.randint(1, 365))
            for _ in range(n_people)
        ],
        'has_property': np.random.choice([0, 1], n_people, p=[0.6, 0.4]),
        'has_job': np.random.choice([0, 1], n_people, p=[0.4, 0.6]),
        'region': np.random.choice(['Астана', 'Алматы', 'Шымкент', 'Караганда', 'Актобе'], n_people),
        'days_since_last': np.random.randint(1, 730, n_people),
        'age_at_first_violation': np.random.normal(25, 8, n_people).clip(14, 50).astype(int),
        'recidivism_rate': np.random.uniform(0.1, 3, n_people),
        'has_escalation': np.random.choice([0, 1], n_people, p=[0.8, 0.2])
    }
    
    return pd.DataFrame(demo_data)

# Базовые временные окна из исследования
CRIME_FORECAST_BASE = {
    'Мошенничество': {'days': 109, 'probability_base': 82.3, 'color': '#e74c3c'},
    'Кража': {'days': 146, 'probability_base': 87.3, 'color': '#f39c12'},
    'Убийство': {'days': 143, 'probability_base': 97.0, 'color': '#8e44ad'},
    'Вымогательство': {'days': 144, 'probability_base': 100.7, 'color': '#e67e22'},
    'Грабеж': {'days': 148, 'probability_base': 60.2, 'color': '#3498db'},
    'Разбой': {'days': 150, 'probability_base': 20.2, 'color': '#27ae60'},
    'Изнасилование': {'days': 157, 'probability_base': 65.6, 'color': '#c0392b'},
    'Хулиганство': {'days': 155, 'probability_base': 45.0, 'color': '#f1c40f'}
}

# Загружаем данные
forecast_df = load_forecast_data()

if forecast_df is not None and len(forecast_df) > 0:
    
    # Фильтры в боковой панели
    st.sidebar.header("🎛️ Настройки прогноза")
    
    # Фильтр по уровню риска
    risk_filter = st.sidebar.select_slider(
        "Минимальный риск-балл:",
        options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        value=5
    )
    
    # Фильтруем данные
    filtered_df = forecast_df[forecast_df['risk_total_risk_score'] >= risk_filter].copy()
    
    if len(filtered_df) == 0:
        st.warning(f"Нет людей с риск-баллом ≥ {risk_filter}. Показываем всех.")
        filtered_df = forecast_df.copy()
    
    # Сортируем по риску
    filtered_df = filtered_df.sort_values('risk_total_risk_score', ascending=False)
    
    # Ограничиваем количество для производительности
    if len(filtered_df) > 50:
        filtered_df = filtered_df.head(50)
        st.info("Показаны топ-50 человек с наивысшим риском")
    
    # Выбор человека для анализа
    st.subheader("👤 Выберите лицо для анализа")
    
    # Подготовка списка для выбора
    person_options = []
    for _, row in filtered_df.iterrows():
        risk_emoji = "🔴" if row['risk_total_risk_score'] >= 7 else "🟡" if row['risk_total_risk_score'] >= 5 else "🟠"
        option = f"{risk_emoji} {row['ИИН']} | {row.get('ФИО', 'Без имени')} | Риск: {row['risk_total_risk_score']:.1f}"
        person_options.append(option)
    
    selected_option = st.selectbox(
        "Выберите человека:",
        options=person_options,
        help="Список отсортирован по убыванию риска"
    )
    
    # Получаем выбранного человека
    selected_idx = person_options.index(selected_option)
    selected_person = filtered_df.iloc[selected_idx]
    
    # Типы преступлений для анализа
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Типы преступлений")
    
    all_crimes = list(CRIME_FORECAST_BASE.keys())
    selected_crimes = st.sidebar.multiselect(
        "Анализировать:",
        all_crimes,
        default=['Кража', 'Мошенничество', 'Убийство', 'Грабеж']
    )
    
    # Временной горизонт
    time_horizon = st.sidebar.slider(
        "Временной горизонт (дни):",
        min_value=90,
        max_value=365,
        value=270,
        step=30
    )
    
    # Дополнительные настройки
    st.sidebar.markdown("---")
    show_confidence = st.sidebar.checkbox("Показывать доверительные интервалы", value=True)
    show_calendar = st.sidebar.checkbox("Показывать календарь", value=True)
    show_gantt = st.sidebar.checkbox("Показывать план мероприятий", value=True)
    
    # Основной анализ
    st.markdown("---")
    
    # Информация о выбранном человеке
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("#### 👤 Личность")
        st.write(f"**ИИН:** {selected_person['ИИН']}")
        st.write(f"**Возраст:** {selected_person.get('current_age', 'Н/Д')} лет")
        st.write(f"**Пол:** {selected_person.get('gender', 'Н/Д')}")
    
    with col2:
        st.markdown("#### 🎯 Риск-профиль")
        risk_score = selected_person.get('risk_total_risk_score', 0)
        risk_category = "🔴 Критический" if risk_score >= 7 else "🟡 Высокий" if risk_score >= 5 else "🟠 Средний" if risk_score >= 3 else "🟢 Низкий"
        st.metric("Риск-балл", f"{risk_score:.1f}/10")
        st.write(f"**Категория:** {risk_category}")
    
    with col3:
        st.markdown("#### 📊 История")
        st.write(f"**Всего дел:** {selected_person.get('total_cases', 0)}")
        st.write(f"**Уголовных:** {selected_person.get('criminal_count', 0)}")
        st.write(f"**Админ:** {selected_person.get('admin_count', 0)}")
    
    with col4:
        st.markdown("#### 🔄 Паттерн")
        pattern = selected_person.get('pattern_type', 'unknown')
        pattern_translation = {
            'mixed_unstable': 'Нестабильное',
            'chronic_criminal': 'Хронический',
            'escalating': 'Эскалация',
            'deescalating': 'Деэскалация',
            'single': 'Единичное'
        }
        st.write(f"**Тип:** {pattern_translation.get(pattern, pattern)}")
        st.write(f"**Последнее:** {selected_person.get('days_since_last', 0)} дн. назад")
    
    # Расчет прогнозов
    st.markdown("---")
    st.subheader("📈 Временные прогнозы")
    
    if MODULES_AVAILABLE:
        # Используем реальные модули
        forecaster = CrimeForecaster()
        forecasts = forecaster.forecast_crime_timeline(selected_person.to_dict())
        
        # Фильтруем по выбранным преступлениям
        filtered_forecasts = {k: v for k, v in forecasts.items() if k in selected_crimes}
        
        if filtered_forecasts:
            # Визуализация временной шкалы
            visualizer = TimelineVisualizer()
            timeline_fig = visualizer.create_risk_timeline(filtered_forecasts, selected_crimes, time_horizon)
            st.plotly_chart(timeline_fig, use_container_width=True)
            
            # Календарная визуализация
            if show_calendar:
                st.subheader("📅 Календарь критических дат")
                calendar_fig = visualizer.create_calendar_heatmap(filtered_forecasts)
                if calendar_fig:
                    st.plotly_chart(calendar_fig, use_container_width=True)
        else:
            st.warning("Выберите хотя бы один тип преступления для анализа")
    
    else:
        # Демо-режим прогнозирования
        st.info("🔮 Демо-режим прогнозирования")
        
        # Создаем демо-прогнозы
        demo_forecasts = {}
        person_dict = selected_person.to_dict()
        
        for crime_type in selected_crimes:
            base_data = CRIME_FORECAST_BASE[crime_type]
            
            # Простые модификаторы
            age_mod = 0.8 if person_dict.get('current_age', 35) < 25 else 1.2 if person_dict.get('current_age', 35) > 45 else 1.0
            pattern_mod = 0.7 if pattern == 'chronic_criminal' else 0.9 if pattern == 'mixed_unstable' else 1.0
            social_mod = 0.85 if person_dict.get('has_property', 0) == 0 else 1.0
            
            forecast_days = int(base_data['days'] * age_mod * pattern_mod * social_mod)
            forecast_days = max(30, min(365, forecast_days))
            
            probability = min(95, max(10, risk_score * 10 * (base_data['probability_base'] / 100)))
            
            demo_forecasts[crime_type] = {
                'days': forecast_days,
                'date': datetime.now() + timedelta(days=forecast_days),
                'probability': probability,
                'ci_lower': int(forecast_days * 0.7),
                'ci_upper': int(forecast_days * 1.4),
                'color': base_data['color']
            }
        
        # Визуализация демо-прогнозов
        if demo_forecasts:
            # Создаем график временной шкалы
            fig = go.Figure()
            
            for crime_type, forecast in demo_forecasts.items():
                # Создаем временную линию
                dates = [datetime.now() + timedelta(days=i) for i in range(0, time_horizon, 7)]
                risk_values = []
                
                for date in dates:
                    days_from_now = (date - datetime.now()).days
                    days_to_forecast = forecast['days']
                    
                    if days_from_now < days_to_forecast * 0.5:
                        risk = forecast['probability'] * 0.3
                    elif days_from_now < days_to_forecast:
                        progress = (days_from_now - days_to_forecast * 0.5) / (days_to_forecast * 0.5)
                        risk = forecast['probability'] * (0.3 + 0.7 * progress)
                    elif days_from_now == days_to_forecast:
                        risk = forecast['probability']
                    else:
                        decay = np.exp(-0.02 * (days_from_now - days_to_forecast))
                        risk = forecast['probability'] * 0.7 * decay
                    
                    risk_values.append(risk)
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=risk_values,
                    mode='lines+markers',
                    name=f"{crime_type} ({forecast['probability']:.0f}%)",
                    line=dict(color=forecast['color'], width=2),
                    marker=dict(size=4)
                ))
                
                # Вертикальная линия на дату прогноза
                fig.add_vline(
                    x=forecast['date'],
                    line_dash="dash",
                    line_color=forecast['color'],
                    annotation_text=f"{crime_type}<br>{forecast['days']}д",
                    annotation_position="top"
                )
            
            fig.update_layout(
                title="Временная шкала изменения рисков",
                xaxis_title="Дата",
                yaxis_title="Уровень риска (%)",
                height=500,
                hovermode='x unified',
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Таблица прогнозов
    st.subheader("📋 Детальные прогнозы")
    
    forecast_table = []
    
    if MODULES_AVAILABLE and 'filtered_forecasts' in locals():
        for crime_type, forecast in filtered_forecasts.items():
            forecast_table.append({
                'Тип преступления': crime_type,
                'Прогноз (дни)': forecast['days'],
                'Дата': forecast['date'].strftime('%d.%m.%Y'),
                'Вероятность (%)': f"{forecast['probability']:.1f}",
                'Доверительный интервал': f"{forecast['ci_lower']}-{forecast['ci_upper']} дней",
                'Уровень риска': forecast['risk_level'],
                'Уверенность': forecast.get('confidence', 'Средняя')
            })
    else:
        # Демо таблица
        for crime_type, forecast in demo_forecasts.items():
            risk_level = "🔴 Критический период" if forecast['days'] < 60 else "🟡 Высокий риск" if forecast['days'] < 120 else "🟠 Средний риск" if forecast['days'] < 180 else "🟢 Низкий риск"
            
            forecast_table.append({
                'Тип преступления': crime_type,
                'Прогноз (дни)': forecast['days'],
                'Дата': forecast['date'].strftime('%d.%m.%Y'),
                'Вероятность (%)': f"{forecast['probability']:.1f}",
                'Доверительный интервал': f"{forecast['ci_lower']}-{forecast['ci_upper']} дней",
                'Уровень риска': risk_level,
                'Уверенность': 'Средняя'
            })
    
    if forecast_table:
        forecast_df_display = pd.DataFrame(forecast_table)
        forecast_df_display = forecast_df_display.sort_values('Прогноз (дни)')
        
        # Стилизация таблицы
        def style_risk_level(val):
            if 'Критический' in str(val):
                return 'background-color: #ffcdd2'
            elif 'Высокий' in str(val):
                return 'background-color: #ffe0b2'
            elif 'Средний' in str(val):
                return 'background-color: #fff9c4'
            else:
                return 'background-color: #c8e6c9'
        
        styled_df = forecast_df_display.style.applymap(
            style_risk_level, 
            subset=['Уровень риска']
        )
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Календарь критических дат
    if show_calendar and forecast_table:
        st.subheader("📅 Календарь критических периодов")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Ближайшие 90 дней:")
            critical_dates = []
            
            for item in forecast_table:
                if item['Прогноз (дни)'] <= 90:
                    date = datetime.now() + timedelta(days=item['Прогноз (дни)'])
                    critical_dates.append({
                        'date': date,
                        'crime': item['Тип преступления'],
                        'days': item['Прогноз (дни)'],
                        'prob': float(item['Вероятность (%)'].replace('%', ''))
                    })
            
            critical_dates.sort(key=lambda x: x['days'])
            
            for event in critical_dates[:5]:
                color = "🔴" if event['days'] <= 30 else "🟡" if event['days'] <= 60 else "🟠"
                st.markdown(f"""
                <div class="timeline-item {'risk-level-critical' if event['days'] <= 30 else 'risk-level-high' if event['days'] <= 60 else ''}">
                    {color} <strong>{event['crime']}</strong><br>
                    Через {event['days']} дней ({event['date'].strftime('%d.%m.%Y')})<br>
                    Вероятность: {event['prob']:.0f}%
                </div>
                """, unsafe_allow_html=True)
            
            if not critical_dates:
                st.success("✅ Нет критических рисков в ближайшие 90 дней")
        
        with col2:
            st.markdown("#### Среднесрочные риски (90-180 дней):")
            medium_dates = []
            
            for item in forecast_table:
                if 90 < item['Прогноз (дни)'] <= 180:
                    date = datetime.now() + timedelta(days=item['Прогноз (дни)'])
                    medium_dates.append({
                        'date': date,
                        'crime': item['Тип преступления'],
                        'days': item['Прогноз (дни)'],
                        'prob': float(item['Вероятность (%)'].replace('%', ''))
                    })
            
            medium_dates.sort(key=lambda x: x['days'])
            
            for event in medium_dates[:5]:
                st.markdown(f"""
                <div class="timeline-item">
                    🟡 <strong>{event['crime']}</strong><br>
                    Через {event['days']} дней ({event['date'].strftime('%d.%m.%Y')})<br>
                    Вероятность: {event['prob']:.0f}%
                </div>
                """, unsafe_allow_html=True)
            
            if not medium_dates:
                st.info("ℹ️ Нет среднесрочных рисков")
    
    # План мероприятий
    if show_gantt and MODULES_AVAILABLE:
        st.markdown("---")
        st.subheader("📋 План превентивных мероприятий")
        
        try:
            planner = InterventionPlanner()
            plan = planner.create_intervention_plan(selected_person.to_dict(), filtered_forecasts)
            
            # Информация о плане
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Приоритет:** {plan['priority_level']}")
                st.markdown(f"**Частота мониторинга:** {plan['monitoring_frequency']}")
            
            with col2:
                if plan['responsible_agencies']:
                    st.markdown("**Ответственные службы:**")
                    for agency in plan['responsible_agencies']:
                        st.write(f"• {agency}")
            
            # Диаграмма Ганта
            gantt_fig = planner.create_intervention_gantt(plan)
            if gantt_fig:
                st.plotly_chart(gantt_fig, use_container_width=True)
            
            # Список программ
            if plan['programs']:
                st.markdown("#### Рекомендуемые программы:")
                program_cols = st.columns(3)
                for i, program in enumerate(plan['programs']):
                    with program_cols[i % 3]:
                        st.markdown(f"""
                        <div class="recommendation-box">
                            • {program}
                        </div>
                        """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Ошибка создания плана: {e}")
    
    # Рекомендации
    st.markdown("---")
    st.subheader("💡 Рекомендации на основе прогноза")
    
    recommendations = []
    
    # Анализируем критичные риски
    if forecast_table:
        critical_risks = [f for f in forecast_table if f['Прогноз (дни)'] <= 60]
        
        if critical_risks:
            top_risk = critical_risks[0]
            recommendations.append(f"🚨 **КРИТИЧЕСКИЙ РИСК**: {top_risk['Тип преступления']} через {top_risk['Прогноз (дни)']} дней")
            recommendations.append(f"⏰ **Немедленные действия требуются до**: {(datetime.now() + timedelta(days=top_risk['Прогноз (дни)'] - 30)).strftime('%d.%m.%Y')}")
            
            # Специфические рекомендации по типу преступления
            crime_type = top_risk['Тип преступления']
            if crime_type in ['Кража', 'Мошенничество']:
                recommendations.extend([
                    "💼 **Срочное трудоустройство** через службу занятости",
                    "💰 **Финансовое консультирование** и помощь с долгами",
                    "🏠 **Оценка жилищных условий** и социальная поддержка"
                ])
            elif crime_type in ['Убийство', 'Разбой', 'Грабеж']:
                recommendations.extend([
                    "🧠 **Экстренная психологическая помощь** - управление агрессией",
                    "👮 **Усиленный полицейский контроль** - ежедневные контакты",
                    "💊 **Медицинское обследование** на предмет психических расстройств"
                ])
            elif crime_type == 'Хулиганство':
                recommendations.extend([
                    "🏃 **Досуговые программы** - спорт, творчество",
                    "🚫 **Контроль алкоголя** - программа трезвости",
                    "👥 **Социальная интеграция** - общественные работы"
                ])
    
    # Общие рекомендации на основе профиля
    if risk_score >= 7:
        recommendations.append("🚨 **Максимальный уровень контроля** - персональный куратор 24/7")
    elif risk_score >= 5:
        recommendations.append("⚠️ **Усиленный мониторинг** - встречи 3 раза в неделю")
    
    if selected_person.get('has_job', 0) == 0:
        recommendations.append("💼 **Трудоустройство** - ключевой фактор снижения риска")
    
    if selected_person.get('has_property', 0) == 0:
        recommendations.append("🏠 **Жилищная программа** - стабилизация условий жизни")
    
    if pattern == 'mixed_unstable':
        recommendations.append("🧠 **Психологическая стабилизация** - работа с импульсивностью")
    elif pattern == 'chronic_criminal':
        recommendations.append("🔒 **Программа декриминализации** - изменение образа жизни")
    
    # Отображаем рекомендации
    for rec in recommendations:
        st.markdown(f"- {rec}")
    
    # Экспорт прогноза
    st.markdown("---")
    st.subheader("📥 Экспорт результатов")
    
    # Подготовка данных для экспорта
    export_data = {
        'person_info': {
            'ИИН': selected_person['ИИН'],
            'ФИО': selected_person.get('ФИО', 'Не указано'),
            'Возраст': selected_person.get('current_age', 'Н/Д'),
            'Риск_балл': risk_score,
            'Категория_риска': risk_category,
            'Паттерн': pattern_translation.get(pattern, pattern)
        },
        'forecasts': forecast_table,
        'recommendations': recommendations,
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON экспорт
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2, default=str)
        st.download_button(
            label="📊 Скачать полный отчет (JSON)",
            data=json_str,
            file_name=f'forecast_{selected_person["ИИН"]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            mime='application/json'
        )
    
    with col2:
        # CSV экспорт прогнозов
        if forecast_table:
            forecast_export_df = pd.DataFrame(forecast_table)
            csv = forecast_export_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📋 Скачать прогнозы (CSV)",
                data=csv,
                file_name=f'forecasts_{selected_person["ИИН"]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
    
    with col3:
        # Текстовый отчет
        text_report = f"""ОТЧЕТ О ВРЕМЕННЫХ ПРОГНОЗАХ
Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}

ИНФОРМАЦИЯ О ЛИЦЕ:
ИИН: {selected_person['ИИН']}
Возраст: {selected_person.get('current_age', 'Н/Д')} лет
Риск-балл: {risk_score:.1f}/10 ({risk_category})
Паттерн: {pattern_translation.get(pattern, pattern)}

КРИТИЧЕСКИЕ ДАТЫ:
"""
        for item in forecast_table[:5]:
            text_report += f"\n{item['Тип преступления']}: {item['Дата']} ({item['Прогноз (дни)']} дней) - {item['Вероятность (%)']}"
        
        text_report += "\n\nРЕКОМЕНДАЦИИ:\n"
        for rec in recommendations:
            text_report += f"\n{rec.replace('**', '')}"
        
        st.download_button(
            label="📄 Скачать отчет (TXT)",
            data=text_report,
            file_name=f'report_{selected_person["ИИН"]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            mime='text/plain'
        )

else:
    st.error("❌ Данные для прогнозирования не загружены")
    
    st.markdown("""
    ### 📁 Требуемые файлы данных:
    Разместите в папке `data/` один из файлов:
    - `RISK_ANALYSIS_RESULTS.xlsx` (приоритетный)
    - `ML_DATASET_COMPLETE.xlsx` (альтернативный)
    
    ### 📊 Формат данных:
    Файл должен содержать колонки:
    - ИИН, ФИО
    - risk_total_risk_score (риск-балл)
    - current_age (возраст)
    - pattern_type (тип паттерна)
    - total_cases, criminal_count, admin_count
    - has_property, has_job (социальные факторы)
    """)

# Боковая панель со статистикой
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 Статистика прогнозов")
    
    if forecast_df is not None and not forecast_df.empty:
        total_people = len(forecast_df)
        high_risk = len(forecast_df[forecast_df['risk_total_risk_score'] >= 5])
        critical_risk = len(forecast_df[forecast_df['risk_total_risk_score'] >= 7])
        
        st.metric("Всего в базе", f"{total_people:,}")
        st.metric("Высокий риск (5+)", f"{high_risk:,}")
        st.metric("Критический риск (7+)", f"{critical_risk:,}")
        
        # Распределение по паттернам
        if 'pattern_type' in forecast_df.columns:
            st.markdown("---")
            st.markdown("### 🔄 Паттерны поведения")
            pattern_counts = forecast_df['pattern_type'].value_counts()
            for pattern, count in pattern_counts.items():
                percent = count / total_people * 100
                st.write(f"**{pattern}**: {count} ({percent:.1f}%)")
    
    st.markdown("---")
    st.markdown("### ℹ️ Справка")
    
    with st.expander("Как работают прогнозы"):
        st.markdown("""
        **Алгоритм прогнозирования учитывает:**
        - Базовые временные окна из исследования
        - Возрастные факторы
        - Паттерн поведения
        - Социально-экономический статус
        - Историю правонарушений
        
        **Временные окна (базовые):**
        - Мошенничество: 109 дней
        - Убийство: 143 дня
        - Кража: 146 дней
        - Разбой: 150 дней
        - Изнасилование: 157 дней
        
        **Модификаторы:**
        - Молодой возраст: -20% времени
        - Нестабильный паттерн: -10%
        - Отсутствие работы: -10%
        - Отсутствие имущества: -15%
        """)