"""
👥 Списки лиц под риском
Категоризированные списки лиц с различными уровнями риска рецидива
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from datetime import datetime, timedelta

# Настройка страницы
st.set_page_config(
    page_title="Списки лиц под риском",
    page_icon="👥",
    layout="wide"
)

st.title("👥 Списки лиц под риском")
st.markdown("### Категоризированные списки лиц с различными уровнями риска рецидива")

# Функция загрузки данных о лицах под риском
@st.cache_data
def load_risk_persons_data():
    """Загружаем данные о лицах под риском"""
    
    # Проверяем наличие файла с результатами анализа рисков
    risk_file = "data/RISK_ANALYSIS_RESULTS.xlsx"
    
    if os.path.exists(risk_file):
        try:
            df = pd.read_excel(risk_file)
            st.success("✅ Данные загружены из RISK_ANALYSIS_RESULTS.xlsx")
            return df
        except Exception as e:
            st.warning(f"⚠️ Ошибка загрузки данных: {e}")
    
    # Если файл не найден, создаем демо-данные
    np.random.seed(42)
    n_people = 12333  # Количество рецидивистов из исследования
    
    # Создаем реалистичные демо-данные
    demo_data = {
        'ИИН': [f"***-***-{str(i).zfill(4)}" for i in range(1, n_people + 1)],
        'Фамилия': [f"ФАМИЛИЯ_{i:05d}" for i in range(1, n_people + 1)],
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
            datetime.now() - timedelta(days=np.random.randint(1, 730))
            for _ in range(n_people)
        ],
        'last_violation_type': np.random.choice([
            'Административное правонарушение', 'Кража', 'Мошенничество', 
            'Хулиганство', 'Грабеж', 'Побои'
        ], n_people, p=[0.4, 0.25, 0.15, 0.1, 0.05, 0.05])
    }
    
    df = pd.DataFrame(demo_data)
    st.info("ℹ️ Используются демо-данные на основе исследования")
    return df

# Функция для определения категории риска
def get_risk_category(risk_score):
    """Определяем категорию риска по баллу"""
    if risk_score >= 7:
        return "🔴 Критический"
    elif risk_score >= 5:
        return "🟡 Высокий" 
    elif risk_score >= 3:
        return "🟠 Средний"
    else:
        return "🟢 Низкий"

# Функция для определения статуса контроля
def get_control_status(risk_score, days_since_last):
    """Определяем статус контроля"""
    if risk_score >= 7:
        return "🚨 Требует немедленного вмешательства"
    elif risk_score >= 5:
        return "⚠️ Усиленный контроль"
    elif days_since_last < 90:
        return "👁️ На мониторинге"
    else:
        return "📋 Стандартный контроль"

# Загружаем данные
risk_df = load_risk_persons_data()

if risk_df is not None and len(risk_df) > 0:
    
    # Добавляем категории риска и статусы
    if 'risk_total_risk_score' in risk_df.columns:
        risk_df['risk_category'] = risk_df['risk_total_risk_score'].apply(get_risk_category)
    else:
        risk_df['risk_category'] = np.random.choice([
            "🔴 Критический", "🟡 Высокий", "🟠 Средний", "🟢 Низкий"
        ], len(risk_df), p=[0.15, 0.25, 0.35, 0.25])
    
    # Создаем объединенное поле ФИО если есть отдельные поля
    if all(col in risk_df.columns for col in ['Фамилия', 'Имя', 'Отчество']):
        risk_df['ФИО_full'] = risk_df['Фамилия'].astype(str) + ' ' + risk_df['Имя'].astype(str) + ' ' + risk_df['Отчество'].astype(str)
        risk_df['ФИО_full'] = risk_df['ФИО_full'].str.replace(' nan', '').str.replace('nan ', '').str.strip()
    elif 'ФИО' not in risk_df.columns:
        # Если нет ни отдельных полей, ни объединенного ФИО
        risk_df['ФИО_full'] = risk_df['ИИН'].astype(str)  # Используем ИИН как резерв
    else:
        risk_df['ФИО_full'] = risk_df['ФИО']
    
    # Добавляем дни с последнего нарушения
    if 'last_violation_date' in risk_df.columns:
        risk_df['days_since_last'] = (datetime.now() - risk_df['last_violation_date']).dt.days
        risk_df['control_status'] = risk_df.apply(
            lambda x: get_control_status(x.get('risk_total_risk_score', 0), x['days_since_last']), 
            axis=1
        )
    else:
        risk_df['days_since_last'] = np.random.randint(1, 730, len(risk_df))
        risk_df['control_status'] = "📋 Стандартный контроль"
    
    # Фильтры в боковой панели
    st.sidebar.header("🎛️ Фильтры")
    
    # Фильтр по категории риска
    selected_categories = st.sidebar.multiselect(
        "Категории риска:",
        options=risk_df['risk_category'].unique(),
        default=risk_df['risk_category'].unique()
    )
    
    # Фильтр по возрасту
    age_range = st.sidebar.slider(
        "Возраст:",
        min_value=int(risk_df['current_age'].min()) if 'current_age' in risk_df.columns else 18,
        max_value=int(risk_df['current_age'].max()) if 'current_age' in risk_df.columns else 70,
        value=(25, 45)
    )
    
    # Фильтр по количеству дел
    if 'total_cases' in risk_df.columns:
        min_cases = st.sidebar.number_input(
            "Минимум дел:",
            min_value=1,
            max_value=int(risk_df['total_cases'].max()),
            value=1
        )
    else:
        min_cases = 1
    
    # Фильтр по дням с последнего нарушения
    max_days_since = st.sidebar.slider(
        "Максимум дней с последнего нарушения:",
        min_value=1,
        max_value=730,
        value=365
    )
    
    # Применяем фильтры
    filtered_df = risk_df[
        (risk_df['risk_category'].isin(selected_categories)) &
        (risk_df['current_age'] >= age_range[0]) &
        (risk_df['current_age'] <= age_range[1]) &
        (risk_df['total_cases'] >= min_cases) &
        (risk_df['days_since_last'] <= max_days_since)
    ]
    
    # Общая статистика
    st.subheader("📊 Общая статистика после фильтрации")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Всего лиц", f"{len(filtered_df):,}")
    
    with col2:
        critical_count = len(filtered_df[filtered_df['risk_category'] == "🔴 Критический"])
        st.metric("Критический риск", f"{critical_count:,}")
    
    with col3:
        if 'total_cases' in filtered_df.columns:
            avg_cases = filtered_df['total_cases'].mean()
            st.metric("Среднее кол-во дел", f"{avg_cases:.1f}")
    
    with col4:
        if 'risk_total_risk_score' in filtered_df.columns:
            avg_risk = filtered_df['risk_total_risk_score'].mean()
            st.metric("Средний риск-балл", f"{avg_risk:.2f}")
    
    # Списки по категориям риска
    st.subheader("👥 Списки лиц по категориям риска")
    
    # Создаем вкладки для каждой категории
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔴 Критический", "🟡 Высокий", "🟠 Средний", "🟢 Низкий"
    ])
    
    # Функция для отображения списка категории
    def display_category_list(category, tab):
        with tab:
            category_df = filtered_df[filtered_df['risk_category'] == category].copy()
            
            if len(category_df) > 0:
                # Сортируем по риск-баллу (по убыванию)
                if 'risk_total_risk_score' in category_df.columns:
                    category_df = category_df.sort_values('risk_total_risk_score', ascending=False)
                
                st.markdown(f"**Найдено: {len(category_df)} человек**")
                
                # Выбор количества записей для отображения
                display_count = st.selectbox(
                    f"Показать записей ({category}):",
                    options=[10, 25, 50, 100, "Все"],
                    key=f"display_count_{category}"
                )
                
                if display_count != "Все":
                    display_df = category_df.head(display_count)
                else:
                    display_df = category_df
                
                # Подготавливаем данные для отображения
                display_columns = ['ИИН']
                
                # Добавляем ФИО если есть
                if 'ФИО_full' in display_df.columns:
                    display_columns.append('ФИО_full')
                
                # Добавляем остальные колонки
                display_columns.extend(['current_age', 'gender'])
                
                if 'risk_total_risk_score' in display_df.columns:
                    display_columns.append('risk_total_risk_score')
                if 'total_cases' in display_df.columns:
                    display_columns.append('total_cases')
                if 'criminal_count' in display_df.columns:
                    display_columns.append('criminal_count')
                if 'last_violation_type' in display_df.columns:
                    display_columns.append('last_violation_type')
                if 'days_since_last' in display_df.columns:
                    display_columns.append('days_since_last')
                if 'control_status' in display_df.columns:
                    display_columns.append('control_status')
                
                # Фильтруем только существующие колонки
                available_columns = [col for col in display_columns if col in display_df.columns]
                table_df = display_df[available_columns].copy()
                
                # Переименовываем колонки для лучшего отображения
                column_rename = {
                    'ИИН': 'ИИН',
                    'ФИО_full': 'ФИО',
                    'current_age': 'Возраст',
                    'gender': 'Пол',
                    'risk_total_risk_score': 'Риск-балл',
                    'total_cases': 'Всего дел',
                    'criminal_count': 'Уголовных',
                    'last_violation_type': 'Последнее нарушение',
                    'days_since_last': 'Дней назад',
                    'control_status': 'Статус контроля'
                }
                
                table_df = table_df.rename(columns=column_rename)
                
                # Форматируем числовые колонки
                if 'Риск-балл' in table_df.columns:
                    table_df['Риск-балл'] = table_df['Риск-балл'].round(2)
                
                # Применяем стилизацию для категории
                def style_category_table(df, category):
                    def highlight_rows(row):
                        if category == "🔴 Критический":
                            return ['background-color: #ffe6e6'] * len(row)
                        elif category == "🟡 Высокий":
                            return ['background-color: #fff8e1'] * len(row)
                        elif category == "🟠 Средний":
                            return ['background-color: #f3e5f5'] * len(row)
                        else:
                            return ['background-color: #e8f5e8'] * len(row)
                    
                    styled = df.style.apply(highlight_rows, axis=1)
                    
                    # Форматирование для числовых колонок
                    format_dict = {}
                    if 'Риск-балл' in df.columns:
                        format_dict['Риск-балл'] = '{:.2f}'
                    
                    if format_dict:
                        styled = styled.format(format_dict)
                    
                    return styled
                
                # Отображаем таблицу
                st.dataframe(
                    style_category_table(table_df, category),
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                
                # Кнопка экспорта для категории
                csv = table_df.to_csv(index=False).encode('utf-8')
                category_name = category.replace("🔴 ", "").replace("🟡 ", "").replace("🟠 ", "").replace("🟢 ", "")
                st.download_button(
                    label=f"📥 Скачать список ({category})",
                    data=csv,
                    file_name=f'risk_list_{category_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    mime='text/csv',
                    key=f"download_{category}"
                )
                
                # Дополнительная статистика для категории
                if len(category_df) > 0:
                    st.markdown("**Статистика категории:**")
                    
                    stats_col1, stats_col2, stats_col3 = st.columns(3)
                    
                    with stats_col1:
                        if 'current_age' in category_df.columns:
                            avg_age = category_df['current_age'].mean()
                            st.write(f"Средний возраст: **{avg_age:.1f}** лет")
                    
                    with stats_col2:
                        if 'total_cases' in category_df.columns:
                            avg_cases = category_df['total_cases'].mean()
                            st.write(f"Среднее кол-во дел: **{avg_cases:.1f}**")
                    
                    with stats_col3:
                        if 'days_since_last' in category_df.columns:
                            avg_days = category_df['days_since_last'].mean()
                            st.write(f"Среднее дней с последнего: **{avg_days:.0f}**")
            
            else:
                st.info(f"Нет данных для категории {category} с выбранными фильтрами")
    
    # Отображаем списки для каждой категории
    display_category_list("🔴 Критический", tab1)
    display_category_list("🟡 Высокий", tab2) 
    display_category_list("🟠 Средний", tab3)
    display_category_list("🟢 Низкий", tab4)
    
    # Сводный экспорт всех данных
    st.markdown("---")
    st.subheader("📥 Экспорт всех данных")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Экспорт отфильтрованных данных
        if len(filtered_df) > 0:
            export_df = filtered_df.copy()
            
            # Переименовываем колонки для экспорта
            column_rename = {
                'ИИН': 'ИИН',
                'ФИО_full': 'ФИО',
                'current_age': 'Возраст',
                'gender': 'Пол',
                'risk_category': 'Категория_риска',
                'risk_total_risk_score': 'Риск_балл',
                'total_cases': 'Всего_дел',
                'criminal_count': 'Уголовных',
                'admin_count': 'Административных',
                'last_violation_type': 'Последнее_нарушение',
                'days_since_last': 'Дней_с_последнего',
                'control_status': 'Статус_контроля'
            }
            
            # Переименовываем только существующие колонки
            rename_dict = {k: v for k, v in column_rename.items() if k in export_df.columns}
            export_df = export_df.rename(columns=rename_dict)
            
            csv_all = export_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Скачать все отфильтрованные данные",
                data=csv_all,
                file_name=f'all_risk_persons_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
    
    with col2:
        # Экспорт только критических
        critical_df = filtered_df[filtered_df['risk_category'] == "🔴 Критический"]
        if len(critical_df) > 0:
            csv_critical = critical_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="🚨 Скачать только критических",
                data=csv_critical,
                file_name=f'critical_risk_persons_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )

else:
    st.error("❌ Не удалось загрузить данные о лицах под риском")
    
    st.markdown("""
    ### 📁 Требуемые файлы данных:
    Разместите в папке `data/`:
    - `RISK_ANALYSIS_RESULTS.xlsx` (файл с результатами анализа рисков)
    
    ### 📊 Формат данных:
    Файл должен содержать колонки:
    - ИИН
    - risk_total_risk_score (риск-балл от 0 до 10)
    - current_age (текущий возраст)
    - total_cases (общее количество дел)
    - criminal_count (количество уголовных дел)
    - pattern_type (тип паттерна поведения)
    """)

# Справочная информация
with st.expander("ℹ️ Справка по странице"):
    st.markdown("""
    **Что показывает эта страница:**
    - Списки людей по 4 категориям риска
    - Детальную информацию о каждом лице
    - Статусы контроля и рекомендации
    - Возможность фильтрации и сортировки
    
    **Категории риска:**
    - 🔴 **Критический (7-10 баллов)**: Требует немедленного вмешательства
    - 🟡 **Высокий (5-6 баллов)**: Требует усиленного контроля
    - 🟠 **Средний (3-4 балла)**: Стандартный мониторинг
    - 🟢 **Низкий (0-2 балла)**: Минимальный контроль
    
    **Статусы контроля:**
    - 🚨 **Требует немедленного вмешательства**: Риск 7+ баллов
    - ⚠️ **Усиленный контроль**: Риск 5-6 баллов
    - 👁️ **На мониторинге**: Недавние нарушения (<90 дней)
    - 📋 **Стандартный контроль**: Обычное наблюдение
    
    **Как пользоваться:**
    - Используйте фильтры в боковой панели
    - Переключайтесь между вкладками категорий
    - Экспортируйте списки для практической работы
    - Сортировка автоматически по риск-баллу (по убыванию)
    """)
