"""
🚨 Система раннего предупреждения преступлений
Главная страница приложения
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импорт из наших модулей
try:
    from utils.data_loader import (
        load_all_data, 
        get_crime_statistics, 
        calculate_statistics_summary,
        get_risk_data,
        get_pattern_distribution
    )
    from utils.risk_calculator import RiskCalculator
    from utils.forecasting import TimelineVisualizer
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    st.warning("⚠️ Модули utils не найдены. Работаем в демо-режиме.")

# Настройка страницы
st.set_page_config(
    page_title="Система раннего предупреждения преступлений",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные стили
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #e74c3c, #c0392b);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border-left: 5px solid #e74c3c;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .big-number {
        font-size: 3rem;
        font-weight: bold;
        color: #e74c3c;
        margin: 0;
    }
    .metric-label {
        font-size: 1.1rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: bold;
    }
    .status-critical { background-color: #f8d7da; color: #721c24; }
    .status-warning { background-color: #fff3cd; color: #856404; }
    .status-success { background-color: #d4edda; color: #155724; }
    .sidebar .sidebar-content { padding-top: 2rem; }
    .risk-indicator {
        display: inline-block;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    .risk-critical { background-color: #e74c3c; }
    .risk-high { background-color: #f39c12; }
    .risk-medium { background-color: #fd7e14; }
    .risk-low { background-color: #27ae60; }
</style>
""", unsafe_allow_html=True)

# Функция для проверки наличия файлов данных
@st.cache_data
def check_data_files():
    """Проверяем наличие необходимых файлов данных"""
    data_dir = "data"
    required_files = [
        "RISK_ANALYSIS_RESULTS.xlsx",
        "ML_DATASET_COMPLETE.xlsx", 
        "crime_analysis_results.xlsx",
        "serious_crimes_analysis.xlsx",
        "risk_escalation_matrix.xlsx"
    ]
    
    # Создаем папку data если её нет
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    file_status = {}
    for file in required_files:
        file_path = os.path.join(data_dir, file)
        file_status[file] = os.path.exists(file_path)
    
    return file_status

# Функция для загрузки базовых данных
@st.cache_data
def load_basic_stats():
    """Загружаем базовую статистику для главной страницы"""
    if MODULES_AVAILABLE:
        try:
            # Пытаемся загрузить реальные данные
            stats = get_crime_statistics()
            return stats
        except Exception as e:
            st.error(f"Ошибка загрузки данных: {e}")
    
    # Возвращаем данные из исследования
    return {
        "total_analyzed": 146570,
        "recidivists": 12333,
        "preventable_percent": 97.0,
        "avg_time_to_crime": 143,
        "unstable_pattern_percent": 72.7,
        "high_risk_count": 1856,
        "admin_to_theft": 6465,
        "crime_windows": {
            'Мошенничество': {'days': 109, 'preventable': 82.3},
            'Кража': {'days': 146, 'preventable': 87.3},
            'Убийство': {'days': 143, 'preventable': 97.0},
            'Вымогательство': {'days': 144, 'preventable': 100.7},
            'Грабеж': {'days': 148, 'preventable': 60.2},
            'Разбой': {'days': 150, 'preventable': 20.2},
            'Изнасилование': {'days': 157, 'preventable': 65.6}
        }
    }

# Главный заголовок
st.markdown("""
<div class="main-header">
    <h1>🚨 СИСТЕМА РАННЕГО ПРЕДУПРЕЖДЕНИЯ ПРЕСТУПЛЕНИЙ</h1>
    <h3>Анализ 146,570 правонарушений | 12,333 рецидивистов | 97% преступлений предотвратимы</h3>
</div>
""", unsafe_allow_html=True)

# Проверяем статус файлов данных
file_status = check_data_files()

# Если есть модули, пытаемся загрузить реальные данные
real_data_loaded = False
if MODULES_AVAILABLE:
    try:
        all_data = load_all_data()
        if any(v is not None for v in all_data.values()):
            real_data_loaded = True
            st.success("✅ Данные успешно загружены из файлов")
    except Exception as e:
        st.warning(f"⚠️ Не удалось загрузить все данные: {e}")

# Основные метрики
stats = load_basic_stats()

# Если загружены реальные данные, обновляем статистику
if real_data_loaded and MODULES_AVAILABLE:
    try:
        summary = calculate_statistics_summary()
        # Обновляем статистику реальными данными
        if summary['total_people'] > 0:
            stats['recidivists'] = summary['total_people']
            stats['high_risk_count'] = summary['critical_risk'] + summary['high_risk']
    except:
        pass

st.subheader("📊 Ключевые показатели исследования")

# Основные метрики в 4 колонки
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="big-number">{stats.get('preventable_percent', 97):.0f}%</div>
        <div class="metric-label">тяжких преступлений<br>имеют предшественников</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="big-number">{stats.get('avg_time_to_crime', 143)}</div>
        <div class="metric-label">дня в среднем<br>до убийства</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="big-number">{stats.get('unstable_pattern_percent', 72.7):.1f}%</div>
        <div class="metric-label">нестабильный<br>паттерн поведения</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="big-number">{stats.get('admin_to_theft', 6465):,}</div>
        <div class="metric-label">переходов<br>админ → кража</div>
    </div>
    """, unsafe_allow_html=True)

# Статус данных
st.markdown("---")
st.subheader("📁 Статус системы")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Файлы данных:")
    files_ready = sum(file_status.values())
    total_files = len(file_status)
    
    # Прогресс бар
    progress = files_ready / total_files if total_files > 0 else 0
    st.progress(progress)
    st.write(f"Загружено {files_ready} из {total_files} файлов")
    
    # Детали по файлам
    with st.expander("Подробности о файлах"):
        for file, exists in file_status.items():
            if exists:
                st.success(f"✅ {file}")
            else:
                st.error(f"❌ {file}")

with col2:
    st.markdown("#### Статус системы:")
    
    if files_ready == total_files and real_data_loaded:
        st.markdown('<div class="status-box status-success">🟢 Система полностью готова к работе</div>', 
                   unsafe_allow_html=True)
    elif files_ready > 0 or real_data_loaded:
        st.markdown('<div class="status-box status-warning">🟡 Система работает частично</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box status-critical">🔴 Работа в демо-режиме</div>', 
                   unsafe_allow_html=True)
    
    # Дополнительная информация
    st.write(f"**Режим работы:** {'Реальные данные' if real_data_loaded else 'Демо-данные'}")
    st.write(f"**Модули аналитики:** {'✅ Подключены' if MODULES_AVAILABLE else '❌ Не найдены'}")

# Интерактивные графики
st.markdown("---")
st.subheader("📈 Аналитика в реальном времени")

col1, col2 = st.columns(2)

with col1:
    # График временных окон
    st.markdown("#### ⏰ Временные окна до преступлений")
    
    crime_windows = stats.get('crime_windows', {})
    if crime_windows:
        crimes_df = pd.DataFrame([
            {'Преступление': crime, 'Дни': data['days'], 'Предотвратимость': data['preventable']}
            for crime, data in crime_windows.items()
        ])
        crimes_df = crimes_df.sort_values('Дни')
        
        fig = px.bar(crimes_df, x='Дни', y='Преступление', orientation='h',
                    color='Предотвратимость',
                    color_continuous_scale='RdYlGn',
                    title='Среднее время от админ нарушения до преступления',
                    labels={'Предотвратимость': '% предотвратимых'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Распределение паттернов
    st.markdown("#### 🔄 Паттерны поведения")
    
    if real_data_loaded and MODULES_AVAILABLE:
        try:
            pattern_df = get_pattern_distribution()
            fig = px.pie(pattern_df, values='percent', names='pattern',
                        title='Распределение паттернов криминального поведения',
                        color_discrete_sequence=px.colors.sequential.Reds)
        except:
            # Демо данные
            pattern_data = pd.DataFrame({
                'pattern': ['Нестабильное поведение', 'Хронические преступники', 
                           'Эскалация', 'Деэскалация', 'Единичные'],
                'percent': [72.7, 13.6, 7.0, 5.7, 1.0]
            })
            fig = px.pie(pattern_data, values='percent', names='pattern',
                        title='Распределение паттернов криминального поведения',
                        color_discrete_sequence=px.colors.sequential.Reds)
    else:
        # Демо данные
        pattern_data = pd.DataFrame({
            'pattern': ['Нестабильное поведение', 'Хронические преступники', 
                       'Эскалация', 'Деэскалация', 'Единичные'],
            'percent': [72.7, 13.6, 7.0, 5.7, 1.0]
        })
        fig = px.pie(pattern_data, values='percent', names='pattern',
                    title='Распределение паттернов криминального поведения',
                    color_discrete_sequence=px.colors.sequential.Reds)
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Информация о навигации
st.markdown("---")
st.subheader("🧭 Функциональные модули системы")

# Создаем карточки для каждой страницы
pages_info = [
    {
        "icon": "🗺️",
        "title": "Карта временных окон",
        "description": "Интерактивная визуализация временных промежутков до различных типов преступлений",
        "status": "active"
    },
    {
        "icon": "🚦",
        "title": "Статус регионов",
        "description": "Светофор статусов по категориям риска и региональная аналитика",
        "status": "active"
    },
    {
        "icon": "👥",
        "title": "Списки лиц риска",
        "description": "Категоризированные списки лиц с различными уровнями риска рецидива",
        "status": "active"
    },
    {
        "icon": "🔍",
        "title": "Поиск по ИИН",
        "description": "Мгновенная оценка риска и детальная информация по конкретному лицу",
        "status": "active"
    },
    {
        "icon": "⏰",
        "title": "Временные прогнозы",
        "description": "Персональные прогнозы временных окон до возможных преступлений",
        "status": "active"
    }
]

# Отображаем карточки в две колонки
for i in range(0, len(pages_info), 2):
    col1, col2 = st.columns(2)
    
    for j, col in enumerate([col1, col2]):
        if i + j < len(pages_info):
            page = pages_info[i + j]
            with col:
                st.markdown(f"""
                <div style="
                    background-color: #f8f9fa;
                    padding: 1.5rem;
                    border-radius: 10px;
                    border-left: 5px solid {'#27ae60' if page['status'] == 'active' else '#e74c3c'};
                    margin: 0.5rem 0;
                    height: 120px;
                ">
                    <h4>{page['icon']} {page['title']}</h4>
                    <p style="color: #666; margin: 0;">{page['description']}</p>
                </div>
                """, unsafe_allow_html=True)

# Боковая панель с общей информацией
with st.sidebar:
    st.markdown("### 📊 Общая статистика")
    
    if stats:
        st.metric("Всего проанализировано", f"{stats.get('total_analyzed', 146570):,}")
        st.metric("Рецидивистов", f"{stats.get('recidivists', 12333):,}")
        st.metric("Лиц высокого риска", f"{stats.get('high_risk_count', 1856):,}")
        
        # Индикаторы риска
        st.markdown("---")
        st.markdown("### 🎯 Уровни риска")
        
        risk_levels = [
            ("🔴 Критический", "7-10 баллов", "#e74c3c"),
            ("🟡 Высокий", "5-6 баллов", "#f39c12"),
            ("🟠 Средний", "3-4 балла", "#fd7e14"),
            ("🟢 Низкий", "0-2 балла", "#27ae60")
        ]
        
        for level, range_text, color in risk_levels:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <div class="risk-indicator" style="background-color: {color};"></div>
                <span><b>{level}</b> ({range_text})</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎯 Ключевые выводы")
    st.markdown("""
    - **97%** тяжких преступлений предотвратимы
    - **143 дня** - среднее время до убийства
    - **3-5 месяцев** - окно для вмешательства
    - **72.7%** имеют нестабильный паттерн
    - **ROI 50x** - возврат инвестиций
    """)
    
    st.markdown("---")
    st.markdown("### 📁 Требуемые файлы")
    st.markdown("""
    Для полной работы системы разместите в папке `data/`:
    - RISK_ANALYSIS_RESULTS.xlsx
    - ML_DATASET_COMPLETE.xlsx
    - crime_analysis_results.xlsx
    - serious_crimes_analysis.xlsx
    - risk_escalation_matrix.xlsx
    """)
    
    # Кнопка обновления данных
    if st.button("🔄 Обновить данные", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### ℹ️ Информация")
    st.markdown("**Версия:** 2.0")
    st.markdown("**Последнее обновление:** " + datetime.now().strftime("%d.%m.%Y"))
    
    # Экспорт статистики
    if st.button("📥 Экспорт статистики", use_container_width=True):
        stats_df = pd.DataFrame([{
            'Показатель': 'Всего проанализировано',
            'Значение': stats.get('total_analyzed', 146570)
        }, {
            'Показатель': 'Рецидивистов',
            'Значение': stats.get('recidivists', 12333)
        }, {
            'Показатель': 'Процент предотвратимых',
            'Значение': f"{stats.get('preventable_percent', 97)}%"
        }, {
            'Показатель': 'Средний паттерн нестабильности',
            'Значение': f"{stats.get('unstable_pattern_percent', 72.7)}%"
        }])
        
        csv = stats_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Скачать CSV",
            data=csv,
            file_name=f'statistics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv'
        )

# Футер
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <h4>🚨 Система раннего предупреждения преступлений</h4>
    <p>Основано на анализе реальных данных о рецидивизме</p>
    <p><strong>Преступления можно предотвратить!</strong></p>
    <p style='font-size: 0.9em; margin-top: 1rem;'>
        Разработано для КПСиСУ Республики Казахстан<br>
        © 2025 Все права защищены
    </p>
</div>
""", unsafe_allow_html=True)