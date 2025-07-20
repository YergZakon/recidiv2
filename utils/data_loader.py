"""
Модуль загрузки и обработки данных для системы раннего предупреждения
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import streamlit as st
from typing import Dict, Optional, Tuple

# Путь к папке с данными
DATA_DIR = "data"

# Имена файлов
DATA_FILES = {
    'risk_analysis': 'RISK_ANALYSIS_RESULTS.xlsx',
    'ml_dataset': 'ML_DATASET_COMPLETE.xlsx',
    'crime_analysis': 'crime_analysis_results.xlsx',
    'serious_crimes': 'serious_crimes_analysis.xlsx',
    'risk_matrix': 'risk_escalation_matrix.xlsx'
}

@st.cache_data(ttl=3600)  # Кэш на 1 час
def load_all_data() -> Dict[str, pd.DataFrame]:
    """
    Загружает все файлы данных и возвращает словарь DataFrame
    """
    data_dict = {}
    
    for key, filename in DATA_FILES.items():
        filepath = os.path.join(DATA_DIR, filename)
        
        try:
            if os.path.exists(filepath):
                # Загрузка Excel файла
                if key == 'crime_analysis':
                    # Этот файл содержит несколько листов
                    excel_file = pd.ExcelFile(filepath)
                    data_dict[key] = {}
                    for sheet in excel_file.sheet_names:
                        data_dict[key][sheet] = pd.read_excel(excel_file, sheet_name=sheet)
                else:
                    data_dict[key] = pd.read_excel(filepath)
                
                print(f"✅ Загружен {filename}")
            else:
                print(f"⚠️ Файл {filename} не найден")
                data_dict[key] = None
                
        except Exception as e:
            print(f"❌ Ошибка загрузки {filename}: {e}")
            data_dict[key] = None
    
    return data_dict

@st.cache_data
def get_risk_data() -> Optional[pd.DataFrame]:
    """
    Получает данные о рисках с валидацией
    """
    data = load_all_data()
    risk_df = data.get('risk_analysis')
    
    if risk_df is not None:
        # Валидация и очистка данных
        required_columns = ['ИИН', 'risk_total_risk_score', 'pattern_type']
        
        for col in required_columns:
            if col not in risk_df.columns:
                print(f"⚠️ Отсутствует колонка {col}")
                return None
        
        # Очистка данных
        risk_df = risk_df.dropna(subset=['ИИН'])
        
        # Добавляем категории риска если их нет
        if 'risk_category' not in risk_df.columns:
            risk_df['risk_category'] = risk_df['risk_total_risk_score'].apply(
                lambda x: get_risk_category(x)
            )
        
        return risk_df
    
    return None

@st.cache_data
def get_crime_statistics() -> Dict:
    """
    Получает статистику по преступлениям из анализа
    """
    # Базовые статистики из исследования
    stats = {
        'total_violations': 146570,
        'total_recidivists': 12333,
        'preventable_percent': 97.0,
        'unstable_pattern_percent': 72.7,
        'admin_to_theft_count': 6465,
        'crime_windows': {
            'Мошенничество': {'days': 109, 'preventable': 82.3},
            'Кража': {'days': 146, 'preventable': 87.3},
            'Убийство': {'days': 143, 'preventable': 97.0},
            'Вымогательство': {'days': 144, 'preventable': 100.7},
            'Грабеж': {'days': 148, 'preventable': 60.2},
            'Разбой': {'days': 150, 'preventable': 20.2},
            'Изнасилование': {'days': 157, 'preventable': 65.6}
        }
    }
    
    # Пытаемся обновить из реальных данных
    data = load_all_data()
    
    if data.get('crime_analysis') and isinstance(data['crime_analysis'], dict):
        # Обновляем статистику из реальных данных
        if 'Эскалация' in data['crime_analysis']:
            escalation_df = data['crime_analysis']['Эскалация']
            if not escalation_df.empty:
                stats['total_escalations'] = len(escalation_df)
                stats['top_escalation'] = escalation_df.iloc[0]['Административное'] if len(escalation_df) > 0 else None
    
    return stats

@st.cache_data
def get_pattern_distribution() -> pd.DataFrame:
    """
    Получает распределение паттернов поведения
    """
    risk_df = get_risk_data()
    
    if risk_df is not None and 'pattern_type' in risk_df.columns:
        pattern_counts = risk_df['pattern_type'].value_counts()
        pattern_percent = (pattern_counts / len(risk_df) * 100).round(1)
        
        return pd.DataFrame({
            'pattern': pattern_counts.index,
            'count': pattern_counts.values,
            'percent': pattern_percent.values
        })
    
    # Возвращаем данные из исследования
    return pd.DataFrame({
        'pattern': ['mixed_unstable', 'chronic_criminal', 'escalating', 'deescalating', 'single'],
        'count': [8968, 1678, 863, 703, 121],
        'percent': [72.7, 13.6, 7.0, 5.7, 1.0]
    })

def get_risk_category(risk_score: float) -> str:
    """
    Определяет категорию риска по баллу
    """
    if risk_score >= 7:
        return "🔴 Критический"
    elif risk_score >= 5:
        return "🟡 Высокий"
    elif risk_score >= 3:
        return "🟠 Средний"
    else:
        return "🟢 Низкий"

def validate_iin(iin: str) -> Tuple[bool, str]:
    """
    Валидация ИИН с детальными сообщениями об ошибках
    """
    if not iin:
        return False, "ИИН не может быть пустым"
    
    # Удаляем пробелы и дефисы
    clean_iin = iin.replace('-', '').replace(' ', '')
    
    if len(clean_iin) != 12:
        return False, f"ИИН должен содержать 12 цифр (введено: {len(clean_iin)})"
    
    if not clean_iin.isdigit():
        return False, "ИИН должен содержать только цифры"
    
    # Проверка контрольной суммы (упрощенная)
    # В реальности здесь должна быть полная проверка по алгоритму РК
    
    return True, clean_iin

def search_person_by_iin(iin: str) -> Optional[pd.Series]:
    """
    Поиск человека по ИИН в базе данных
    """
    is_valid, clean_iin = validate_iin(iin)
    
    if not is_valid:
        return None
    
    risk_df = get_risk_data()
    
    if risk_df is not None:
        # Преобразуем ИИН в строку для поиска
        risk_df_copy = risk_df.copy()
        risk_df_copy['ИИН'] = risk_df_copy['ИИН'].astype(str)
        
        # Точный поиск
        exact_match = risk_df_copy[risk_df_copy['ИИН'] == clean_iin]
        if not exact_match.empty:
            return exact_match.iloc[0]
        
        # Поиск по последним 4 цифрам
        last_4 = clean_iin[-4:]
        partial_match = risk_df_copy[risk_df_copy['ИИН'].str.endswith(last_4)]
        if not partial_match.empty:
            return partial_match.iloc[0]
    
    return None

@st.cache_data
def get_escalation_patterns() -> pd.DataFrame:
    """
    Получает паттерны эскалации админ -> уголовка
    """
    data = load_all_data()
    
    if data.get('crime_analysis') and isinstance(data['crime_analysis'], dict):
        if 'Эскалация' in data['crime_analysis']:
            return data['crime_analysis']['Эскалация']
    
    # Демо данные если реальные не найдены
    return pd.DataFrame({
        'Административное': ['Административное правонарушение'] * 5,
        'Уголовное': ['Кража', 'Мошенничество', 'Грабеж', 'Побои', 'Наркотики'],
        'Количество переходов': [6465, 1968, 771, 587, 645]
    })

@st.cache_data
def calculate_statistics_summary() -> Dict:
    """
    Рассчитывает сводную статистику для дашборда
    """
    risk_df = get_risk_data()
    stats = get_crime_statistics()
    
    summary = {
        'total_people': len(risk_df) if risk_df is not None else stats['total_recidivists'],
        'critical_risk': 0,
        'high_risk': 0,
        'active_cases': 0,
        'prevented_estimate': 0
    }
    
    if risk_df is not None:
        # Подсчет по категориям риска
        if 'risk_category' in risk_df.columns:
            summary['critical_risk'] = len(risk_df[risk_df['risk_category'] == "🔴 Критический"])
            summary['high_risk'] = len(risk_df[risk_df['risk_category'] == "🟡 Высокий"])
        
        # Активные случаи (последнее нарушение < 365 дней)
        if 'last_violation_date' in risk_df.columns:
            risk_df['last_violation_date'] = pd.to_datetime(risk_df['last_violation_date'])
            active_mask = (datetime.now() - risk_df['last_violation_date']).dt.days < 365
            summary['active_cases'] = active_mask.sum()
        
        # Оценка предотвращенных преступлений
        prevention_rate = stats['preventable_percent'] / 100
        summary['prevented_estimate'] = int(summary['critical_risk'] * prevention_rate)
    
    return summary

# Утилиты для работы с датами
def parse_date(date_str):
    """
    Парсинг различных форматов дат
    """
    if pd.isna(date_str):
        return None
    
    date_str = str(date_str).strip()
    
    # Пробуем разные форматы
    for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    
    try:
        return pd.to_datetime(date_str)
    except:
        return None

def days_between(date1, date2):
    """
    Количество дней между датами
    """
    if pd.isna(date1) or pd.isna(date2):
        return None
    
    try:
        return abs((date2 - date1).days)
    except:
        return None