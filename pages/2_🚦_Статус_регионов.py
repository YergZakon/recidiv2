"""
🚦 Статус регионов
Светофор статусов по категориям риска и региональная аналитика
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# Настройка страницы
st.set_page_config(
    page_title="Статус регионов",
    page_icon="🚦",
    layout="wide"
)

st.title("🚦 Статус категорий риска")
st.markdown("### Светофор статусов и аналитика по уровням риска рецидива")

# Функция загрузки данных о рисках
@st.cache_data
def load_risk_status_data():
    """Загружаем данные о статусе рисков"""
    
    # Проверяем наличие файла с результатами анализа рисков
    risk_file = "data/RISK_ANALYSIS_RESULTS.xlsx"
    
    if os.path.exists(risk_file):
        try:
            df = pd.read_excel(risk_file)
            st.success("✅ Данные загружены из RISK_ANALYSIS_RESULTS.xlsx")
            return df
        except Exception as e:
            st.warning(f"⚠️ Ошибка загрузки данных: {e}")
    
    # Если файл не найден, создаем демо-данные на основе исследования
    np.random.seed(42)
    n_people = 12333  # Количество рецидивистов из исследования
    
    # Создаем демо-данные на основе реальных паттернов
    demo_data = {
        'ИИН': [f"***-***-{str(i).zfill(4)}" for i in range(1, n_people + 1)],
        'current_age': np.random.normal(35, 12, n_people).clip(18, 70).astype(int),
        'pattern_type': np.random.choice([
            'mixed_unstable', 'chronic_criminal', 'escalating', 'deescalating', 'single'
        ], n_people, p=[0.727, 0.136, 0.07, 0.057, 0.01]),
        'total_cases': np.random.poisson(4, n_people) + 1,
        'criminal_count': np.random.poisson(1.5, n_people),
        'admin_count': np.random.poisson(2.5, n_people),
        'risk_total_risk_score': np.random.beta(2, 5, n_people) * 10
    }
    
    df = pd.DataFrame(demo_data)
    st.info("ℹ️ Используются демо-данные на основе исследования")
    return df

# Функция для определения категории риска
def get_risk_category(risk_score):
    """Определяем категорию риска по баллу"""
    if risk_score >= 7:
        return "Критический"
    elif risk_score >= 5:
        return "Высокий" 
    elif risk_score >= 3:
        return "Средний"
    else:
        return "Низкий"

# Функция для получения эмодзи категории риска
def get_risk_emoji(category):
    """Получаем эмодзи для категории риска"""
    emoji_map = {
        "Критический": "🔴",
        "Высокий": "🟡",
        "Средний": "🟠",
        "Низкий": "🟢"
    }
    return emoji_map.get(category, "")

# Функция для получения полного названия с эмодзи
def get_risk_display_name(category):
    """Получаем полное название категории с эмодзи для отображения"""
    emoji = get_risk_emoji(category)
    return f"{emoji} {category}"

# Функция для определения статуса категории
def get_category_status(percentage):
    """Определяем статус категории по проценту людей в ней"""
    if percentage > 30:
        return "🔴 Критично"
    elif percentage > 15:
        return "🟡 Внимание"
    else:
        return "🟢 Норма"

# Загружаем данные
risk_df = load_risk_status_data()

if risk_df is not None and len(risk_df) > 0:
    
    # Добавляем категории риска
    if 'risk_total_risk_score' in risk_df.columns:
        risk_df['risk_category'] = risk_df['risk_total_risk_score'].apply(get_risk_category)
    else:
        # Если нет риск-балла, создаем случайные категории
        risk_df['risk_category'] = np.random.choice([
            "Критический", "Высокий", "Средний", "Низкий"
        ], len(risk_df), p=[0.15, 0.25, 0.35, 0.25])
    
    # Светофор статусов - основная панель
    st.subheader("🚦 Светофор статусов по категориям риска")
    
    # Подсчитываем распределение по категориям
    category_stats = risk_df['risk_category'].value_counts()
    total_people = len(risk_df)
    
    # Создаем 4 колонки для категорий
    col1, col2, col3, col4 = st.columns(4)
    
    # Критический уровень
    with col1:
        critical_count = category_stats.get("Критический", 0)
        critical_percent = (critical_count / total_people) * 100
        status = get_category_status(critical_percent)
        
        st.markdown(f"""
        <div style="
            background-color: #f8d7da; 
            border: 3px solid #dc3545; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <h3>🔴 КРИТИЧЕСКИЙ</h3>
            <h2 style="color: #dc3545; margin: 10px 0;">{critical_count:,}</h2>
            <p><strong>{critical_percent:.1f}%</strong> от общего числа</p>
            <p>Риск-балл: 7-10</p>
            <p><strong>{status}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Высокий уровень
    with col2:
        high_count = category_stats.get("Высокий", 0)
        high_percent = (high_count / total_people) * 100
        status = get_category_status(high_percent)
        
        st.markdown(f"""
        <div style="
            background-color: #fff3cd; 
            border: 3px solid #ffc107; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <h3>🟡 ВЫСОКИЙ</h3>
            <h2 style="color: #856404; margin: 10px 0;">{high_count:,}</h2>
            <p><strong>{high_percent:.1f}%</strong> от общего числа</p>
            <p>Риск-балл: 5-6</p>
            <p><strong>{status}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Средний уровень
    with col3:
        medium_count = category_stats.get("Средний", 0)
        medium_percent = (medium_count / total_people) * 100
        status = get_category_status(medium_percent)
        
        st.markdown(f"""
        <div style="
            background-color: #e2e3e5; 
            border: 3px solid #fd7e14; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <h3>🟠 СРЕДНИЙ</h3>
            <h2 style="color: #fd7e14; margin: 10px 0;">{medium_count:,}</h2>
            <p><strong>{medium_percent:.1f}%</strong> от общего числа</p>
            <p>Риск-балл: 3-4</p>
            <p><strong>{status}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Низкий уровень
    with col4:
        low_count = category_stats.get("Низкий", 0)
        low_percent = (low_count / total_people) * 100
        status = "🟢 Хорошо"  # Для низкого риска всегда хорошо
        
        st.markdown(f"""
        <div style="
            background-color: #d4edda; 
            border: 3px solid #28a745; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <h3>🟢 НИЗКИЙ</h3>
            <h2 style="color: #28a745; margin: 10px 0;">{low_count:,}</h2>
            <p><strong>{low_percent:.1f}%</strong> от общего числа</p>
            <p>Риск-балл: 0-2</p>
            <p><strong>{status}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Общая сводка
    st.markdown("---")
    st.subheader("📊 Общая аналитика")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Круговая диаграмма распределения
        fig_pie = px.pie(
            values=category_stats.values,
            names=category_stats.index,
            title="Распределение по категориям риска",
            color_discrete_map={
                "Критический": "#dc3545",
                "Высокий": "#ffc107", 
                "Средний": "#fd7e14",
                "Низкий": "#28a745"
            }
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Столбчатая диаграмма для лучшего сравнения
        fig_bar = px.bar(
            x=category_stats.index,
            y=category_stats.values,
            title="Количество людей по категориям",
            color=category_stats.index,
            color_discrete_map={
                "Критический": "#dc3545",
                "Высокий": "#ffc107", 
                "Средний": "#fd7e14",
                "Низкий": "#28a745"
            }
        )
        fig_bar.update_layout(
            height=400,
            xaxis_title="Категория риска",
            yaxis_title="Количество людей",
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Анализ паттернов поведения
    if 'pattern_type' in risk_df.columns:
        st.subheader("🔄 Анализ паттернов поведения")
        
        pattern_stats = risk_df['pattern_type'].value_counts()
        
        # Переводим названия паттернов
        pattern_translation = {
            'mixed_unstable': 'Нестабильное поведение',
            'chronic_criminal': 'Хронические преступники', 
            'escalating': 'Эскалация (админ→уголовка)',
            'deescalating': 'Деэскалация',
            'single': 'Единичные случаи'
        }
        
        pattern_stats.index = pattern_stats.index.map(pattern_translation)
        
        fig_patterns = px.bar(
            x=pattern_stats.values,
            y=pattern_stats.index,
            orientation='h',
            title="Распределение паттернов криминального поведения",
            color=pattern_stats.values,
            color_continuous_scale='Reds'
        )
        fig_patterns.update_layout(
            height=400,
            xaxis_title="Количество людей",
            yaxis_title="Тип паттерна"
        )
        st.plotly_chart(fig_patterns, use_container_width=True)
    
    # Возрастной анализ
    if 'current_age' in risk_df.columns:
        st.subheader("👥 Возрастной анализ по категориям риска")
        
        fig_age = px.box(
            risk_df,
            x='risk_category',
            y='current_age',
            title="Распределение возрастов по категориям риска",
            color='risk_category',
            color_discrete_map={
                "Критический": "#dc3545",
                "Высокий": "#ffc107", 
                "Средний": "#fd7e14",
                "Низкий": "#28a745"
            }
        )
        fig_age.update_layout(
            height=400,
            xaxis_title="Категория риска",
            yaxis_title="Возраст",
            showlegend=False
        )
        st.plotly_chart(fig_age, use_container_width=True)
    
    # Таблица сводной статистики
    st.subheader("📋 Сводная статистика по категориям")
    
    summary_stats = []
    for category in ["Критический", "Высокий", "Средний", "Низкий"]:
        category_data = risk_df[risk_df['risk_category'] == category]
        
        if len(category_data) > 0:
            stats = {
                "Категория": category,
                "Количество": len(category_data),
                "Процент": f"{len(category_data)/total_people*100:.1f}%",
                "Средний возраст": f"{category_data['current_age'].mean():.1f}" if 'current_age' in category_data.columns else "N/A",
                "Среднее кол-во дел": f"{category_data['total_cases'].mean():.1f}" if 'total_cases' in category_data.columns else "N/A",
                "Средний риск-балл": f"{category_data['risk_total_risk_score'].mean():.2f}" if 'risk_total_risk_score' in category_data.columns else "N/A"
            }
            summary_stats.append(stats)
    
    if summary_stats:
        summary_df = pd.DataFrame(summary_stats)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Экспорт сводки
        csv = summary_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Скачать сводку в CSV",
            data=csv,
            file_name=f'risk_categories_summary_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv'
        )

else:
    st.error("❌ Не удалось загрузить данные о рисках")
    
    st.markdown("""
    ### 📁 Требуемые файлы данных:
    Разместите в папке `data/`:
    - `RISK_ANALYSIS_RESULTS.xlsx` (файл с результатами анализа рисков)
    
    ### 📊 Формат данных:
    Файл должен содержать колонки:
    - ИИН
    - risk_total_risk_score (риск-балл от 0 до 10)
    - pattern_type (тип паттерна поведения)
    - current_age (текущий возраст)
    - total_cases (общее количество дел)
    """)

# Справочная информация
with st.expander("ℹ️ Справка по странице"):
    st.markdown("""
    **Что показывает эта страница:**
    - Распределение людей по 4 категориям риска
    - Светофор статусов (критично/внимание/норма)
    - Анализ паттернов криминального поведения
    - Возрастной анализ по категориям
    
    **Категории риска:**
    - 🔴 **Критический (7-10 баллов)**: Требует немедленного вмешательства
    - 🟡 **Высокий (5-6 баллов)**: Требует усиленного контроля
    - 🟠 **Средний (3-4 балла)**: Стандартный мониторинг
    - 🟢 **Низкий (0-2 балла)**: Минимальный контроль
    
    **Интерпретация статусов:**
    - 🔴 **Критично**: >30% людей в категории - требуются срочные меры
    - 🟡 **Внимание**: 15-30% людей в категории - усилить работу
    - 🟢 **Норма**: <15% людей в категории - ситуация под контролем
    """)
