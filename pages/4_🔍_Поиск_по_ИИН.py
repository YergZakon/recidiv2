"""
🔍 Поиск по ИИН
Мгновенная оценка риска и детальная информация по конкретному лицу
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import re
import sys
from datetime import datetime, timedelta

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импорт из наших модулей
try:
    from utils.data_loader import (
        load_all_data,
        get_risk_data,
        validate_iin,
        search_person_by_iin
    )
    from utils.risk_calculator import (
        RiskCalculator,
        CrimeForecaster,
        quick_risk_assessment
    )
    from utils.forecasting import (
        TimelineVisualizer,
        InterventionPlanner,
        generate_risk_report,
        format_risk_summary
    )
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    st.warning("⚠️ Модули utils не найдены. Работаем в демо-режиме.")

# Настройка страницы
st.set_page_config(
    page_title="Поиск по ИИН",
    page_icon="🔍",
    layout="wide"
)

# Кастомные стили
st.markdown("""
<style>
    .person-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .risk-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .risk-critical { background-color: #dc3545; color: white; }
    .risk-high { background-color: #ffc107; color: #000; }
    .risk-medium { background-color: #fd7e14; color: white; }
    .risk-low { background-color: #28a745; color: white; }
    .info-item {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #007bff;
    }
    .recommendation-card {
        background-color: #e3f2fd;
        border: 1px solid #2196f3;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .timeline-marker {
        position: relative;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #e74c3c;
        background-color: #fff5f5;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔍 Поиск по ИИН")
st.markdown("### Мгновенная оценка риска и детальная информация по конкретному лицу")

# Функция для создания демо-данных
@st.cache_data
def create_demo_data():
    """Создаем демо-данные для тестирования"""
    np.random.seed(42)
    n_people = 100
    
    demo_data = {
        'ИИН': [f"{np.random.randint(100000, 999999)}{np.random.randint(100000, 999999)}" for _ in range(n_people)],
        'Фамилия': [f"ФАМИЛИЯ_{i:03d}" for i in range(1, n_people + 1)],
        'Имя': [f"ИМЯ_{i:03d}" for i in range(1, n_people + 1)], 
        'Отчество': [f"ОТЧЕСТВО_{i:03d}" for i in range(1, n_people + 1)],
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
        'last_violation_type': np.random.choice([
            'Административное правонарушение', 'Кража', 'Мошенничество', 
            'Хулиганство', 'Грабеж', 'Побои'
        ], n_people, p=[0.4, 0.25, 0.15, 0.1, 0.05, 0.05]),
        'has_property': np.random.choice([0, 1], n_people, p=[0.6, 0.4]),
        'has_job': np.random.choice([0, 1], n_people, p=[0.4, 0.6]),
        'days_since_last': np.random.randint(1, 730, n_people),
        'age_at_first_violation': np.random.normal(25, 8, n_people).clip(14, 50).astype(int),
        'recidivism_rate': np.random.uniform(0.1, 3, n_people),
        'has_escalation': np.random.choice([0, 1], n_people, p=[0.8, 0.2]),
        'is_active': np.random.choice([0, 1], n_people, p=[0.6, 0.4])
    }
    
    return pd.DataFrame(demo_data)

# Функция для формирования ФИО
def get_person_fio(person_dict):
    """Формирует ФИО из доступных полей"""
    # Проверяем есть ли готовое поле ФИО
    if 'ФИО' in person_dict and person_dict['ФИО'] and str(person_dict['ФИО']).strip() != 'nan':
        return str(person_dict['ФИО']).strip()
    
    # Собираем из отдельных полей
    parts = []
    if 'Фамилия' in person_dict and person_dict['Фамилия'] and str(person_dict['Фамилия']).strip() != 'nan':
        parts.append(str(person_dict['Фамилия']).strip())
    if 'Имя' in person_dict and person_dict['Имя'] and str(person_dict['Имя']).strip() != 'nan':
        parts.append(str(person_dict['Имя']).strip())
    if 'Отчество' in person_dict and person_dict['Отчество'] and str(person_dict['Отчество']).strip() != 'nan':
        parts.append(str(person_dict['Отчество']).strip())
    
    if parts:
        return ' '.join(parts)
    
    # Если ничего нет, возвращаем ИИН
    return f"Лицо {person_dict.get('ИИН', 'НЕИЗВЕСТНО')}"

# Функция для отображения результатов поиска
def display_person_card(person_data, is_dict=False):
    """Отображает карточку человека с полной информацией"""
    
    # Если это Series, конвертируем в словарь
    if not is_dict:
        person_dict = person_data.to_dict()
    else:
        person_dict = person_data
    
    # Получаем ФИО
    fio = get_person_fio(person_dict)
    
    # Расчет риска
    if MODULES_AVAILABLE:
        assessment = quick_risk_assessment(person_dict)
        risk_score = assessment['risk_score']
        risk_level = assessment['risk_level']
        recommendation = assessment['recommendation']
        components = assessment['components']
    else:
        # Демо расчет
        risk_score = person_dict.get('risk_total_risk_score', 5.0)
        risk_level = "🔴 Критический" if risk_score >= 7 else "🟡 Высокий" if risk_score >= 5 else "🟠 Средний" if risk_score >= 3 else "🟢 Низкий"
        recommendation = "Требует внимания" if risk_score >= 5 else "Стандартный контроль"
        components = None
    
    # Определяем цвет риска
    risk_colors = {
        "🔴 Критический": "#dc3545",
        "🟡 Высокий": "#ffc107",
        "🟠 Средний": "#fd7e14",
        "🟢 Низкий": "#28a745"
    }
    risk_color = risk_colors.get(risk_level, "#6c757d")
    
    # Шапка карточки
    st.markdown(f"""
    <div class="person-card" style="border-left: 5px solid {risk_color};">
        <h2>👤 {fio}</h2>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <p><strong>ИИН:</strong> {person_dict.get('ИИН', 'Не указан')}</p>
                <p><strong>Возраст:</strong> {person_dict.get('current_age', 'Н/Д')} лет | 
                   <strong>Пол:</strong> {person_dict.get('gender', 'Н/Д')}</p>
            </div>
            <div style="text-align: right;">
                <h3 style="color: {risk_color};">РИСК-БАЛЛ: {risk_score:.1f}/10</h3>
                <span class="risk-badge risk-{risk_level.split()[1].lower()}">{risk_level}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Основная информация в колонках
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Статистика дел")
        st.metric("Всего дел", f"{person_dict.get('total_cases', 0)}")
        st.metric("Уголовных дел", f"{person_dict.get('criminal_count', 0)}")
        st.metric("Административных", f"{person_dict.get('admin_count', 0)}")
        
        if person_dict.get('recidivism_rate', 0) > 0:
            st.metric("Частота рецидива", f"{person_dict.get('recidivism_rate', 0):.2f} дел/год")
    
    with col2:
        st.markdown("### 🔄 Паттерн поведения")
        pattern = person_dict.get('pattern_type', 'unknown')
        pattern_translation = {
            'mixed_unstable': 'Нестабильное поведение',
            'chronic_criminal': 'Хронический преступник',
            'escalating': 'Эскалация (админ→уголовка)',
            'deescalating': 'Деэскалация',
            'single': 'Единичные случаи',
            'unknown': 'Неизвестно'
        }
        st.write(f"**Тип:** {pattern_translation.get(pattern, pattern)}")
        
        days_since = person_dict.get('days_since_last', 365)
        st.write(f"**Последнее нарушение:** {days_since} дней назад")
        
        if 'last_violation_type' in person_dict:
            st.write(f"**Тип нарушения:** {person_dict['last_violation_type']}")
        
        age_first = person_dict.get('age_at_first_violation', 0)
        if age_first > 0:
            st.write(f"**Возраст первого нарушения:** {age_first} лет")
    
    with col3:
        st.markdown("### 🏠 Социальные факторы")
        
        has_property = person_dict.get('has_property', 0)
        property_status = "✅ Есть" if has_property else "❌ Нет"
        st.write(f"**Имущество:** {property_status}")
        
        has_job = person_dict.get('has_job', 0)
        job_status = "✅ Есть" if has_job else "❌ Нет"
        st.write(f"**Работа:** {job_status}")
        
        is_active = person_dict.get('is_active', 0)
        active_status = "🔴 Активный" if is_active else "🟢 Неактивный"
        st.write(f"**Статус активности:** {active_status}")
        
        has_escalation = person_dict.get('has_escalation', 0)
        escalation_status = "⚠️ Есть" if has_escalation else "✅ Нет"
        st.write(f"**История эскалации:** {escalation_status}")
    
    # Компоненты риска
    if components:
        st.markdown("---")
        st.subheader("🎯 Компоненты риск-балла")
        
        comp_cols = st.columns(6)
        comp_names = {
            'pattern': 'Паттерн',
            'history': 'История',
            'time': 'Время',
            'age': 'Возраст',
            'social': 'Социальные',
            'escalation': 'Эскалация'
        }
        
        for i, (key, value) in enumerate(components.items()):
            with comp_cols[i % 6]:
                st.metric(comp_names.get(key, key), f"{value:.1f}")
    
    # Прогноз
    st.markdown("---")
    st.subheader("🔮 Прогноз риска")
    
    if MODULES_AVAILABLE:
        # Используем реальный прогноз
        forecaster = CrimeForecaster()
        forecasts = forecaster.forecast_crime_timeline(person_dict)
        
        # Визуализация временной шкалы
        if MODULES_AVAILABLE:
            try:
                visualizer = TimelineVisualizer()
                
                # Выбираем топ-4 наиболее вероятных преступления
                top_crimes = list(forecasts.keys())[:4]
                
                timeline_fig = visualizer.create_risk_timeline(forecasts, top_crimes, 270)
                st.plotly_chart(timeline_fig, use_container_width=True)
            except Exception as e:
                st.error(f"⚠️ Не удалось создать график временной шкалы: {str(e)}")
                st.info("📊 Временной график временно недоступен. Остальные данные отображаются корректно.")
        else:
            st.info("📊 График временной шкалы недоступен в демо-режиме.")
        
        # Таблица прогнозов
        st.markdown("#### 📋 Детальные прогнозы")
        
        forecast_data = []
        for crime_type, forecast in list(forecasts.items())[:6]:
            forecast_data.append({
                'Тип преступления': crime_type,
                'Прогноз (дни)': forecast['days'],
                'Дата': forecast['date'].strftime('%d.%m.%Y'),
                'Вероятность': f"{forecast['probability']:.1f}%",
                'Период риска': f"{forecast['ci_lower']}-{forecast['ci_upper']} дней",
                'Уровень': forecast['risk_level']
            })
        
        forecast_df = pd.DataFrame(forecast_data)
        st.dataframe(forecast_df, use_container_width=True, hide_index=True)
        
        # План вмешательства
        planner = InterventionPlanner()
        plan = planner.create_intervention_plan(person_dict, forecasts)
        
        st.markdown("---")
        st.subheader("💡 План превентивных мероприятий")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Приоритет:** {plan['priority_level']}")
            st.markdown(f"**Мониторинг:** {plan['monitoring_frequency']}")
            
            if plan['responsible_agencies']:
                st.markdown("**Ответственные службы:**")
                for agency in plan['responsible_agencies']:
                    st.write(f"• {agency}")
        
        with col2:
            if plan['programs']:
                st.markdown("**Рекомендуемые программы:**")
                for program in plan['programs'][:5]:
                    st.write(f"• {program}")
        
        # Диаграмма Ганта для плана
        gantt_fig = planner.create_intervention_gantt(plan)
        if gantt_fig:
            st.plotly_chart(gantt_fig, use_container_width=True)
        
    else:
        # Демо прогноз с корректной структурой данных
        st.info("🔮 Для полного прогноза требуется подключение модулей аналитики")
        
        # Создаем демо прогнозы с правильной структурой данных
        from datetime import datetime, timedelta
        
        demo_forecasts = {
            'Кража': {
                'crime_type': 'Кража',
                'days': 120,
                'date': datetime.now() + timedelta(days=120),
                'probability': 75.0,
                'ci_lower': 90,
                'ci_upper': 150,
                'confidence': 0.8,
                'risk_level': 'Высокий'
            },
            'Хулиганство': {
                'crime_type': 'Хулиганство',
                'days': 85,
                'date': datetime.now() + timedelta(days=85),
                'probability': 60.0,
                'ci_lower': 65,
                'ci_upper': 110,
                'confidence': 0.7,
                'risk_level': 'Средний'
            },
            'Побои': {
                'crime_type': 'Побои',
                'days': 200,
                'date': datetime.now() + timedelta(days=200),
                'probability': 45.0,
                'ci_lower': 150,
                'ci_upper': 250,
                'confidence': 0.6,
                'risk_level': 'Средний'
            }
        }
        
        # Простая визуализация
        likely_crime = "Кража"
        forecast_days = 120
        probability = 75
        
        st.markdown(f"""
        <div class="info-item">
            <h4>Наиболее вероятное преступление: {likely_crime}</h4>
            <p>Прогноз: через <strong>{forecast_days} дней</strong> (вероятность {probability}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Попытка создать график с демо данными
        if MODULES_AVAILABLE:
            try:
                visualizer = TimelineVisualizer()
                top_crimes = list(demo_forecasts.keys())
                timeline_fig = visualizer.create_risk_timeline(demo_forecasts, top_crimes, 270)
                st.plotly_chart(timeline_fig, use_container_width=True)
            except Exception as e:
                st.warning(f"График временной шкалы недоступен: {str(e)}")
        
        # Таблица демо прогнозов
        st.markdown("#### 📋 Демо прогнозы")
        
        forecast_data = []
        for crime_type, forecast in demo_forecasts.items():
            forecast_data.append({
                'Тип преступления': crime_type,
                'Дней до события': forecast['days'],
                'Вероятность': f"{forecast['probability']:.0f}%",
                'Уровень риска': forecast['risk_level']
            })
        
        df_forecasts = pd.DataFrame(forecast_data)
        st.dataframe(df_forecasts, use_container_width=True)
    
    # Рекомендации
    st.markdown("---")
    st.subheader("📝 Рекомендации по работе")
    
    recommendations = []
    
    # Основная рекомендация
    st.markdown(f"""
    <div class="recommendation-card">
        <h4>🎯 Основная рекомендация</h4>
        <p><strong>{recommendation}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Специфические рекомендации
    if risk_score >= 7:
        recommendations.extend([
            "🚨 Назначить персонального куратора немедленно",
            "📅 Ежедневные контакты и мониторинг",
            "🏥 Обязательная психологическая диагностика"
        ])
    elif risk_score >= 5:
        recommendations.extend([
            "⚠️ Встречи с куратором 2-3 раза в неделю",
            "📊 Еженедельные отчеты о прогрессе",
            "🎯 Включение в программы превенции"
        ])
    
    if person_dict.get('has_job', 0) == 0:
        recommendations.append("💼 Приоритетное трудоустройство через службу занятости")
    
    if person_dict.get('has_property', 0) == 0:
        recommendations.append("🏠 Оценка жилищных условий и социальная поддержка")
    
    if pattern == 'mixed_unstable':
        recommendations.append("🧠 Программа психологической стабилизации")
    elif pattern == 'chronic_criminal':
        recommendations.append("🔒 Усиленный контроль и мониторинг")
    elif pattern == 'escalating':
        recommendations.append("⚡ Срочное вмешательство для предотвращения эскалации")
    
    if person_dict.get('current_age', 35) < 25:
        recommendations.append("👨‍🎓 Образовательные и молодежные программы")
    
    # Отображаем рекомендации
    for rec in recommendations:
        st.markdown(f"- {rec}")

# Основной интерфейс поиска
st.markdown("---")

# Поисковая строка
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    search_input = st.text_input(
        "Введите ИИН для поиска:",
        placeholder="Например: 123456789012",
        help="Формат: 12 цифр, можно с дефисами или пробелами"
    )

with col2:
    search_button = st.button("🔍 Найти", type="primary", use_container_width=True)

with col3:
    if st.button("🎲 Случайный", use_container_width=True):
        # Генерируем случайный ИИН для демо
        random_iin = f"{np.random.randint(100000, 999999)}{np.random.randint(100000, 999999)}"
        search_input = random_iin
        st.rerun()

# Обработка поиска
if search_input or search_button:
    with st.spinner('Поиск в базе данных...'):
        
        if MODULES_AVAILABLE:
            # Используем реальный поиск
            is_valid, result = validate_iin(search_input)
            
            if is_valid:
                person = search_person_by_iin(result)
                
                if person is not None:
                    st.success(f"✅ Найден человек по ИИН: {result}")
                    display_person_card(person)
                    
                    # Экспорт карточки
                    st.markdown("---")
                    
                    # Создаем полный отчет
                    report = generate_risk_report(person.to_dict())
                    
                    # Кнопки экспорта
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # CSV экспорт
                        person_df = pd.DataFrame([person])
                        csv = person_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Скачать данные (CSV)",
                            data=csv,
                            file_name=f'person_{result}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                            mime='text/csv'
                        )
                    
                    with col2:
                        # JSON экспорт с прогнозами
                        import json
                        report_json = json.dumps(report, default=str, ensure_ascii=False, indent=2)
                        st.download_button(
                            label="📊 Скачать отчет (JSON)",
                            data=report_json,
                            file_name=f'report_{result}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                            mime='application/json'
                        )
                    
                    with col3:
                        # Текстовый отчет
                        text_report = format_risk_summary(report)
                        st.download_button(
                            label="📄 Скачать резюме (TXT)",
                            data=text_report,
                            file_name=f'summary_{result}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
                            mime='text/plain'
                        )
                else:
                    st.error(f"❌ ИИН {result} не найден в базе данных")
                    st.info("💡 Попробуйте другой ИИН или используйте примеры ниже")
            else:
                st.error(f"❌ {result}")
        
        else:
            # Демо режим
            st.info("ℹ️ Работаем в демо-режиме")
            
            # Создаем демо данные
            demo_df = create_demo_data()
            
            # Преобразуем ИИН в строку для поиска
            demo_df['ИИН'] = demo_df['ИИН'].astype(str)
            
            # Ищем по последним цифрам ИИН
            clean_iin = re.sub(r'[^\d]', '', search_input)
            
            if len(clean_iin) >= 4:
                # Ищем совпадение по последним 4 цифрам
                last_4 = clean_iin[-4:]
                matches = demo_df[demo_df['ИИН'].str.endswith(last_4)]
                
                if not matches.empty:
                    person = matches.iloc[0]
                    st.success(f"✅ Найден человек в демо-базе")
                    display_person_card(person)
                else:
                    # Показываем случайного человека
                    person = demo_df.sample(1).iloc[0]
                    st.warning(f"⚠️ ИИН не найден, показываем случайную запись для демонстрации")
                    display_person_card(person)
            else:
                st.error("❌ Введите корректный ИИН")

# Примеры для поиска
st.markdown("---")
st.subheader("💡 Примеры для поиска")

if MODULES_AVAILABLE:
    # Загружаем реальные примеры
    risk_df = get_risk_data()
    
    if risk_df is not None and not risk_df.empty and 'ИИН' in risk_df.columns:
        # Показываем примеры с разными уровнями риска
        examples = []
        
        # Критический риск
        critical = risk_df[risk_df['risk_total_risk_score'] >= 7].head(2)
        for _, row in critical.iterrows():
            examples.append((row['ИИН'], "🔴 Критический риск"))
        
        # Высокий риск
        high = risk_df[(risk_df['risk_total_risk_score'] >= 5) & (risk_df['risk_total_risk_score'] < 7)].head(2)
        for _, row in high.iterrows():
            examples.append((row['ИИН'], "🟡 Высокий риск"))
        
        # Средний риск
        medium = risk_df[(risk_df['risk_total_risk_score'] >= 3) & (risk_df['risk_total_risk_score'] < 5)].head(2)
        for _, row in medium.iterrows():
            examples.append((row['ИИН'], "🟠 Средний риск"))
        
        # Низкий риск
        low = risk_df[risk_df['risk_total_risk_score'] < 3].head(2)
        for _, row in low.iterrows():
            examples.append((row['ИИН'], "🟢 Низкий риск"))
        
        # Отображаем примеры
        cols = st.columns(4)
        for i, (iin, risk_text) in enumerate(examples[:8]):
            with cols[i % 4]:
                iin_str = str(iin)  # Преобразуем в строку
                if st.button(f"{iin_str[-4:]}...\n{risk_text}", key=f"example_{i}", use_container_width=True):
                    search_input = iin_str
                    st.rerun()
    else:
        # Демо примеры
        st.info("Примеры ИИН для демо-режима:")
        demo_df = create_demo_data()
        
        cols = st.columns(5)
        for i in range(10):
            with cols[i % 5]:
                demo_iin = demo_df.iloc[i]['ИИН']
                demo_iin_str = str(demo_iin)  # Преобразуем в строку
                if st.button(f"...{demo_iin_str[-4:]}", key=f"demo_{i}"):
                    search_input = demo_iin_str
                    st.rerun()

# Справка
with st.expander("ℹ️ Справка по использованию"):
    st.markdown("""
    ### 🔍 Как пользоваться поиском:
    - Введите полный 12-значный ИИН
    - Можно использовать дефисы и пробелы (они будут автоматически удалены)
    - Система также ищет по последним 4 цифрам ИИН
    
    ### 📊 Что показывает результат:
    - **Риск-балл** - комплексная оценка от 0 до 10
    - **Компоненты риска** - детализация по 6 факторам
    - **Временной прогноз** - вероятные сроки до преступления
    - **План вмешательства** - конкретные программы и сроки
    
    ### 🎯 Интерпретация риск-балла:
    - 🔴 **7-10 баллов**: Критический риск - немедленное вмешательство
    - 🟡 **5-6 баллов**: Высокий риск - усиленный контроль
    - 🟠 **3-4 балла**: Средний риск - стандартный мониторинг
    - 🟢 **0-2 балла**: Низкий риск - минимальный контроль
    
    ### 📈 Компоненты риска:
    - **Паттерн** - тип криминального поведения (25% веса)
    - **История** - количество и тяжесть нарушений (20%)
    - **Время** - давность последнего нарушения (15%)
    - **Возраст** - текущий возраст и возраст дебюта (10%)
    - **Социальные** - работа, имущество, семья (15%)
    - **Эскалация** - тенденция к утяжелению (15%)
    
    ### 💾 Экспорт данных:
    - **CSV** - табличные данные о человеке
    - **JSON** - полный отчет с прогнозами
    - **TXT** - текстовое резюме для документов
    """)

# Статистика использования в боковой панели
with st.sidebar:
    st.markdown("### 📊 Статистика поиска")
    
    # Счетчики (в реальном приложении брать из БД)
    st.metric("Поисков сегодня", "127")
    st.metric("Найдено лиц", "89")
    st.metric("Критических рисков", "12")
    
    st.markdown("---")
    
    # Быстрые фильтры
    st.markdown("### 🎯 Быстрый поиск по категориям")
    
    if st.button("🔴 Критические риски", use_container_width=True):
        st.info("Функция в разработке")
    
    if st.button("🟡 Требуют внимания", use_container_width=True):
        st.info("Функция в разработке")
    
    if st.button("📅 Активные за месяц", use_container_width=True):
        st.info("Функция в разработке")
    
    st.markdown("---")
    
    # Настройки
    st.markdown("### ⚙️ Настройки поиска")
    
    show_components = st.checkbox("Показывать компоненты риска", value=True)
    show_timeline = st.checkbox("Показывать временную шкалу", value=True)
    show_plan = st.checkbox("Показывать план вмешательства", value=True)