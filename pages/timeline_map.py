"""
Карта временных окон
Интерактивная карта временных промежутков до различных типов преступлений
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# Настройка страницы
st.set_page_config(
    page_title="Карта временных окон",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Карта временных окон преступлений")
st.markdown("### Интерактивная визуализация временных промежутков от административных нарушений до тяжких преступлений")

# Функция загрузки данных
@st.cache_data
def load_crime_timeline_data():
    """Загружаем данные о временных окнах преступлений"""
    
    # Проверяем наличие файла с результатами анализа
    crime_file = "data/crime_analysis_results.xlsx"
    
    if os.path.exists(crime_file):
        try:
            # Пытаемся загрузить разные листы для создания timeline
            with pd.ExcelFile(crime_file) as excel_file:
                sheets = excel_file.sheet_names
                st.success(f"✅ Данные загружены из crime_analysis_results.xlsx (листы: {sheets})")
                
                # Пытаемся найти лист с временными данными или создать их из эскалации
                escalation_data = None
                if "Эскалация" in sheets:
                    escalation_df = pd.read_excel(crime_file, sheet_name="Эскалация")
                    
                    # Преобразуем данные эскалации в timeline
                    if not escalation_df.empty and 'Уголовное' in escalation_df.columns:
                        # Группируем по типам уголовных преступлений
                        crime_counts = escalation_df.groupby('Уголовное')['Количество переходов'].sum().reset_index()
                        
                        # Базовые временные окна из исследования
                        time_windows = {
                            'Мошенничество': 109,
                            'Кража': 146, 
                            'Убийство': 143,
                            'Вымогательство': 144,
                            'Грабеж': 148,
                            'Разбой': 150,
                            'Изнасилование': 157,
                            'Хулиганство': 155,
                            'Побои': 140
                        }
                        
                        # Базовые проценты предотвратимости
                        prevention_rates = {
                            'Мошенничество': 82.3,
                            'Кража': 87.3,
                            'Убийство': 97.0,
                            'Вымогательство': 100.7,
                            'Грабеж': 60.2,
                            'Разбой': 20.2,
                            'Изнасилование': 65.6,
                            'Хулиганство': 45.0,
                            'Побои': 75.0
                        }
                        
                        # Создаем timeline данные на основе реальных данных эскалации
                        timeline_data = []
                        for _, row in crime_counts.iterrows():
                            crime_type = row['Уголовное']
                            count = row['Количество переходов']
                            
                            # Определяем временное окно
                            days = time_windows.get(crime_type, 140)  # 140 дней по умолчанию
                            
                            # Определяем процент предотвратимости
                            prevention = prevention_rates.get(crime_type, 60.0)
                            
                            # Определяем категорию риска
                            if count > 1000:
                                risk_category = 'Критический'
                            elif count > 500:
                                risk_category = 'Высокий'
                            elif count > 100:
                                risk_category = 'Средний'
                            else:
                                risk_category = 'Низкий'
                            
                            timeline_data.append({
                                'Преступление': crime_type,
                                'Среднее_время_дней': days,
                                'Процент_предотвратимых': prevention,
                                'Количество_случаев': count,
                                'Категория_риска': risk_category
                            })
                        
                        if timeline_data:
                            df = pd.DataFrame(timeline_data)
                            st.info(f"📊 Создан timeline из {len(timeline_data)} типов преступлений на основе данных эскалации")
                            return df
                
                # Если не удалось создать из эскалации, используем демо-данные
                st.warning("⚠️ Не удалось создать timeline из файла, используем базовые данные")
                
        except Exception as e:
            st.warning(f"⚠️ Ошибка загрузки данных: {e}")
    
    # Если файл не найден или ошибка, используем данные из исследования
    timeline_data = {
        'Преступление': [
            'Мошенничество', 'Кража', 'Убийство', 'Вымогательство', 
            'Грабеж', 'Разбой', 'Изнасилование'
        ],
        'Среднее_время_дней': [109, 146, 143, 144, 148, 150, 157],
        'Процент_предотвратимых': [82.3, 87.3, 97.0, 100.7, 60.2, 20.2, 65.6],
        'Количество_случаев': [8832, 25201, 406, 564, 4130, 718, 299],
        'Категория_риска': [
            'Критический', 'Высокий', 'Критический', 'Критический',
            'Средний', 'Средний', 'Высокий'
        ]
    }
    
    df = pd.DataFrame(timeline_data)
    st.info("ℹ️ Используются данные из исследования (демо-режим)")
    return df

# Загружаем данные
timeline_df = load_crime_timeline_data()

if timeline_df is not None and len(timeline_df) > 0:
    
    # Фильтры в боковой панели
    st.sidebar.header("🎛️ Фильтры и настройки")
    
    # Фильтр по типу преступления
    if 'Преступление' in timeline_df.columns:
        selected_crimes = st.sidebar.multiselect(
            "Выберите типы преступлений:",
            options=timeline_df['Преступление'].unique(),
            default=timeline_df['Преступление'].unique()
        )
        filtered_df = timeline_df[timeline_df['Преступление'].isin(selected_crimes)]
    else:
        filtered_df = timeline_df
    
    # Фильтр по времени
    if 'Среднее_время_дней' in filtered_df.columns:
        min_days = int(filtered_df['Среднее_время_дней'].min())
        max_days = int(filtered_df['Среднее_время_дней'].max())
        
        time_range = st.sidebar.slider(
            "Диапазон времени (дни):",
            min_value=min_days,
            max_value=max_days,
            value=(min_days, max_days)
        )
        
        filtered_df = filtered_df[
            (filtered_df['Среднее_время_дней'] >= time_range[0]) &
            (filtered_df['Среднее_время_дней'] <= time_range[1])
        ]
    
    # Основная визуализация - Bubble Chart
    st.subheader("📊 Карта временных окон (Bubble Chart)")
    
    if len(filtered_df) > 0:
        # Проверяем наличие необходимых колонок
        required_columns = ['Преступление', 'Среднее_время_дней', 'Процент_предотвратимых', 'Количество_случаев']
        missing_columns = [col for col in required_columns if col not in filtered_df.columns]
        
        if missing_columns:
            st.error(f"❌ Отсутствуют колонки: {missing_columns}")
            st.write("📋 Доступные колонки:", list(filtered_df.columns))
            st.write("📄 Структура данных:")
            st.dataframe(filtered_df.head(), use_container_width=True)
        else:
            # Создаем bubble chart только если все колонки есть
            try:
                fig = px.scatter(
                    filtered_df,
                    x='Среднее_время_дней',
                    y='Процент_предотвратимых',
                    size='Количество_случаев',
                    color='Категория_риска',
                    hover_name='Преступление',
                    hover_data={
                        'Среднее_время_дней': ':,.0f',
                        'Процент_предотвратимых': ':,.1f',
                        'Количество_случаев': ':,.0f'
                    },
                    labels={
                        'Среднее_время_дней': 'Среднее время до преступления (дни)',
                        'Процент_предотвратимых': 'Процент предотвратимых (%)',
                        'Количество_случаев': 'Количество случаев'
                    },
                    color_discrete_map={
                        'Критический': '#e74c3c',
                        'Высокий': '#f39c12', 
                        'Средний': '#f1c40f',
                        'Низкий': '#27ae60'
                    },
                    title="Временные окна преступлений: размер = количество случаев, цвет = уровень риска"
                )
                
                fig.update_layout(
                    height=600,
                    showlegend=True,
                    xaxis_title="Среднее время до преступления (дни)",
                    yaxis_title="Процент предотвратимых случаев (%)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Ошибка создания графика: {e}")
                st.write("📄 Отладочная информация:")
                st.write("Структура данных:", filtered_df.dtypes)
                st.dataframe(filtered_df.head(), use_container_width=True)
        
        # Дополнительная информация в двух колонках
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⏰ Критические временные окна")
            
            # Сортируем по времени для отображения критических периодов
            critical_df = filtered_df.sort_values('Среднее_время_дней').head(5)
            
            for _, row in critical_df.iterrows():
                if 'Преступление' in row and 'Среднее_время_дней' in row:
                    days = int(row['Среднее_время_дней'])
                    crime = row['Преступление']
                    
                    if days <= 120:
                        color = "🔴"
                    elif days <= 150:
                        color = "🟡"
                    else:
                        color = "🟢"
                    
                    st.markdown(f"{color} **{crime}**: {days} дней")
        
        with col2:
            st.subheader("📈 Возможности превенции")
            
            # Сортируем по проценту предотвратимых
            preventable_df = filtered_df.sort_values('Процент_предотвратимых', ascending=False).head(5)
            
            for _, row in preventable_df.iterrows():
                if 'Преступление' in row and 'Процент_предотвратимых' in row:
                    percent = row['Процент_предотвратимых']
                    crime = row['Преступление']
                    
                    if percent >= 80:
                        icon = "🎯"
                    elif percent >= 60:
                        icon = "🎪"
                    else:
                        icon = "📋"
                    
                    st.markdown(f"{icon} **{crime}**: {percent:.1f}% предотвратимо")
        
        # Временная шкала
        st.subheader("📅 Временная шкала эскалации")
        
        # Создаем timeline chart
        fig_timeline = px.bar(
            filtered_df.sort_values('Среднее_время_дней'),
            x='Преступление',
            y='Среднее_время_дней',
            color='Категория_риска',
            title="Временная шкала: от быстрой к медленной эскалации",
            color_discrete_map={
                'Критический': '#e74c3c',
                'Высокий': '#f39c12', 
                'Средний': '#f1c40f',
                'Низкий': '#27ae60'
            }
        )
        
        fig_timeline.update_layout(
            height=400,
            xaxis_title="Тип преступления",
            yaxis_title="Дни до преступления"
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Таблица с данными
        st.subheader("📋 Детальные данные")
        
        # Форматируем таблицу для отображения
        display_df = filtered_df.copy()
        
        if 'Среднее_время_дней' in display_df.columns:
            display_df['Среднее_время_дней'] = display_df['Среднее_время_дней'].round(0).astype(int)
        if 'Процент_предотвратимых' in display_df.columns:
            display_df['Процент_предотвратимых'] = display_df['Процент_предотвратимых'].round(1)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Экспорт данных
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Скачать данные в CSV",
            data=csv,
            file_name=f'timeline_data_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv'
        )
    
    else:
        st.warning("⚠️ Нет данных для отображения с выбранными фильтрами")

else:
    st.error("❌ Не удалось загрузить данные. Проверьте наличие файлов в папке data/")
    
    # Инструкции по устранению проблемы
    st.markdown("""
    ### 📁 Требуемые файлы данных:
    Разместите в папке `data/`:
    - `crime_analysis_results.xlsx` (основной файл с результатами анализа)
    - Или любой другой файл с данными о временных окнах преступлений
    
    ### 📊 Формат данных:
    Файл должен содержать колонки:
    - Название преступления
    - Среднее время в днях
    - Процент предотвратимых случаев
    - Количество случаев
    """)

# Справочная информация
with st.expander("ℹ️ Справка по странице"):
    st.markdown("""
    **Что показывает эта страница:**
    - Среднее время от административного нарушения до тяжкого преступления
    - Процент случаев, которые можно предотвратить
    - Количество зарегистрированных случаев каждого типа
    
    **Как пользоваться:**
    - Используйте фильтры в боковой панели для настройки отображения
    - Наводите курсор на точки для получения детальной информации
    - Размер точки показывает количество случаев
    - Цвет точки показывает уровень критичности
    
    **Интерпретация:**
    - Чем левее точка (меньше дней), тем быстрее происходит эскалация
    - Чем выше точка (больше %), тем больше возможностей для превенции
    - Большие точки показывают наиболее распространенные преступления
    """) 